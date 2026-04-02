import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ReferenceLine, ResponsiveContainer,
} from 'recharts'
import { format } from 'date-fns'

export function ErrorRateChart({ metrics }) {
  const data = metrics.map(m => ({
    timestamp: m.timestamp,
    errorPct: +(m.errorRate * 100).toFixed(3),
    requestRate: +m.requestRate.toFixed(1),
  }))

  return (
    <div style={{ width: '100%' }}>
      <h3 style={{
        fontSize: 13, color: 'var(--muted)',
        textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 12,
      }}>
        Error Rate %
      </h3>
      <ResponsiveContainer width="100%" height={160}>
        <LineChart data={data} margin={{ top: 4, right: 16, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
          <XAxis
            dataKey="timestamp"
            tickFormatter={t => format(new Date(t), 'HH:mm')}
            tick={{ fill: '#8b949e', fontSize: 11 }}
            interval="preserveStartEnd"
          />
          <YAxis
            unit="%"
            tick={{ fill: '#8b949e', fontSize: 11 }}
            width={42}
          />
          <Tooltip
            formatter={(v, name) => [`${v}%`, name === 'errorPct' ? 'Error Rate' : 'RPS']}
            labelFormatter={t => format(new Date(t), 'HH:mm:ss')}
            contentStyle={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 6, fontSize: 12 }}
          />
          <ReferenceLine y={1} stroke="#d29922" strokeDasharray="4 4"
            label={{ value: 'SLO 1%', fill: '#d29922', fontSize: 11 }} />
          <ReferenceLine y={5} stroke="#f85149" strokeDasharray="4 4"
            label={{ value: 'Critical 5%', fill: '#f85149', fontSize: 11 }} />
          <Line type="monotone" dataKey="errorPct" stroke="#f85149"
            strokeWidth={2} dot={false} activeDot={{ r: 4 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
