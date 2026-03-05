"""
Options chain data from Yahoo Finance.
"""
from datetime import date
from typing import Optional
import yfinance as yf

from database import SessionLocal
from models import Stock, OptionsData


def fetch_options_chain(ticker: str) -> dict:
    """
    Fetch options chain and return call_volume, put_volume, put_call_ratio.
    """
    try:
        t = yf.Ticker(ticker)
        exp_dates = t.options
        if not exp_dates:
            return {"call_volume": 0, "put_volume": 0, "put_call_ratio": 0.0}

        # Use nearest expiry
        opt = t.option_chain(exp_dates[0])
        calls = opt.calls if opt.calls is not None else __import__("pandas").DataFrame()
        puts = opt.puts if opt.puts is not None else __import__("pandas").DataFrame()

        call_vol = int(calls["volume"].sum()) if "volume" in calls.columns else 0
        put_vol = int(puts["volume"].sum()) if "volume" in puts.columns else 0
        put_call_ratio = (put_vol / call_vol) if call_vol else 0.0

        return {
            "call_volume": call_vol,
            "put_volume": put_vol,
            "put_call_ratio": round(put_call_ratio, 4),
        }
    except Exception:
        return {"call_volume": 0, "put_volume": 0, "put_call_ratio": 0.0}


def update_options_data(ticker: str) -> bool:
    """Persist options data for ticker."""
    data = fetch_options_chain(ticker)
    db = SessionLocal()
    try:
        stock = db.query(Stock).filter(Stock.ticker == ticker).first()
        if not stock:
            db.close()
            return False
        today = date.today()
        existing = db.query(OptionsData).filter(
            OptionsData.stock_id == stock.id,
            OptionsData.date == today,
        ).first()
        if not existing:
            db.add(OptionsData(
                stock_id=stock.id,
                call_volume=data["call_volume"],
                put_volume=data["put_volume"],
                put_call_ratio=data["put_call_ratio"],
                date=today,
            ))
            db.commit()
        return True
    finally:
        db.close()
