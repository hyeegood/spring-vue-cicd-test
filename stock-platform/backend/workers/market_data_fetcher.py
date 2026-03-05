# =======================================
# 시장 데이터 수집 워커
# 가격·거래량을 DB(price_history)에 저장
# =======================================
from database import SessionLocal
from models import Stock, PriceHistory
from datetime import datetime
from data_fetcher import update_stock_prices_and_financials

def run_market_data_fetch(symbol: str = None):
    """단일 종목 또는 전체 종목 가격/재무 갱신."""
    db = SessionLocal()
    try:
        if symbol:
            update_stock_prices_and_financials(symbol)
        else:
            for row in db.query(Stock.ticker).limit(500).all():
                if row[0]:
                    try:
                        update_stock_prices_and_financials(row[0])
                    except Exception:
                        pass
    finally:
        db.close()
