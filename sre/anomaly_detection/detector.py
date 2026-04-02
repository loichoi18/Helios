"""
helios/sre/anomaly_detection/detector.py
────────────────────────────────────────
Unsupervised anomaly detection using Isolation Forest.

Runs against the Helios metrics API and prints (or exits non-zero on) any
anomalous windows — suitable for use as a post-deploy reliability gate in CI.

Usage:
    python detector.py --source http://localhost:8080
    python detector.py --source http://localhost:8080 --fail-on-anomaly
"""

from __future__ import annotations

import argparse
import sys
import logging
from dataclasses import dataclass

import numpy as np
import requests
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

FEATURES = ["p99Latency", "errorRate", "requestRate"]


@dataclass
class AnomalyResult:
    total: int
    anomaly_count: int
    anomaly_indices: list[int]
    scores: np.ndarray   # raw decision scores (lower = more anomalous)

    @property
    def anomaly_rate(self) -> float:
        return self.anomaly_count / self.total if self.total else 0.0


def fetch_metrics(api_url: str, minutes: int = 60) -> list[dict]:
    """Pull recent metric events from the Helios REST API."""
    resp = requests.get(
        f"{api_url}/api/metrics/recent",
        params={"minutes": minutes},
        timeout=10,
    )
    resp.raise_for_status()
    events: list[dict] = resp.json()
    log.info("Fetched %d metric events (last %d min)", len(events), minutes)
    return events


def build_feature_matrix(events: list[dict]) -> np.ndarray:
    """Extract and stack numeric features into an (n_samples, n_features) array."""
    rows = []
    for evt in events:
        row = [float(evt.get(f, 0.0)) for f in FEATURES]
        rows.append(row)
    return np.array(rows, dtype=np.float64)


def detect(
    X: np.ndarray,
    contamination: float = 0.05,
    random_state: int = 42,
) -> AnomalyResult:
    """
    Fit an Isolation Forest and return anomalous indices.

    contamination: expected proportion of anomalies in the data.
    Suitable for infrastructure data where ~5% of windows may be noisy.
    """
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = IsolationForest(
        n_estimators=200,
        contamination=contamination,
        random_state=random_state,
        n_jobs=-1,
    )
    labels = model.fit_predict(X_scaled)    # -1 = anomaly, 1 = normal
    scores = model.decision_function(X_scaled)

    anomaly_indices = [i for i, label in enumerate(labels) if label == -1]
    return AnomalyResult(
        total=len(X),
        anomaly_count=len(anomaly_indices),
        anomaly_indices=anomaly_indices,
        scores=scores,
    )


def report(result: AnomalyResult, events: list[dict]) -> None:
    log.info(
        "Anomaly detection complete — %d / %d windows flagged (%.1f%%)",
        result.anomaly_count, result.total, result.anomaly_rate * 100,
    )
    for idx in result.anomaly_indices[:10]:   # print top-10 anomalies
        evt = events[idx]
        log.warning(
            "  ANOMALY idx=%d service=%s p99=%.0fms errorRate=%.3f rps=%.0f score=%.4f",
            idx,
            evt.get("serviceName"),
            evt.get("p99Latency", 0),
            evt.get("errorRate", 0),
            evt.get("requestRate", 0),
            result.scores[idx],
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Helios anomaly detector")
    parser.add_argument("--source",          default="http://localhost:8080")
    parser.add_argument("--minutes",         type=int,   default=60)
    parser.add_argument("--contamination",   type=float, default=0.05)
    parser.add_argument("--fail-on-anomaly", action="store_true",
                        help="Exit with code 1 if anomalies are found (for CI gates)")
    args = parser.parse_args()

    events = fetch_metrics(args.source, args.minutes)
    if len(events) < 10:
        log.warning("Too few events (%d) for reliable detection — skipping", len(events))
        sys.exit(0)

    X = build_feature_matrix(events)
    result = detect(X, contamination=args.contamination)
    report(result, events)

    if args.fail_on_anomaly and result.anomaly_count > 0:
        log.error("CI gate FAILED: %d anomalous windows detected", result.anomaly_count)
        sys.exit(1)


if __name__ == "__main__":
    main()
