from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models import Watchlist

router = APIRouter()

class WatchlistAdd(BaseModel):
    symbol: str
    user_id: str = "default"

class WatchlistRemove(BaseModel):
    symbol: str
    user_id: str = "default"

@router.post("/watchlist/add")
def watchlist_add(body: WatchlistAdd, db: Session = Depends(get_db)):
    symbol = body.symbol.upper().strip()
    if not symbol:
        raise HTTPException(status_code=400, detail="symbol required")
    existing = db.query(Watchlist).filter(Watchlist.user_id == body.user_id, Watchlist.symbol == symbol).first()
    if existing:
        return {"status": "ok", "message": "already in watchlist"}
    db.add(Watchlist(user_id=body.user_id, symbol=symbol))
    db.commit()
    return {"status": "ok", "symbol": symbol}

@router.post("/watchlist/remove")
def watchlist_remove(body: WatchlistRemove, db: Session = Depends(get_db)):
    symbol = body.symbol.upper().strip()
    db.query(Watchlist).filter(Watchlist.user_id == body.user_id, Watchlist.symbol == symbol).delete()
    db.commit()
    return {"status": "ok", "symbol": symbol}
