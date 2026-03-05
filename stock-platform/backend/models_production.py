# =======================================
# 프로덕션 정규화 스키마용 SQLAlchemy 모델
# prod_* 테이블: 기존 테이블과 공존 (기존 구조 유지)
# =======================================
from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text, BigInteger, Index
from database import Base


class ProdStock(Base):
    """종목 마스터. 티커, 회사명, 섹터, 산업, 설명, 시가총액."""
    __tablename__ = "prod_stocks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(20), unique=True, nullable=False, index=True)
    company_name = Column(String(255))
    company_name_ko = Column(String(255))
    sector = Column(String(100), index=True)
    industry = Column(String(100))
    description = Column(Text)
    market_cap = Column(BigInteger)
    created_at = Column(DateTime, default=datetime.utcnow)


class ProdFundamentals(Base):
    """재무 지표. PE, PBR, ROE, 성장률, 부채비율, FCF 등."""
    __tablename__ = "prod_fundamentals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(20), nullable=False, index=True)
    pe_ratio = Column(Float)
    pbr = Column(Float)
    roe = Column(Float)
    revenue_growth = Column(Float)
    earnings_growth = Column(Float)
    debt_ratio = Column(Float)
    free_cash_flow = Column(Float)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ProdPriceHistory(Base):
    """가격 시계열. ticker, date 기준 OHLCV."""
    __tablename__ = "prod_price_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(20), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float, nullable=False)
    volume = Column(BigInteger)

    __table_args__ = (Index("idx_prod_ph_ticker_date", "ticker", "date", unique=True),)


class ProdScores(Base):
    """정량 투자 점수. Value/Growth/Quality/Sentiment/Risk + Investment."""
    __tablename__ = "prod_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(20), nullable=False, index=True)
    value_score = Column(Float)
    growth_score = Column(Float)
    quality_score = Column(Float)
    sentiment_score = Column(Float)
    risk_adjustment = Column(Float)
    investment_score = Column(Float)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ProdCompanyRatings(Base):
    """Glassdoor 등 기업 평점."""
    __tablename__ = "prod_company_ratings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(20), nullable=False, index=True)
    glassdoor_rating = Column(Float)
    glassdoor_review_count = Column(Integer)
    ceo_approval = Column(Float)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ProdNews(Base):
    """뉴스. ticker, published_at 인덱스."""
    __tablename__ = "prod_news"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(20), nullable=False, index=True)
    title = Column(String(500))
    source = Column(String(100))
    url = Column(String(1000))
    published_at = Column(DateTime, nullable=False, index=True)

    __table_args__ = (Index("idx_prod_news_ticker_pub", "ticker", "published_at"),)


class ProdWatchlist(Base):
    """관심 종목. user_id + ticker 유일."""
    __tablename__ = "prod_watchlist"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), nullable=False, index=True)
    ticker = Column(String(20), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (Index("idx_prod_watchlist_user_ticker", "user_id", "ticker", unique=True),)


class ProdPortfolio(Base):
    """포트폴리오 보유. user_id, ticker, 수량, 평균단가."""
    __tablename__ = "prod_portfolio"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), nullable=False, index=True)
    ticker = Column(String(20), nullable=False, index=True)
    quantity = Column(Float, nullable=False)
    average_price = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
