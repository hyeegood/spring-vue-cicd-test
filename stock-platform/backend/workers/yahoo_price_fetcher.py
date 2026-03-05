# Yahoo Finance price fetcher for prod_price_history
from datetime import date, datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from database import SessionLocal
from models_production import ProdPriceHistory, ProdStock

def _safe_float(v):
    if v is None: return None
    try: return float(v)
    except (TypeError, ValueError): return None

def fetch_prices_yahoo(ticker: str, days: int = 365) -> List[dict]:
    try:
        import yfinance as yf
        t = yf.Ticker(ticker)
        end = datetime.now()
        start = end - timedelta(days=days)
        df = t.history(start=start, end=end)
        if df is None or df.empty: return []
        return [{"date": (dt.date() if hasattr(dt, "date") else dt), "open": _safe_float(row.get("Open")), "high": _safe_float(row.get("High")), "low": _safe_float(row.get("Low")), "close": _safe_float(row.get("Close")) or 0, "volume": int(row["Volume"]) if row.get("Volume") else None} for dt, row in df.iterrows()]
    except Exception:
        return []

def upsert_price_history(db: Session, ticker: str, records: List[dict]) -> int:
    c = 0
    for r in records:
        d = r.get("date"); d = date.fromisoformat(d[:10]) if isinstance(d, str) else d
        if d is None or r.get("close") is None: continue
        ex = db.query(ProdPriceHistory).filter(ProdPriceHistory.ticker == ticker, ProdPriceHistory.date == d).first()
        if ex: ex.open, ex.high, ex.low, ex.close, ex.volume = r.get("open"), r.get("high"), r.get("low"), r.get("close"), r.get("volume")
        else: db.add(ProdPriceHistory(ticker=ticker, date=d, open=r.get("open"), high=r.get("high"), low=r.get("low"), close=r.get("close"), volume=r.get("volume")))
        c += 1
    return c

def run_yahoo_price_fetcher(tickers: Optional[List[str]] = None, days: int = 365) -> dict:
    db = SessionLocal()
    try:
        tickers = tickers or [r[0] for r in db.query(ProdStock.ticker).all()]
        out = {}
        for t in tickers:
            try:
                rec = fetch_prices_yahoo(t, days=days)
                if rec: out[t] = upsert_price_history(db, t, rec)
            except Exception: out[t] = 0
        db.commit()
        return out
    finally:
        db.close()
