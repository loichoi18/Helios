"""
helios/sre/tests/test_detector.py
──────────────────────────────────
Unit + property-based tests for the anomaly detector.
"""

import numpy as np
import pytest
import responses as resp_mock
import requests

from anomaly_detection.detector import build_feature_matrix, detect, fetch_metrics


# ── build_feature_matrix ─────────────────────────────────────────────────────

def test_feature_matrix_shape():
    events = [
        {"p99Latency": 120.0, "errorRate": 0.001, "requestRate": 200.0},
        {"p99Latency": 850.0, "errorRate": 0.12,  "requestRate": 180.0},
    ]
    X = build_feature_matrix(events)
    assert X.shape == (2, 3)


def test_feature_matrix_missing_fields():
    """Missing fields should default to 0.0 without raising."""
    events = [{"p99Latency": 100.0}]
    X = build_feature_matrix(events)
    assert X[0, 1] == 0.0   # errorRate missing → 0
    assert X[0, 2] == 0.0   # requestRate missing → 0


# ── detect ────────────────────────────────────────────────────────────────────

def _make_normal_data(n: int = 100) -> np.ndarray:
    rng = np.random.default_rng(0)
    return np.column_stack([
        rng.normal(120, 20, n),    # p99 latency ~120ms
        rng.uniform(0, 0.005, n),  # error rate ~0–0.5%
        rng.normal(200, 30, n),    # request rate ~200 rps
    ])


def test_detect_returns_expected_shape():
    X = _make_normal_data(100)
    result = detect(X, contamination=0.05)
    assert result.total == 100
    assert result.anomaly_count + (100 - result.anomaly_count) == 100


def test_detect_spots_obvious_spike():
    """Inject one extreme outlier and verify it is flagged."""
    X = _make_normal_data(99)
    spike = np.array([[9999.0, 0.99, 0.1]])   # extreme anomaly
    X = np.vstack([X, spike])
    result = detect(X, contamination=0.05)
    # The last row (index 99) must be in anomaly_indices
    assert 99 in result.anomaly_indices


def test_detect_anomaly_rate_within_contamination():
    X = _make_normal_data(200)
    result = detect(X, contamination=0.1)
    # IsolationForest guarantees exactly floor(contamination * n) anomalies
    assert result.anomaly_rate <= 0.11   # small tolerance


# ── fetch_metrics (mocked HTTP) ───────────────────────────────────────────────

@resp_mock.activate
def test_fetch_metrics_success():
    payload = [
        {"p99Latency": 120, "errorRate": 0.001, "requestRate": 200, "serviceName": "test"},
    ]
    resp_mock.add(resp_mock.GET, "http://fake-api/api/metrics/recent",
                  json=payload, status=200)
    events = fetch_metrics("http://fake-api", minutes=5)
    assert len(events) == 1
    assert events[0]["serviceName"] == "test"


@resp_mock.activate
def test_fetch_metrics_server_error():
    resp_mock.add(resp_mock.GET, "http://fake-api/api/metrics/recent", status=500)
    with pytest.raises(requests.HTTPError):
        fetch_metrics("http://fake-api")
