# Stock Analytics Platform – Product Architecture

## 스택

- **Frontend (Vue)**: `frontend-vue/` — Vue 3, Vue Router, Vite, Tailwind, Lightweight Charts
- **Backend**: FastAPI — `api/` 라우트, `services/` 비즈니스 로직, `models/` DB
- **Database**: SQLite (기본), MariaDB 가능

## 백엔드 구조

- `main.py` — FastAPI 앱, 라이프사이클, CORS, 라우트 등록
- `services/investment_score.py` — 통합 투자 점수 (Value 40% + Growth 25% + Sentiment 20% + StockRel 15%), 의견 레이블(Strong Buy / Buy / Hold / Weak / Avoid)
- `services/ai_insight.py` — AI 인사이트 문장 생성 (규칙 기반)
- `reliability_engine.py` — 섹터/종목 신뢰도, 해석 문구
- `scoring_engine.py` — 재무/대안/기술/감성 세부 점수
- `recommendation_engine.py` — 진입가/손절/목표가

## API (1초 이내 응답 목표)

| 엔드포인트 | 설명 |
|-----------|------|
| `GET /api/dashboard` | 대시보드 종목 목록 (DB만 사용) |
| `GET /api/dashboard/analytics` | 카드형 대시보드용 집계 (Market Overview, Top Picks, Trending, Top Sectors, Market News) |
| `GET /api/stocks/{ticker}` | 종목 상세 (가격 이력, 재무, 옵션, 뉴스, 신뢰도, **investment_score**, **investment_interpretation**, **ai_insight**) |
| `GET /api/rankings/{list_type}` | 랭킹 (score / value / growth) |

## 투자 점수 체계

- **통합 투자 점수** = Value 40% + Growth 25% + Sentiment 20% + Stock Reliability 15%
- **의견**: 80+ Strong Buy, 70–79 Buy, 55–69 Hold, 40–54 Weak, &lt;40 Avoid
- Value: PER, PBR, EV/EBITDA, 영업이익률, 부채비율
- Growth: ROE, 영업이익률, 인력 성장
- Sentiment: 뉴스/애널리스트 감성 (-1~1 → 0–100)
- Stock Reliability: reliability_engine (섹터 40% + 수익/매출 안정성 등)

## Vue 프론트엔드

- **페이지**: 대시보드, 종목 상세, 랭킹
- **컴포넌트**: StockCard, ScoreWidget, MetricCard, ChartWidget, NewsCard, RecommendationCard
- **디자인**: 배경 #F7F9FC, Primary #2563EB, Positive #22C55E, Negative #EF4444, Neutral #6B7280, 카드 레이아웃
- **차트**: TradingView Lightweight Charts (Area, 시간축)

## 실행

```bash
# 백엔드 (기존)
cd stock-platform/backend && py -3 -m uvicorn main:app --host 0.0.0.0 --port 8000

# Vue 프론트 (신규)
cd stock-platform/frontend-vue && npm run dev
```

Vue 앱: http://localhost:5175 (API 프록시 → 8000)
