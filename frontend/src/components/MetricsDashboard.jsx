import { useState } from 'react'
import { useMetricsWebSocket } from '../hooks/useMetricsWebSocket'
import { useSLAStatus } from '../hooks/useSLAStatus'
import { LatencyHeatmap } from './LatencyHeatmap'
import { SLAGauge } from './SLAGauge'
import { AlertFeed } from './AlertFeed'
import { ErrorRateChart } from './ErrorRateChart'

const SERVICES = ['all', 'canvas-renderer', 'export-service', 'auth-service', 'asset-cdn']

const css = {
  header: {
    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
    padding: '16px 24px', borderBottom: '1px solid var(--border)',
    background: 'var(--surface)',
  },
  logo: { fontSize: 20, fontWeight: 700, letterSpacing: '-0.02em' },
  pill: (connected) => ({
    fontSize: 11, fontWeight: 600,
    padding: '3px 10px', borderRadius: 12,
    background: connected ? 'rgba(63,185,80,0.15)' : 'rgba(248,81,73,0.15)',
    color: connected ? '#3fb950' : '#f85149',
    border: `1px solid ${connected ? '#3fb95050' : '#f8514950'}`,
    fontFamily: 'JetBrains Mono, monospace',
  }),
  grid: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr 220px',
    gridTemplateRows: 'auto auto',
    gap: 16, padding: 24,
  },
  card: {
    background: 'var(--surface)',
    border: '1px solid var(--border)',
    borderRadius: 10, padding: 20,
  },
  serviceBar: {
    display: 'flex', gap: 8, padding: '12px 24px',
    borderBottom: '1px solid var(--border)',
  },
  tab: (active) => ({
    fontSize: 12, fontWeight: 500, padding: '4px 14px',
    borderRadius: 6, cursor: 'pointer', border: 'none',
    background: active ? '#58a6ff22' : 'transparent',
    color: active ? '#58a6ff' : 'var(--muted)',
    outline: 'none',
  }),
  statRow: {
    display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16,
    padding: '0 24px 24px',
  },
  stat: {
    background: 'var(--surface)', border: '1px solid var(--border)',
    borderRadius: 10, padding: '16px 20px',
  },
}

function StatCard({ label, value, unit, colour }) {
  return (
    <div style={css.stat}>
      <p style={{ fontSize: 11, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 6 }}>{label}</p>
      <p style={{ fontSize: 26, fontWeight: 600, fontFamily: 'JetBrains Mono, monospace', color: colour ?? 'var(--text)' }}>
        {value}<span style={{ fontSize: 13, marginLeft: 3, color: 'var(--muted)' }}>{unit}</span>
      </p>
    </div>
  )
}

export function MetricsDashboard() {
  const [activeService, setActiveService] = useState('all')
  const { metrics, connected, reconnecting } = useMetricsWebSocket(
    activeService === 'all' ? null : activeService
  )
  const { sla, breaches, total, status } = useSLAStatus(metrics)

  const latest = metrics[metrics.length - 1]
  const avgP99  = metrics.length ? (metrics.reduce((s, m) => s + m.p99Latency, 0) / metrics.length).toFixed(0) : '—'
  const avgErr  = metrics.length ? (metrics.reduce((s, m) => s + m.errorRate, 0) / metrics.length * 100).toFixed(2) : '—'
  const rps     = latest ? latest.requestRate.toFixed(0) : '—'

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg)' }}>
      {/* Header */}
      <header style={css.header}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{ fontSize: 22 }}>☀️</span>
          <span style={css.logo}>Helios</span>
          <span style={{ fontSize: 12, color: 'var(--muted)', marginLeft: 4 }}>SRE Dashboard</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <span style={{ fontSize: 11, color: 'var(--muted)' }}>
            {metrics.length} events
          </span>
          <span style={css.pill(connected)}>
            {reconnecting ? '⟳ reconnecting' : connected ? '● live' : '○ disconnected'}
          </span>
        </div>
      </header>

      {/* Service selector */}
      <div style={css.serviceBar}>
        {SERVICES.map(svc => (
          <button key={svc} style={css.tab(activeService === svc)}
            onClick={() => setActiveService(svc)}>
            {svc}
          </button>
        ))}
      </div>

      {/* Stat row */}
      <div style={css.statRow}>
        <StatCard label="Avg p99 Latency" value={avgP99} unit="ms"
          colour={+avgP99 > 500 ? '#f85149' : '#3fb950'} />
        <StatCard label="Avg Error Rate" value={avgErr} unit="%"
          colour={+avgErr > 1 ? '#f85149' : '#3fb950'} />
        <StatCard label="Request Rate" value={rps} unit="rps" />
        <StatCard label="Events Received" value={metrics.length} unit="" />
      </div>

      {/* Main grid */}
      <div style={css.grid}>
        {/* Latency heatmap — spans 2 cols */}
        <div style={{ ...css.card, gridColumn: '1 / 3' }}>
          <LatencyHeatmap metrics={metrics} />
        </div>

        {/* SLA gauge */}
        <div style={{ ...css.card, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <SLAGauge sla={sla} status={status} breaches={breaches} total={total} />
        </div>

        {/* Error rate chart */}
        <div style={{ ...css.card, gridColumn: '1 / 3' }}>
          <ErrorRateChart metrics={metrics} />
        </div>

        {/* Alert feed */}
        <div style={{ ...css.card, gridRow: '2 / 4' }}>
          <AlertFeed metrics={metrics} />
        </div>
      </div>
    </div>
  )
}
