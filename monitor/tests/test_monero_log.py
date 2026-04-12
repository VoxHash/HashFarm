from __future__ import annotations

import tempfile
from pathlib import Path

from app import monero_log


def test_sync_heights_from_bitmonero_log_picks_last_line() -> None:
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "bitmonero.log"
        p.write_bytes(
            b"noise\n"
            b"2026-04-12 14:39:14 INFO Synced 2492524/3650881 (68%, left)\n"
            b"2026-04-12 14:50:51 INFO Synced 2492624/3650893 (68%, left)\n"
        )
        got = monero_log.sync_heights_from_bitmonero_log(d)
        assert got is not None
        assert got["height"] == 2492624
        assert got["target_height"] == 3650893
        assert got["sync_lag_blocks"] == 3650893 - 2492624
        assert got["synchronized_flag"] is False


def test_sync_heights_missing_file_returns_none() -> None:
    with tempfile.TemporaryDirectory() as d:
        assert monero_log.sync_heights_from_bitmonero_log(d) is None
