from datetime import datetime

from pydantic import BaseModel

from app.services.price import PricePeriod


class PricePoint(BaseModel):
    date: datetime
    close: float


class PriceResponse(BaseModel):
    ticker: str
    period: PricePeriod
    points: list[PricePoint]
