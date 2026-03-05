# =======================================
# Production schema: SQLAlchemy models
# Matches schema/schema.sql (normalized, indexed)
# Use these for new features or migration from models.py
# =======================================
from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text, BigInteger, Index
from sqlalchemy.orm import relationship

# Import Base from main database module so tables are created in same DB
from database import Base


class StockProd(Base):
    """종목 마스터. symbol 유일, 인덱스: symbol, sector."""
    __tablename__ = "stocks_prod"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    name = Column(String(255))
    name_ko = Column(String(255))
    sector = Column(String(100), index=True)
    industry = Column(String(100))
    market_cap = Column(BigInteger)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    price_history = relationship("PriceHistoryProd", back_populates="stock")
    fundamentals = relationship("FundamentalsProd", back_populates="stock")
    scores = relationship("ScoresProd", back_populates="stock")
    news = relationship("NewsProd", back_populates="stock")
    recommendations = relationship("RecommendationsProd", back_populates="stock")

    __table_args__ = (Index("idx_stocks_prod_symbol", "symbol", unique=True),)


class PriceHistoryProd(Base):
    """가격 시계열. 인덱스: stock_id, timestamp, (stock_id, timestamp)."""
    __tablename__ = "price_history_prod"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_id = Column(Integer, ForeignKey("stocks_prod.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float, nullable=False)
    volume = Column(BigInteger)
    created_at = Column(DateTime, default=datetime.utcnow)

    stock = relationship("StockProd", back_populates="price_history")

    __table_args__ = (Index("idx_ph_prod_stock_ts", "stock_id", "timestamp", unique=True),)


class FundamentalsProd(Base):
    """재무 지표 스냅샷. 인덱스: stock_id, as_of_date, (stock_id, as_of_date)."""
    __tablename__ = "fundamentals_prod"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_id = Column(Integer, ForeignKey("stocks_prod.id", ondelete="CASCADE"), nullable=False, index=True)
    as_of_date = Column(Date, nullable=False, index=True)
    pe = Column(Float)
    pbr = Column(Float)
    peg = Column(Float)
    ev_ebitda = Column(Float)
    fcf_yield = Column(Float)
    revenue_growth = Column(Float)
    eps_growth = Column(Float)
    roe = Column(Float)
    operating_margin = Column(Float)
    debt_ratio = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    stock = relationship("StockProd", back_populates="fundamentals")

    __table_args__ = (Index("idx_fund_prod_stock_date", "stock_id", "as_of_date", unique=True),)


class ScoresProd(Base):
    """정량 점수 스냅샷. 인덱스: stock_id, as_of_date, investment_score DESC."""
    __tablename__ = "scores_prod"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_id = Column(Integer, ForeignKey("stocks_prod.id", ondelete="CASCADE"), nullable=False, index=True)
    as_of_date = Column(Date, nullable=False, index=True)
    value_score = Column(Float)
    growth_score = Column(Float)
    quality_score = Column(Float)
    sentiment_score = Column(Float)
    risk_adjustment = Column(Float)
    investment_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    stock = relationship("StockProd", back_populates="scores")

    __table_args__ = (
        Index("idx_scores_prod_stock_date", "stock_id", "as_of_date", unique=True),
        Index("idx_scores_prod_investment", "investment_score"),
    )


class NewsProd(Base):
    """뉴스. 인덱스: stock_id, published_at, (stock_id, published_at)."""
    __tablename__ = "news_prod"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_id = Column(Integer, ForeignKey("stocks_prod.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(500))
    summary = Column(Text)
    url = Column(String(1000))
    source = Column(String(100))
    sentiment = Column(Float)
    published_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    stock = relationship("StockProd", back_populates="news")

    __table_args__ = (Index("idx_news_prod_stock_pub", "stock_id", "published_at"),)


class RecommendationsProd(Base):
    """추천 (종목당 1건 또는 이력). 인덱스: stock_id."""
    __tablename__ = "recommendations_prod"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_id = Column(Integer, ForeignKey("stocks_prod.id", ondelete="CASCADE"), nullable=False, index=True)
    entry_price = Column(Float)
    stop_loss = Column(Float)
    target_price = Column(Float)
    recommendation_type = Column(String(20))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    stock = relationship("StockProd", back_populates="recommendations")


class UserProd(Base):
    """사용자. 인덱스: email (unique)."""
    __tablename__ = "users_prod"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, index=True)
    password_hash = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    watchlist = relationship("WatchlistProd", back_populates="user")

    __table_args__ = (Index("idx_users_prod_email", "email", unique=True),)


class WatchlistProd(Base):
    """관심 종목. 인덱스: user_id, stock_id, (user_id, stock_id) unique."""
    __tablename__ = "watchlist_prod"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users_prod.id", ondelete="CASCADE"), nullable=False, index=True)
    stock_id = Column(Integer, ForeignKey("stocks_prod.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("UserProd", back_populates="watchlist")
    stock = relationship("StockProd")

    __table_args__ = (Index("idx_watchlist_prod_user_stock", "user_id", "stock_id", unique=True),)
