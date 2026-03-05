from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from services.dashboard_service import get_dashboard_analytics

router = APIRouter()

@router.get("/screener")
def screener(
    db: Session = Depends(get_db),
    min_score: float = Query(None),
    sector: str = Query(None),
    limit: int = Query(100, le=200),
):
    data = get_dashboard_analytics(db)
    items = data.get("all_items", [])
    if min_score is not None:
        items = [i for i in items if (i.get("investment_score") or 0) >= min_score]
    if sector:
        items = [i for i in items if (i.get("sector") or "").lower() == sector.lower()]
    items.sort(key=lambda x: (-(x.get("investment_score") or 0), x.get("symbol") or ""))
    return {"items": items[:limit], "total": len(items)}
