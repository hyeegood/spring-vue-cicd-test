"""
Investment Probability Score (0-100) from financial, alternative, technical, sentiment.
Implements all specified scoring rules.
"""
from datetime import date
from typing import Optional

# --- Financial (60) ---

def score_roe(roe: Optional[float]) -> float:
    if roe is None: return 0
    if roe >= 20: return 12
    if roe >= 15: return 9
    if roe >= 10: return 6
    if roe >= 5: return 3
    return 0


def score_fcf(fcf_growth: Optional[int]) -> float:
    # fcf_growth: 5 -> 12, 3 -> 9, 1 (positive) -> 6, 0 -> 0; unstable -> 3
    if fcf_growth is None: return 0
    if fcf_growth >= 5: return 12
    if fcf_growth >= 3: return 9
    if fcf_growth == 1: return 6
    if fcf_growth == -1: return 3  # unstable
    return 0


def score_per(per: Optional[float]) -> float:
    if per is None or per <= 0: return 0
    if 10 <= per <= 15: return 8
    if 15 < per <= 20: return 6
    if 20 < per <= 30: return 4
    if 30 < per <= 50: return 2
    return 0


def score_operating_margin(om: Optional[float]) -> float:
    if om is None: return 0
    if om >= 25: return 8
    if om >= 15: return 6
    if om >= 10: return 4
    if om >= 5: return 2
    return 0


def score_debt_ratio(dr: Optional[float]) -> float:
    if dr is None: return 8  # no debt info treat as good
    if dr <= 50: return 8
    if dr <= 100: return 6
    if dr <= 150: return 4
    if dr <= 200: return 2
    return 0


def score_ev_ebitda(ev: Optional[float]) -> float:
    if ev is None: return 4
    if ev <= 8: return 8
    if ev <= 12: return 6
    if ev <= 18: return 4
    if ev <= 25: return 2
    return 0


def score_pbr(pbr: Optional[float]) -> float:
    if pbr is None or pbr <= 0: return 0
    if 0 < pbr <= 2: return 2
    return 0


def score_peg(peg: Optional[float]) -> float:
    if peg is None or peg <= 0: return 0
    if 0 < peg <= 2: return 2
    return 0


# --- Alternative (20) ---

def score_institutional(inst: Optional[float]) -> float:
    if inst is None: return 0
    if inst > 70: return 5
    if inst > 50: return 3
    if inst > 30: return 2
    return 0


def score_insider_buying(activity: str) -> float:
    if activity == "buying": return 5
    if activity == "neutral": return 2
    return 0


def score_short_interest(short: Optional[float]) -> float:
    if short is None: return 3
    if short < 5: return 5
    if short < 10: return 3
    if short < 20: return 1
    return 0


def score_employee_growth(emp: Optional[float]) -> float:
    if emp is None: return 0
    if emp > 10: return 5
    if emp > 5: return 3
    if emp > 0: return 1
    return 0


# --- Technical (10) ---

def score_rsi(rsi: Optional[float]) -> float:
    if rsi is None: return 2
    if 30 <= rsi <= 45: return 4
    if 45 < rsi <= 60: return 3
    if 60 < rsi <= 75: return 1
    return 0


def score_ma_trend(trend: str) -> float:
    if trend == "golden_cross": return 3
    if trend == "uptrend": return 2
    return 0


def score_momentum(mom: str) -> float:
    if mom == "strong": return 3
    if mom == "neutral": return 1
    return 0


# --- Sentiment (10) ---

def score_sentiment(sentiment_raw: float) -> float:
    """sentiment_raw in [-1, 1]. Map to 0-5 for news, 0-5 for analyst (we use same)."""
    # -1 -> 0, +1 -> 5 linear
    news_pts = max(0, min(5, (sentiment_raw + 1) * 2.5))
    analyst_pts = news_pts  # same source for now
    return news_pts + analyst_pts


def compute_total_score(
    roe=None, per=None, pbr=None, peg=None, ev_ebitda=None,
    operating_margin=None, debt_ratio=None, fcf_growth=None,
    institutional_ownership=None, insider_activity="neutral", short_interest=None, employee_growth=None,
    rsi=None, ma_trend="downtrend", momentum="neutral",
    sentiment_score=0.0,
) -> float:
    total = 0.0
    total += score_roe(roe)
    total += score_fcf(fcf_growth)
    total += score_per(per)
    total += score_operating_margin(operating_margin)
    total += score_debt_ratio(debt_ratio)
    total += score_ev_ebitda(ev_ebitda)
    total += score_pbr(pbr)
    total += score_peg(peg)
    total += score_institutional(institutional_ownership)
    total += score_insider_buying(insider_activity)
    total += score_short_interest(short_interest)
    total += score_employee_growth(employee_growth)
    total += score_rsi(rsi)
    total += score_ma_trend(ma_trend)
    total += score_momentum(momentum)
    total += score_sentiment(sentiment_score)
    return min(100.0, max(0.0, total))
