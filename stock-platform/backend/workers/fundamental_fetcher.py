# =======================================
# 재무 지표 수집 워커 (Yahoo Finance)
# prod_fundamentals, prod_stocks 업데이트
# =======================================
from typing import Optional, List
from datetime import datetime

from sqlalchemy.orm import Session

from database import SessionLocal
from models_production import ProdStock, ProdFundamentals


def _safe_float(v) -> Optional[float]:
    if v is None: return None
    try: return float(v)
    except (TypeError, ValueError): return None


def fetch_fundamentals_yahoo(ticker: str) -> dict:
    """Yahoo Finance에서 재무 지표를 가져오는 함수."""
    try:
        import yfinance as yf
    except ImportError:
        return {}
    try:
        t = yf.Ticker(ticker)
        info = t.info or {}
        # PE, PBR, ROE
        pe_ratio = _safe_float(info.get("trailingPE") or info.get("forwardPE"))
        pbr = _safe_float(info.get("priceToBook"))
        roe = _safe_float(info.get("returnOnEquity"))
        if roe is not None and abs(roe) <= 1:
            roe = roe * 100
        # 성장률: revenueGrowth, earningsGrowth (0.15 = 15%)
        revenue_growth = _safe_float(info.get("revenueGrowth"))
        if revenue_growth is not None and abs(revenue_growth) <= 1:
            revenue_growth = revenue_growth * 100
        earnings_growth = _safe_float(info.get("earningsGrowth"))
        if earnings_growth is not None and abs(earnings_growth) <= 1:
            earnings_growth = earnings_growth * 100
        # 부채, FCF
        debt_ratio = None
        try:
            bs = t.balance_sheet
            if bs is not None and not bs.empty:
                td = 0
                if "Total Debt" in bs.index:
                    td = bs.loc["Total Debt"].iloc[0]
                elif "Long Term Debt" in bs.index:
                    td = bs.loc["Long Term Debt"].iloc[0]
                te = bs.loc["Total Stockholder Equity"].iloc[0] if "Total Stockholder Equity" in bs.index else None
                if te and te != 0:
                    debt_ratio = (td / te) * 100
        except Exception:
            pass
        free_cash_flow = None
        try:
            cf = t.cashflow
            if cf is not None and "Free Cash Flow" in cf.index:
                free_cash_flow = _safe_float(cf.loc["Free Cash Flow"].iloc[0])
        except Exception:
            pass
        return {
            "pe_ratio": pe_ratio,
            "pbr": pbr,
            "roe": roe,
            "revenue_growth": revenue_growth,
            "earnings_growth": earnings_growth,
            "debt_ratio": debt_ratio,
            "free_cash_flow": free_cash_flow,
        }
    except Exception:
        return {}


def ensure_stock(db: Session, ticker: str, company_name: Optional[str] = None,
                 sector: Optional[str] = None, industry: Optional[str] = None,
                 description: Optional[str] = None, market_cap: Optional[int] = None) -> ProdStock:
    """prod_stocks에 종목이 없으면 생성 후 반환."""
    s = db.query(ProdStock).filter(ProdStock.ticker == ticker).first()
    if s:
        if company_name is not None: s.company_name = company_name
        if sector is not None: s.sector = sector
        if industry is not None: s.industry = industry
        if description is not None: s.description = description
        if market_cap is not None: s.market_cap = market_cap
        return s
    s = ProdStock(
        ticker=ticker,
        company_name=company_name,
        sector=sector,
        industry=industry,
        description=description,
        market_cap=market_cap,
    )
    db.add(s)
    return s


def upsert_fundamentals(db: Session, ticker: str, data: dict) -> None:
    """prod_fundamentals에 ticker당 1행 유지 (최신만)."""
    row = db.query(ProdFundamentals).filter(ProdFundamentals.ticker == ticker).first()
    if row:
        row.pe_ratio = data.get("pe_ratio")
        row.pbr = data.get("pbr")
        row.roe = data.get("roe")
        row.revenue_growth = data.get("revenue_growth")
        row.earnings_growth = data.get("earnings_growth")
        row.debt_ratio = data.get("debt_ratio")
        row.free_cash_flow = data.get("free_cash_flow")
        row.updated_at = datetime.utcnow()
    else:
        db.add(ProdFundamentals(
            ticker=ticker,
            pe_ratio=data.get("pe_ratio"),
            pbr=data.get("pbr"),
            roe=data.get("roe"),
            revenue_growth=data.get("revenue_growth"),
            earnings_growth=data.get("earnings_growth"),
            debt_ratio=data.get("debt_ratio"),
            free_cash_flow=data.get("free_cash_flow"),
        ))


def run_fundamental_fetcher(tickers: Optional[List[str]] = None) -> dict:
    """재무 지표 수집 후 DB 반영. tickers 없으면 prod_stocks 기준."""
    db = SessionLocal()
    try:
        if not tickers:
            tickers = [r[0] for r in db.query(ProdStock.ticker).all()]
        if not tickers:
            return {"updated": 0}
        try:
            import yfinance as yf
        except ImportError:
            return {"updated": 0}
        updated = 0
        for ticker in tickers:
            try:
                data = fetch_fundamentals_yahoo(ticker)
                if data:
                    t = yf.Ticker(ticker)
                    info = t.info or {}
                    ensure_stock(
                        db, ticker,
                        company_name=info.get("shortName") or info.get("longName"),
                        sector=info.get("sector"),
                        industry=info.get("industry"),
                        description=info.get("longBusinessSummary"),
                        market_cap=int(info.get("marketCap") or 0) or None,
                    )
                    upsert_fundamentals(db, ticker, data)
                    updated += 1
            except Exception:
                pass
        db.commit()
        return {"updated": updated}
    finally:
        db.close()
