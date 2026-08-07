import type { TrendingTicker } from "../types";

interface TrendingGridProps {
  tickers: TrendingTicker[];
  onSelect: (symbol: string) => void;
}

function sentimentColor(score: number): string {
  if (score > 0.05) return "text-emerald-600";
  if (score < -0.05) return "text-red-600";
  return "text-slate-500";
}

export default function TrendingGrid({ tickers, onSelect }: TrendingGridProps) {
  if (tickers.length === 0) {
    return <p className="text-slate-400">No trending tickers yet.</p>;
  }

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-5">
      {tickers.map((ticker) => (
        <button
          key={ticker.symbol}
          onClick={() => onSelect(ticker.symbol)}
          className="rounded-lg border border-slate-200 bg-white p-3 text-left shadow-sm
                     transition hover:border-slate-400 hover:shadow"
        >
          <div className="font-semibold">{ticker.symbol}</div>
          <div className={`text-sm font-medium ${sentimentColor(ticker.avg_sentiment)}`}>
            {ticker.avg_sentiment.toFixed(2)}
          </div>
          <div className="text-xs text-slate-400">{ticker.mention_count} mentions</div>
        </button>
      ))}
    </div>
  );
}
