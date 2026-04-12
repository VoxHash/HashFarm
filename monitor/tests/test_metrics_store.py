from __future__ import annotations

import sqlite3
from pathlib import Path

from app.metrics import record_snapshot


def test_record_snapshot_inserts_and_prunes(tmp_path: Path) -> None:
    db = str(tmp_path / "m.sqlite")
    snap = {
        "aggregate_hashrate_hs": 1234.5,
        "monero": {"height": 3_000_000, "sync_lag_blocks": 2, "_error": None},
    }
    record_snapshot(db, snap, retention_days=365)
    record_snapshot(db, snap, retention_days=365)
    with sqlite3.connect(db) as conn:
        n = conn.execute("SELECT COUNT(*) FROM snapshot_metrics").fetchone()[0]
    assert n == 2
