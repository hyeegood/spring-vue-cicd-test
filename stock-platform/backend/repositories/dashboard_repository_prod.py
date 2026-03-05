# 프로덕션 대시보드 리포지토리: prod_* 테이블 기반 집계
from datetime import date, timedelta
from typing import List, Optional
from sqlalchemy import desc, func
from sqlalchemy.orm import Session
from models_production import ProdStock, ProdScores, ProdPriceHistory, ProdNews

class DashboardRepositoryProd:
    def __init__(self, db: Session):
        self.db = db

    def get_market_indexes(self) -> dict:
        """시장 지수 (S&P 500, NASDAQ, VIX). Yahoo 등 외부 연동 시 여기서 반환. 현재는 플레이스홀더."""
        return {"sp500": None, "nasdaq": None, "vix": None}

    def get_top_recommendations(self, limit: int = 10) -> List[dict]:
        """투자 점수 상위 종목 + 최신 가격."""
        rows = (
            self.db.query(ProdStock, ProdScores)
            .outerjoin(ProdScores, ProdStock.ticker == ProdScores.ticker)
            .order_by(desc(ProdScores.investment_score))
            .limit(limit * 2)
            .all()
        )
        tickers = [r[0].ticker for r in rows[:limit]]
        prices = self.get_latest_prices_by_ticker(tickers)
        out = []
        for stock, score in rows[:limit]:
            s = {
                "symbol": stock.ticker,
                "ticker": stock.ticker,
                "name": stock.company_name,
                "company_name": stock.company_name,
                "name_ko": stock.company_name_ko,
                "sector": stock.sector or "Technology",
                "current_price": prices.get(stock.ticker),
                "investment_score": score.investment_score if score else None,
                "score": score.investment_score if score else None,
                "value_score": score.value_score if score else None,
                "growth_score": score.growth_score if score else None,
            }
            out.append(s)
        return out

    def get_trending_stocks(self, limit: int = 15) -> List[dict]:
        """트렌딩: 최근 거래량/변동 기준 또는 점수 상위."""
        return self.get_top_recommendations(limit=limit)

    def get_top_sectors(self, limit: int = 10) -> List[dict]:
        """섹터별 종목 수 상위."""
        q = (
            self.db.query(ProdStock.sector, func.count(ProdStock.ticker).label("cnt"))
            .filter(ProdStock.sector.isnot(None), ProdStock.sector != "")
            .group_by(ProdStock.sector)
            .order_by(desc("cnt"))
            .limit(limit)
            .all()
        )
        return [{"sector": s or "Unknown", "count": c} for s, c in q]

    def get_latest_news(self, limit: int = 20) -> List:
        """전체 뉴스 최신순."""
        return (
            self.db.query(ProdNews)
            .order_by(desc(ProdNews.published_at))
            .limit(limit)
            .all()
        )

    def get_latest_prices_by_ticker(self, tickers: List[str]) -> dict:
        """ticker별 최신 close 가격 1건."""
        if not tickers:
            return {}
        out = {}
        for ticker in tickers:
            row = (
                self.db.query(ProdPriceHistory.close)
                .filter(ProdPriceHistory.ticker == ticker)
                .order_by(desc(ProdPriceHistory.date))
                .first()
            )
            if row:
                out[ticker] = row[0]
        return out
