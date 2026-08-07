import { useCallback, useEffect, useState } from "react";

import {
  ApiError,
  getCurrentSentiment,
  getPriceHistory,
  getSentimentHistory,
  getTrendingTickers,
} from "../api/client";
import SearchBar from "../components/SearchBar";
import SentimentCard from "../components/SentimentCard";
import TrendChart from "../components/TrendChart";
import TrendingGrid from "../components/TrendingGrid";
import type {
  PricePoint,
  SentimentCurrent,
  SentimentHistoryPoint,
  TrendingTicker,
} from "../types";

export default function Dashboard() {
  const [ticker, setTicker] = useState<string | null>(null);
  const [sentiment, setSentiment] = useState<SentimentCurrent | null>(null);
  const [history, setHistory] = useState<SentimentHistoryPoint[]>([]);
  const [prices, setPrices] = useState<PricePoint[]>([]);
  const [showPrice, setShowPrice] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [trending, setTrending] = useState<TrendingTicker[]>([]);
  const [trendingError, setTrendingError] = useState<string | null>(null);

  useEffect(() => {
    getTrendingTickers()
      .then((res) => setTrending(res.items))
      .catch(() => setTrendingError("Couldn't load trending tickers."));
  }, []);

  const search = useCallback((symbol: string) => {
    setTicker(symbol);
    setLoading(true);
    setError(null);

    Promise.all([
      getCurrentSentiment(symbol),
      getSentimentHistory(symbol),
      getPriceHistory(symbol).catch(() => ({ ticker: symbol, period: "1mo", points: [] })),
    ])
      .then(([currentRes, historyRes, priceRes]) => {
        setSentiment(currentRes);
        setHistory(historyRes.points);
        setPrices(priceRes.points);
      })
      .catch((err: unknown) => {
        setSentiment(null);
        setHistory([]);
        setPrices([]);
        if (err instanceof ApiError && err.status === 404) {
          setError(`No data found for "${symbol}". Try a well-known ticker like AAPL or GME.`);
        } else {
          setError("Something went wrong fetching that ticker. Please try again.");
        }
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="mx-auto max-w-5xl space-y-8 px-4 py-8">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Stock Sentiment Analyzer</h1>
        <p className="mt-1 text-slate-500">
          Real-time Reddit sentiment for any ticker, weighted by engagement.
        </p>
      </div>

      <SearchBar onSearch={search} initialValue={ticker ?? ""} />

      {loading && <p className="text-slate-400">Loading…</p>}
      {error && <p className="rounded-lg bg-red-50 p-4 text-red-700">{error}</p>}

      {sentiment && !loading && !error && (
        <div className="space-y-4">
          <SentimentCard data={sentiment} />

          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-slate-800">Sentiment trend</h3>
            <label className="flex items-center gap-2 text-sm text-slate-500">
              <input
                type="checkbox"
                checked={showPrice}
                onChange={(e) => setShowPrice(e.target.checked)}
              />
              Overlay price
            </label>
          </div>
          <TrendChart sentimentPoints={history} pricePoints={prices} showPrice={showPrice} />
        </div>
      )}

      <div>
        <h3 className="mb-3 text-lg font-semibold text-slate-800">Trending tickers (24h)</h3>
        {trendingError ? (
          <p className="text-red-500">{trendingError}</p>
        ) : (
          <TrendingGrid tickers={trending} onSelect={search} />
        )}
      </div>
    </div>
  );
}
