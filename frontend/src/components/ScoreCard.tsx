export function ScoreCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-xl border border-neutral-800 bg-neutral-900/50 p-6 text-center">
      <p className="text-3xl font-bold text-white">{Math.round(value * 100)}%</p>
      <p className="mt-1 text-sm text-neutral-400">{label}</p>
    </div>
  )
}
