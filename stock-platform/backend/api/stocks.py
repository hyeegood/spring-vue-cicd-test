from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from repositories import StockRepository
from services.quantitative_scoring_engine import compute_all_scores_from_stock_score

router = APIRouter()

@router.get("/stocks/{symbol}/scores")
def stock_quantitative_scores(symbol: str, db: Session = Depends(get_db)):
    """정량 투자 스코어링 엔진 결과: value_score, growth_score, quality_score, sentiment_score, risk_adjustment, investment_score (0-100)."""
    repo = StockRepository(db)
    stock = repo.get_by_symbol(symbol)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    today = date.today()
    score = repo.get_latest_score(stock.id, today)
    if not score:
        from services.quantitative_scoring_engine import compute_all_scores
        return compute_all_scores()  # 전부 None이면 기본값
    return compute_all_scores_from_stock_score(stock, score)

@router.get("/stocks/{symbol}/chart")
def stock_chart(symbol: str, db: Session = Depends(get_db)):
    repo = StockRepository(db)
    stock = repo.get_by_symbol(symbol)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    ph = repo.get_price_history(stock.id, 365)
    return {"symbol": symbol, "data": [{"timestamp": d.isoformat(), "price": p, "volume": None} for d, p in ph]}
