import logging

from app.api.dependencies import SessionLocal
from app.services.aggregator import compute_all_aggregates
from app.services.sentiment import score_unscored_posts
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.score.process_new_posts")
def process_new_posts() -> int:
    """Score every unscored post, then recompute rolling aggregates for every ticker.
    Returns the number of sentiment scores created."""
    db = SessionLocal()
    try:
        scores = score_unscored_posts(db)
        compute_all_aggregates(db)
        logger.info("process_new_posts: created %d sentiment scores", len(scores))
        return len(scores)
    finally:
        db.close()
