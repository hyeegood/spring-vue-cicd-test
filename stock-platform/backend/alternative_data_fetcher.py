"""
Alternative data: institutional ownership, insider trading, short interest, employee growth.
Sources: Yahoo Finance info + optional external APIs.
"""
from typing import Optional
import yfinance as yf

from database import SessionLocal
from models import Stock


def fetch_institutional_ownership(ticker: str) -> Optional[float]:
    """Percentage of shares held by institutions. yfinance major_holders."""
    try:
        t = yf.Ticker(ticker)
        maj = t.institutional_holders  # DataFrame or None
        if maj is not None and not maj.empty and "Holdings" in maj.columns:
            total = maj["Holdings"].sum()
            if total > 0:
                # Approximate: % of float
                return min(100.0, float(total) / 1e6)  # simplistic
        # Alternative from info
        info = t.info
        v = info.get("heldPercentInstitutions")
        if v is not None:
            return float(v) * 100 if abs(v) <= 1 else float(v)
        return None
    except Exception:
        return None


def fetch_short_interest(ticker: str) -> Optional[float]:
    """Short interest as percentage of float."""
    try:
        t = yf.Ticker(ticker)
        info = t.info
        v = info.get("shortPercentOfFloat")
        if v is not None:
            return float(v) * 100 if abs(v) <= 1 else float(v)
        return None
    except Exception:
        return None


def fetch_insider_activity(ticker: str) -> str:
    """
    'buying' | 'neutral' | 'selling' based on recent insider transactions.
    yfinance has no direct insider; we use placeholder or external API.
    """
    try:
        t = yf.Ticker(ticker)
        # yfinance: insiders might be in .insider_transactions
        ins = getattr(t, "insider_transactions", None)
        if ins is not None and not ins.empty and "Transactions" in str(type(ins)):
            # Simplified: if more buys than sells -> buying
            return "buying"
        return "neutral"
    except Exception:
        return "neutral"


def fetch_employee_growth(ticker: str) -> Optional[float]:
    """
    직원증가율 %. LinkedIn 등 없으면 yfinance 이익/매출 성장률로 대체.
    """
    try:
        t = yf.Ticker(ticker)
        info = t.info or {}
        # Yahoo Finance 성장률 (소수 0.15 = 15%)
        eg = info.get("earningsGrowth")
        rg = info.get("revenueGrowth")
        sg = info.get("earningsQuarterlyGrowth")
        growths = []
        for g in (eg, rg, sg):
            if g is not None:
                try:
                    v = float(g)
                    if abs(v) < 10:  # 이미 비율(0.15 등)이면
                        growths.append(v * 100)
                    else:
                        growths.append(v)
                except (TypeError, ValueError):
                    pass
        if growths:
            # 이익/매출 성장률을 직원증가 대리지표로 사용 (상한 25%로 제한)
            proxy = sum(growths) / len(growths)
            return round(max(-5.0, min(25.0, proxy)), 1)
        # get_earnings_estimate 등에서 growth 컬럼 시도
        try:
            est = t.get_earnings_estimate()
            if est is not None and not est.empty and "growth" in est.columns:
                v = float(est["growth"].iloc[0])
                return round(max(-5.0, min(25.0, v)), 1)
        except Exception:
            pass
        return None
    except Exception:
        return None


def update_alternative_data(ticker: str) -> dict:
    """Fetch and return alternative metrics; optionally persist to Stock."""
    inst = fetch_institutional_ownership(ticker)
    short = fetch_short_interest(ticker)
    insider = fetch_insider_activity(ticker)
    emp = fetch_employee_growth(ticker)

    db = SessionLocal()
    try:
        stock = db.query(Stock).filter(Stock.ticker == ticker).first()
        if stock:
            if emp is not None:
                stock.linkedin_employee_growth = emp
            db.commit()
    finally:
        db.close()

    return {
        "institutional_ownership": inst,
        "short_interest": short,
        "insider_activity": insider,
        "employee_growth": emp,
    }
