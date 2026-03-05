# =======================================
# 정량 투자 점수 재계산 워커
# prod_fundamentals, prod_company_ratings, prod_news 기반으로
# prod_scores 테이블 업데이트
# =======================================
from typing import Optional, List
from datetime import datetime

from sqlalchemy.orm import Session

from database import SessionLocal
from models_production import ProdStock, ProdFundamentals, ProdScores, ProdCompanyRatings, ProdNews
from services.quantitative_scoring_engine import (
    compute_value_score,
    compute_growth_score,
    compute_quality_score,
    compute_sentiment_score,
    compute_risk_adjustment,
    compute_investment_score,
    sector_to_risk,
)


def get_latest_news_sentiment(db: Session, ticker: str) -> Optional[float]:
    """해당 ticker 최신 뉴스 감성 평균. prod_news에 sentiment 컬럼 없으면 None 반환."""
    # prod_news에는 sentiment 필드가 없을 수 있음 → None
    return None


def recalculate_scores_for_ticker(db: Session, ticker: str) -> bool:
    """한 종목에 대해 재무·평점·감성 기반으로 6개 점수 계산 후 prod_scores 반영."""
    fund = db.query(ProdFundamentals).filter(ProdFundamentals.ticker == ticker).first()
    rating = db.query(ProdCompanyRatings).filter(ProdCompanyRatings.ticker == ticker).first()
    stock = db.query(ProdStock).filter(ProdStock.ticker == ticker).first()
    sector_risk = sector_to_risk(stock.sector if stock else None) if stock else 50.0

    # Value: PE, PBR, FCF
    pe = fund.pe_ratio if fund else None
    pbr = fund.pbr if fund else None
    fcf = fund.free_cash_flow if fund else None
    fcf_yield = (fcf / 1e9 * 100) if fcf and fcf != 0 else None  # 단순화: FCF를 억 단위 가정해 yield 유사값
    value_score = compute_value_score(per=pe, pbr=pbr, fcf_yield=fcf_yield)

    # Growth: revenue_growth, earnings_growth
    rev_g = fund.revenue_growth if fund else None
    earn_g = fund.earnings_growth if fund else None
    growth_score = compute_growth_score(revenue_growth=rev_g, eps_growth=earn_g, roe=fund.roe if fund else None)

    # Quality: ROE, debt_ratio
    quality_score = compute_quality_score(
        roe=fund.roe if fund else None,
        debt_ratio=fund.debt_ratio if fund else None,
        fcf=fcf,
    )

    # Sentiment: Glassdoor rating, news sentiment
    glassdoor = rating.glassdoor_rating if rating else None
    analyst_rating = (glassdoor * 20) if glassdoor is not None else None  # 5점 만점 → 100 스케일
    news_sent = get_latest_news_sentiment(db, ticker)
    sentiment_score = compute_sentiment_score(
        news_sentiment=news_sent,
        analyst_rating=analyst_rating,
    )

    # Risk: volatility 없으면 debt_ratio, sector_risk로
    risk_adjustment = compute_risk_adjustment(
        sector_risk=sector_risk,
        debt_ratio=fund.debt_ratio if fund else None,
    )

    investment_score = compute_investment_score(
        value_score=value_score,
        growth_score=growth_score,
        quality_score=quality_score,
        sentiment_score=sentiment_score,
        risk_adjustment=risk_adjustment,
    )

    row = db.query(ProdScores).filter(ProdScores.ticker == ticker).first()
    if row:
        row.value_score = value_score
        row.growth_score = growth_score
        row.quality_score = quality_score
        row.sentiment_score = sentiment_score
        row.risk_adjustment = risk_adjustment
        row.investment_score = investment_score
        row.updated_at = datetime.utcnow()
    else:
        db.add(ProdScores(
            ticker=ticker,
            value_score=value_score,
            growth_score=growth_score,
            quality_score=quality_score,
            sentiment_score=sentiment_score,
            risk_adjustment=risk_adjustment,
            investment_score=investment_score,
        ))
    return True


def run_score_recalculator_prod(tickers: Optional[List[str]] = None) -> dict:
    """전체 또는 지정 ticker에 대해 투자 점수 재계산."""
    db = SessionLocal()
    try:
        if not tickers:
            tickers = [r[0] for r in db.query(ProdStock.ticker).all()]
        count = 0
        for ticker in tickers:
            try:
                recalculate_scores_for_ticker(db, ticker)
                count += 1
            except Exception:
                pass
        db.commit()
        return {"updated": count}
    finally:
        db.close()
