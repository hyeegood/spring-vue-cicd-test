# Stock Analytics (Vue)

Vue 3 + Vite + Tailwind 기반 투자 분석 플랫폼 프론트엔드.

## 실행

```bash
npm install
npm run dev
```

기본 포트: 5175. API는 `vite.config.js`에서 `http://localhost:8000`으로 프록시됩니다.

## 구조

- `src/pages/` - 대시보드, 종목 상세, 랭킹
- `src/components/` - StockCard, ScoreWidget, MetricCard, ChartWidget, NewsCard, RecommendationCard
- `src/services/api.js` - 대시보드 집계, 종목 상세, 랭킹 API 호출
- `src/router/` - Vue Router

## 디자인

- 배경: #F7F9FC (light neutral)
- Primary: #2563EB (deep blue)
- Positive: #22C55E, Negative: #EF4444, Neutral: #6B7280
- 카드 레이아웃, 둥근 모서리, 일관된 간격
