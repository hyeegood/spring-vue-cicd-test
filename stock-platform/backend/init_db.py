"""
Create DB tables and optionally seed a few tickers.
Run: python init_db.py
Set DATABASE_URL if not using default.
"""
import os
from database import engine, Base
from models import Stock

def init():
    Base.metadata.create_all(bind=engine)
    print("Tables created.")

# 시드 종목: 주요 미국 상장사 (섹터 다양)
DEFAULT_TICKERS = [
    "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "NVDA", "META", "TSLA", "BRK-B", "UNH",
    "JNJ", "JPM", "V", "PG", "MA", "HD", "DIS", "XOM", "CVX", "ABBV", "MRK", "PEP",
    "KO", "COST", "AVGO", "WMT", "MCD", "CSCO", "ACN", "ABT", "TMO", "DHR", "NEE",
    "ADBE", "NFLX", "PM", "BMY", "UNP", "RTX", "HON", "INTC", "AMD", "QCOM", "TXN",
    "UPS", "AMGN", "LOW", "INTU", "SPGI", "CAT", "BA", "GE", "DE", "IBM", "AXP",
    "GS", "VZ", "T", "CVS", "MDT", "GILD", "LMT", "SBUX", "AMAT", "ADI", "REGN",
    "PLD", "ISRG", "SYK", "BLK", "BKNG", "CI", "C", "MO", "LRCX", "MMC", "CB",
    "SO", "DUK", "ZTS", "BDX", "EOG", "SLB", "CMCSA", "APD", "PGR", "CL", "FIS",
    "EQIX", "WM", "APTV", "ITW", "HCA", "AON", "SHW", "KLAC", "MCK", "PSA",
    "NOC", "CME", "PANW", "SNPS", "CDNS", "ORLY", "MAR", "MCO", "APH", "AIG",
    "DXCM", "ECL", "AZO", "WELL", "PSX", "AFL", "YUM", "MNST", "IDXX", "FAST",
    "CTAS", "ODFL", "ROST", "VRSK", "PCAR", "EXC", "AEP", "MET", "HLT", "TDG",
]

def seed_tickers():
    from database import SessionLocal
    db = SessionLocal()
    try:
        added = 0
        for t in DEFAULT_TICKERS:
            if db.query(Stock).filter(Stock.ticker == t).first():
                continue
            db.add(Stock(ticker=t, company_name=t))
            added += 1
        db.commit()
        print(f"Seeded {added} new tickers (total list: {len(DEFAULT_TICKERS)} tickers)")
    finally:
        db.close()

if __name__ == "__main__":
    init()
    seed_tickers()
