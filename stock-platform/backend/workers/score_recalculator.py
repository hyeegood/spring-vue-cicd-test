# =======================================
# 점수 재계산 워커
# DB 재무/감성 데이터로 Value, Growth, Sentiment, Reliability, InvestmentScore 계산
# 기존 stock_scores.score 유지 또는 확장
# =======================================
from datetime import date
from database import SessionLocal
from models import Stock, StockScore
from reliability_engine import get_sector_reliability, compute_stock_reliability
from services.investment_score import (
    compute_value_score,
    compute_growth_score,
    compute_sentiment_score_normalized,
    compute_unified_investment_score,
)

def run_score_recalculate():
    """전체 종목에 대해 통합 투자 점수 재계산 (오늘 날짜 스코어 업데이트)."""
    db = SessionLocal()
    try:
        today = date.today()
        rows = db.query(Stock, StockScore).outerjoin(
            StockScore, (Stock.id == StockScore.stock_id) & (StockScore.date == today)
        ).limit(500).all()
        for stock, score in rows:
            if not score:
                continue
            sector_rel = get_sector_reliability(stock.sector)
            stock_rel = compute_stock_reliability(
                sector=stock.sector,
                operating_margin=score.operating_margin,
                debt_ratio=score.debt_ratio,
                roe=score.roe,
                institutional_ownership=score.institutional_ownership,
                rsi=score.rsi,
            )
            val = compute_value_score(score.per, score.pbr, getattr(score, "ev_ebitda", None), score.operating_margin, score.debt_ratio)
            gr = compute_growth_score(score.roe, score.operating_margin, getattr(stock, "linkedin_employee_growth", None))
            sent = compute_sentiment_score_normalized(score.sentiment_score)
            inv = compute_unified_investment_score(val, gr, sent, stock_rel)
            score.score = inv
        db.commit()
    finally:
        db.close()
