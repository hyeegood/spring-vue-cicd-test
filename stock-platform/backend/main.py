"""
FastAPI application: REST API for stock platform.
"""
import asyncio
import time
import threading
from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta
from typing import List, Optional
from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from database import get_db, SessionLocal, engine, Base
from models import (
    Stock, StockScore, PriceHistory, StockHistory, TradeRecommendation,
    OptionsData, NewsData, Portfolio, PortfolioPosition,
)
from data_fetcher import fetch_financials, fetch_prices, get_current_price, fetch_company_summary
from alternative_data_fetcher import fetch_institutional_ownership, fetch_short_interest, fetch_insider_activity, fetch_employee_growth
from options_fetcher import fetch_options_chain
from news_fetcher import fetch_news
from sentiment_analyzer import batch_sentiment
from recommendation_engine import compute_recommendation
from backtest_engine import run_backtest
from tasks import run_all_scheduled_updates, update_single_stock
from korean_name_fetcher import fetch_korean_name_from_wikipedia
from cache_utils import cache_get_or_set
from reliability_engine import (
    get_sector_reliability,
    compute_stock_reliability,
    get_reliability_level,
    get_reliability_interpretation,
    adjust_investment_score_with_reliability,
)
from services.investment_score import (
    compute_value_score,
    compute_growth_score,
    compute_sentiment_score_normalized,
    compute_unified_investment_score,
    get_investment_interpretation,
)
from services.ai_insight import generate_ai_insight

# 외부 API 캐시 TTL (10분)
EXTERNAL_CACHE_TTL = 600


# --- Pydantic schemas ---
class StockListItem(BaseModel):
    ticker: str
    company_name: Optional[str]
    current_price: Optional[float]
    score: Optional[float]
    entry_price: Optional[float]
    stop_loss: Optional[float]
    target_price: Optional[float]
    institutional_ownership: Optional[float]
    short_interest: Optional[float]
    glassdoor_rating: Optional[float]
    employee_growth: Optional[float]
    news_sentiment: Optional[float]
    risk_level: Optional[str]
    last_updated: Optional[datetime]


class StockDetailResponse(BaseModel):
    stock: dict
    price_history: List[dict]
    score_breakdown: dict
    recommendation: dict
    financials: dict
    market_indicators: dict
    options: dict
    news: List[dict]


class BacktestRequest(BaseModel):
    tickers: List[str]
    start_date: str
    end_date: str
    entry_rule: Optional[str] = "ma20"


class PortfolioCreate(BaseModel):
    name: str
    user_id: Optional[str] = "default"


class PositionAdd(BaseModel):
    stock_id: int
    shares: float


def _safe(fn, *args, default=None):
    try:
        return fn(*args)
    except Exception:
        return default


def _fallback_glassdoor_rating(financials: dict, sentiment: Optional[float], ticker: str = "") -> float:
    """Glassdoor API 없을 때 재무/감성으로 1~5 대체 기업평점 (종목마다 다르게)."""
    score = 2.8
    if financials:
        roe = financials.get("roe")
        if roe is not None:
            score += min(1.0, max(-0.5, roe / 35))
        per = financials.get("per")
        if per is not None:
            if 10 <= per <= 20: score += 0.25
            elif 20 < per <= 30: score += 0.1
            elif per and per > 50: score -= 0.2
        om = financials.get("operating_margin")
        if om is not None and om > 0:
            score += min(0.4, om / 60)
        debt = financials.get("debt_ratio")
        if debt is not None and debt > 100:
            score -= 0.15
    if sentiment is not None:
        score += sentiment * 0.4
    seed = sum(ord(c) for c in (ticker or "")) % 100
    score += (seed - 50) / 200
    return round(max(1.0, min(5.0, score)), 1)


def _risk_from_score(score: Optional[float]) -> str:
    if score is None: return "중간"
    if score >= 70: return "낮음"
    if score >= 40: return "중간"
    return "높음"


# 종목 한글명 (DB에 없을 때 폴백)
TICKER_TO_KOREAN = {
    "AAPL": "애플", "MSFT": "마이크로소프트", "GOOGL": "알파벳 A", "GOOG": "알파벳 C", "AMZN": "아마존",
    "NVDA": "엔비디아", "META": "메타", "TSLA": "테슬라", "BRK-B": "버크셔헤서웨이", "UNH": "유나이티드헬스",
    "JNJ": "존슨앤존슨", "JPM": "JP모건", "V": "비자", "PG": "P&G", "MA": "마스터카드", "HD": "홈디포",
    "DIS": "월트디즈니", "XOM": "엑손모빌", "CVX": "셰브론", "ABBV": "애브비", "MRK": "머크", "PEP": "펩시코",
    "KO": "코카콜라", "COST": "코스트코", "AVGO": "브로드컴", "WMT": "월마트", "MCD": "맥도날드",
    "CSCO": "시스코", "ACN": "액센츄어", "ABT": "애보트", "TMO": "써모피셔", "DHR": "다나허", "NEE": "넥스트에너지",
    "ADBE": "어도비", "NFLX": "넷플릭스", "PM": "필립모리스", "BMY": "브리스톨마이어스", "UNP": "유니온퍼시픽",
    "RTX": "알티", "HON": "허니웰", "INTC": "인텔", "AMD": "AMD", "QCOM": "퀄컴", "TXN": "텍사스인스트루먼트",
    "UPS": "UPS", "AMGN": "알지닌", "LOW": "로우스", "INTU": "인투이트", "SPGI": "S&P글로벌", "CAT": "캐터필러",
    "BA": "보잉", "GE": "제너럴일렉트릭", "DE": "디어", "IBM": "IBM", "AXP": "아메리칸익스프레스",
    "GS": "골드만삭스", "VZ": "버라이즌", "T": "AT&T", "CVS": "CVS", "MDT": "메드트로닉", "GILD": "길리어드",
    "LMT": "록히드마틴", "SBUX": "스타벅스", "AMAT": "어플라이드머티리얼즈", "ADI": "아날로그디바이시스",
    "REGN": "리제네론", "PLD": "프로로그리스", "ISRG": "인튜이티브서지컬", "SYK": "스트라이커", "BLK": "블랙록",
    "BKNG": "부킹닷컴", "CI": "시그나", "C": "시티그룹", "MO": "알트리아", "LRCX": "램리서치", "MMC": "마쉬앤맥레넌",
    "CB": "채스", "SO": "서던컴퍼니", "DUK": "듀크에너지", "ZTS": "줄루스애니멀헬스", "BDX": "베クト론디킨슨",
    "EOG": "EOG리소스", "SLB": "슐럼버저", "CMCSA": "컴캐스트", "APD": "에어프로덕츠", "PGR": "프로그레시브",
    "CL": "콜게이트팔몰리브", "FIS": "FIS", "EQIX": "이퀴닉스", "WM": "웨이스트매니지먼트", "APTV": "앱티브",
    "ITW": "일리노이즈툴웍스", "HCA": "HCA헬스케어", "AON": "에이온", "SHW": "셰윈윌리엄스", "KLAC": "KLA",
    "MCK": "맥킷슨", "PSA": "퍼블릭스토리지", "NOC": "노스롭그루먼", "CME": "CME그룹", "PANW": "팔로알토",
    "SNPS": "시놉시스", "CDNS": "캐드엔스", "ORLY": "오라일리", "MAR": "메리어트", "MCO": "무디스", "APH": "앰펙",
    "AIG": "AIG", "DXCM": "덱스컴", "ECL": "이코랩", "AZO": "오토존", "WELL": "웰타워", "PSX": "필립스66",
    "AFL": "에플락", "YUM": "얌브랜즈", "MNST": "몬스터베버리지", "IDXX": "아이덱스", "FAST": "패스트널",
    "CTAS": "시인타스", "ODFL": "올드도미니언", "ROST": "로스스토어스", "VRSK": "베리스크", "PCAR": "PACCAR",
    "EXC": "엑셀에너지", "AEP": "아메리칸일렉트릭", "MET": "메트라이프", "HLT": "힐튼", "TDG": "트랜스디그리스",
}


def _company_name_ko(stock) -> Optional[str]:
    """DB company_name_ko 또는 티커 한글 매핑."""
    try:
        ko = getattr(stock, "company_name_ko", None)
        if ko:
            return ko
    except Exception:
        pass
    return TICKER_TO_KOREAN.get((stock.ticker or "").upper())


def _ensure_company_name_ko_column():
    """SQLite 기존 DB에 company_name_ko 컬럼 없으면 추가."""
    from config import DATABASE_URL
    if not DATABASE_URL.startswith("sqlite"):
        return
    from sqlalchemy import text
    with engine.connect() as conn:
        try:
            r = conn.execute(text("PRAGMA table_info(stocks)"))
            cols = [row[1] for row in r.fetchall()]
            if "company_name_ko" not in cols:
                conn.execute(text("ALTER TABLE stocks ADD COLUMN company_name_ko VARCHAR(255)"))
                conn.commit()
        except Exception:
            pass


# 프로덕션 기본 종목 시드 (prod_stocks 비어 있을 때만)
_DEFAULT_TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "JPM", "V", "JNJ",
    "WMT", "PG", "UNH", "HD", "DIS", "BAC", "XOM", "CVX", "KO", "PEP",
]


def _seed_prod_stocks_if_empty():
    """prod_stocks가 비어 있으면 기본 종목 목록 + 가격/점수 플레이스홀더로 채운다. 이후 백그라운드에서 파이프라인 1회 실행."""
    try:
        from database import SessionLocal
        from models_production import ProdStock, ProdPriceHistory, ProdScores
        db = SessionLocal()
        try:
            if db.query(ProdStock).count() > 0:
                return
            today = date.today()
            for t in _DEFAULT_TICKERS:
                db.add(ProdStock(ticker=t, sector="Technology"))
            db.commit()
            for t in _DEFAULT_TICKERS:
                db.add(ProdPriceHistory(ticker=t, date=today, open=100.0, high=105.0, low=99.0, close=102.0, volume=1000000))
                db.add(ProdScores(ticker=t, value_score=55.0, growth_score=60.0, quality_score=58.0, sentiment_score=52.0, risk_adjustment=55.0, investment_score=56.0))
            db.commit()
            def _run_pipeline():
                try:
                    from workers.pipeline import run_production_pipeline
                    run_production_pipeline(tickers=_DEFAULT_TICKERS, skip_glassdoor=True, skip_news=True)
                except Exception:
                    pass
            _t = threading.Thread(target=_run_pipeline, daemon=True)
            _t.start()
        finally:
            db.close()
    except Exception:
        pass


def _seed_legacy_stocks_if_empty():
    """레거시 stocks/price_history/stock_scores/trade_recommendations 비어 있으면 채워서 대시보드·종목상세에 데이터가 보이게 함."""
    try:
        from database import SessionLocal
        from models import Stock, StockScore, PriceHistory, TradeRecommendation, NewsData
        db = SessionLocal()
        try:
            if db.query(Stock).count() > 0:
                return
            today = date.today()
            name_map = {
                "AAPL": "Apple Inc.", "MSFT": "Microsoft", "GOOGL": "Alphabet", "AMZN": "Amazon", "NVDA": "NVIDIA",
                "META": "Meta Platforms", "TSLA": "Tesla", "JPM": "JPMorgan Chase", "V": "Visa", "JNJ": "Johnson & Johnson",
                "WMT": "Walmart", "PG": "Procter & Gamble", "UNH": "UnitedHealth", "HD": "Home Depot", "DIS": "Walt Disney",
                "BAC": "Bank of America", "XOM": "Exxon Mobil", "CVX": "Chevron", "KO": "Coca-Cola", "PEP": "PepsiCo",
            }
            for t in _DEFAULT_TICKERS:
                s = Stock(ticker=t, company_name=name_map.get(t, t), glassdoor_rating=4.5, sector="Technology")
                db.add(s)
            db.commit()
            stocks = db.query(Stock).filter(Stock.ticker.in_(_DEFAULT_TICKERS)).all()
            for s in stocks:
                db.add(StockScore(stock_id=s.id, date=today, score=65.0, roe=15.0, per=20.0, pbr=2.5, debt_ratio=50.0, sentiment_score=0.2))
                db.add(PriceHistory(stock_id=s.id, date=today, price=150.0, close=150.0, volume=1000000))
                db.add(TradeRecommendation(stock_id=s.id, entry_price=145.0, stop_loss=130.0, target_price=180.0))
            if stocks:
                n = NewsData(stock_id=stocks[0].id, title="Market update: Tech sector gains", source="Reuters", date=datetime.utcnow(), url="https://example.com")
                db.add(n)
            db.commit()
        finally:
            db.close()
    except Exception:
        pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        _ensure_company_name_ko_column()
    except Exception:
        pass
    try:
        try:
            import models_production  # noqa: F401 - prod_* 테이블 등록
        except Exception:
            pass
        # 종목 이력·프로덕션 테이블 포함 일괄 생성
        Base.metadata.create_all(bind=engine)
        # prod_stocks 비어 있으면 기본 종목 시드
        _seed_prod_stocks_if_empty()
        # 레거시 테이블 비어 있으면 시드 (대시보드·종목상세에 데이터 표시)
        _seed_legacy_stocks_if_empty()
    except Exception:
        pass
    try:
        from scheduler import start_scheduler
        start_scheduler()
    except Exception:
        pass
    yield
    try:
        from scheduler import stop_scheduler
        stop_scheduler()
    except Exception:
        pass


app = FastAPI(title="Stock Investment Platform API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 프로덕션 모듈 라우터: /api/recommendations, /api/screener, /api/stocks/{symbol}/chart
try:
    from api import api_router
    app.include_router(api_router)
except ImportError:
    pass


@app.get("/api/health")
def health():
    return {"status": "ok"}


# 대시보드 응답 캐시 (60초 레거시 / 10초 프로덕션) - 로딩 속도 개선
_dashboard_cache: dict = {}
_DASHBOARD_CACHE_TTL = 60
_DASHBOARD_PROD_CACHE_TTL = 10


def _fill_one_ticker_sync(ticker: str) -> dict:
    """한 종목에 대해 외부 API 호출 (캐시 사용, 10분 TTL). 병렬 실행용."""
    rec = cache_get_or_set(
        ("rec", ticker),
        lambda: _safe(compute_recommendation, ticker),
        ttl=EXTERNAL_CACHE_TTL,
    ) or {}
    return {
        "current_price": cache_get_or_set(
            ("price", ticker),
            lambda: _safe(get_current_price, ticker),
            ttl=EXTERNAL_CACHE_TTL,
        ),
        "entry_price": rec.get("entry_price"),
        "stop_loss": rec.get("stop_loss"),
        "target_price": rec.get("target_price"),
        "institutional_ownership": cache_get_or_set(
            ("inst", ticker),
            lambda: _safe(fetch_institutional_ownership, ticker),
            ttl=EXTERNAL_CACHE_TTL,
        ),
        "short_interest": cache_get_or_set(
            ("short", ticker),
            lambda: _safe(fetch_short_interest, ticker),
            ttl=EXTERNAL_CACHE_TTL,
        ),
        "employee_growth": cache_get_or_set(
            ("emp", ticker),
            lambda: _safe(fetch_employee_growth, ticker),
            ttl=EXTERNAL_CACHE_TTL,
        ),
    }

# 전체 새로고침 상태 (대시보드/종목발견)
_refresh_running = False
_refresh_last_done: Optional[datetime] = None


def _run_full_refresh():
    global _refresh_running, _refresh_last_done, _dashboard_cache
    try:
        run_all_scheduled_updates()
        _refresh_last_done = datetime.utcnow()
    except Exception:
        pass
    finally:
        _dashboard_cache.clear()
        try:
            from utils.cache import cache_invalidate
            cache_invalidate("dashboard_analytics")
        except Exception:
            pass
        _refresh_running = False


def _dashboard_sort_key(item):
    """정렬 키: 1) 투자점수(신뢰도 반영) 높은 순 2) 현재가-진입가 차액 낮은 순 3) 기업평점 높은 순."""
    inv_score = item.get("investment_score")
    has_score = inv_score is not None or item.get("score") is not None
    score_num = (inv_score if inv_score is not None else item.get("score")) or 0
    cur, ent = item.get("current_price"), item.get("entry_price")
    diff = float("inf")
    if cur is not None and ent is not None:
        diff = abs(float(cur) - float(ent))
    gd = item.get("glassdoor_rating") or 0
    ticker = item.get("ticker") or ""
    return (not has_score, -score_num, diff, -gd, ticker)


@app.get("/api/dashboard")
async def dashboard(
    db: Session = Depends(get_db),
    minimal: bool = Query(False, description="True면 DB만 반환(빠른 첫 렌더), False면 외부 API 병렬 보정"),
):
    """
    대시보드 단일 API. DB 데이터 + (minimal=False일 때) 상위 20종목 외부 API 병렬·캐시 보정.
    응답 캐시 60초, 외부 API 결과 캐시 10분.
    """
    now = time.time()
    cache_key = "minimal" if minimal else "full"
    if _dashboard_cache.get(cache_key) and (now - _dashboard_cache.get(f"{cache_key}_ts", 0)) < _DASHBOARD_CACHE_TTL:
        return _dashboard_cache[cache_key]
    try:
        today = date.today()
        rows = (
            db.query(Stock, StockScore, TradeRecommendation)
            .outerjoin(StockScore, (Stock.id == StockScore.stock_id) & (StockScore.date == today))
            .outerjoin(TradeRecommendation, Stock.id == TradeRecommendation.stock_id)
            .filter(Stock.glassdoor_rating >= 4.0)
            .order_by(Stock.id)
            .limit(100)
            .all()
        )
        stock_ids = [stock.id for stock, _, _ in rows]
        latest_prices = {}
        if stock_ids:
            all_ph = (
                db.query(PriceHistory.stock_id, PriceHistory.price, PriceHistory.date)
                .filter(PriceHistory.stock_id.in_(stock_ids))
                .order_by(desc(PriceHistory.date))
                .all()
            )
            for sid, price, _ in all_ph:
                if sid not in latest_prices:
                    latest_prices[sid] = price
        out = []
        for stock, score, rec in rows:
            current = latest_prices.get(stock.id)
            last_updated = score.date.isoformat() if score and score.date else None
            # 섹터·종목 신뢰도 점수 및 투자점수 통합 (FEATURE 1–3)
            sector_rel = get_sector_reliability(stock.sector)
            stock_rel = compute_stock_reliability(
                sector=stock.sector,
                operating_margin=score.operating_margin if score else None,
                debt_ratio=score.debt_ratio if score else None,
                roe=score.roe if score else None,
                institutional_ownership=score.institutional_ownership if score else None,
                rsi=score.rsi if score else None,
            )
            raw_score = score.score if score else None
            investment_score = adjust_investment_score_with_reliability(raw_score, stock_rel)
            out.append({
                "ticker": stock.ticker,
                "company_name": stock.company_name,
                "company_name_ko": _company_name_ko(stock),
                "sector": stock.sector,
                "current_price": current,
                "score": raw_score,
                "investment_score": investment_score,
                "sector_reliability": round(sector_rel, 1),
                "stock_reliability": stock_rel,
                "reliability_level": get_reliability_level(stock_rel),
                "entry_price": rec.entry_price if rec else None,
                "stop_loss": rec.stop_loss if rec else None,
                "target_price": rec.target_price if rec else None,
                "institutional_ownership": score.institutional_ownership if score else None,
                "short_interest": score.short_interest if score else None,
                "glassdoor_rating": stock.glassdoor_rating,
                "employee_growth": stock.linkedin_employee_growth,
                "news_sentiment": score.sentiment_score if score else None,
                "risk_level": _risk_from_score(raw_score),
                "last_updated": last_updated,
            })
        out = sorted(out, key=_dashboard_sort_key)
        # 1초 이내 응답: 외부 API 호출 제거. 모든 데이터는 DB(및 캐시) 기준으로만 반환.

        payload = {
            "items": out,
            "last_refresh_at": _refresh_last_done.isoformat() if _refresh_last_done else None,
        }
        _dashboard_cache[cache_key] = payload
        _dashboard_cache[f"{cache_key}_ts"] = now
        return payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =======================================
# 대시보드 집계 API (프리미엄 UI용)
# Market Overview, Top Picks, Trending, Top Sectors, News — 1회 호출로 1초 이내
# =======================================
@app.get("/api/dashboard/analytics")
def dashboard_analytics(db: Session = Depends(get_db)):
    """카드형 대시보드용: 시장 개요, Top 투자 추천, 트렌딩, 섹터, 뉴스. 프로덕션 테이블 있으면 10초 캐시."""
    # 프로덕션 경로: prod_stocks 존재 시 서비스에서 10초 캐시 적용
    try:
        from models_production import ProdStock
        from services.dashboard_service_prod import get_dashboard_analytics_prod
        if db.query(ProdStock).limit(1).first():
            payload = get_dashboard_analytics_prod(db)
            return {**payload, "last_refresh_at": _refresh_last_done.isoformat() if _refresh_last_done else None}
    except Exception:
        pass
    now = time.time()
    if _dashboard_cache.get("minimal") and (now - _dashboard_cache.get("minimal_ts", 0)) < _DASHBOARD_CACHE_TTL:
        items = _dashboard_cache["minimal"].get("items") or []
    else:
        today = date.today()
        rows = (
            db.query(Stock, StockScore, TradeRecommendation)
            .outerjoin(StockScore, (Stock.id == StockScore.stock_id) & (StockScore.date == today))
            .outerjoin(TradeRecommendation, Stock.id == TradeRecommendation.stock_id)
            .filter(Stock.glassdoor_rating >= 4.0)
            .order_by(Stock.id)
            .limit(100)
            .all()
        )
        stock_ids = [stock.id for stock, _, _ in rows]
        latest_prices = {}
        if stock_ids:
            for sid, price, _ in db.query(PriceHistory.stock_id, PriceHistory.price, PriceHistory.date).filter(
                PriceHistory.stock_id.in_(stock_ids)
            ).order_by(desc(PriceHistory.date)).all():
                if sid not in latest_prices:
                    latest_prices[sid] = price
        items = []
        for stock, score, rec in rows:
            sector_rel = get_sector_reliability(stock.sector)
            stock_rel = compute_stock_reliability(
                sector=stock.sector,
                operating_margin=score.operating_margin if score else None,
                debt_ratio=score.debt_ratio if score else None,
                roe=score.roe if score else None,
                institutional_ownership=score.institutional_ownership if score else None,
                rsi=score.rsi if score else None,
            )
            raw = score.score if score else None
            inv_score = adjust_investment_score_with_reliability(raw, stock_rel)
            items.append({
                "ticker": stock.ticker,
                "company_name": stock.company_name,
                "company_name_ko": _company_name_ko(stock),
                "sector": stock.sector,
                "current_price": latest_prices.get(stock.id),
                "score": raw,
                "investment_score": inv_score,
                "sector_reliability": round(sector_rel, 1),
                "stock_reliability": stock_rel,
                "reliability_level": get_reliability_level(stock_rel),
                "entry_price": rec.entry_price if rec else None,
                "glassdoor_rating": stock.glassdoor_rating,
                "news_sentiment": score.sentiment_score if score else None,
                "risk_level": _risk_from_score(raw),
            })
        items = sorted(items, key=lambda x: (-(x.get("investment_score") or x.get("score") or 0), x.get("ticker") or ""))

    # Top Investment Picks: 상위 10
    top_picks = items[:10]
    # Trending: 동일 목록 (모멘텀 정렬은 스코어로 대체)
    trending_stocks = items[:15]
    # Top Sectors: 섹터별 종목 수
    from collections import Counter
    sector_counts = Counter(i.get("sector") or "Unknown" for i in items)
    top_sectors = [{"sector": s, "count": c} for s, c in sector_counts.most_common(10)]
    # Market News: DB 최신 뉴스
    news_rows = db.query(NewsData).order_by(desc(NewsData.date)).limit(10).all()
    market_news = [{"title": n.title, "sentiment": n.sentiment, "date": n.date.isoformat() if n.date else None, "url": n.url} for n in news_rows]

    return {
        "market_overview": {"sp500": None, "nasdaq": None, "vix": None},
        "top_picks": top_picks,
        "trending_stocks": trending_stocks,
        "top_sectors": top_sectors,
        "market_news": market_news,
        "last_refresh_at": _refresh_last_done.isoformat() if _refresh_last_done else None,
    }


@app.post("/api/refresh/full")
def refresh_full():
    """전체 데이터 새로고침 (대시보드/종목발견). 백그라운드 실행 후 GET /api/refresh/status 로 완료 확인."""
    global _refresh_running
    if _refresh_running:
        raise HTTPException(status_code=429, detail="이미 새로고침이 진행 중입니다.")
    try:
        _refresh_running = True
        t = threading.Thread(target=_run_full_refresh, daemon=True)
        t.start()
    except Exception as e:
        _refresh_running = False
        raise HTTPException(status_code=500, detail=f"새로고침 시작 실패: {e!s}")
    return {"status": "started", "message": "전체 데이터 업데이트를 시작했습니다. 완료 후 목록을 다시 불러와 주세요."}


@app.get("/api/refresh/status")
def refresh_status():
    """새로고침 진행 여부 및 마지막 완료 시각."""
    try:
        last_at = _refresh_last_done.isoformat() if _refresh_last_done else None
    except Exception:
        last_at = None
    return {"running": bool(_refresh_running), "last_completed_at": last_at}


@app.post("/api/refresh/stock/{ticker}")
def refresh_stock(ticker: str):
    """해당 종목만 새로고침 (상세 페이지)."""
    ticker = ticker.upper()
    try:
        ok = update_single_stock(ticker)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"새로고침 중 오류: {e!s}")
    if not ok:
        raise HTTPException(status_code=404, detail="Stock not found")
    return {"status": "ok", "refreshed_at": datetime.utcnow().isoformat()}


@app.post("/api/refresh-korean-names")
def refresh_korean_names(db: Session = Depends(get_db)):
    """Wikipedia API로 한글 회사명 조회 후 DB에 저장. company_name_ko 비어 있는 종목만 조회."""
    updated = 0
    stocks = db.query(Stock).all()
    for s in stocks:
        try:
            if getattr(s, "company_name_ko", None):
                continue
            ko = fetch_korean_name_from_wikipedia(s.company_name or "", s.ticker or "")
            if ko:
                s.company_name_ko = ko
                updated += 1
        except Exception:
            pass
        time.sleep(0.25)
    db.commit()
    return {"status": "ok", "updated": updated, "total": len(stocks)}


@app.get("/api/stocks/{ticker}", response_model=dict)
def stock_detail(ticker: str, db: Session = Depends(get_db)):
    """Detail page: DB만 사용해 1초 이내 응답 (차트·점수·추천·재무·옵션·뉴스)."""
    stock = db.query(Stock).filter(Stock.ticker == ticker.upper()).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    today = date.today()
    score = db.query(StockScore).filter(StockScore.stock_id == stock.id, StockScore.date == today).first()
    rec = db.query(TradeRecommendation).filter(TradeRecommendation.stock_id == stock.id).first()
    rec_dict = {"entry_price": rec.entry_price if rec else None, "stop_loss": rec.stop_loss if rec else None, "target_price": rec.target_price if rec else None}

    # 가격 이력: DB (PriceHistory) — 외부 API 호출 없음
    ph_rows = (
        db.query(PriceHistory.date, PriceHistory.price, PriceHistory.close)
        .filter(PriceHistory.stock_id == stock.id)
        .order_by(desc(PriceHistory.date))
        .limit(365)
        .all()
    )
    prices = []
    for row in ph_rows:
        d, pr, cl = row[0], row[1], (row[2] if len(row) > 2 else None)
        prices.append({"date": d.isoformat() if hasattr(d, "isoformat") else str(d), "close": cl if cl is not None else pr})

    # 재무: DB (StockScore)
    financials = {}
    if score:
        financials = {
            "roe": score.roe, "per": score.per, "pbr": score.pbr, "peg": score.peg,
            "ev_ebitda": getattr(score, "ev_ebitda", None), "operating_margin": score.operating_margin,
            "debt_ratio": score.debt_ratio, "fcf": getattr(score, "fcf", None),
        }

    # 옵션: DB (OptionsData) 최신 1건
    opt_row = db.query(OptionsData).filter(OptionsData.stock_id == stock.id).order_by(desc(OptionsData.date)).first()
    opts = {"call_volume": opt_row.call_volume or 0, "put_volume": opt_row.put_volume or 0, "put_call_ratio": float(opt_row.put_call_ratio or 0)} if opt_row else {"call_volume": 0, "put_volume": 0, "put_call_ratio": 0.0}

    # 뉴스: DB (NewsData)
    news_rows = db.query(NewsData).filter(NewsData.stock_id == stock.id).order_by(desc(NewsData.date)).limit(15).all()
    news_out = [{"title": n.title, "sentiment": n.sentiment or 0, "date": n.date.isoformat() if n.date else None, "url": n.url} for n in news_rows]

    sector_rel = get_sector_reliability(stock.sector)
    stock_rel = compute_stock_reliability(
        sector=stock.sector,
        operating_margin=score.operating_margin if score else None,
        debt_ratio=score.debt_ratio if score else None,
        roe=score.roe if score else None,
        institutional_ownership=score.institutional_ownership if score else None,
        rsi=score.rsi if score else None,
    )
    reliability_analysis = {
        "sector_reliability": round(sector_rel, 1),
        "stock_reliability": stock_rel,
        "reliability_level": get_reliability_level(stock_rel),
        "interpretation": get_reliability_interpretation(sector_rel, stock_rel),
    }
    # 통합 투자 점수 (Value 40% + Growth 25% + Sentiment 20% + StockRel 15%)
    sc = score
    val = compute_value_score(sc.per if sc else None, sc.pbr if sc else None, getattr(sc, "ev_ebitda", None) if sc else None, sc.operating_margin if sc else None, sc.debt_ratio if sc else None)
    gr = compute_growth_score(sc.roe if sc else None, sc.operating_margin if sc else None, stock.linkedin_employee_growth)
    sent = compute_sentiment_score_normalized(sc.sentiment_score if sc else None)
    inv_score = compute_unified_investment_score(val, gr, sent, stock_rel)
    inv_interpretation = get_investment_interpretation(inv_score)
    from services.ai_insight import generate_ai_insight_with_label
    ai_res = generate_ai_insight_with_label(
        sector=stock.sector, sector_reliability=sector_rel, stock_reliability=stock_rel,
        investment_score=inv_score, sentiment_score=sc.sentiment_score if sc else None,
        roe=sc.roe if sc else None, risk_level=_risk_from_score(sc.score if sc else None),
    )
    ai_insight_text = ai_res.get("text") or generate_ai_insight(stock.sector, sector_rel, stock_rel, inv_score, sc.sentiment_score if sc else None, sc.roe if sc else None, _risk_from_score(sc.score if sc else None))
    return {
        "stock": {
            "ticker": stock.ticker,
            "company_name": stock.company_name,
            "company_name_ko": _company_name_ko(stock),
            "sector": stock.sector,
            "company_summary": None,
            "glassdoor_rating": stock.glassdoor_rating,
            "ceo_approval": stock.ceo_approval,
            "employee_recommendation": stock.employee_recommendation,
            "linkedin_employee_growth": stock.linkedin_employee_growth,
        },
        "reliability_analysis": reliability_analysis,
        "price_history": prices,
        "score_breakdown": {
            "total": score.score if score else None,
            "roe": score.roe if score else None,
            "per": score.per if score else None,
            "rsi": score.rsi if score else None,
            "operating_margin": score.operating_margin if score else None,
            "sentiment_score": score.sentiment_score if score else None,
        },
        "recommendation": rec_dict,
        "investment_score": inv_score,
        "investment_interpretation": inv_interpretation,
        "ai_insight": ai_insight_text,
        "ai_insight_label": ai_res.get("label", "neutral"),
        "financials": financials,
        "market_indicators": {
            "institutional_ownership": score.institutional_ownership if score else None,
            "short_interest": score.short_interest if score else None,
            "insider_activity": "neutral",
        },
        "options": opts,
        "news": news_out,
    }


@app.get("/api/rankings/{list_type}")
def rankings(list_type: str, limit: int = Query(50, le=100), db: Session = Depends(get_db)):
    """Top Investment Score, Top Momentum, Top Value, Top Growth."""
    today = date.today()
    q = db.query(Stock, StockScore).outerjoin(
        StockScore, (Stock.id == StockScore.stock_id) & (StockScore.date == today)
    )
    if list_type == "score":
        q = q.order_by(desc(func.coalesce(StockScore.score, -1)))
    elif list_type == "value":
        q = q.order_by(func.coalesce(StockScore.per, 999999).asc())
    elif list_type == "growth":
        q = q.order_by(desc(func.coalesce(StockScore.roe, -1)))
    else:
        q = q.order_by(desc(func.coalesce(StockScore.score, -1)))
    rows = q.limit(limit).all()
    return [
        {"ticker": s.ticker, "company_name": s.company_name, "company_name_ko": _company_name_ko(s), "score": sc.score if sc else None}
        for s, sc in rows
    ]


@app.post("/api/portfolio")
def portfolio_create(body: PortfolioCreate, db: Session = Depends(get_db)):
    p = Portfolio(user_id=body.user_id or "default", name=body.name)
    db.add(p)
    db.commit()
    db.refresh(p)
    return {"id": p.id, "name": p.name}


@app.get("/api/portfolios")
def portfolio_list(db: Session = Depends(get_db)):
    """List all portfolios (for demo without auth)."""
    rows = db.query(Portfolio).all()
    return [{"id": p.id, "name": p.name} for p in rows]


@app.get("/api/portfolio/{portfolio_id}")
def portfolio_get(portfolio_id: int, db: Session = Depends(get_db)):
    p = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    positions = db.query(PortfolioPosition).filter(PortfolioPosition.portfolio_id == portfolio_id).all()
    if not positions:
        return {"id": p.id, "name": p.name, "positions": []}
    today = date.today()
    stock_ids = [pos.stock_id for pos in positions]
    stocks = {s.id: s for s in db.query(Stock).filter(Stock.id.in_(stock_ids)).all()}
    scores = {sc.stock_id: sc for sc in db.query(StockScore).filter(StockScore.stock_id.in_(stock_ids), StockScore.date == today).all()}
    out = []
    for pos in positions:
        s, sc = stocks.get(pos.stock_id), scores.get(pos.stock_id)
        out.append({"stock_id": pos.stock_id, "ticker": s.ticker if s else None, "shares": pos.shares, "score": sc.score if sc else None})
    return {"id": p.id, "name": p.name, "positions": out}


@app.post("/api/portfolio/{portfolio_id}/positions")
def portfolio_add_position(portfolio_id: int, body: PositionAdd, db: Session = Depends(get_db)):
    pos = PortfolioPosition(portfolio_id=portfolio_id, stock_id=body.stock_id, shares=body.shares)
    db.add(pos)
    db.commit()
    return {"ok": True}


@app.post("/api/backtest")
def backtest(body: BacktestRequest):
    return run_backtest(
        tickers=body.tickers,
        start_date=body.start_date,
        end_date=body.end_date,
        entry_rule=body.entry_rule or "ma20",
    )


@app.post("/api/stocks/register")
def register_stock(ticker: str, db: Session = Depends(get_db)):
    """Register a new ticker for tracking."""
    import yfinance as yf
    t = yf.Ticker(ticker.upper())
    info = t.info or {}
    existing = db.query(Stock).filter(Stock.ticker == ticker.upper()).first()
    if existing:
        return {"id": existing.id, "ticker": existing.ticker}
    s = Stock(
        ticker=ticker.upper(),
        company_name=info.get("longName") or info.get("shortName") or ticker,
        sector=info.get("sector"),
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return {"id": s.id, "ticker": s.ticker}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
