from datetime import date
from typing import List, Optional
from sqlalchemy import desc
from sqlalchemy.orm import Session
from models import Stock, StockScore, PriceHistory, TradeRecommendation, NewsData

class StockRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_symbol(self, symbol: str) -> Optional[Stock]:
        return self.db.query(Stock).filter(Stock.ticker == symbol.upper()).first()

    def get_all_symbols(self, limit: int = 500) -> List[str]:
        rows = self.db.query(Stock.ticker).limit(limit).all()
        return [r[0] for r in rows if r[0]]

    def get_latest_score(self, stock_id: int, as_of: Optional[date] = None) -> Optional[StockScore]:
        d = as_of or date.today()
        return self.db.query(StockScore).filter(StockScore.stock_id == stock_id, StockScore.date == d).first()

    def get_price_history(self, stock_id: int, limit: int = 365) -> List[tuple]:
        rows = (
            self.db.query(PriceHistory.date, PriceHistory.price, PriceHistory.close)
            .filter(PriceHistory.stock_id == stock_id)
            .order_by(desc(PriceHistory.date))
            .limit(limit)
            .all()
        )
        return [(r[0], r[2] if r[2] is not None else r[1]) for r in rows]

    def get_recommendation(self, stock_id: int):
        return self.db.query(TradeRecommendation).filter(TradeRecommendation.stock_id == stock_id).first()

    def get_news(self, stock_id: int, limit: int = 15) -> List:
        return self.db.query(NewsData).filter(NewsData.stock_id == stock_id).order_by(desc(NewsData.date)).limit(limit).all()
