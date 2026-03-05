-- =======================================
-- 프로덕션 정규화 스키마 (Production Normalized Schema)
-- SQLite / MariaDB 호환
-- =======================================

-- 종목 마스터
CREATE TABLE IF NOT EXISTS prod_stocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker VARCHAR(20) NOT NULL UNIQUE,
    company_name VARCHAR(255),
    company_name_ko VARCHAR(255),
    sector VARCHAR(100),
    industry VARCHAR(100),
    description TEXT,
    market_cap BIGINT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_prod_stocks_ticker ON prod_stocks(ticker);
CREATE INDEX IF NOT EXISTS idx_prod_stocks_sector ON prod_stocks(sector);

-- 재무 지표 (Yahoo/핵심 재무)
CREATE TABLE IF NOT EXISTS prod_fundamentals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker VARCHAR(20) NOT NULL,
    pe_ratio REAL,
    pbr REAL,
    roe REAL,
    revenue_growth REAL,
    earnings_growth REAL,
    debt_ratio REAL,
    free_cash_flow REAL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_prod_fundamentals_ticker ON prod_fundamentals(ticker);

-- 가격 시계열 (Yahoo)
CREATE TABLE IF NOT EXISTS prod_price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    open REAL,
    high REAL,
    low REAL,
    close REAL NOT NULL,
    volume BIGINT
);
CREATE INDEX IF NOT EXISTS idx_prod_ph_ticker_date ON prod_price_history(ticker, date);
CREATE UNIQUE INDEX IF NOT EXISTS idx_prod_ph_ticker_date_uq ON prod_price_history(ticker, date);

-- 정량 투자 점수
CREATE TABLE IF NOT EXISTS prod_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker VARCHAR(20) NOT NULL,
    value_score REAL,
    growth_score REAL,
    quality_score REAL,
    sentiment_score REAL,
    risk_adjustment REAL,
    investment_score REAL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_prod_scores_ticker ON prod_scores(ticker);

-- Glassdoor 등 기업 평점
CREATE TABLE IF NOT EXISTS prod_company_ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker VARCHAR(20) NOT NULL,
    glassdoor_rating REAL,
    glassdoor_review_count INTEGER,
    ceo_approval REAL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_prod_company_ratings_ticker ON prod_company_ratings(ticker);

-- 뉴스
CREATE TABLE IF NOT EXISTS prod_news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker VARCHAR(20) NOT NULL,
    title VARCHAR(500),
    source VARCHAR(100),
    url VARCHAR(1000),
    published_at DATETIME NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_prod_news_ticker_pub ON prod_news(ticker, published_at);

-- 관심 종목
CREATE TABLE IF NOT EXISTS prod_watchlist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(100) NOT NULL,
    ticker VARCHAR(20) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, ticker)
);
CREATE INDEX IF NOT EXISTS idx_prod_watchlist_user ON prod_watchlist(user_id);

-- 포트폴리오 보유
CREATE TABLE IF NOT EXISTS prod_portfolio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(100) NOT NULL,
    ticker VARCHAR(20) NOT NULL,
    quantity REAL NOT NULL,
    average_price REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_prod_portfolio_user ON prod_portfolio(user_id);
