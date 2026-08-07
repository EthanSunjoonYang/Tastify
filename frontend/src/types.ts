export type Window = "1h" | "4h" | "24h" | "7d";
export type TrendDirection = "bullish" | "bearish" | "neutral";

export interface SentimentCurrent {
  ticker: string;
  window: Window;
  avg_sentiment: number;
  trend_direction: TrendDirection;
  mention_count: number;
  last_updated: string | null;
}

export interface SentimentHistoryPoint {
  period_start: string;
  period_end: string;
  avg_sentiment: number;
  mention_count: number;
  trend_direction: TrendDirection;
}

export interface SentimentHistory {
  ticker: string;
  window: Window;
  points: SentimentHistoryPoint[];
}

export interface TrendingTicker {
  symbol: string;
  name: string;
  avg_sentiment: number;
  mention_count: number;
}

export interface PricePoint {
  date: string;
  close: number;
}

export interface PriceResponse {
  ticker: string;
  period: string;
  points: PricePoint[];
}
