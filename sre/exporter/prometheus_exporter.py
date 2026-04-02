"""
helios/sre/exporter/prometheus_exporter.py
──────────────────────────────────────────
Custom Prometheus exporter that scrapes the Helios metrics API and
re-exposes the data as Prometheus gauges so Grafana / Alertmanager
can consume them via the standard /metrics endpoint.

Usage:
    python prometheus_exporter.py --api http://localhost:8080 --port 9100
"""

import argparse
import time
import logging
from typing import Optional

import requests
from prometheus_client import start_http_server, Gauge, REGISTRY, CollectorRegistry

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# ── Prometheus metric definitions ────────────────────────────────────────────

LABELS = ["service", "host"]

p50_gauge  = Gauge("helios_latency_p50_ms",   "p50 latency in milliseconds",  LABELS)
p95_gauge  = Gauge("helios_latency_p95_ms",   "p95 latency in milliseconds",  LABELS)
p99_gauge  = Gauge("helios_latency_p99_ms",   "p99 latency in milliseconds",  LABELS)
err_gauge  = Gauge("helios_error_rate",        "Error rate (0.0–1.0)",         LABELS)
rps_gauge  = Gauge("helios_request_rate_rps",  "Requests per second",          LABELS)
scrape_ok  = Gauge("helios_scrape_success",    "1 if last scrape succeeded, 0 otherwise")


def fetch_recent(api_url: str, minutes: int = 1) -> Optional[list[dict]]:
    """Fetch recent metric events from the Helios REST API."""
    try:
        resp = requests.get(
            f"{api_url}/api/metrics/recent",
            params={"minutes": minutes},
            timeout=5,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        log.error("Failed to fetch metrics from %s: %s", api_url, exc)
        return None


def update_gauges(events: list[dict]) -> None:
    """Aggregate latest value per (service, host) and update Prometheus gauges."""
    # Keep only the most recent event per (service, host) pair
    latest: dict[tuple[str, str], dict] = {}
    for event in events:
        key = (event.get("serviceName", "unknown"), event.get("sourceHost", "unknown"))
        latest[key] = event

    for (service, host), evt in latest.items():
        labels = [service, host]
        p50_gauge.labels(*labels).set(evt.get("p50Latency", 0))
        p95_gauge.labels(*labels).set(evt.get("p95Latency", 0))
        p99_gauge.labels(*labels).set(evt.get("p99Latency", 0))
        err_gauge.labels(*labels).set(evt.get("errorRate", 0))
        rps_gauge.labels(*labels).set(evt.get("requestRate", 0))


def run(api_url: str, scrape_interval: int, port: int) -> None:
    log.info("Starting Helios Prometheus exporter on :%d (scraping %s)", port, api_url)
    start_http_server(port)

    while True:
        events = fetch_recent(api_url)
        if events is not None:
            update_gauges(events)
            scrape_ok.set(1)
            log.info("Scraped %d events", len(events))
        else:
            scrape_ok.set(0)

        time.sleep(scrape_interval)


def main() -> None:
    parser = argparse.ArgumentParser(description="Helios → Prometheus exporter")
    parser.add_argument("--api",      default="http://localhost:8080", help="Helios API base URL")
    parser.add_argument("--port",     type=int, default=9100,          help="Exporter HTTP port")
    parser.add_argument("--interval", type=int, default=15,            help="Scrape interval seconds")
    args = parser.parse_args()

    run(args.api, args.interval, args.port)


if __name__ == "__main__":
    main()
