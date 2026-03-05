# Glassdoor 기업 평점 수집 워커 -> prod_company_ratings
import os
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from database import SessionLocal
from models_production import ProdCompanyRatings, ProdStock

def fetch_glassdoor_rating(ticker: str, company_name: Optional[str] = None) -> Optional[dict]:
    api_key = os.getenv("RAPIDAPI_KEY", "").strip()
    if not api_key:
        return None
    try:
        import requests
        url = "https://glassdoor.p.rapidapi.com/reviews"
        headers = {"X-RapidAPI-Key": api_key, "X-RapidAPI-Host": "glassdoor.p.rapidapi.com"}
        params = {"company": company_name or ticker}
        r = requests.get(url, headers=headers, params=params, timeout=10)
        if r.status_code != 200:
            return None
        data = r.json()
        rating = data.get("rating") or data.get("overallRating")
        review_count = data.get("reviewCount") or data.get("numberOfReviews")
        ceo = data.get("ceoApproval") or data.get("ceoRating")
        return {
            "glassdoor_rating": float(rating) if rating else None,
            "glassdoor_review_count": int(review_count) if review_count else None,
            "ceo_approval": float(ceo) if ceo else None,
        }
    except Exception:
        return None

def upsert_company_ratings(db: Session, ticker: str, data: dict) -> None:
    row = db.query(ProdCompanyRatings).filter(ProdCompanyRatings.ticker == ticker).first()
    if row:
        row.glassdoor_rating = data.get("glassdoor_rating")
        row.glassdoor_review_count = data.get("glassdoor_review_count")
        row.ceo_approval = data.get("ceo_approval")
        row.updated_at = datetime.utcnow()
    else:
        db.add(ProdCompanyRatings(ticker=ticker, glassdoor_rating=data.get("glassdoor_rating"),
            glassdoor_review_count=data.get("glassdoor_review_count"), ceo_approval=data.get("ceo_approval")))

def run_glassdoor_fetcher(tickers: Optional[List[str]] = None) -> dict:
    db = SessionLocal()
    try:
        if not tickers:
            rows = db.query(ProdStock.ticker, ProdStock.company_name).all()
            tickers = [r[0] for r in rows]
            names = {r[0]: r[1] for r in rows}
        else:
            names = {}
        updated = 0
        for ticker in tickers or []:
            try:
                data = fetch_glassdoor_rating(ticker, names.get(ticker))
                if data and (data.get("glassdoor_rating") or data.get("ceo_approval")):
                    upsert_company_ratings(db, ticker, data)
                    updated += 1
            except Exception:
                pass
        db.commit()
        return {"updated": updated}
    finally:
        db.close()
