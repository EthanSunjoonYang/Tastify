from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.dependencies import get_redis
from app.api.middleware import RateLimitMiddleware
from app.api.routes import health, price, sentiment, tickers
from app.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name)
app.state.get_redis = get_redis
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(sentiment.router, prefix="/api", tags=["sentiment"])
app.include_router(tickers.router, prefix="/api", tags=["tickers"])
app.include_router(price.router, prefix="/api", tags=["price"])
