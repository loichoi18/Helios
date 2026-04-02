import { useState, useEffect, useRef, useCallback } from 'react'

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8080/ws/metrics'
const MAX_POINTS = 300   // rolling window — ~25 min at 5s cadence

/**
 * Streams live MetricEvent objects from the backend WebSocket.
 *
 * @param {string} service  Filter to a specific service name, or null for all
 * @returns {{ metrics: MetricEvent[], connected: boolean, reconnecting: boolean }}
 */
export function useMetricsWebSocket(service = null) {
  const [metrics, setMetrics] = useState([])
  const [connected, setConnected] = useState(false)
  const [reconnecting, setReconnecting] = useState(false)
  const wsRef = useRef(null)
  const retryTimerRef = useRef(null)
  const retryCount = useRef(0)

  const connect = useCallback(() => {
    const url = service ? `${WS_URL}?service=${service}` : WS_URL
    const ws = new WebSocket(url)
    wsRef.current = ws

    ws.onopen = () => {
      setConnected(true)
      setReconnecting(false)
      retryCount.current = 0
    }

    ws.onmessage = (evt) => {
      try {
        const point = JSON.parse(evt.data)
        setMetrics(prev => {
          const filtered = service
            ? [...prev, point].filter(m => m.serviceName === service)
            : [...prev, point]
          return filtered.slice(-MAX_POINTS)
        })
      } catch (e) {
        console.warn('Failed to parse metric event', e)
      }
    }

    ws.onclose = () => {
      setConnected(false)
      // Exponential backoff: 1s, 2s, 4s, 8s … capped at 30s
      const delay = Math.min(1000 * 2 ** retryCount.current, 30_000)
      retryCount.current += 1
      setReconnecting(true)
      retryTimerRef.current = setTimeout(connect, delay)
    }

    ws.onerror = () => ws.close()
  }, [service])

  useEffect(() => {
    connect()
    return () => {
      clearTimeout(retryTimerRef.current)
      wsRef.current?.close()
    }
  }, [connect])

  return { metrics, connected, reconnecting }
}
