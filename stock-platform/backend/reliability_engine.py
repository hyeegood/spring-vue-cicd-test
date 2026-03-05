"""
섹터 신뢰도 점수(Sector Reliability) 및 종목 신뢰도 점수(Stock Reliability).
밸류에이션 지표(PER, PBR 등)가 섹터별로 신뢰도가 다르다는 전제를 반영합니다.
"""
from typing import Optional, Tuple

# --- FEATURE 1: 섹터별 신뢰도 점수 (0–100). 높을수록 밸류에이션 지표 해석이 신뢰 가능 ---
# yfinance sector/industry 문자열에 맞춘 매핑 (대소문자 무시 후 매칭)
SECTOR_RELIABILITY_SCORES = {
    "consumer staples": 90,
    "consumer defensive": 90,
    "consumer staples & discretionary": 90,
    "banking": 85,
    "financial services": 85,
    "financial": 85,
    "utilities": 88,
    "utility": 88,
    "industrials": 75,
    "industrial": 75,
    "semiconductor": 65,
    "semiconductors": 65,
    "technology": 60,
    "software": 60,
    "internet": 55,
    "communication services": 55,
    "communication": 55,
    "ev": 45,
    "electric vehicle": 45,
    "automotive": 45,
    "consumer cyclical": 50,
    "biotech": 30,
    "biotechnology": 30,
    "healthcare": 40,
    "health care": 40,
    "energy": 70,
    "real estate": 72,
}
DEFAULT_SECTOR_RELIABILITY = 50


def get_sector_reliability(sector: Optional[str]) -> float:
    """섹터명으로 신뢰도 점수(0–100) 반환. 매칭 실패 시 기본값 50."""
    if not sector or not str(sector).strip():
        return float(DEFAULT_SECTOR_RELIABILITY)
    key = str(sector).strip().lower()
    for pattern, score in SECTOR_RELIABILITY_SCORES.items():
        if pattern in key or key in pattern:
            return float(score)
    return float(DEFAULT_SECTOR_RELIABILITY)


def _earnings_stability_proxy(operating_margin: Optional[float], debt_ratio: Optional[float], roe: Optional[float]) -> float:
    """재무 지표로 수익 안정성 프록시 (0–100). 영업이익률·부채·ROE 기반."""
    score = 50.0
    if operating_margin is not None and operating_margin > 0:
        score += min(25, operating_margin)
    if debt_ratio is not None and debt_ratio < 100:
        score += 10
    elif debt_ratio is not None and debt_ratio > 200:
        score -= 15
    if roe is not None and roe > 10:
        score += 10
    return max(0.0, min(100.0, score))


def _revenue_stability_proxy(operating_margin: Optional[float], institutional_ownership: Optional[float]) -> float:
    """매출 안정성 프록시 (0–100). 영업이익률·기관보유로 간이 추정."""
    score = 50.0
    if operating_margin is not None and operating_margin > 10:
        score += min(20, operating_margin * 0.5)
    if institutional_ownership is not None and institutional_ownership > 50:
        score += 15
    return max(0.0, min(100.0, score))


def _analyst_coverage_proxy(institutional_ownership: Optional[float]) -> float:
    """애널리스트 커버리지 프록시 (0–100). 기관보유율로 추정."""
    if institutional_ownership is None:
        return 50.0
    return max(0.0, min(100.0, 30 + institutional_ownership * 0.7))


def _volatility_factor(rsi: Optional[float]) -> float:
    """변동성 역지표 (0–100). RSI가 극단에 가까울수록 낮음."""
    if rsi is None:
        return 50.0
    # RSI 50 근처일수록 안정, 30 이하·70 이상일수록 변동성 높음
    dev = abs(rsi - 50)
    return max(0.0, min(100.0, 100 - dev * 1.2))


# --- FEATURE 2: 종목 신뢰도 점수 (0–100). 섹터 + 수익/매출 안정성 + 커버리지 + 변동성 ---
def compute_stock_reliability(
    sector: Optional[str] = None,
    operating_margin: Optional[float] = None,
    debt_ratio: Optional[float] = None,
    roe: Optional[float] = None,
    institutional_ownership: Optional[float] = None,
    rsi: Optional[float] = None,
) -> float:
    """
    Stock Reliability = 섹터(0.40) + 수익안정(0.25) + 매출안정(0.20) + 애널커버(0.10) + 변동성(0.05).
    각 요소 0–100, 가중합 후 0–100으로 클리핑.
    """
    sector_score = get_sector_reliability(sector)
    earnings = _earnings_stability_proxy(operating_margin, debt_ratio, roe)
    revenue = _revenue_stability_proxy(operating_margin, institutional_ownership)
    analyst = _analyst_coverage_proxy(institutional_ownership)
    vol = _volatility_factor(rsi)
    total = (
        sector_score * 0.40
        + earnings * 0.25
        + revenue * 0.20
        + analyst * 0.10
        + vol * 0.05
    )
    return round(max(0.0, min(100.0, total)), 1)


def get_reliability_level(score: float) -> str:
    """신뢰도 점수 → High / Medium / High Risk."""
    if score >= 70:
        return "high"
    if score >= 40:
        return "medium"
    return "high_risk"


def get_reliability_interpretation(sector_score: float, stock_score: float) -> str:
    """섹터·종목 신뢰도에 따른 해석 문구 (한국어)."""
    if sector_score < 40:
        return "이 섹터는 불확실성이 높아 밸류에이션 지표(PER, PBR 등)를 해석할 때 주의가 필요합니다."
    if sector_score < 60:
        return "이 섹터는 밸류에이션 지표의 신뢰도가 중간 수준입니다. 다른 지표와 함께 참고하세요."
    if stock_score < 40:
        return "해당 종목은 수익·매출 안정성 또는 변동성 측면에서 신뢰도가 낮을 수 있습니다."
    if stock_score >= 70:
        return "밸류에이션 및 재무 지표가 상대적으로 신뢰 가능한 수준으로 해석할 수 있습니다."
    return "종목 신뢰도가 중간 수준입니다. 투자 결정 시 다양한 지표를 함께 확인하세요."


# --- FEATURE 3: 투자 점수에 신뢰도 반영. 기존 점수(0–100) * 0.85 + 신뢰도 * 0.15 ---
def adjust_investment_score_with_reliability(raw_score: Optional[float], reliability_score: float) -> float:
    """기존 투자확률점수와 신뢰도 점수를 반영한 최종 투자 점수(0–100)."""
    base = float(raw_score) if raw_score is not None else 50.0
    return round(max(0.0, min(100.0, base * 0.85 + reliability_score * 0.15)), 1)
