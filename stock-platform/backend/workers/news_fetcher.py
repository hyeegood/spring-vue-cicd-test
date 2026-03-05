from database import SessionLocal
from models import Stock
from news_fetcher import fetch_news, save_news_for_stock
from sentiment_analyzer import batch_sentiment

def run_news_fetch(symbol=None):
    db = SessionLocal()
    try:
        stocks = db.query(Stock).filter(Stock.ticker == symbol.upper()).all() if symbol else db.query(Stock).limit(100).all()
        for s in stocks:
            try:
                articles = fetch_news(s.ticker or "", s.company_name or "")
                sentiments = batch_sentiment([a.get("title") or "" for a in articles]) if articles else {}
                save_news_for_stock(s.id, articles or [], sentiments)
            except Exception:
                pass
        db.commit()
    finally:
        db.close()
