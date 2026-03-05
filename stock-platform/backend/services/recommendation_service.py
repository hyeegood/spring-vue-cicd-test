# =======================================
# 추천 엔진: InvestmentScore > 75, Risk != High, Positive sentiment
# 점수 내림차순 정렬
# =======================================
from typing import List

from sqlalchemy.orm import Session

from services.dashboard_service import get_dashboard_analytics


def get_recommendations(db: Session, limit: int = 50, last_refresh_at: str = None) -> List[dict]:
    data = get_dashboard_analytics(db, last_refresh_at=last_refresh_at)
    all_items = data.get("all_items", data.get("top_picks", []) + data.get("trending_stocks", []))
    seen = set()
    unique = []
    for i in all_items:
        s = i.get("symbol")
        if not s or s in seen:
            continue
        seen.add(s)
        inv = i.get("investment_score") or 0
        risk = (i.get("risk_level") or "").lower()
        sent = i.get("sentiment_score")
        if inv <= 75:
            continue
        if "high" in risk:
            continue
        if sent is not None and sent < 50:
            continue
        unique.append(i)
    unique.sort(key=lambda x: -(x.get("investment_score") or 0))
    return unique[:limit]
