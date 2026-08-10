function ringColor(percent: number): string {
  if (percent >= 70) return '#34d399'
  if (percent >= 40) return '#fbbf24'
  return '#f87171'
}

export function ScoreRing({
  percent,
  size = 220,
  strokeWidth = 16,
  label,
}: {
  percent: number
  size?: number
  strokeWidth?: number
  label?: string
}) {
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const offset = circumference * (1 - Math.min(Math.max(percent, 0), 100) / 100)
  const color = ringColor(percent)

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#2a2d33"
          strokeWidth={strokeWidth}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: 'stroke-dashoffset 0.6s ease' }}
        />
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className="text-6xl font-bold text-white">{Math.round(percent)}%</span>
        {label && <span className="mt-1 text-sm text-neutral-400">{label}</span>}
      </div>
    </div>
  )
}
