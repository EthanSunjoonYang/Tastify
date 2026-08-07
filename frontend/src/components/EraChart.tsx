import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

interface Series {
  key: string
  name: string
  color: string
}

export function EraChart<T extends { decade: string }>({
  data,
  series,
}: {
  data: T[]
  series: Series[]
}) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={data} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#2a2d33" vertical={false} />
        <XAxis dataKey="decade" stroke="#8a8f98" fontSize={13} tickLine={false} />
        <YAxis
          stroke="#8a8f98"
          fontSize={13}
          tickLine={false}
          tickFormatter={(value: number) => `${Math.round(value * 100)}%`}
        />
        <Tooltip
          contentStyle={{ background: '#16181d', border: '1px solid #2a2d33', borderRadius: 8 }}
          labelStyle={{ color: '#f2f2f2' }}
          formatter={(value) => `${Math.round(Number(value) * 100)}%`}
        />
        {series.length > 1 && <Legend />}
        {series.map((s) => (
          <Bar
            key={s.key}
            dataKey={s.key}
            name={s.name}
            fill={s.color}
            radius={[4, 4, 0, 0]}
            isAnimationActive={false}
          />
        ))}
      </BarChart>
    </ResponsiveContainer>
  )
}
