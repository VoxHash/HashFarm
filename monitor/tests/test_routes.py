from __future__ import annotations

from app.main import app
from starlette.testclient import TestClient


def test_health_liveness() -> None:
    with TestClient(app) as client:
        r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_ready_without_fresh_snapshot() -> None:
    """Initial SNAPSHOT has no updated_at — orchestration should see not-ready."""
    with TestClient(app) as client:
        r = client.get("/ready")
    assert r.status_code == 503
    body = r.json()
    assert body.get("ready") is False


def test_metrics_prometheus_text() -> None:
    with TestClient(app) as client:
        r = client.get("/metrics")
    assert r.status_code == 200
    assert "hashfarm_aggregate_hashrate_hs" in r.text
    assert "hashfarm_sync_lag_blocks" in r.text
