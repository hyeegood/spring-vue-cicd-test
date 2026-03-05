"""
Company culture data from RapidAPI Glassdoor Real-Time API (구독 중인 API).
Host: glassdoor-real-time.p.rapidapi.com
"""
import requests
from typing import Optional

from config import RAPIDAPI_KEY
from database import SessionLocal
from models import Stock

# 티커 -> Glassdoor 검색용 회사명 (DB에 ticker만 있을 때)
TICKER_TO_COMPANY = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "GOOGL": "Google",
    "GOOG": "Google",
    "AMZN": "Amazon",
    "NVDA": "NVIDIA",
    "META": "Meta",
    "TSLA": "Tesla",
    "JPM": "JPMorgan Chase",
    "V": "Visa",
    "JNJ": "Johnson & Johnson",
    "WMT": "Walmart",
    "PG": "Procter & Gamble",
    "MA": "Mastercard",
    "HD": "Home Depot",
    "DIS": "Walt Disney",
    "PYPL": "PayPal",
    "NFLX": "Netflix",
    "ADBE": "Adobe",
}


def fetch_glassdoor_rating(company_name: str, ticker: str = "") -> Optional[dict]:
    """
    Glassdoor Real-Time API: /companies/search -> employerRatings.overallRating, reviewCount.
    """
    if not RAPIDAPI_KEY:
        return None
    url = "https://glassdoor-real-time.p.rapidapi.com/companies/search"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "glassdoor-real-time.p.rapidapi.com",
    }
    query = (TICKER_TO_COMPANY.get((ticker or "").upper()) or company_name or ticker or "").strip()
    if not query:
        return None
    params = {"query": query}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=12)
        if r.status_code != 200:
            return None
        data = r.json()
        results = (data.get("data") or {}).get("employerResults") or []
        if not results:
            return None
        # 첫 번째 결과 사용 (검색어와 가장 잘 맞는 회사; 필요하면 reviewCount 최대인 것 선택)
        best = results[0]
        emp = best.get("employer") or {}
        ratings = best.get("employerRatings") or {}
        review_count = (emp.get("counts") or {}).get("reviewCount") or 0
        overall = ratings.get("overallRating")
        if overall is None:
            return None
        return {
            "glassdoor_rating": float(overall),
            "ceo_approval": None,
            "employee_recommendation": None,
            "review_count": int(review_count),
        }
    except Exception:
        return None


def update_stock_glassdoor(stock_id: int, company_name: str, ticker: str = "") -> bool:
    """Update stock row with Glassdoor data."""
    data = fetch_glassdoor_rating(company_name, ticker)
    if not data:
        return False
    db = SessionLocal()
    try:
        stock = db.query(Stock).filter(Stock.id == stock_id).first()
        if stock:
            stock.glassdoor_rating = data.get("glassdoor_rating")
            if data.get("ceo_approval") is not None:
                stock.ceo_approval = data.get("ceo_approval")
            if data.get("employee_recommendation") is not None:
                stock.employee_recommendation = data.get("employee_recommendation")
            stock.review_count = data.get("review_count")
            db.commit()
        return True
    finally:
        db.close()
