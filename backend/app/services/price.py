from typing import Literal

import yfinance as yf

PricePeriod = Literal["1d", "5d", "1mo", "3mo", "6mo", "1y"]


def get_price_history(symbol: str, period: PricePeriod) -> list[dict]:
    history = yf.Ticker(symbol).history(period=period)
    return [
        {"date": index.to_pydatetime(), "close": float(row["Close"])}
        for index, row in history.iterrows()
    ]
