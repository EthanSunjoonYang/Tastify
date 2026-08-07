from datetime import UTC, datetime, timedelta

from app.config import get_settings
from app.models.sentiment_aggregate import SentimentAggregate
from app.models.ticker import Ticker


def _seed_ticker_with_aggregate(db_session, symbol="AAPL", window=timedelta(hours=24), **overrides):
    ticker = Ticker(symbol=symbol, name=f"{symbol} Inc.")
    db_session.add(ticker)
    db_session.commit()

    now = datetime.now(UTC)
    defaults = dict(
        ticker_id=ticker.id,
        period_start=now - window,
        period_end=now,
        avg_sentiment=0.42,
        mention_count=7,
        trend_direction="bullish",
    )
    defaults.update(overrides)
    aggregate = SentimentAggregate(**defaults)
    db_session.add(aggregate)
    db_session.commit()
    return ticker, aggregate


def test_get_current_sentiment_unknown_ticker_404(client):
    response = client.get("/api/sentiment/NOTAREALTICKER")
    assert response.status_code == 404


def test_get_current_sentiment_known_ticker_with_no_aggregate_defaults_to_neutral(
    client, db_session
):
    db_session.add(Ticker(symbol="GME", name="GameStop"))
    db_session.commit()

    response = client.get("/api/sentiment/GME")

    assert response.status_code == 200
    body = response.json()
    assert body["avg_sentiment"] == 0.0
    assert body["trend_direction"] == "neutral"
    assert body["mention_count"] == 0


def test_get_current_sentiment_returns_latest_aggregate(client, db_session):
    _seed_ticker_with_aggregate(db_session, symbol="AAPL")

    response = client.get("/api/sentiment/aapl")  # lowercase should be normalized

    assert response.status_code == 200
    body = response.json()
    assert body["ticker"] == "AAPL"
    assert body["avg_sentiment"] == 0.42
    assert body["trend_direction"] == "bullish"
    assert body["mention_count"] == 7


def test_get_current_sentiment_is_cached(client, db_session, fake_redis_client):
    ticker, _ = _seed_ticker_with_aggregate(db_session, symbol="TSLA")

    first = client.get("/api/sentiment/TSLA").json()

    # Mutate the underlying data directly; a cache hit should still return the stale value.
    fresh_aggregate = SentimentAggregate(
        ticker_id=ticker.id,
        period_start=datetime.now(UTC) - timedelta(hours=24),
        period_end=datetime.now(UTC),
        avg_sentiment=-0.9,
        mention_count=999,
        trend_direction="bearish",
    )
    db_session.add(fresh_aggregate)
    db_session.commit()

    second = client.get("/api/sentiment/TSLA").json()

    assert second == first
    assert fake_redis_client.get("sentiment:current:TSLA:24h") is not None


def test_get_sentiment_history_returns_matching_window_points(client, db_session):
    ticker, _ = _seed_ticker_with_aggregate(db_session, symbol="MSFT", window=timedelta(hours=1))

    response = client.get("/api/sentiment/MSFT/history?period=7d&window=1h")

    assert response.status_code == 200
    body = response.json()
    assert body["ticker"] == "MSFT"
    assert len(body["points"]) == 1
    assert body["points"][0]["mention_count"] == 7


def test_trending_tickers_ranked_by_mention_count(client, db_session):
    _seed_ticker_with_aggregate(db_session, symbol="AAPL", mention_count=5)
    _seed_ticker_with_aggregate(db_session, symbol="GME", mention_count=50)
    _seed_ticker_with_aggregate(db_session, symbol="TSLA", mention_count=20)

    response = client.get("/api/tickers/trending")

    assert response.status_code == 200
    symbols = [item["symbol"] for item in response.json()["items"]]
    assert symbols == ["GME", "TSLA", "AAPL"]


def test_price_endpoint_returns_points(client, monkeypatch):
    fake_points = [{"date": datetime(2026, 1, 1, tzinfo=UTC), "close": 150.25}]
    monkeypatch.setattr(
        "app.api.routes.price.get_price_history", lambda symbol, period: fake_points
    )

    response = client.get("/api/price/AAPL?period=1mo")

    assert response.status_code == 200
    body = response.json()
    assert body["ticker"] == "AAPL"
    assert body["points"][0]["close"] == 150.25


def test_price_endpoint_404_when_no_data(client, monkeypatch):
    monkeypatch.setattr("app.api.routes.price.get_price_history", lambda symbol, period: [])

    response = client.get("/api/price/ZZZZZ")

    assert response.status_code == 404


def test_price_endpoint_502_on_upstream_failure(client, monkeypatch):
    def _boom(symbol, period):
        raise RuntimeError("yfinance timeout")

    monkeypatch.setattr("app.api.routes.price.get_price_history", _boom)

    response = client.get("/api/price/AAPL")

    assert response.status_code == 502


def test_rate_limit_returns_429_after_threshold(client):
    limit = get_settings().rate_limit_per_minute
    for _ in range(limit):
        response = client.get("/api/health")
        assert response.status_code == 200

    response = client.get("/api/health")
    assert response.status_code == 429
