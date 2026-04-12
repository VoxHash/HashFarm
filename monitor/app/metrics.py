"""Append-only SQLite metrics and Prometheus text exposition."""

from __future__ import annotations

import sqlite3
import time
from pathlib import Path
from typing import Any


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS snapshot_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts INTEGER NOT NULL,
            aggregate_hashrate_hs REAL NOT NULL,
            sync_lag_blocks INTEGER NOT NULL,
            height INTEGER NOT NULL,
            monero_error INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_snapshot_metrics_ts ON snapshot_metrics(ts)")


def record_snapshot(path: str, snap: dict[str, Any], retention_days: int) -> None:
    """Insert one row and prune rows older than retention_days."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    monero = snap.get("monero") or {}
    err = 1 if monero.get("_error") else 0
    ts = int(time.time())
    hr = float(snap.get("aggregate_hashrate_hs") or 0.0)
    lag = int(monero.get("sync_lag_blocks") or 0)
    height = int(monero.get("height") or 0)
    cutoff = ts - max(1, retention_days) * 86400
    with sqlite3.connect(p, timeout=10.0) as conn:
        _ensure_schema(conn)
        conn.execute(
            "INSERT INTO snapshot_metrics (ts, aggregate_hashrate_hs, sync_lag_blocks, height, monero_error) VALUES (?,?,?,?,?)",
            (ts, hr, lag, height, err),
        )
        conn.execute("DELETE FROM snapshot_metrics WHERE ts < ?", (cutoff,))
        conn.commit()


def prometheus_text(snap: dict[str, Any]) -> str:
    """OpenMetrics-style gauges from the current in-memory snapshot."""
    monero = snap.get("monero") or {}
    hr = float(snap.get("aggregate_hashrate_hs") or 0.0)
    lag = int(monero.get("sync_lag_blocks") or 0)
    height = int(monero.get("height") or 0)
    target = int(monero.get("target_height") or 0)
    diff = float(monero.get("difficulty") or 0.0)
    err = 1.0 if monero.get("_error") else 0.0
    stale = 1.0 if monero.get("monero_rpc_stale") else 0.0
    lines = [
        "# HELP hashfarm_aggregate_hashrate_hs Sum of rig hashrate.total (H/s).",
        "# TYPE hashfarm_aggregate_hashrate_hs gauge",
        f"hashfarm_aggregate_hashrate_hs {hr}",
        "# HELP hashfarm_sync_lag_blocks Monero target_height minus height (blocks).",
        "# TYPE hashfarm_sync_lag_blocks gauge",
        f"hashfarm_sync_lag_blocks {lag}",
        "# HELP hashfarm_height Monero chain height from last snapshot.",
        "# TYPE hashfarm_height gauge",
        f"hashfarm_height {height}",
        "# HELP hashfarm_target_height Monero network target height.",
        "# TYPE hashfarm_target_height gauge",
        f"hashfarm_target_height {target}",
        "# HELP hashfarm_difficulty Monero difficulty from last snapshot.",
        "# TYPE hashfarm_difficulty gauge",
        f"hashfarm_difficulty {diff}",
        "# HELP hashfarm_monero_rpc_error 1 if monero JSON-RPC failed on last poll.",
        "# TYPE hashfarm_monero_rpc_error gauge",
        f"hashfarm_monero_rpc_error {err}",
        "# HELP hashfarm_monero_rpc_stale 1 if heights were merged from last-good snapshot.",
        "# TYPE hashfarm_monero_rpc_stale gauge",
        f"hashfarm_monero_rpc_stale {stale}",
        "",
    ]
    return "\n".join(lines)
