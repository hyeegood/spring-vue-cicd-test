# 뉴스 수집 워커: prod_news (News API / Yahoo 폴백)
import os
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from database import SessionLocal
from models_production import ProdNews, ProdStock

def fetch_news_for_ticker(ticker: str, limit: int = 20) -> List[dict]:
    if os.getenv("NEWS_API_KEY", "").strip():
        try:
            import requests
            r = requests.get(
                "https://newsapi.org/v2/everything",
                params={"q": ticker, "apiKey": os.getenv("NEWS_API_KEY"), "pageSize": limit, "sortBy": "publishedAt"},
                timeout=10,
            )
            if r.status_code == 200:
                articles = (r.json() or {}).get("articles") or []
                return [{"title": a.get("title") or "", "source": (a.get("source") or {}).get("name") or "",
                    "url": a.get("url") or "", "published_at": datetime.utcnow()} for a in articles]
        except Exception:
            pass
    try:
        import yfinance as yf
        news = getattr(yf.Ticker(ticker), "news", None) or []
        return [{"title": n.get("title") or "", "source": n.get("publisher") or "Yahoo", "url": n.get("link") or "",
            "published_at": datetime.fromtimestamp(n["providerPublishTime"]) if n.get("providerPublishTime") else datetime.utcnow()}
            for n in news[:limit]]
    except Exception:
        return []

def run_news_fetcher(tickers: Optional[List[str]] = None, limit_per_ticker: int = 15) -> dict:
    db = SessionLocal()
    try:
        if not tickers:
            tickers = [r[0] for r in db.query(ProdStock.ticker).all()]
        total = 0
        for ticker in tickers or []:
            try:
                for it in fetch_news_for_ticker(ticker, limit_per_ticker):
                    db.add(ProdNews(ticker=ticker, title=(it.get("title") or "")[:500],
                        source=(it.get("source") or "")[:100], url=(it.get("url") or "")[:1000],
                        published_at=it.get("published_at") or datetime.utcnow()))
                    total += 1
            except Exception:
                pass
        db.commit()
        return {"inserted": total}
    finally:
        db.close()
