from fastapi import APIRouter, HTTPException

from app.schemas.price import PricePoint, PriceResponse
from app.services.price import PricePeriod, get_price_history

router = APIRouter()


@router.get("/price/{ticker}", response_model=PriceResponse)
def get_price(ticker: str, period: PricePeriod = "1mo") -> PriceResponse:
    symbol = ticker.upper()
    try:
        raw_points = get_price_history(symbol, period)
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Failed to fetch price data") from exc

    if not raw_points:
        raise HTTPException(status_code=404, detail=f"No price data for '{symbol}'")

    return PriceResponse(
        ticker=symbol, period=period, points=[PricePoint(**point) for point in raw_points]
    )
