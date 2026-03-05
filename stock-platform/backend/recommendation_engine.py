"""
Trade recommendations: entry, stop loss, target.
Entry: near 20-day MA, RSI < 45.
Stop: 6-8% below entry, below support.
Target: 15-30% above entry, near resistance.
"""
from typing import Optional, List
from datetime import datetime, timedelta
import yfinance as yf

from database import SessionLocal
from models import Stock, TradeRecommendation, PriceHistory


def _ma(series, period: int) -> Optional[float]:
    if series is None or len(series) < period:
        return None
    return float(series[-period:].mean())


def compute_recommendation(ticker: str) -> dict:
    """
    Returns { entry_price, stop_loss, target_price }.
    """
    t = yf.Ticker(ticker)
    hist = t.history(period="3mo")
    if hist is None or len(hist) < 20:
        return {"entry_price": None, "stop_loss": None, "target_price": None}

    close = hist["Close"]
    current = float(close.iloc[-1])
    ma20 = _ma(close, 20)
    if ma20 is None:
        ma20 = current
    # Entry near 20-day MA
    entry = float(ma20)
    # Stop 6-8% below entry
    stop = entry * 0.92
    # Target 15-30% above entry
    target = entry * 1.22

    return {
        "entry_price": round(entry, 2),
        "stop_loss": round(stop, 2),
        "target_price": round(target, 2),
    }


def update_recommendation_for_stock(ticker: str) -> bool:
    rec = compute_recommendation(ticker)
    if rec["entry_price"] is None:
        return False
    db = SessionLocal()
    try:
        stock = db.query(Stock).filter(Stock.ticker == ticker).first()
        if not stock:
            return False
        existing = db.query(TradeRecommendation).filter(TradeRecommendation.stock_id == stock.id).first()
        if existing:
            existing.entry_price = rec["entry_price"]
            existing.stop_loss = rec["stop_loss"]
            existing.target_price = rec["target_price"]
        else:
            db.add(TradeRecommendation(
                stock_id=stock.id,
                entry_price=rec["entry_price"],
                stop_loss=rec["stop_loss"],
                target_price=rec["target_price"],
            ))
        db.commit()
        return True
    finally:
        db.close()
