import { RadialBarChart, RadialBar, ResponsiveContainer } from 'recharts'

const STATUS_COLOUR = {
  healthy:  '#3fb950',
  degraded: '#d29922',
  critical: '#f85149',
}

/**
 * Circular gauge showing live SLA compliance percentage.
 * Colour transitions: green ≥99.9% → yellow ≥99% → red below.
 */
export function SLAGauge({ sla, status, breaches, total }) {
  const colour = STATUS_COLOUR[status] ?? '#8b949e'
  const data = [{ value: sla, fill: colour }]

  return (
    <div style={{ textAlign: 'center' }}>
      <h3 style={{
        fontSize: 13, color: 'var(--muted)',
        textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 8,
      }}>
        SLA (last 60 min)
      </h3>

      <div style={{ position: 'relative', width: 160, margin: '0 auto' }}>
        <ResponsiveContainer width={160} height={160}>
          <RadialBarChart
            cx="50%" cy="50%"
            innerRadius="70%" outerRadius="100%"
            startAngle={210} endAngle={-30}
            data={data}
            barSize={14}
          >
            <RadialBar dataKey="value" cornerRadius={6} background={{ fill: '#21262d' }} />
          </RadialBarChart>
        </ResponsiveContainer>

        {/* Centre label */}
        <div style={{
          position: 'absolute', inset: 0,
          display: 'flex', flexDirection: 'column',
          alignItems: 'center', justifyContent: 'center',
        }}>
          <span style={{ fontSize: 28, fontWeight: 600, color: colour, fontFamily: 'JetBrains Mono, monospace' }}>
            {sla.toFixed(2)}%
          </span>
          <span style={{ fontSize: 11, color: 'var(--muted)', marginTop: 2, textTransform: 'uppercase' }}>
            {status}
          </span>
        </div>
      </div>

      <p style={{ fontSize: 12, color: 'var(--muted)', marginTop: 8 }}>
        {breaches} breach{breaches !== 1 ? 'es' : ''} / {total} samples
      </p>
    </div>
  )
}
