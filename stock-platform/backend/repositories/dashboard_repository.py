# =======================================
# 대시보드 집계용 리포지토리
# 한 번에 필요한 데이터만 조회해 1초 이내 응답
# =======================================
from datetime import date
from typing import List, Optional

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from models import Stock, StockScore, PriceHistory, TradeRecommendation, NewsData


class DashboardRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_dashboard_candidates(self, min_rating: float = 4.0, limit: int = 100) -> List[tuple]:
        """대시보드 후보: glassdoor_rating >= min_rating, Stock+Score+Recommendation 조인."""
        today = date.today()
        rows = (
            self.db.query(Stock, StockScore, TradeRecommendation)
            .outerjoin(StockScore, (Stock.id == StockScore.stock_id) & (StockScore.date == today))
            .outerjoin(TradeRecommendation, Stock.id == TradeRecommendation.stock_id)
            .filter(Stock.glassdoor_rating >= min_rating)
            .order_by(Stock.id)
            .limit(limit)
            .all()
        )
        return rows

    def get_latest_prices_for_stocks(self, stock_ids: List[int]) -> dict:
        """종목별 최신 가격 1건 (stock_id -> price)."""
        if not stock_ids:
            return {}
        sub = (
            self.db.query(
                PriceHistory.stock_id,
                PriceHistory.price,
                PriceHistory.close,
                PriceHistory.date,
            )
            .filter(PriceHistory.stock_id.in_(stock_ids))
            .order_by(desc(PriceHistory.date))
            .distinct(PriceHistory.stock_id)
        )
        # SQLite distinct on 미지원 시 서브쿼리 또는 파이썬에서 첫 값만
        all_rows = (
            self.db.query(PriceHistory.stock_id, PriceHistory.price, PriceHistory.close)
            .filter(PriceHistory.stock_id.in_(stock_ids))
            .order_by(desc(PriceHistory.date))
            .all()
        )
        out = {}
        for sid, price, close in all_rows:
            if sid not in out:
                out[sid] = close if close is not None else price
        return out

    def get_latest_news(self, limit: int = 20) -> List:
        """전체 시장 뉴스 최신순 (종목 무관)."""
        return (
            self.db.query(NewsData)
            .order_by(desc(NewsData.date))
            .limit(limit)
            .all()
        )
