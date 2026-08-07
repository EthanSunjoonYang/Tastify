import logging

from app.api.dependencies import SessionLocal
from app.services.reddit_client import get_reddit_client
from app.services.scraper import scrape_subreddits
from app.tasks.celery_app import celery_app
from app.tasks.score import process_new_posts

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.scrape.scrape_reddit")
def scrape_reddit() -> int:
    """Pull new posts from all target subreddits, store them, then hand off to
    scoring/aggregation so each scrape run ends with fresh sentiment data."""
    db = SessionLocal()
    try:
        reddit = get_reddit_client()
        new_posts = scrape_subreddits(db, reddit)
        logger.info("scrape_reddit: stored %d new posts", len(new_posts))
    finally:
        db.close()

    if new_posts:
        process_new_posts.delay()
    return len(new_posts)
