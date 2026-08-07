from datetime import datetime
from typing import Literal

from pydantic import BaseModel

WindowLiteral = Literal["1h", "4h", "24h", "7d"]


class SentimentCurrent(BaseModel):
    ticker: str
    window: WindowLiteral
    avg_sentiment: float
    trend_direction: str
    mention_count: int
    last_updated: datetime | None


class SentimentHistoryPoint(BaseModel):
    period_start: datetime
    period_end: datetime
    avg_sentiment: float
    mention_count: int
    trend_direction: str


class SentimentHistory(BaseModel):
    ticker: str
    window: WindowLiteral
    points: list[SentimentHistoryPoint]
