"""
Application configuration. Load from environment.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
_env_file = BASE_DIR / ".env"
if _env_file.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_env_file)
    except ImportError:
        pass

# Database (DATABASE_URL 없으면 SQLite로 로컬 실행)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./stock_platform.db"
)

# Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Celery
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL)
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)

# API Keys (set in .env)
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")  # Glassdoor
YAHOO_FINANCE_ENABLED = True  # yfinance no key

# Scheduler times (KST or server time)
SCHEDULE_TIMES = ["09:00", "13:00", "18:00", "23:30"]

# Scoring weights (total 100)
WEIGHTS = {
    "financial": 60,
    "alternative": 20,
    "technical": 10,
    "sentiment": 10,
}
