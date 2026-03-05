# Stock Investment Platform

Bloomberg/SeekingAlpha/Finviz/TradingView 스타일의 **주식 투자 플랫폼**입니다.  
재무·기술·대안 데이터·감성 분석·AI 점수를 활용해 **투자 확률 점수(0–100)** 와 **매매 추천**을 제공합니다.

## 기능 요약

- **재무 분석**: ROE, PER, PBR, PEG, EV/EBITDA, FCF, 영업이익률, 부채비율
- **기술적 분석**: RSI, 이평선 추세, 모멘텀
- **AI 예측·감성**: 뉴스 감성(transformers), 점수 반영
- **대안 데이터**: 기관 보유, 내부자 매수, 공매도, 직원 증가율
- **옵션**: 콜/풋 거래량, 풋/콜 비율
- **포트폴리오**: 포트폴리오 생성·종목 추가·점수·리스크
- **백테스트**: 기간·종목·진입 규칙 설정 후 승률·평균 수익률·최대 낙폭
- **종목 발견**: 투자 점수 / 밸류 / 성장 Top 50

## 기술 스택

| 구분 | 기술 |
|------|------|
| Backend | Python, FastAPI, SQLAlchemy, MariaDB, Redis, APScheduler, Celery |
| AI/데이터 | scikit-learn, transformers, pandas, numpy |
| Frontend | React, Vite, TailwindCSS, Chart.js, Lightweight-charts |
| 인프라 | Docker, Nginx, Gunicorn |

## 데이터 소스

- **시세/재무**: Yahoo Finance (yfinance)
- **기업 문화**: RapidAPI Glassdoor
- **대안**: 기관 보유, 내부자, 공매도, 직원 증가(LinkedIn 등)
- **옵션**: Yahoo Finance 옵션 체인
- **뉴스**: NewsAPI

## 자동 업데이트

스케줄: **09:00, 13:00, 18:00, 23:30** (재무·가격·지표·점수·뉴스 감성·대안 데이터)  
Glassdoor: **1일 1회** (02:00)

## 로컬 실행

### 요구 사항

- Python 3.11+, Node 18+, MariaDB(또는 MySQL), Redis

### 1) MariaDB·Redis 실행

```bash
docker run -d --name mariadb -e MYSQL_ROOT_PASSWORD=password -e MYSQL_DATABASE=stock_platform -p 3306:3306 mariadb:11
docker run -d --name redis -p 6379:6379 redis:7-alpine
```

### 2) 백엔드

```bash
cd stock-platform/backend
pip install -r requirements.txt
# .env에 DATABASE_URL, REDIS_URL, NEWS_API_KEY, RAPIDAPI_KEY 설정
export DATABASE_URL="mysql+pymysql://root:password@localhost:3306/stock_platform"
python init_db.py
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 3) 프론트엔드

```bash
cd stock-platform/frontend
npm install
npm run dev
```

브라우저: http://localhost:5174  
API: http://localhost:8000  
대시보드에 데이터가 없으면 `POST /api/stocks/register?ticker=AAPL` 등으로 종목을 먼저 등록하세요.

## Docker Compose로 한 번에 실행

```bash
cd stock-platform
# 백엔드 DB 초기화는 backend 컨테이너에서 한 번 실행
docker compose up -d
docker compose exec backend python init_db.py
```

- 프론트: http://localhost:5174 (Nginx)
- API: http://localhost:8000

## 투자 점수 모델 (총 100점)

| 영역 | 항목 | 배점 |
|------|------|------|
| 재무(60) | ROE, FCF, PER, 영업이익률, 부채비율, EV/EBITDA, PBR, PEG | 12+12+8+8+8+8+2+2 |
| 대안(20) | 기관보유, 내부자매수, 공매도, 직원증가 | 5+5+5+5 |
| 기술(10) | RSI, 이평추세, 모멘텀 | 4+3+3 |
| 감성(10) | 뉴스 감성, 애널리스트 감성 | 5+5 |

상세 스코어링 규칙은 `backend/scoring_engine.py` 참고.

## API 예시

- `GET /api/dashboard` – 대시보드 목록
- `GET /api/stocks/{ticker}` – 종목 상세(차트·점수·추천·재무·옵션·뉴스)
- `GET /api/rankings/score?limit=50` – 투자 점수 Top
- `POST /api/portfolio` – 포트폴리오 생성
- `POST /api/backtest` – 백테스트 실행

## 라이선스

MIT.
