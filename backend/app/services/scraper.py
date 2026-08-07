from datetime import UTC, datetime

import praw
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.reddit_post import RedditPost

POSTS_PER_SUBREDDIT = 100


def _existing_reddit_ids(db: Session, reddit_ids: list[str]) -> set[str]:
    if not reddit_ids:
        return set()
    rows = db.execute(
        select(RedditPost.reddit_id).where(RedditPost.reddit_id.in_(reddit_ids))
    ).scalars()
    return set(rows)


def scrape_subreddits(db: Session, reddit: praw.Reddit) -> list[RedditPost]:
    """Pull hot posts from every configured subreddit, storing only unseen posts.

    Returns the RedditPost rows newly inserted in this run (not previously-seen ones),
    since only new posts need to flow into sentiment scoring downstream.
    """
    settings = get_settings()
    candidates: list[dict] = []

    for subreddit_name in settings.target_subreddits:
        subreddit = reddit.subreddit(subreddit_name)
        for submission in subreddit.hot(limit=POSTS_PER_SUBREDDIT):
            candidates.append(
                {
                    "reddit_id": submission.id,
                    "subreddit": subreddit_name,
                    "title": submission.title,
                    "body": submission.selftext or None,
                    "score": submission.score,
                    "num_comments": submission.num_comments,
                    "created_utc": datetime.fromtimestamp(submission.created_utc, tz=UTC),
                }
            )

    seen = _existing_reddit_ids(db, [c["reddit_id"] for c in candidates])
    new_posts = []
    for candidate in candidates:
        if candidate["reddit_id"] in seen:
            continue
        seen.add(candidate["reddit_id"])  # guard against dupes within this same batch
        post = RedditPost(**candidate)
        db.add(post)
        new_posts.append(post)

    db.commit()
    for post in new_posts:
        db.refresh(post)
    return new_posts
