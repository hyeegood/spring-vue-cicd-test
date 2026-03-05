# Production-Ready Architecture

## Backend

```
backend/
  api/           # REST 라우터
    dashboard.py
    stocks.py    # GET /api/stocks/{symbol}/chart
    recommendations.py
    screener.py
    watchlist.py # POST /api/watchlist/add, /api/watchlist/remove
  services/      # 비즈니스 로직
    investment_score.py  # Value 40% + Growth 25% + Sentiment 20% + Reliability 15%
    dashboard_service.py # 집계 + 캐시 (1초 목표)
    recommendation_service.py # Score>75, Risk!=High, Positive sentiment
    ai_insight.py
  repositories/  # DB 접근
    stock_repository.py
    dashboard_repository.py
  workers/       # 백그라운드
    market_data_fetcher.py
    news_fetcher.py
    score_recalculator.py
  utils/
    cache.py     # Redis 또는 메모리 캐시, cache_invalidate
  models.py      # User, Watchlist 추가
```

## API

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | /api/dashboard | 기존 (main) |
| GET | /api/dashboard/analytics | 기존 (main) |
| GET | /api/stocks/{symbol}/chart | 차트 전용 (api) |
| GET | /api/recommendations | 추천 종목 (Score>75, Risk!=High, Positive) |
| GET | /api/screener | min_score, sector 필터 |
| POST | /api/watchlist/add | body: { symbol, user_id? } |
| POST | /api/watchlist/remove | body: { symbol, user_id? } |

## Investment Score

- Formula: `Value*0.40 + Growth*0.25 + Sentiment*0.20 + StockReliability*0.15`
- 80+ Strong Buy, 70-79 Buy, 55-69 Hold, 40-54 Weak, <40 Avoid
- Sector Reliability: Consumer Staples 90, Banking 85, Industrial 75, Semiconductor 65, Software 60, EV 45, Biotech 30
- Stock Reliability: Sector 40% + EarningsStability 25% + RevenueStability 20% + AnalystCoverage 10% + Volatility 5%

## Frontend (Vue)

```
frontend-vue/src/
  components/    # StockCard, ScoreWidget, MetricCard, ChartWidget, NewsCard, RecommendationCard
  pages/         # Dashboard, StockDetail, Rankings, Screener, Comparison
  composables/   # useDashboard
  store/         # useDashboardStore
  services/      # api.js (getDashboardAnalytics, getRecommendations, getScreener, getStockChart)
  router/
```

## Performance

- Dashboard: `utils.cache` (TTL 60s), Redis 사용 시 REDIS_URL 설정
- Full refresh 시 `cache_invalidate("dashboard_analytics")` 호출
- 프론트는 DB/캐시만 읽고, 워커가 시장/뉴스/점수 갱신
