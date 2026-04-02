import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ReferenceLine, ResponsiveContainer, Legend,
} from 'recharts'
import { format } from 'date-fns'

const SLO_THRESHOLD = 500   // ms

function formatTime(ts) {
  return format(new Date(ts), 'HH:mm:ss')
}

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div style={{
      background: 'var(--surface)',
      border: '1px solid var(--border)',
      borderRadius: 6,
      padding: '8px 12px',
      fontFamily: 'JetBrains Mono, monospace',
      fontSize: 12,
    }}>
      <p style={{ color: 'var(--muted)', marginBottom: 4 }}>{formatTime(label)}</p>
      {payload.map(p => (
        <p key={p.dataKey} style={{ color: p.color }}>
          {p.dataKey}: <strong>{p.value?.toFixed(1)}ms</strong>
        </p>
      ))}
    </div>
  )
}

/**
 * Renders a stacked area chart of p50/p95/p99 latency over time.
 * Draws a red dashed reference line at the p99 SLO threshold.
 */
export function LatencyHeatmap({ metrics }) {
  const data = metrics.map(m => ({
    timestamp: m.timestamp,
    p50: Math.round(m.p50Latency),
    p95: Math.round(m.p95Latency),
    p99: Math.round(m.p99Latency),
  }))

  return (
    <div style={{ width: '100%' }}>
      <h3 style={{ marginBottom: 12, fontSize: 13, color: 'var(--muted)', letterSpacing: '0.05em', textTransform: 'uppercase' }}>
        Latency Distribution
      </h3>
      <ResponsiveContainer width="100%" height={220}>
        <AreaChart data={data} margin={{ top: 4, right: 16, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="grad-p99" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="#f85149" stopOpacity={0.25} />
              <stop offset="95%" stopColor="#f85149" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="grad-p95" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="#d29922" stopOpacity={0.2} />
              <stop offset="95%" stopColor="#d29922" stopOpacity={0} />
            </linearGradient>
          </defs>

          <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
          <XAxis
            dataKey="timestamp"
            tickFormatter={formatTime}
            tick={{ fill: '#8b949e', fontSize: 11 }}
            interval="preserveStartEnd"
          />
          <YAxis
            unit="ms"
            tick={{ fill: '#8b949e', fontSize: 11 }}
            width={55}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ fontSize: 12, color: '#8b949e' }} />

          <ReferenceLine
            y={SLO_THRESHOLD}
            stroke="#f85149"
            strokeDasharray="5 5"
            label={{ value: `SLO ${SLO_THRESHOLD}ms`, fill: '#f85149', fontSize: 11 }}
          />

          <Area type="monotone" dataKey="p50" stroke="#3fb950" fill="none"     strokeWidth={1.5} dot={false} />
          <Area type="monotone" dataKey="p95" stroke="#d29922" fill="url(#grad-p95)" strokeWidth={1.5} dot={false} />
          <Area type="monotone" dataKey="p99" stroke="#f85149" fill="url(#grad-p99)" strokeWidth={2}   dot={false} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
