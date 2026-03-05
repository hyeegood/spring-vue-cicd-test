"""
SQLAlchemy models for MariaDB. Matches required schema.
"""
from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base


class Stock(Base):
    """종목 테이블. 종목에 관한 모든 기본 정보(티커, 회사명, 섹터, 평점 등)를 보관."""
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(20), unique=True, nullable=False, index=True)
    company_name = Column(String(255))
    company_name_ko = Column(String(255))  # 종목 한글명
    sector = Column(String(100))
    glassdoor_rating = Column(Float)
    ceo_approval = Column(Float)
    employee_recommendation = Column(Float)
    review_count = Column(Integer)
    linkedin_employee_growth = Column(Float)  # e.g. 5.2 = 5.2%
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    scores = relationship("StockScore", back_populates="stock")
    price_history = relationship("PriceHistory", back_populates="stock")
    history = relationship("StockHistory", back_populates="stock", order_by="StockHistory.refreshed_at")
    recommendations = relationship("TradeRecommendation", back_populates="stock")
    options_data = relationship("OptionsData", back_populates="stock")
    news_data = relationship("NewsData", back_populates="stock")


class StockScore(Base):
    __tablename__ = "stock_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)

    # Financial (60)
    roe = Column(Float)
    per = Column(Float)
    pbr = Column(Float)
    peg = Column(Float)
    ev_ebitda = Column(Float)
    operating_margin = Column(Float)
    debt_ratio = Column(Float)
    fcf = Column(Float)

    # Alternative (20)
    institutional_ownership = Column(Float)
    insider_buying = Column(Float)  # score 0-5
    short_interest = Column(Float)
    # employee growth on Stock.linkedin_employee_growth

    # Technical (10)
    rsi = Column(Float)
    ma_trend = Column(Float)  # 0/2/3
    momentum = Column(Float)  # 0/1/3

    # Sentiment (10)
    sentiment_score = Column(Float)  # -1 to 1
    score = Column(Float, nullable=False)  # total 0-100

    created_at = Column(DateTime, default=datetime.utcnow)
    stock = relationship("Stock", back_populates="scores")


class PriceHistory(Base):
    """날짜별 가격 (일봉). 같은 날짜는 한 행만 유지."""
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False, index=True)
    price = Column(Float, nullable=False)
    volume = Column(Integer)
    date = Column(Date, nullable=False, index=True)
    open_ = Column("open", Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)

    stock = relationship("Stock", back_populates="price_history")


class StockHistory(Base):
    """종목 이력 테이블. 새로고침할 때마다 종목별로 1행씩 쌓이는 스냅샷(가격·점수 등)."""
    __tablename__ = "stock_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False, index=True)
    refreshed_at = Column(DateTime, nullable=False, index=True)  # 새로고침 시점
    price = Column(Float)  # 해당 시점 종가
    score = Column(Float)   # 해당 시점 투자점수
    roe = Column(Float)
    per = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    stock = relationship("Stock", back_populates="history")


class TradeRecommendation(Base):
    __tablename__ = "trade_recommendations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False, index=True)
    entry_price = Column(Float)
    stop_loss = Column(Float)
    target_price = Column(Float)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    stock = relationship("Stock", back_populates="recommendations")


class OptionsData(Base):
    __tablename__ = "options_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False, index=True)
    call_volume = Column(Integer)
    put_volume = Column(Integer)
    put_call_ratio = Column(Float)
    date = Column(Date, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow)

    stock = relationship("Stock", back_populates="options_data")


class NewsData(Base):
    __tablename__ = "news_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False, index=True)
    title = Column(String(500))
    sentiment = Column(Float)  # -1 to 1
    date = Column(DateTime, nullable=False)
    url = Column(String(1000))
    source = Column(String(100))

    stock = relationship("Stock", back_populates="news_data")


class Portfolio(Base):
    __tablename__ = "portfolio"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), nullable=False, index=True)  # optional auth
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    positions = relationship("PortfolioPosition", back_populates="portfolio")


class PortfolioPosition(Base):
    __tablename__ = "portfolio_positions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    portfolio_id = Column(Integer, ForeignKey("portfolio.id"), nullable=False)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    shares = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    portfolio = relationship("Portfolio", back_populates="positions")
    stock = relationship("Stock")


class User(Base):
    """사용자 (프로덕션 인증용)."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255))


class Watchlist(Base):
    """사용자별 관심 종목. user_id + symbol 유일."""
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
