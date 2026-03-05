-- =======================================
-- Production-ready relational schema
-- Stock Analytics Platform
-- Normalized design, indexes for symbol/timestamp
-- =======================================

-- ---------------------------------------
-- 1. stocks (종목 마스터)
-- ---------------------------------------
CREATE TABLE IF NOT EXISTS stocks (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol          VARCHAR(20) NOT NULL,
    name            VARCHAR(255),
    name_ko         VARCHAR(255),
    sector          VARCHAR(100),
    industry        VARCHAR(100),
    market_cap      BIGINT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_stocks_symbol ON stocks(symbol);
CREATE INDEX IF NOT EXISTS idx_stocks_sector ON stocks(sector);

-- ---------------------------------------
-- 2. price_history (stocks -> price_history)
-- 시계열 조회: (stock_id, timestamp) 복합 인덱스
-- ---------------------------------------
CREATE TABLE IF NOT EXISTS price_history (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_id        INTEGER NOT NULL,
    timestamp       DATETIME NOT NULL,
    open            REAL,
    high            REAL,
    low             REAL,
    close           REAL NOT NULL,
    volume         BIGINT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_price_history_stock_id ON price_history(stock_id);
CREATE INDEX IF NOT EXISTS idx_price_history_timestamp ON price_history(timestamp);
CREATE UNIQUE INDEX IF NOT EXISTS idx_price_history_stock_timestamp ON price_history(stock_id, timestamp);

-- ---------------------------------------
-- 3. fundamentals (stocks -> fundamentals)
-- 일별/스냅샷 재무 지표
-- ---------------------------------------
CREATE TABLE IF NOT EXISTS fundamentals (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_id            INTEGER NOT NULL,
    as_of_date          DATE NOT NULL,
    pe                  REAL,
    pbr                 REAL,
    peg                 REAL,
    ev_ebitda           REAL,
    fcf_yield           REAL,
    revenue_growth      REAL,
    eps_growth          REAL,
    roe                 REAL,
    operating_margin    REAL,
    debt_ratio          REAL,
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_fundamentals_stock_id ON fundamentals(stock_id);
CREATE INDEX IF NOT EXISTS idx_fundamentals_as_of_date ON fundamentals(as_of_date);
CREATE UNIQUE INDEX IF NOT EXISTS idx_fundamentals_stock_date ON fundamentals(stock_id, as_of_date);

-- ---------------------------------------
-- 4. scores (stocks -> scores)
-- 일별 정량 점수
-- ---------------------------------------
CREATE TABLE IF NOT EXISTS scores (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_id            INTEGER NOT NULL,
    as_of_date          DATE NOT NULL,
    value_score         REAL,
    growth_score        REAL,
    quality_score       REAL,
    sentiment_score     REAL,
    risk_adjustment     REAL,
    investment_score    REAL,
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_scores_stock_id ON scores(stock_id);
CREATE INDEX IF NOT EXISTS idx_scores_as_of_date ON scores(as_of_date);
CREATE UNIQUE INDEX IF NOT EXISTS idx_scores_stock_date ON scores(stock_id, as_of_date);
CREATE INDEX IF NOT EXISTS idx_scores_investment_score ON scores(investment_score DESC);

-- ---------------------------------------
-- 5. news (stocks -> news)
-- ---------------------------------------
CREATE TABLE IF NOT EXISTS news (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_id        INTEGER NOT NULL,
    title           VARCHAR(500),
    summary         TEXT,
    url             VARCHAR(1000),
    source          VARCHAR(100),
    sentiment       REAL,
    published_at    DATETIME NOT NULL,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_news_stock_id ON news(stock_id);
CREATE INDEX IF NOT EXISTS idx_news_published_at ON news(published_at);
CREATE INDEX IF NOT EXISTS idx_news_stock_published ON news(stock_id, published_at DESC);

-- ---------------------------------------
-- 6. recommendations (stocks -> recommendations)
-- 종목당 최신 추천 1건 또는 이력
-- ---------------------------------------
CREATE TABLE IF NOT EXISTS recommendations (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_id            INTEGER NOT NULL,
    entry_price         REAL,
    stop_loss           REAL,
    target_price        REAL,
    recommendation_type VARCHAR(20),
    updated_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_recommendations_stock_id ON recommendations(stock_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_stock_id ON recommendations(stock_id);

-- ---------------------------------------
-- 7. users
-- ---------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    email           VARCHAR(255) NOT NULL,
    password_hash   VARCHAR(255),
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- ---------------------------------------
-- 8. watchlist (users + stocks)
-- ---------------------------------------
CREATE TABLE IF NOT EXISTS watchlist (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    stock_id        INTEGER NOT NULL,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_watchlist_user_stock ON watchlist(user_id, stock_id);
CREATE INDEX IF NOT EXISTS idx_watchlist_user_id ON watchlist(user_id);
CREATE INDEX IF NOT EXISTS idx_watchlist_stock_id ON watchlist(stock_id);
