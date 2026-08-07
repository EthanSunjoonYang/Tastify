import {
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { PricePoint, SentimentHistoryPoint } from "../types";

interface TrendChartProps {
  sentimentPoints: SentimentHistoryPoint[];
  pricePoints: PricePoint[];
  showPrice: boolean;
}

interface ChartRow {
  date: string;
  sentiment: number | null;
  price: number | null;
}

function dayKey(isoString: string): string {
  return isoString.slice(0, 10);
}

function buildChartRows(
  sentimentPoints: SentimentHistoryPoint[],
  pricePoints: PricePoint[]
): ChartRow[] {
  const sentimentByDay = new Map<string, { sum: number; count: number }>();
  for (const point of sentimentPoints) {
    const key = dayKey(point.period_end);
    const existing = sentimentByDay.get(key) ?? { sum: 0, count: 0 };
    existing.sum += point.avg_sentiment;
    existing.count += 1;
    sentimentByDay.set(key, existing);
  }

  const priceByDay = new Map<string, number>();
  for (const point of pricePoints) {
    priceByDay.set(dayKey(point.date), point.close);
  }

  const allDays = new Set([...sentimentByDay.keys(), ...priceByDay.keys()]);

  return Array.from(allDays)
    .sort()
    .map((date) => {
      const sentiment = sentimentByDay.get(date);
      return {
        date,
        sentiment: sentiment ? sentiment.sum / sentiment.count : null,
        price: priceByDay.get(date) ?? null,
      };
    });
}

export default function TrendChart({ sentimentPoints, pricePoints, showPrice }: TrendChartProps) {
  const rows = buildChartRows(sentimentPoints, pricePoints);

  if (rows.length === 0) {
    return <p className="py-12 text-center text-slate-400">No sentiment history yet.</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={320}>
      <ComposedChart data={rows}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis dataKey="date" tick={{ fontSize: 12 }} />
        <YAxis
          yAxisId="sentiment"
          domain={[-1, 1]}
          tick={{ fontSize: 12 }}
          label={{ value: "Sentiment", angle: -90, position: "insideLeft" }}
        />
        {showPrice && (
          <YAxis
            yAxisId="price"
            orientation="right"
            tick={{ fontSize: 12 }}
            label={{ value: "Price ($)", angle: 90, position: "insideRight" }}
          />
        )}
        <Tooltip />
        <Legend />
        <Line
          yAxisId="sentiment"
          type="monotone"
          dataKey="sentiment"
          name="Sentiment"
          stroke="#4f46e5"
          dot={false}
          connectNulls
        />
        {showPrice && (
          <Line
            yAxisId="price"
            type="monotone"
            dataKey="price"
            name="Price"
            stroke="#0d9488"
            dot={false}
            connectNulls
          />
        )}
      </ComposedChart>
    </ResponsiveContainer>
  );
}
