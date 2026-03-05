# Production-Ready Relational Schema

## Entity Relationship Overview

```
users
  └── watchlist ──► stocks

stocks
  ├── price_history   (1:N, by timestamp)
  ├── fundamentals    (1:N, by as_of_date)
  ├── scores          (1:N, by as_of_date)
  ├── news            (1:N, by published_at)
  └── recommendations (1:1 or 1:N, latest per stock)
```

## Tables

| Table | Purpose |
|-------|---------|
| **stocks** | 종목 마스터 (symbol, name, sector, market_cap) |
| **price_history** | 시계열 가격 (stock_id, timestamp, OHLCV) |
| **fundamentals** | 재무 지표 스냅샷 (PE, PBR, ROE, 성장률 등) |
| **scores** | 정량 점수 스냅샷 (value, growth, quality, sentiment, risk, investment) |
| **news** | 뉴스 (stock_id, title, sentiment, published_at) |
| **recommendations** | 진입가/손절/목표가 (stock_id, 1 row per stock or history) |
| **users** | 사용자 (email, password_hash) |
| **watchlist** | 사용자별 관심 종목 (user_id, stock_id) |

## Relationships (Normalized)

- **stocks → price_history**: One stock has many price records. FK `price_history.stock_id` → `stocks.id`.
- **stocks → fundamentals**: One stock has many fundamental snapshots (e.g. daily). FK `fundamentals.stock_id` → `stocks.id`.
- **stocks → scores**: One stock has many score snapshots (e.g. daily). FK `scores.stock_id` → `stocks.id`.
- **stocks → news**: One stock has many news items. FK `news.stock_id` → `stocks.id`.
- **stocks → recommendations**: One stock has one (or many) recommendation rows. FK `recommendations.stock_id` → `stocks.id`.
- **users → watchlist → stocks**: Watchlist links user to stock. FK `watchlist.user_id` → `users.id`, `watchlist.stock_id` → `stocks.id`.

## Indexes (High-Performance Queries)

### symbol

- **stocks.symbol**: `UNIQUE INDEX idx_stocks_symbol` — lookup by symbol, dashboard filters.
- **watchlist**: resolved via `stock_id` (join to stocks.symbol when needed).

### timestamp / date

- **price_history.timestamp**: `INDEX idx_price_history_timestamp` — time-range queries.
- **price_history**: `UNIQUE INDEX idx_price_history_stock_timestamp (stock_id, timestamp)` — latest N for a stock, range by time.
- **fundamentals.as_of_date**: `INDEX idx_fundamentals_as_of_date` — latest fundamentals by date.
- **fundamentals**: `UNIQUE INDEX idx_fundamentals_stock_date (stock_id, as_of_date)` — one row per stock per day.
- **scores.as_of_date**: `INDEX idx_scores_as_of_date` — dashboard “latest score by date”.
- **scores**: `UNIQUE INDEX idx_scores_stock_date (stock_id, as_of_date)` — one row per stock per day.
- **scores.investment_score**: `INDEX idx_scores_investment_score DESC` — dashboard “top picks” by score.
- **news.published_at**: `INDEX idx_news_published_at` — recent news.
- **news**: `INDEX idx_news_stock_published (stock_id, published_at DESC)` — latest news per stock.

### Other

- **stocks.sector**: `INDEX idx_stocks_sector` — sector filter on dashboard.
- **users.email**: `UNIQUE INDEX idx_users_email` — login lookup.
- **watchlist**: `UNIQUE INDEX idx_watchlist_user_stock (user_id, stock_id)` — prevent duplicate, fast list by user.

## Query Patterns Supported

1. **Dashboard (top picks, by sector)**  
   - Join `stocks` + `scores` on `stock_id` and `as_of_date = today`.  
   - Filter/order by `scores.investment_score` (use `idx_scores_investment_score`, `idx_scores_stock_date`).

2. **Stock detail (one symbol)**  
   - Lookup `stocks` by `symbol` (`idx_stocks_symbol`).  
   - Latest `price_history`: `WHERE stock_id = ? ORDER BY timestamp DESC LIMIT N` (`idx_price_history_stock_timestamp`).  
   - Latest `fundamentals` / `scores`: `WHERE stock_id = ? AND as_of_date = ?` (`idx_fundamentals_stock_date`, `idx_scores_stock_date`).  
   - Recent `news`: `WHERE stock_id = ? ORDER BY published_at DESC LIMIT N` (`idx_news_stock_published`).  
   - `recommendations`: `WHERE stock_id = ?` (`idx_recommendations_stock_id`).

3. **Time-series chart**  
   - `price_history` WHERE `stock_id = ?` AND `timestamp BETWEEN ? AND ?` ORDER BY `timestamp` — uses `idx_price_history_stock_timestamp`.

4. **User watchlist**  
   - `watchlist` WHERE `user_id = ?` JOIN `stocks` — uses `idx_watchlist_user_id`.

## File

- **schema/schema.sql**: SQLite-compatible DDL; use for SQLite MVP. For MySQL/MariaDB, replace `AUTOINCREMENT` with `AUTO_INCREMENT` and adjust types (e.g. `BIGINT`, `DATETIME`) as needed.
