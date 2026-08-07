from celery import Celery

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "stock_sentiment_analyzer",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.timezone = "UTC"
celery_app.conf.beat_schedule = {
    "scrape-reddit-every-15-minutes": {
        "task": "app.tasks.scrape.scrape_reddit",
        "schedule": settings.scrape_interval_minutes * 60,
    },
}

# Task modules register themselves with celery_app via the @celery_app.task decorator,
# but only if imported. celery_app.py itself is the only module the worker/beat CLI
# imports directly, so pull the task modules in here (after celery_app exists, to
# avoid a circular import with their `from app.tasks.celery_app import celery_app`).
import app.tasks.score  # noqa: E402, F401
import app.tasks.scrape  # noqa: E402, F401
