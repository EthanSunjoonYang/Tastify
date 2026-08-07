from pydantic import BaseModel


class TrendingTicker(BaseModel):
    symbol: str
    name: str
    avg_sentiment: float
    mention_count: int


class TrendingResponse(BaseModel):
    items: list[TrendingTicker]
