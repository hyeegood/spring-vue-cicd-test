# =======================================
# AI 인사이트 패널
# 재무·신뢰도·감성 요약 문장 생성 (규칙 기반)
# 반환: { "text": str, "label": "bullish"|"neutral"|"bearish" }
# =======================================
from typing import Optional, Literal

LabelType = Literal["bullish", "neutral", "bearish"]


def generate_ai_insight(
    sector: Optional[str] = None,
    sector_reliability: float = 50,
    stock_reliability: float = 50,
    investment_score: float = 50,
    sentiment_score: Optional[float] = None,
    roe: Optional[float] = None,
    risk_level: Optional[str] = None,
) -> str:
    """종목에 대한 한 줄 요약 인사이트 (한국어). 레거시 호환용."""
    res = generate_ai_insight_with_label(
        sector=sector,
        sector_reliability=sector_reliability,
        stock_reliability=stock_reliability,
        investment_score=investment_score,
        sentiment_score=sentiment_score,
        roe=roe,
        risk_level=risk_level,
    )
    return res["text"]


def generate_ai_insight_with_label(
    sector: Optional[str] = None,
    sector_reliability: float = 50,
    stock_reliability: float = 50,
    investment_score: float = 50,
    sentiment_score: Optional[float] = None,
    roe: Optional[float] = None,
    risk_level: Optional[str] = None,
) -> dict:
    """
    종목에 대한 간단한 분석 문장 + bullish/neutral/bearish 라벨.
    예: "Strong growth stock with high ROE and strong employee sentiment."
    """
    parts = []
    score_signal = 0  # 양수=bullish, 음수=bearish

    # 투자 점수
    if investment_score >= 70:
        parts.append("Strong investment score and")
        score_signal += 1
    elif investment_score < 40:
        score_signal -= 1

    # 성장/가치 (ROE)
    if roe is not None and roe >= 15:
        parts.append("high ROE")
        score_signal += 1
    elif roe is not None and roe >= 10:
        parts.append("stable profitability")

    # 감성
    if sentiment_score is not None:
        if sentiment_score > 0.2:
            parts.append("positive sentiment")
            score_signal += 1
        elif sentiment_score < -0.2:
            parts.append("negative sentiment")
            score_signal -= 1

    # 신뢰도
    if stock_reliability >= 70:
        parts.append("strong reliability")
    elif stock_reliability < 40:
        parts.append("weak reliability")
        score_signal -= 1

    # 리스크
    if risk_level and (risk_level == "high" or risk_level == "High Risk"):
        parts.append("elevated risk; caution advised.")
        score_signal -= 1
    elif sector_reliability < 60:
        parts.append("moderate sector volatility; use with other indicators.")
    else:
        parts.append("reasonable reference for investment decisions.")

    if not parts:
        text = "Insufficient data for analysis. Consider more data before deciding."
    else:
        text = " ".join(parts)
        if not text.strip().endswith((".", "!")):
            text = text.rstrip(".") + "."
        text = text.replace("..", ".")

    # 라벨 결정
    if score_signal >= 1:
        label: LabelType = "bullish"
    elif score_signal <= -1:
        label = "bearish"
    else:
        label = "neutral"

    return {"text": text, "label": label}
