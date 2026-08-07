import time
from dataclasses import dataclass, field

from sqlalchemy import select

from app.models.reddit_post import RedditPost
from app.services.scraper import scrape_subreddits


@dataclass
class FakeSubmission:
    id: str
    title: str
    selftext: str = ""
    score: int = 10
    num_comments: int = 2
    created_utc: float = field(default_factory=lambda: time.time())


class FakeSubreddit:
    def __init__(self, submissions: list[FakeSubmission]):
        self._submissions = submissions

    def hot(self, limit: int):
        return iter(self._submissions[:limit])


class FakeReddit:
    def __init__(self, submissions_by_subreddit: dict[str, list[FakeSubmission]]):
        self._submissions_by_subreddit = submissions_by_subreddit

    def subreddit(self, name: str) -> FakeSubreddit:
        return FakeSubreddit(self._submissions_by_subreddit.get(name, []))


def _fake_reddit_with(posts: list[FakeSubmission]) -> FakeReddit:
    # target_subreddits defaults to wallstreetbets/stocks/investing/stockmarket;
    # put all fixture posts under the first one so they're actually reachable.
    return FakeReddit({"wallstreetbets": posts})


def test_scrape_stores_new_posts(db_session):
    posts = [
        FakeSubmission(id="abc123", title="$AAPL to the moon", selftext="bullish"),
        FakeSubmission(id="def456", title="GME earnings soon"),
    ]
    reddit = _fake_reddit_with(posts)

    new_posts = scrape_subreddits(db_session, reddit)

    assert len(new_posts) == 2
    stored = db_session.execute(select(RedditPost)).scalars().all()
    assert {p.reddit_id for p in stored} == {"abc123", "def456"}


def test_scrape_dedupes_already_seen_posts(db_session):
    posts = [FakeSubmission(id="abc123", title="$AAPL to the moon")]
    reddit = _fake_reddit_with(posts)

    first_run = scrape_subreddits(db_session, reddit)
    second_run = scrape_subreddits(db_session, reddit)

    assert len(first_run) == 1
    assert len(second_run) == 0
    stored = db_session.execute(select(RedditPost)).scalars().all()
    assert len(stored) == 1


def test_scrape_dedupes_within_same_batch(db_session):
    # Same reddit_id showing up twice in one pull (edge case) should only be stored once.
    posts = [
        FakeSubmission(id="abc123", title="first"),
        FakeSubmission(id="abc123", title="duplicate"),
    ]
    reddit = _fake_reddit_with(posts)

    new_posts = scrape_subreddits(db_session, reddit)

    assert len(new_posts) == 1
