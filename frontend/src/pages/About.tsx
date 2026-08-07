export default function About() {
  return (
    <div className="mx-auto max-w-3xl space-y-6 px-4 py-8 text-slate-700">
      <h1 className="text-3xl font-bold text-slate-900">Methodology</h1>

      <section>
        <h2 className="text-xl font-semibold text-slate-900">Data collection</h2>
        <p className="mt-1">
          A scheduled job pulls hot posts every 15 minutes from r/wallstreetbets, r/stocks,
          r/investing, and r/stockmarket via the Reddit API, deduplicating by Reddit post ID.
        </p>
      </section>

      <section>
        <h2 className="text-xl font-semibold text-slate-900">Ticker extraction</h2>
        <p className="mt-1">
          Mentions are matched against an allowlist of official NASDAQ/NYSE/AMEX ticker symbols.
          <code className="mx-1 rounded bg-slate-100 px-1">$TICKER</code>
          mentions are always trusted; bare all-caps mentions are additionally checked against a
          stopword list of common English words and forum acronyms (e.g. "ARE", "IT", "CEO") that
          collide with real ticker symbols, since those produce the bulk of false positives.
        </p>
      </section>

      <section>
        <h2 className="text-xl font-semibold text-slate-900">Sentiment scoring</h2>
        <p className="mt-1">
          Each post is scored once with VADER, a sentiment model tuned for informal/social text,
          then weighted by engagement:
        </p>
        <pre className="mt-2 overflow-x-auto rounded-lg bg-slate-100 p-3 text-sm">
          weighted_score = compound_score * log(upvotes + comments + 1)
        </pre>
        <p className="mt-1">
          This ensures a highly-upvoted post counts more than a zero-engagement post making the
          same claim.
        </p>
      </section>

      <section>
        <h2 className="text-xl font-semibold text-slate-900">Trend classification</h2>
        <p className="mt-1">
          Rolling averages are computed over 1h/4h/24h/7d windows. A window is classified relative
          to the window immediately before it:
        </p>
        <pre className="mt-2 overflow-x-auto rounded-lg bg-slate-100 p-3 text-sm">
{`if current_avg - previous_avg > 0.05: "bullish"
elif previous_avg - current_avg > 0.05: "bearish"
else: "neutral"`}
        </pre>
      </section>
    </div>
  );
}
