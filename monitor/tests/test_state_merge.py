from __future__ import annotations

import time

from app import state


def test_merge_without_last_good_no_stale_overlay() -> None:
    failure = state.monero_collector_failure("monerod RPC timed out")
    merged = state.merge_stale_monero(failure)
    assert merged.get("_error")
    assert not merged.get("monero_rpc_stale")


def test_connect_error_clears_last_good() -> None:
    state._LAST_GOOD_MONERO = {"height": 100, "target_height": 200}  # type: ignore[misc]
    state._LAST_GOOD_MONERO_TS = time.monotonic()
    failure = state.monero_collector_failure("Cannot connect to monerod at 'http://127.0.0.1:18081/json_rpc'")
    state.merge_stale_monero(failure)
    assert state._LAST_GOOD_MONERO is None
