from fastapi import APIRouter
from .stocks import router as stocks_router
from .recommendations import router as recommendations_router
from .screener import router as screener_router
from .watchlist import router as watchlist_router

api_router = APIRouter(prefix="/api", tags=["api"])
api_router.include_router(stocks_router)
api_router.include_router(recommendations_router)
api_router.include_router(screener_router)
api_router.include_router(watchlist_router)
