# 프로덕션 대시보드 서비스: market indexes, top_picks, trending, sectors, news. 캐시 10초.
from sqlalchemy.orm import Session
from utils.cache import cache_get, cache_set
from repositories.dashboard_repository_prod import DashboardRepositoryProd

CACHE_KEY = "dashboard_analytics_prod"
CACHE_TTL = 10  # 10초

def get_dashboard_analytics_prod(db: Session) -> dict:
    """프로덕션 대시보드: 시장 지수, Top 추천, 트렌딩, Top 섹터, 최신 뉴스. 캐시 10초."""
    cached = cache_get(CACHE_KEY)
    if cached is not None:
        return cached
    repo = DashboardRepositoryProd(db)
    market_overview = repo.get_market_indexes()
    top_picks = repo.get_top_recommendations(limit=10)
    trending_stocks = repo.get_trending_stocks(limit=15)
    top_sectors = repo.get_top_sectors(limit=10)
    news_rows = repo.get_latest_news(limit=10)
    market_news = [
        {"title": n.title, "url": n.url, "source": n.source, "published_at": n.published_at.isoformat() if n.published_at else None, "date": n.published_at.isoformat() if n.published_at else None}
        for n in news_rows
    ]
    payload = {
        "market_overview": market_overview,
        "top_picks": top_picks,
        "trending_stocks": trending_stocks,
        "top_sectors": top_sectors,
        "market_news": market_news,
    }
    cache_set(CACHE_KEY, payload, CACHE_TTL)
    return payload
