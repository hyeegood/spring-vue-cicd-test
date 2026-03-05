from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from services.dashboard_service import get_dashboard_analytics

router = APIRouter()

@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    return get_dashboard_analytics(db)
