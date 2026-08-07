from fastapi import APIRouter, Depends
from redis import Redis
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_redis
from app.config import get_settings
from app.schemas.trending import TrendingResponse, TrendingTicker
from app.services.aggregator import AGGREGATION_WINDOWS, get_trending

router = APIRouter()

TRENDING_CACHE_KEY = "tickers:trending"


@router.get("/tickers/trending", response_model=TrendingResponse)
def get_trending_tickers(
    db: Session = Depends(get_db), redis_client: Redis = Depends(get_redis)
) -> TrendingResponse:
    settings = get_settings()

    cached = redis_client.get(TRENDING_CACHE_KEY)
    if cached:
        return TrendingResponse.model_validate_json(cached)

    ranked = get_trending(db, AGGREGATION_WINDOWS["24h"], limit=10)
    result = TrendingResponse(
        items=[
            TrendingTicker(
                symbol=ticker.symbol,
                name=ticker.name,
                avg_sentiment=aggregate.avg_sentiment,
                mention_count=aggregate.mention_count,
            )
            for ticker, aggregate in ranked
        ]
    )
    redis_client.setex(
        TRENDING_CACHE_KEY, settings.trending_cache_ttl_seconds, result.model_dump_json()
    )
    return result
