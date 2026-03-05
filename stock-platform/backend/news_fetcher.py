"""
News data from NewsAPI.
"""
from datetime import datetime, timedelta
import os
import requests
from typing import List

from config import NEWS_API_KEY
from database import SessionLocal
from models import Stock, NewsData


def fetch_news(ticker: str, company_name: str = "", page_size: int = 20) -> List[dict]:
    """
    Fetch recent news for ticker/company. Returns list of {title, url, publishedAt, source}.
    Sentiment filled later by sentiment_analyzer.
    """
    if not NEWS_API_KEY:
        return []
    q = ticker if len(ticker) >= 2 else company_name or ticker
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": q,
        "apiKey": NEWS_API_KEY,
        "pageSize": page_size,
        "sortBy": "publishedAt",
        "language": "en",
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code != 200:
            return []
        data = r.json()
        articles = data.get("articles") or []
        return [
            {
                "title": a.get("title") or "",
                "url": a.get("url") or "",
                "publishedAt": a.get("publishedAt"),
                "source": (a.get("source") or {}).get("name", ""),
            }
            for a in articles
        ]
    except Exception:
        return []


def save_news_for_stock(stock_id: int, articles: List[dict], sentiment_by_title: dict) -> None:
    """Persist news with sentiment scores."""
    db = SessionLocal()
    try:
        for a in articles:
            title = a.get("title") or ""
            pub = a.get("publishedAt")
            if not pub:
                continue
            try:
                dt = datetime.fromisoformat(pub.replace("Z", "+00:00"))
            except Exception:
                dt = datetime.utcnow()
            sent = sentiment_by_title.get(title)
            if sent is None:
                sent = 0.0
            db.add(NewsData(
                stock_id=stock_id,
                title=title[:500],
                sentiment=float(sent),
                date=dt,
                url=(a.get("url") or "")[:1000],
                source=(a.get("source") or "")[:100],
            ))
        db.commit()
    finally:
        db.close()
