"""
APScheduler: run at 09:00, 13:00, 18:00, 23:30.
Tasks: fetch financials, update prices, update indicators, scores, news sentiment, alternative data.
Glassdoor once per day.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import task runners (avoid circular imports by calling Celery or inline)
def run_scheduled_tasks():
    try:
        from tasks import run_all_scheduled_updates
        run_all_scheduled_updates()
    except Exception as e:
        logger.exception("Scheduled run failed: %s", e)


def run_glassdoor_daily():
    try:
        from tasks import update_glassdoor_daily
        update_glassdoor_daily()
    except Exception as e:
        logger.exception("Glassdoor daily failed: %s", e)


def run_production_pipeline_hourly():
    """매시간 프로덕션 파이프라인: 가격 -> 재무 -> 뉴스 -> 점수 재계산."""
    try:
        from workers.pipeline import run_production_pipeline
        run_production_pipeline(skip_glassdoor=True, skip_news=False)
        logger.info("Production pipeline (hourly) completed")
    except Exception as e:
        logger.exception("Production pipeline failed: %s", e)


scheduler = BackgroundScheduler()


def start_scheduler():
    # 09:00, 13:00, 18:00, 23:30
    for time in ["09:00", "13:00", "18:00", "23:30"]:
        h, m = time.split(":")
        scheduler.add_job(
            run_scheduled_tasks,
            CronTrigger(hour=int(h), minute=int(m)),
            id=f"main_{time}",
        )
    # Glassdoor once per day at 02:00
    scheduler.add_job(run_glassdoor_daily, CronTrigger(hour=2, minute=0), id="glassdoor_daily")
    # 프로덕션 파이프라인 매시간 (0분)
    scheduler.add_job(run_production_pipeline_hourly, CronTrigger(minute=0), id="prod_pipeline_hourly")
    scheduler.start()
    logger.info("Scheduler started (09:00, 13:00, 18:00, 23:30, Glassdoor 02:00, prod pipeline hourly)")


def stop_scheduler():
    scheduler.shutdown(wait=False)
