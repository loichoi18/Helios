import { useState, useEffect } from 'react'
import { format } from 'date-fns'

const SEVERITY_STYLE = {
  CRITICAL: { color: '#f85149', bg: 'rgba(248,81,73,0.08)', label: '● CRITICAL' },
  WARNING:  { color: '#d29922', bg: 'rgba(210,153,34,0.08)', label: '◆ WARNING' },
  INFO:     { color: '#58a6ff', bg: 'rgba(88,166,255,0.08)', label: '◉ INFO' },
}

const MAX_ALERTS = 50

/**
 * Derives alerts from the live metrics stream and renders them as a scrollable feed.
 * Fires an alert whenever p99 > 500ms or errorRate > 1% on any incoming point.
 */
export function AlertFeed({ metrics }) {
  const [alerts, setAlerts] = useState([])

  useEffect(() => {
    if (!metrics.length) return
    const latest = metrics[metrics.length - 1]
    const newAlerts = []

    if (latest.p99Latency > 500) {
      newAlerts.push({
        id: `${latest.timestamp}-p99`,
        severity: 'CRITICAL',
        service: latest.serviceName,
        message: `p99 latency ${latest.p99Latency.toFixed(0)}ms exceeds 500ms SLO`,
        firedAt: latest.timestamp,
      })
    }

    if (latest.errorRate > 0.05) {
      newAlerts.push({
        id: `${latest.timestamp}-err`,
        severity: 'CRITICAL',
        service: latest.serviceName,
        message: `Error rate ${(latest.errorRate * 100).toFixed(1)}% exceeds 5% threshold`,
        firedAt: latest.timestamp,
      })
    } else if (latest.errorRate > 0.01) {
      newAlerts.push({
        id: `${latest.timestamp}-warn`,
        severity: 'WARNING',
        service: latest.serviceName,
        message: `Error rate ${(latest.errorRate * 100).toFixed(2)}% elevated above 1%`,
        firedAt: latest.timestamp,
      })
    }

    if (newAlerts.length > 0) {
      setAlerts(prev => [...newAlerts, ...prev].slice(0, MAX_ALERTS))
    }
  }, [metrics])

  return (
    <div>
      <h3 style={{
        fontSize: 13, color: 'var(--muted)',
        textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 12,
      }}>
        Alert Feed
        {alerts.length > 0 && (
          <span style={{
            marginLeft: 8, fontSize: 11,
            background: '#f85149', color: '#fff',
            borderRadius: 10, padding: '1px 7px',
          }}>
            {alerts.length}
          </span>
        )}
      </h3>

      <div style={{ maxHeight: 320, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 6 }}>
        {alerts.length === 0 ? (
          <p style={{ color: 'var(--muted)', fontSize: 13 }}>✓ No alerts — all services healthy</p>
        ) : (
          alerts.map(alert => {
            const style = SEVERITY_STYLE[alert.severity] ?? SEVERITY_STYLE.INFO
            return (
              <div key={alert.id} style={{
                background: style.bg,
                border: `1px solid ${style.color}30`,
                borderLeft: `3px solid ${style.color}`,
                borderRadius: 6,
                padding: '8px 12px',
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 3 }}>
                  <span style={{ fontSize: 11, fontWeight: 600, color: style.color }}>
                    {style.label}
                  </span>
                  <span style={{ fontSize: 10, color: 'var(--muted)', fontFamily: 'JetBrains Mono, monospace' }}>
                    {format(new Date(alert.firedAt), 'HH:mm:ss')}
                  </span>
                </div>
                <p style={{ fontSize: 12, color: 'var(--text)', marginBottom: 2 }}>{alert.message}</p>
                <p style={{ fontSize: 11, color: 'var(--muted)' }}>service: {alert.service}</p>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}
