import type { SentimentCurrent } from "../types";

const TREND_STYLES: Record<SentimentCurrent["trend_direction"], string> = {
  bullish: "bg-emerald-50 text-emerald-700 border-emerald-200",
  bearish: "bg-red-50 text-red-700 border-red-200",
  neutral: "bg-slate-50 text-slate-600 border-slate-200",
};

const TREND_ARROWS: Record<SentimentCurrent["trend_direction"], string> = {
  bullish: "↑",
  bearish: "↓",
  neutral: "→",
};

interface SentimentCardProps {
  data: SentimentCurrent;
}

export default function SentimentCard({ data }: SentimentCardProps) {
  const colorClass = TREND_STYLES[data.trend_direction];

  return (
    <div className={`rounded-xl border p-6 ${colorClass}`}>
      <div className="flex items-baseline justify-between">
        <h2 className="text-2xl font-bold">{data.ticker}</h2>
        <span className="text-3xl font-semibold">{TREND_ARROWS[data.trend_direction]}</span>
      </div>
      <p className="mt-2 text-4xl font-bold">{data.avg_sentiment.toFixed(2)}</p>
      <p className="mt-1 text-sm uppercase tracking-wide">{data.trend_direction}</p>
      <div className="mt-4 flex justify-between text-sm text-slate-500">
        <span>{data.mention_count} mentions ({data.window})</span>
        <span>
          {data.last_updated ? new Date(data.last_updated).toLocaleString() : "no data yet"}
        </span>
      </div>
    </div>
  );
}
