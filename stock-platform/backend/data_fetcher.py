"""
Financial data fetcher using Yahoo Finance (yfinance).
"""
from datetime import datetime, timedelta
from typing import Optional
import yfinance as yf
import pandas as pd

from database import SessionLocal
from models import Stock, PriceHistory, StockScore


def fetch_financials(ticker: str) -> dict:
    """Fetch key financial metrics for scoring."""
    t = yf.Ticker(ticker)
    info = t.info
    hist = t.history(period="5y") if hasattr(t, "history") else None

    # ROE
    roe = _safe_float(info.get("returnOnEquity"))
    if roe is None and "returnOnEquity" not in (info or {}):
        try:
            fin = t.financials
            if fin is not None and not fin.empty:
                net_income = fin.loc["Net Income"].iloc[0] if "Net Income" in fin.index else None
                equity = t.balance_sheet.loc["Total Stockholder Equity"].iloc[0] if t.balance_sheet is not None and "Total Stockholder Equity" in t.balance_sheet.index else None
                if net_income and equity and equity != 0:
                    roe = (net_income / equity) * 100
        except Exception:
            roe = None

    # PER, PBR, PEG
    per = _safe_float(info.get("trailingPE") or info.get("forwardPE"))
    pbr = _safe_float(info.get("priceToBook"))
    peg = _safe_float(info.get("pegRatio"))

    # EV/EBITDA
    ev_ebitda = _safe_float(info.get("enterpriseToEbitda"))

    # Operating margin
    operating_margin = _safe_float(info.get("operatingMargins"))
    if operating_margin is not None and abs(operating_margin) <= 1:
        operating_margin = operating_margin * 100

    # Debt ratio (Total Debt / Equity * 100)
    debt_ratio = None
    try:
        bs = t.balance_sheet
        if bs is not None and not bs.empty:
            td = bs.loc["Total Debt"].iloc[0] if "Total Debt" in bs.index else (bs.loc["Long Term Debt"].iloc[0] if "Long Term Debt" in bs.index else 0)
            te = bs.loc["Total Stockholder Equity"].iloc[0] if "Total Stockholder Equity" in bs.index else None
            if te and te != 0:
                debt_ratio = (td / te) * 100
    except Exception:
        pass

    # FCF: 5y/3y growth or positive
    fcf_growth = None
    try:
        cf = t.cashflow
        if cf is not None and "Free Cash Flow" in cf.index:
            fcf_series = cf.loc["Free Cash Flow"]
            if len(fcf_series) >= 5:
                # 5 years growth
                fcf_growth = 5
            elif len(fcf_series) >= 3:
                fcf_growth = 3
            elif len(fcf_series) >= 1 and fcf_series.iloc[0] and fcf_series.iloc[0] > 0:
                fcf_growth = 1  # positive
            else:
                fcf_growth = 0
        else:
            fcf_growth = 0
    except Exception:
        fcf_growth = 0

    return {
        "roe": roe,
        "per": per,
        "pbr": pbr,
        "peg": peg,
        "ev_ebitda": ev_ebitda,
        "operating_margin": operating_margin,
        "debt_ratio": debt_ratio,
        "fcf_growth": fcf_growth,
    }


def fetch_prices(ticker: str, days: int = 365) -> list[dict]:
    """Fetch OHLCV history for chart and MA/RSI."""
    t = yf.Ticker(ticker)
    end = datetime.now()
    start = end - timedelta(days=days)
    df = t.history(start=start, end=end)
    if df is None or df.empty:
        return []
    records = []
    for dt, row in df.iterrows():
        d = dt.date() if hasattr(dt, "date") else dt
        records.append({
            "date": str(d),
            "open": float(row["Open"]) if "Open" in row else None,
            "high": float(row["High"]) if "High" in row else None,
            "low": float(row["Low"]) if "Low" in row else None,
            "close": float(row["Close"]) if "Close" in row else None,
            "volume": int(row["Volume"]) if "Volume" in row else None,
        })
    return records


def fetch_company_summary(ticker: str) -> Optional[str]:
    """Yahoo Finance longBusinessSummary for stock detail page."""
    try:
        t = yf.Ticker(ticker)
        info = t.info or {}
        return (info.get("longBusinessSummary") or "").strip() or None
    except Exception:
        return None


def _safe_float(v):
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def get_current_price(ticker: str) -> Optional[float]:
    """Quick fetch of latest close price for dashboard."""
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="5d")
        if hist is not None and not hist.empty and "Close" in hist.columns:
            return float(hist["Close"].iloc[-1])
        info = t.info or {}
        return _safe_float(info.get("currentPrice") or info.get("regularMarketPrice"))
    except Exception:
        return None


def update_stock_prices_and_financials(ticker: str) -> bool:
    """Update DB: price history and financial metrics for one ticker."""
    db = SessionLocal()
    try:
        stock = db.query(Stock).filter(Stock.ticker == ticker).first()
        if not stock:
            t = yf.Ticker(ticker)
            info = t.info or {}
            stock = Stock(
                ticker=ticker,
                company_name=info.get("longName") or info.get("shortName") or ticker,
                sector=info.get("sector") or info.get("industry"),
            )
            db.add(stock)
            db.commit()
            db.refresh(stock)

        financials = fetch_financials(ticker)
        prices = fetch_prices(ticker, days=60)
        today = datetime.now().date()

        for rec in prices[-30:]:  # last 30 days
            d = datetime.strptime(rec["date"], "%Y-%m-%d").date()
            existing = db.query(PriceHistory).filter(
                PriceHistory.stock_id == stock.id,
                PriceHistory.date == d
            ).first()
            if not existing and rec.get("close"):
                db.add(PriceHistory(
                    stock_id=stock.id,
                    price=rec["close"],
                    volume=rec.get("volume"),
                    date=d,
                    open_=rec.get("open"),
                    high=rec.get("high"),
                    low=rec.get("low"),
                    close=rec.get("close"),
                ))
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
