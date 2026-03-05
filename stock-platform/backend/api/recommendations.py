from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from services.recommendation_service import get_recommendations

router = APIRouter()

@router.get("/recommendations")
def recommendations(db: Session = Depends(get_db), limit: int = 50):
    return get_recommendations(db, limit=limit)
