import type {
  PriceResponse,
  SentimentCurrent,
  SentimentHistory,
  TrendingTicker,
} from "../types";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api";

class ApiError extends Error {
  constructor(
    message: string,
    public status: number
  ) {
    super(message);
  }
}

async function request<T>(path: string): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`);
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new ApiError(body.detail ?? response.statusText, response.status);
  }
  return response.json();
}

export function getCurrentSentiment(ticker: string): Promise<SentimentCurrent> {
  return request(`/sentiment/${encodeURIComponent(ticker)}`);
}

export function getSentimentHistory(ticker: string, period = "7d"): Promise<SentimentHistory> {
  return request(`/sentiment/${encodeURIComponent(ticker)}/history?period=${period}`);
}

export function getTrendingTickers(): Promise<{ items: TrendingTicker[] }> {
  return request("/tickers/trending");
}

export function getPriceHistory(ticker: string, period = "1mo"): Promise<PriceResponse> {
  return request(`/price/${encodeURIComponent(ticker)}?period=${period}`);
}

export { ApiError };
