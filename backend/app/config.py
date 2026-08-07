from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Stock Sentiment Analyzer"
    environment: str = "development"

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/stock_sentiment"
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/1"

    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    reddit_user_agent: str = "stock-sentiment-analyzer/0.1 by u/placeholder"

    target_subreddits: list[str] = ["wallstreetbets", "stocks", "investing", "stockmarket"]
    scrape_interval_minutes: int = 15

    sentiment_cache_ttl_seconds: int = 300
    trending_cache_ttl_seconds: int = 600

    rate_limit_per_minute: int = 60

    cors_origins: list[str] = ["http://localhost:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
