import { useState, useEffect } from 'react'

const SLO_P99_MS    = 500    // p99 latency SLO in milliseconds
const SLO_ERROR_PCT = 0.01   // 1% error rate SLO
const WINDOW_MINS   = 60     // rolling window for SLA calculation

/**
 * Derives live SLA compliance % from a stream of MetricEvent objects.
 *
 * A metric window is "compliant" if BOTH:
 *   - p99 latency < SLO_P99_MS
 *   - errorRate   < SLO_ERROR_PCT
 *
 * @param {MetricEvent[]} metrics  Live metric stream from useMetricsWebSocket
 * @returns {{ sla: number, breaches: number, total: number, status: string }}
 */
export function useSLAStatus(metrics) {
  const [slaInfo, setSlaInfo] = useState({
    sla: 100,
    breaches: 0,
    total: 0,
    status: 'healthy',
  })

  useEffect(() => {
    if (!metrics.length) return

    const cutoff = Date.now() - WINDOW_MINS * 60 * 1000
    const window = metrics.filter(m => new Date(m.timestamp).getTime() >= cutoff)
    if (!window.length) return

    const breaches = window.filter(
      m => m.p99Latency > SLO_P99_MS || m.errorRate > SLO_ERROR_PCT
    ).length

    const sla = ((window.length - breaches) / window.length) * 100
    const status = sla >= 99.9 ? 'healthy' : sla >= 99.0 ? 'degraded' : 'critical'

    setSlaInfo({ sla, breaches, total: window.length, status })
  }, [metrics])

  return slaInfo
}
