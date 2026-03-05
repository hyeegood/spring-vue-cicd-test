# =======================================
# 투자 점수 계산 로직 (통합 공식)
# InvestmentScore = Value*0.40 + Growth*0.25 + Sentiment*0.20 + StockReliability*0.15
# 80+ Strong Buy, 70-79 Buy, 55-69 Hold, 40-54 Weak, <40 Avoid
# =======================================
from typing import Optional


def compute_value_score(
    per: Optional[float] = None,
    pbr: Optional[float] = None,
    ev_ebitda: Optional[float] = None,
    operating_margin: Optional[float] = None,
    debt_ratio: Optional[float] = None,
) -> float:
    """밸류에이션 매력도 점수 (0–100). PER, PBR, EV/EBITDA 등 기반."""
    score = 50.0
    if per is not None and per > 0:
        if 10 <= per <= 20:
            score += 15
        elif 20 < per <= 30:
            score += 5
        elif per > 50:
            score -= 15
    if pbr is not None and 0 < pbr <= 2:
        score += 10
    if ev_ebitda is not None and ev_ebitda <= 15:
        score += 10
    if operating_margin is not None and operating_margin > 10:
        score += 5
    if debt_ratio is not None and debt_ratio < 100:
        score += 5
    return round(max(0.0, min(100.0, score)), 1)


def compute_growth_score(
    roe: Optional[float] = None,
    operating_margin: Optional[float] = None,
    employee_growth: Optional[float] = None,
) -> float:
    """성장성 점수 (0–100). ROE, 영업이익률, 인력 성장 등."""
    score = 50.0
    if roe is not None:
        if roe >= 20:
            score += 25
        elif roe >= 15:
            score += 15
        elif roe >= 10:
            score += 5
        elif roe < 0:
            score -= 15
    if operating_margin is not None and operating_margin > 15:
        score += 15
    if employee_growth is not None and employee_growth > 5:
        score += 10
    return round(max(0.0, min(100.0, score)), 1)


def compute_sentiment_score_normalized(sentiment_raw: Optional[float]) -> float:
    """감성 점수 (-1~1)를 0–100으로 변환."""
    if sentiment_raw is None:
        return 50.0
    return round(max(0.0, min(100.0, (float(sentiment_raw) + 1) * 50)), 1)


def compute_unified_investment_score(
    value_score: float,
    growth_score: float,
    sentiment_score: float,
    stock_reliability: float,
) -> float:
    """통합 투자 점수. Value 40% + Growth 25% + Sentiment 20% + StockRel 15%."""
    total = (
        value_score * 0.40
        + growth_score * 0.25
        + sentiment_score * 0.20
        + stock_reliability * 0.15
    )
    return round(max(0.0, min(100.0, total)), 1)


def get_investment_interpretation(score: float) -> str:
    """점수 구간별 투자 의견: Strong Buy / Buy / Hold / Weak / Avoid."""
    if score >= 80:
        return "Strong Buy"
    if score >= 70:
        return "Buy"
    if score >= 55:
        return "Hold"
    if score >= 40:
        return "Weak"
    return "Avoid"
