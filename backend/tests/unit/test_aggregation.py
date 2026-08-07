import uuid
from datetime import UTC, datetime, timedelta

from app.models.sentiment_score import SentimentScore
from app.models.ticker import Ticker
from app.services.aggregator import classify_trend, compute_aggregate


def test_classify_trend_bullish_above_threshold():
    assert classify_trend(current_avg=0.30, previous_avg=0.20) == "bullish"


def test_classify_trend_bearish_below_threshold():
    assert classify_trend(current_avg=0.10, previous_avg=0.25) == "bearish"


def test_classify_trend_neutral_within_threshold():
    assert classify_trend(current_avg=0.22, previous_avg=0.20) == "neutral"


def test_classify_trend_boundary_is_neutral():
    # Exactly at the 0.05 threshold should not tip into bullish/bearish (strict >).
    assert classify_trend(current_avg=0.25, previous_avg=0.20) == "neutral"


def _make_score(ticker_id, weighted_score: float, scored_at: datetime) -> SentimentScore:
    return SentimentScore(
        ticker_id=ticker_id,
        post_id=uuid.uuid4(),
        compound_score=weighted_score,
        positive=0.0,
        negative=0.0,
        neutral=1.0,
        weighted_score=weighted_score,
        scored_at=scored_at,
    )


def test_compute_aggregate_averages_current_window_and_classifies_trend(db_session):
    ticker = Ticker(symbol="AAPL", name="Apple Inc.")
    db_session.add(ticker)
    db_session.commit()

    now = datetime(2026, 1, 1, tzinfo=UTC)
    window = timedelta(hours=1)

    # Previous window (1h-2h ago): weaker sentiment.
    db_session.add(_make_score(ticker.id, 0.10, now - timedelta(minutes=90)))
    # Current window (last 1h): stronger sentiment -> should classify bullish.
    db_session.add(_make_score(ticker.id, 0.40, now - timedelta(minutes=30)))
    db_session.add(_make_score(ticker.id, 0.60, now - timedelta(minutes=10)))
    db_session.commit()

    aggregate = compute_aggregate(db_session, ticker.id, window, now=now)

    assert aggregate.mention_count == 2
    assert aggregate.avg_sentiment == 0.5
    assert aggregate.trend_direction == "bullish"


def test_compute_aggregate_with_no_scores_is_neutral_zero(db_session):
    ticker = Ticker(symbol="GME", name="GameStop")
    db_session.add(ticker)
    db_session.commit()

    aggregate = compute_aggregate(db_session, ticker.id, timedelta(hours=1))

    assert aggregate.mention_count == 0
    assert aggregate.avg_sentiment == 0.0
    assert aggregate.trend_direction == "neutral"
