"""
helios/sre/chaos/chaos_runner.py
─────────────────────────────────
Controlled fault injection tool for validating alert pipelines,
runbook triggers, and dashboard behaviour under degraded conditions.

Supports two fault modes:
  latency  — adds artificial delay to a target service endpoint
  errors   — injects HTTP 500 responses at a configured rate

Usage:
    python chaos_runner.py latency --target http://localhost:8080 --extra-ms 600 --duration 120
    python chaos_runner.py errors  --target http://localhost:8080 --rate 0.1  --duration 60
    python chaos_runner.py both    --target http://localhost:8080 --extra-ms 400 --rate 0.05 --duration 90
"""

from __future__ import annotations

import argparse
import logging
import signal
import sys
import time
from dataclasses import dataclass
from typing import Optional

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

_stop = False


def _handle_signal(sig, frame):
    global _stop
    log.info("Interrupt received — stopping chaos and cleaning up…")
    _stop = True


signal.signal(signal.SIGINT,  _handle_signal)
signal.signal(signal.SIGTERM, _handle_signal)


@dataclass
class ChaosConfig:
    target: str
    extra_ms: int = 0
    error_rate: float = 0.0
    duration_s: int = 60
    poll_interval_s: int = 5


def _post(url: str, payload: dict) -> bool:
    try:
        r = requests.post(url, json=payload, timeout=5)
        return r.status_code < 400
    except requests.RequestException as exc:
        log.warning("POST failed: %s", exc)
        return False


def _delete(url: str) -> bool:
    try:
        r = requests.delete(url, timeout=5)
        return r.status_code < 400
    except requests.RequestException as exc:
        log.warning("DELETE failed: %s", exc)
        return False


def inject_latency(cfg: ChaosConfig) -> None:
    """Activate latency injection on target for cfg.duration_s seconds."""
    url = f"{cfg.target}/chaos/latency"
    log.info("💥 Injecting %dms latency into %s for %ds", cfg.extra_ms, cfg.target, cfg.duration_s)
    _post(url, {"extra_ms": cfg.extra_ms, "active": True})

    end = time.monotonic() + cfg.duration_s
    while time.monotonic() < end and not _stop:
        remaining = int(end - time.monotonic())
        log.info("  ⏱  latency chaos active — %ds remaining", remaining)
        time.sleep(cfg.poll_interval_s)

    log.info("Removing latency injection…")
    _delete(url)


def inject_errors(cfg: ChaosConfig) -> None:
    """Activate error rate injection on target for cfg.duration_s seconds."""
    url = f"{cfg.target}/chaos/errors"
    log.info("💥 Injecting %.0f%% error rate into %s for %ds",
             cfg.error_rate * 100, cfg.target, cfg.duration_s)
    _post(url, {"error_rate": cfg.error_rate, "active": True})

    end = time.monotonic() + cfg.duration_s
    while time.monotonic() < end and not _stop:
        remaining = int(end - time.monotonic())
        log.info("  ⏱  error chaos active — %ds remaining", remaining)
        time.sleep(cfg.poll_interval_s)

    log.info("Removing error injection…")
    _delete(url)


def run_both(cfg: ChaosConfig) -> None:
    """Inject both latency and errors simultaneously."""
    log.info("💥 Combined chaos: %dms latency + %.0f%% errors for %ds",
             cfg.extra_ms, cfg.error_rate * 100, cfg.duration_s)
    _post(f"{cfg.target}/chaos/latency", {"extra_ms": cfg.extra_ms, "active": True})
    _post(f"{cfg.target}/chaos/errors",  {"error_rate": cfg.error_rate, "active": True})

    end = time.monotonic() + cfg.duration_s
    while time.monotonic() < end and not _stop:
        log.info("  ⏱  combined chaos active — %ds remaining", int(end - time.monotonic()))
        time.sleep(cfg.poll_interval_s)

    _delete(f"{cfg.target}/chaos/latency")
    _delete(f"{cfg.target}/chaos/errors")


def main() -> None:
    parser = argparse.ArgumentParser(description="Helios chaos fault injector")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    def add_common(p):
        p.add_argument("--target",   default="http://localhost:8080")
        p.add_argument("--duration", type=int, default=60)

    lat = subparsers.add_parser("latency")
    add_common(lat)
    lat.add_argument("--extra-ms", type=int, default=500)

    err = subparsers.add_parser("errors")
    add_common(err)
    err.add_argument("--rate", type=float, default=0.1)

    both = subparsers.add_parser("both")
    add_common(both)
    both.add_argument("--extra-ms", type=int, default=400)
    both.add_argument("--rate", type=float, default=0.05)

    args = parser.parse_args()
    cfg = ChaosConfig(
        target=args.target,
        extra_ms=getattr(args, "extra_ms", 0),
        error_rate=getattr(args, "rate", 0.0),
        duration_s=args.duration,
    )

    if args.mode == "latency":
        inject_latency(cfg)
    elif args.mode == "errors":
        inject_errors(cfg)
    elif args.mode == "both":
        run_both(cfg)

    log.info("Chaos run complete.")


if __name__ == "__main__":
    main()
