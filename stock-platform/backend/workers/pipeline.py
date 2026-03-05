# 데이터 수집 파이프라인: 가격 -> 재무 -> DB 갱신 -> 점수 계산
# 매시간 실행 가능 (스케줄러에서 run_production_pipeline 호출)
from workers.yahoo_price_fetcher import run_yahoo_price_fetcher
from workers.fundamental_fetcher import run_fundamental_fetcher
from workers.glassdoor_fetcher import run_glassdoor_fetcher
from workers.news_fetcher_prod import run_news_fetcher
from workers.score_recalculator_prod import run_score_recalculator_prod

def run_production_pipeline(tickers=None, skip_glassdoor=False, skip_news=False):
    # 1) fetch prices
    r1 = run_yahoo_price_fetcher(tickers=tickers, days=365)
    # 2) fetch fundamentals (and ensure prod_stocks)
    r2 = run_fundamental_fetcher(tickers=tickers)
    # 3) update DB (already done in 1,2)
    # 4) glassdoor (optional)
    r3 = run_glassdoor_fetcher(tickers=tickers) if not skip_glassdoor else {"updated": 0}
    # 5) news (optional)
    r4 = run_news_fetcher(tickers=tickers) if not skip_news else {"inserted": 0}
    # 6) calculate investment scores
    r5 = run_score_recalculator_prod(tickers=tickers)
    return {"prices": r1, "fundamentals": r2, "glassdoor": r3, "news": r4, "scores": r5}
