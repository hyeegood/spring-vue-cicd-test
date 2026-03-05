from collections import Counter
from typing import Any, Optional
from sqlalchemy.orm import Session
from repositories import DashboardRepository
from reliability_engine import get_sector_reliability, compute_stock_reliability, get_reliability_level
from services.investment_score import (
    compute_value_score,
    compute_growth_score,
    compute_sentiment_score_normalized,
    compute_unified_investment_score,
    get_investment_interpretation,
)
from utils.cache import cache_get, cache_set

CACHE_KEY = "dashboard_analytics"
CACHE_TTL = 60

def _company_name_ko(stock):
    return getattr(stock, "company_name_ko", None)

def _risk_from_score(score):
    if score is None:
        return "Medium"
    if score >= 70:
        return "Low"
    if score >= 40:
        return "Medium"
    return "High"

def _item_from_row(stock, score, rec, latest_prices):
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
    val = compute_value_score(score.per if score else None, score.pbr if score else None, getattr(score, "ev_ebitda", None) if score else None, score.operating_margin if score else None, score.debt_ratio if score else None)
    gr = compute_growth_score(score.roe if score else None, score.operating_margin if score else None, getattr(stock, "linkedin_employee_growth", None))
    sent = compute_sentiment_score_normalized(score.sentiment_score if score else None)
    inv_score = compute_unified_investment_score(val, gr, sent, stock_rel)
    return {
        "symbol": stock.ticker,
        "name": stock.company_name,
        "name_ko": _company_name_ko(stock),
        "sector": stock.sector,
        "current_price": latest_prices.get(stock.id),
        "value_score": val,
        "growth_score": gr,
        "sentiment_score": sent,
        "reliability_score": stock_rel,
        "investment_score": inv_score,
        "investment_interpretation": get_investment_interpretation(inv_score),
        "reliability_level": get_reliability_level(stock_rel),
        "risk_level": _risk_from_score(raw),
        "entry_price": rec.entry_price if rec else None,
        "glassdoor_rating": stock.glassdoor_rating,
    }

def get_dashboard_analytics(db: Session, last_refresh_at: Optional[str] = None) -> dict:
    cached = cache_get(CACHE_KEY)
    if cached is not None:
        return cached
    repo = DashboardRepository(db)
    rows = repo.get_dashboard_candidates(limit=100)
    stock_ids = [stock.id for stock, _, _ in rows]
    latest_prices = repo.get_latest_prices_for_stocks(stock_ids)
    items = [_item_from_row(stock, score, rec, latest_prices) for stock, score, rec in rows]
    items.sort(key=lambda x: (-(x.get("investment_score") or 0), x.get("symbol") or ""))
    top_picks = items[:10]
    trending_stocks = items[:15]
    sector_counts = Counter(i.get("sector") or "Unknown" for i in items)
    top_sectors = [{"sector": s, "count": c} for s, c in sector_counts.most_common(10)]
    news_rows = repo.get_latest_news(limit=10)
    market_news = [{"title": n.title, "sentiment": n.sentiment, "published_at": n.date.isoformat() if n.date else None} for n in news_rows]
    payload = {"market_overview": {"sp500": None, "nasdaq": None, "vix": None}, "top_picks": top_picks, "trending_stocks": trending_stocks, "all_items": items[:200], "top_sectors": top_sectors, "market_news": market_news, "last_refresh_at": last_refresh_at}
    cache_set(CACHE_KEY, payload, CACHE_TTL)
    return payload
