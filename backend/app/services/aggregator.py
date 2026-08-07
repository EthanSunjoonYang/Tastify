from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.sentiment_aggregate import SentimentAggregate
from app.models.sentiment_score import SentimentScore
from app.models.ticker import Ticker

AGGREGATION_WINDOWS = {
    "1h": timedelta(hours=1),
    "4h": timedelta(hours=4),
    "24h": timedelta(hours=24),
    "7d": timedelta(days=7),
}

TREND_THRESHOLD = 0.05


def classify_trend(current_avg: float, previous_avg: float) -> str:
    delta = current_avg - previous_avg
    if delta > TREND_THRESHOLD:
        return "bullish"
    if -delta > TREND_THRESHOLD:
        return "bearish"
    return "neutral"


def _window_stats(db: Session, ticker_id, start: datetime, end: datetime) -> tuple[float, int]:
    scores = (
        db.execute(
            select(SentimentScore.weighted_score).where(
                SentimentScore.ticker_id == ticker_id,
                SentimentScore.scored_at >= start,
                SentimentScore.scored_at < end,
            )
        )
        .scalars()
        .all()
    )
    if not scores:
        return 0.0, 0
    return sum(scores) / len(scores), len(scores)


def compute_aggregate(
    db: Session, ticker_id, window: timedelta, now: datetime | None = None
) -> SentimentAggregate:
    """Compute the rolling sentiment aggregate for one ticker/window, comparing it
    against the immediately preceding window of the same length to classify trend."""
    now = now or datetime.now(UTC)
    period_start = now - window
    previous_start = period_start - window

    current_avg, mention_count = _window_stats(db, ticker_id, period_start, now)
    previous_avg, _ = _window_stats(db, ticker_id, previous_start, period_start)

    aggregate = SentimentAggregate(
        ticker_id=ticker_id,
        period_start=period_start,
        period_end=now,
        avg_sentiment=current_avg,
        mention_count=mention_count,
        trend_direction=classify_trend(current_avg, previous_avg),
    )
    db.add(aggregate)
    db.commit()
    db.refresh(aggregate)
    return aggregate


def compute_all_aggregates(db: Session, now: datetime | None = None) -> list[SentimentAggregate]:
    now = now or datetime.now(UTC)
    ticker_ids = db.execute(select(Ticker.id)).scalars().all()

    aggregates = []
    for ticker_id in ticker_ids:
        for window in AGGREGATION_WINDOWS.values():
            aggregates.append(compute_aggregate(db, ticker_id, window, now))
    return aggregates


def get_latest_aggregate(db: Session, ticker_id, window: timedelta) -> SentimentAggregate | None:
    """Most recent aggregate snapshot for a ticker at a given window size.

    Window size isn't stored as its own column (the plan's schema tracks it implicitly
    via period_start/period_end), so we scan recent rows and match on that duration.
    """
    rows = (
        db.execute(
            select(SentimentAggregate)
            .where(SentimentAggregate.ticker_id == ticker_id)
            .order_by(SentimentAggregate.period_end.desc())
            .limit(200)
        )
        .scalars()
        .all()
    )
    for row in rows:
        if row.period_end - row.period_start == window:
            return row
    return None


def get_aggregate_history(
    db: Session, ticker_id, window: timedelta, since: datetime
) -> list[SentimentAggregate]:
    rows = (
        db.execute(
            select(SentimentAggregate)
            .where(
                SentimentAggregate.ticker_id == ticker_id,
                SentimentAggregate.period_end >= since,
            )
            .order_by(SentimentAggregate.period_end.asc())
        )
        .scalars()
        .all()
    )
    return [row for row in rows if row.period_end - row.period_start == window]


def get_trending(
    db: Session, window: timedelta, limit: int = 10
) -> list[tuple[Ticker, SentimentAggregate]]:
    tickers = db.execute(select(Ticker)).scalars().all()
    ranked = []
    for ticker in tickers:
        aggregate = get_latest_aggregate(db, ticker.id, window)
        if aggregate and aggregate.mention_count > 0:
            ranked.append((ticker, aggregate))
    ranked.sort(key=lambda pair: pair[1].mention_count, reverse=True)
    return ranked[:limit]
