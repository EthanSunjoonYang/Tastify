from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from redis import Redis
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_redis
from app.config import get_settings
from app.models.ticker import Ticker
from app.schemas.sentiment import (
    SentimentCurrent,
    SentimentHistory,
    SentimentHistoryPoint,
    WindowLiteral,
)
from app.services.aggregator import AGGREGATION_WINDOWS, get_aggregate_history, get_latest_aggregate

router = APIRouter()


def _get_ticker_or_404(db: Session, symbol: str) -> Ticker:
    ticker = db.execute(select(Ticker).where(Ticker.symbol == symbol)).scalar_one_or_none()
    if ticker is None:
        raise HTTPException(status_code=404, detail=f"Unknown ticker '{symbol}'")
    return ticker


@router.get("/sentiment/{ticker}", response_model=SentimentCurrent)
def get_current_sentiment(
    ticker: str,
    window: WindowLiteral = "24h",
    db: Session = Depends(get_db),
    redis_client: Redis = Depends(get_redis),
) -> SentimentCurrent:
    settings = get_settings()
    symbol = ticker.upper()
    cache_key = f"sentiment:current:{symbol}:{window}"

    cached = redis_client.get(cache_key)
    if cached:
        return SentimentCurrent.model_validate_json(cached)

    ticker_row = _get_ticker_or_404(db, symbol)
    aggregate = get_latest_aggregate(db, ticker_row.id, AGGREGATION_WINDOWS[window])

    result = SentimentCurrent(
        ticker=symbol,
        window=window,
        avg_sentiment=aggregate.avg_sentiment if aggregate else 0.0,
        trend_direction=aggregate.trend_direction if aggregate else "neutral",
        mention_count=aggregate.mention_count if aggregate else 0,
        last_updated=aggregate.period_end if aggregate else None,
    )
    redis_client.setex(cache_key, settings.sentiment_cache_ttl_seconds, result.model_dump_json())
    return result


@router.get("/sentiment/{ticker}/history", response_model=SentimentHistory)
def get_sentiment_history(
    ticker: str,
    period: WindowLiteral = "7d",
    window: WindowLiteral = "1h",
    db: Session = Depends(get_db),
) -> SentimentHistory:
    symbol = ticker.upper()
    ticker_row = _get_ticker_or_404(db, symbol)

    since = datetime.now(UTC) - AGGREGATION_WINDOWS[period]
    rows = get_aggregate_history(db, ticker_row.id, AGGREGATION_WINDOWS[window], since)

    points = [
        SentimentHistoryPoint(
            period_start=row.period_start,
            period_end=row.period_end,
            avg_sentiment=row.avg_sentiment,
            mention_count=row.mention_count,
            trend_direction=row.trend_direction,
        )
        for row in rows
    ]
    return SentimentHistory(ticker=symbol, window=window, points=points)
