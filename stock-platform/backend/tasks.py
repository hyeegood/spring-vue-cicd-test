"""
Celery and inline tasks for data updates.
"""
from datetime import date, datetime
from sqlalchemy import desc
from database import SessionLocal
from models import Stock, StockScore, PriceHistory, StockHistory
from data_fetcher import fetch_financials, fetch_prices, update_stock_prices_and_financials
from alternative_data_fetcher import update_alternative_data
from options_fetcher import update_options_data, fetch_options_chain
from news_fetcher import fetch_news, save_news_for_stock
from sentiment_analyzer import batch_sentiment
from scoring_engine import compute_total_score
from recommendation_engine import update_recommendation_for_stock
from glassdoor_fetcher import update_stock_glassdoor
import yfinance as yf
import math


def _technical_from_prices(ticker: str) -> dict:
    """Compute RSI, MA trend, momentum from price history."""
    t = yf.Ticker(ticker)
    hist = t.history(period="3mo")
    if hist is None or len(hist) < 25:
        return {"rsi": None, "ma_trend": "downtrend", "momentum": "neutral"}
    close = hist["Close"]
    # RSI
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)
    avg_gain = gain.rolling(14).mean().iloc[-1] if len(gain) >= 14 else 0
    avg_loss = loss.rolling(14).mean().iloc[-1] if len(loss) >= 14 else 0
    rs = avg_gain / avg_loss if avg_loss and avg_loss != 0 else 0
    rsi = 100 - (100 / (1 + rs)) if rs is not None and not math.isnan(rs) else None
    # MA trend: 20 vs 50
    ma20 = close.rolling(20).mean().iloc[-1] if len(close) >= 20 else None
    ma50 = close.rolling(50).mean().iloc[-1] if len(close) >= 50 else None
    current = close.iloc[-1]
    if ma20 and ma50:
        if ma20 > ma50 and close.iloc[-2] <= close.iloc[-1]:
            ma_trend = "golden_cross"
        elif ma20 > ma50:
            ma_trend = "uptrend"
        else:
            ma_trend = "downtrend"
    else:
        ma_trend = "downtrend"
    # Momentum: 20-day return
    if len(close) >= 20:
        ret = (close.iloc[-1] - close.iloc[-20]) / close.iloc[-20] if close.iloc[-20] else 0
        momentum = "strong" if ret > 0.05 else ("weak" if ret < -0.05 else "neutral")
    else:
        momentum = "neutral"
    return {"rsi": float(rsi) if rsi is not None else None, "ma_trend": ma_trend, "momentum": momentum}


def _set_fallback_glassdoor_rating(db, stock, financials: dict, sentiment: float):
    """Glassdoor API 구독 없을 때 재무/감성으로 1~5 대체 기업평점 (종목마다 다르게)."""
    score = 2.8
    if financials:
        roe = financials.get("roe")
        if roe is not None:
            score += min(1.0, max(-0.5, roe / 35))  # ROE 20 -> +0.57, 10 -> +0.29, 0 -> 0, 음수 -> 감점
        per = financials.get("per")
        if per is not None:
            if 10 <= per <= 20:
                score += 0.25
            elif 20 < per <= 30:
                score += 0.1
            elif per > 50:
                score -= 0.2
        om = financials.get("operating_margin")
        if om is not None and om > 0:
            score += min(0.4, om / 60)
        debt = financials.get("debt_ratio")
        if debt is not None and debt > 100:
            score -= 0.15
    if sentiment is not None:
        score += sentiment * 0.4
    # ticker별 미세 차이 (동일 재무여도 종목마다 다르게)
    seed = sum(ord(c) for c in (stock.ticker or "")) % 100
    score += (seed - 50) / 200
    score = max(1.0, min(5.0, round(score, 1)))
    stock.glassdoor_rating = score
    if stock.ceo_approval is None:
        stock.ceo_approval = min(98, max(40, int(50 + score * 12)))
    if stock.employee_recommendation is None:
        stock.employee_recommendation = min(98, max(40, int(50 + score * 12)))


def update_single_stock(ticker: str) -> bool:
    """Update one stock: prices, financials, score, recommendation, glassdoor, news. Returns True on success."""
    db = SessionLocal()
    try:
        s = db.query(Stock).filter(Stock.ticker == ticker.upper()).first()
        if not s:
            return False
        update_stock_prices_and_financials(ticker)
        financials = fetch_financials(ticker)
        alt = update_alternative_data(ticker)
        update_options_data(ticker)
        tech = _technical_from_prices(ticker)
        articles = fetch_news(ticker, s.company_name or "")
        sentiments = batch_sentiment([a.get("title") or "" for a in articles])
        save_news_for_stock(s.id, articles, sentiments)
        avg_sent = sum(sentiments.values()) / len(sentiments) if sentiments else 0.0
        total = compute_total_score(
            roe=financials.get("roe"),
            per=financials.get("per"),
            pbr=financials.get("pbr"),
            peg=financials.get("peg"),
            ev_ebitda=financials.get("ev_ebitda"),
            operating_margin=financials.get("operating_margin"),
            debt_ratio=financials.get("debt_ratio"),
            fcf_growth=financials.get("fcf_growth"),
            institutional_ownership=alt.get("institutional_ownership"),
            insider_activity=alt.get("insider_activity", "neutral"),
            short_interest=alt.get("short_interest"),
            employee_growth=s.linkedin_employee_growth or alt.get("employee_growth"),
            rsi=tech.get("rsi"),
            ma_trend=tech.get("ma_trend", "downtrend"),
            momentum=tech.get("momentum", "neutral"),
            sentiment_score=avg_sent,
        )
        today = date.today()
        existing = db.query(StockScore).filter(StockScore.stock_id == s.id, StockScore.date == today).first()
        if existing:
            existing.score = total
            existing.roe = financials.get("roe")
            existing.per = financials.get("per")
            existing.rsi = tech.get("rsi")
            existing.sentiment_score = avg_sent
        else:
            db.add(StockScore(
                stock_id=s.id,
                date=today,
                roe=financials.get("roe"),
                per=financials.get("per"),
                pbr=financials.get("pbr"),
                peg=financials.get("peg"),
                ev_ebitda=financials.get("ev_ebitda"),
                operating_margin=financials.get("operating_margin"),
                debt_ratio=financials.get("debt_ratio"),
                fcf=financials.get("fcf_growth"),
                institutional_ownership=alt.get("institutional_ownership"),
                insider_buying=5 if alt.get("insider_activity") == "buying" else (2 if alt.get("insider_activity") == "neutral" else 0),
                short_interest=alt.get("short_interest"),
                rsi=tech.get("rsi"),
                ma_trend=3 if tech.get("ma_trend") == "golden_cross" else (2 if tech.get("ma_trend") == "uptrend" else 0),
                momentum=3 if tech.get("momentum") == "strong" else (1 if tech.get("momentum") == "neutral" else 0),
                sentiment_score=avg_sent,
                score=total,
            ))
        update_recommendation_for_stock(ticker)
        try:
            updated = update_stock_glassdoor(s.id, s.company_name or s.ticker, s.ticker or "")
            if not updated and s.glassdoor_rating is None:
                _set_fallback_glassdoor_rating(db, s, financials, avg_sent)
        except Exception:
            _set_fallback_glassdoor_rating(db, s, financials, avg_sent)
        # 종목 이력: 새로고침 시점마다 1행 쌓기
        latest_ph = db.query(PriceHistory).filter(PriceHistory.stock_id == s.id).order_by(desc(PriceHistory.date)).first()
        db.add(StockHistory(
            stock_id=s.id,
            refreshed_at=datetime.utcnow(),
            price=latest_ph.price if latest_ph else None,
            score=total,
            roe=financials.get("roe"),
            per=financials.get("per"),
        ))
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def run_all_scheduled_updates():
    """Fetch financial data, prices, indicators, scores, news sentiment, alternative data."""
    db = SessionLocal()
    try:
        stocks = db.query(Stock).all()
        for s in stocks:
            ticker = s.ticker
            try:
                update_stock_prices_and_financials(ticker)
                financials = fetch_financials(ticker)
                alt = update_alternative_data(ticker)
                update_options_data(ticker)
                tech = _technical_from_prices(ticker)
                # News + sentiment
                articles = fetch_news(ticker, s.company_name or "")
                sentiments = batch_sentiment([a.get("title") or "" for a in articles])
                save_news_for_stock(s.id, articles, sentiments)
                avg_sent = sum(sentiments.values()) / len(sentiments) if sentiments else 0.0
                # Score
                total = compute_total_score(
                    roe=financials.get("roe"),
                    per=financials.get("per"),
                    pbr=financials.get("pbr"),
                    peg=financials.get("peg"),
                    ev_ebitda=financials.get("ev_ebitda"),
                    operating_margin=financials.get("operating_margin"),
                    debt_ratio=financials.get("debt_ratio"),
                    fcf_growth=financials.get("fcf_growth"),
                    institutional_ownership=alt.get("institutional_ownership"),
                    insider_activity=alt.get("insider_activity", "neutral"),
                    short_interest=alt.get("short_interest"),
                    employee_growth=s.linkedin_employee_growth or alt.get("employee_growth"),
                    rsi=tech.get("rsi"),
                    ma_trend=tech.get("ma_trend", "downtrend"),
                    momentum=tech.get("momentum", "neutral"),
                    sentiment_score=avg_sent,
                )
                today = date.today()
                existing = db.query(StockScore).filter(StockScore.stock_id == s.id, StockScore.date == today).first()
                if existing:
                    existing.score = total
                    existing.roe = financials.get("roe")
                    existing.per = financials.get("per")
                    existing.rsi = tech.get("rsi")
                    existing.sentiment_score = avg_sent
                    # ... other fields
                else:
                    db.add(StockScore(
                        stock_id=s.id,
                        date=today,
                        roe=financials.get("roe"),
                        per=financials.get("per"),
                        pbr=financials.get("pbr"),
                        peg=financials.get("peg"),
                        ev_ebitda=financials.get("ev_ebitda"),
                        operating_margin=financials.get("operating_margin"),
                        debt_ratio=financials.get("debt_ratio"),
                        fcf=financials.get("fcf_growth"),
                        institutional_ownership=alt.get("institutional_ownership"),
                        insider_buying=5 if alt.get("insider_activity") == "buying" else (2 if alt.get("insider_activity") == "neutral" else 0),
                        short_interest=alt.get("short_interest"),
                        rsi=tech.get("rsi"),
                        ma_trend=3 if tech.get("ma_trend") == "golden_cross" else (2 if tech.get("ma_trend") == "uptrend" else 0),
                        momentum=3 if tech.get("momentum") == "strong" else (1 if tech.get("momentum") == "neutral" else 0),
                        sentiment_score=avg_sent,
                        score=total,
                    ))
                update_recommendation_for_stock(ticker)
                # 기업평점(Glassdoor) - API 키 있으면 실데이터, 없으면 재무 기반 대체점수로 채움
                try:
                    updated = update_stock_glassdoor(s.id, s.company_name or s.ticker, s.ticker or "")
                    if not updated:
                        db.refresh(s)
                    if not updated or s.glassdoor_rating is None:
                        _set_fallback_glassdoor_rating(db, s, financials, avg_sent)
                except Exception:
                    _set_fallback_glassdoor_rating(db, s, financials, avg_sent)
                # 종목 이력: 새로고침할 때마다 1행 쌓기
                latest_ph = db.query(PriceHistory).filter(PriceHistory.stock_id == s.id).order_by(desc(PriceHistory.date)).first()
                db.add(StockHistory(
                    stock_id=s.id,
                    refreshed_at=datetime.utcnow(),
                    price=latest_ph.price if latest_ph else None,
                    score=total,
                    roe=financials.get("roe"),
                    per=financials.get("per"),
                ))
            except Exception as e:
                continue
        db.commit()
    finally:
        db.close()


def update_glassdoor_daily():
    db = SessionLocal()
    try:
        for s in db.query(Stock).all():
            try:
                update_stock_glassdoor(s.id, s.company_name or s.ticker, s.ticker or "")
            except Exception:
                pass
        db.commit()
    finally:
        db.close()
