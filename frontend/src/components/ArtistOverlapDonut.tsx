import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'

export function ArtistOverlapDonut({
  sharedCount,
  onlyYouCount,
  onlyThemCount,
  otherLabel,
}: {
  sharedCount: number
  onlyYouCount: number
  onlyThemCount: number
  otherLabel: string
}) {
  const data = [
    { name: 'Shared', value: sharedCount, color: '#c084fc' },
    { name: 'Only you', value: onlyYouCount, color: '#34d399' },
    { name: `Only ${otherLabel}`, value: onlyThemCount, color: '#60a5fa' },
  ].filter((entry) => entry.value > 0)

  if (data.length === 0) {
    return <p className="text-sm text-neutral-500">No artist data yet.</p>
  }

  return (
    <ResponsiveContainer width="100%" height={240}>
      <PieChart>
        <Pie
          data={data}
          dataKey="value"
          nameKey="name"
          innerRadius={60}
          outerRadius={90}
          paddingAngle={2}
          isAnimationActive={false}
        >
          {data.map((entry) => (
            <Cell key={entry.name} fill={entry.color} stroke="none" />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{ background: '#16181d', border: '1px solid #2a2d33', borderRadius: 8 }}
          labelStyle={{ color: '#f2f2f2' }}
        />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  )
}
