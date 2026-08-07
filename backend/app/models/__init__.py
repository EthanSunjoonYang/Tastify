from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Imported for side effects so Base.metadata (and Alembic autogenerate) sees every table.
from app.models.reddit_post import RedditPost  # noqa: E402, F401
from app.models.sentiment_aggregate import SentimentAggregate  # noqa: E402, F401
from app.models.sentiment_score import SentimentScore  # noqa: E402, F401
from app.models.ticker import Ticker  # noqa: E402, F401
