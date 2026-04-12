from __future__ import annotations

import copy
import time
from typing import Any

from . import settings

_SNAPSHOT_BASE: dict[str, Any] = {
    "updated_at": None,
    "monero": {
        "height": 0,
        "target_height": 0,
        "difficulty": 0.0,
        "status": "—",
        "incoming_connections": 0,
        "outgoing_connections": 0,
        "sync_lag_blocks": 0,
        "synchronized_flag": False,
        "expected_reward_atomic": 0,
    },
    "p2pool": {"stratum": None, "p2p": None, "error": None},
    "rigs": [],
    "aggregate_hashrate_hs": 0.0,
    "estimated_mainchain_solo_xmr_per_day": 0.0,
    "total_watts": 0.0,
    "daily_power_usd": 0.0,
    "xmr_usd": None,
    "net_usd_per_day": None,
    "wallet_main": "",
    "last_error": None,
    "endpoints": {},
}

SNAPSHOT: dict[str, Any] = {}

_LAST_GOOD_MONERO: dict[str, Any] | None = None
_LAST_GOOD_MONERO_TS: float = 0.0

_MONERO_KEYS_FOR_STALE: tuple[str, ...] = (
    "height",
    "target_height",
    "difficulty",
    "status",
    "incoming_connections",
    "outgoing_connections",
    "synchronized_flag",
    "expected_reward_atomic",
    "raw_info_subset",
)


def monero_collector_failure(message: str) -> dict[str, Any]:
    m = copy.deepcopy(_SNAPSHOT_BASE["monero"])
    m["_error"] = message
    m["status"] = "RPC unavailable"
    return m


def record_last_good_monero(m: dict[str, Any]) -> None:
    """Remember last successful get_info snapshot for stale display during transient RPC failures."""
    global _LAST_GOOD_MONERO, _LAST_GOOD_MONERO_TS
    if m.get("_error"):
        return
    _LAST_GOOD_MONERO = {k: copy.deepcopy(m[k]) for k in _MONERO_KEYS_FOR_STALE if k in m}
    _LAST_GOOD_MONERO_TS = time.monotonic()


def merge_stale_monero(failure: dict[str, Any]) -> dict[str, Any]:
    """
    If monerod is unreachable (connect refused), do not show stale heights.
    If RPC failed for overload/timeout and we have a recent good snapshot, overlay chain fields.
    """
    global _LAST_GOOD_MONERO, _LAST_GOOD_MONERO_TS
    err = str(failure.get("_error") or "")
    if "Cannot connect to monerod" in err:
        _LAST_GOOD_MONERO = None
        _LAST_GOOD_MONERO_TS = 0.0
        return failure
    if not _LAST_GOOD_MONERO:
        return failure
    if time.monotonic() - _LAST_GOOD_MONERO_TS > float(settings.MONERO_RPC_STALE_TTL_SEC):
        return failure
    out = dict(failure)
    for k in _MONERO_KEYS_FOR_STALE:
        if k in _LAST_GOOD_MONERO:
            out[k] = copy.deepcopy(_LAST_GOOD_MONERO[k])
    th = int(out.get("target_height") or 0)
    h = int(out.get("height") or 0)
    synced = bool(out.get("synchronized_flag"))
    if th > 0 and h > 0:
        out["sync_lag_blocks"] = max(0, th - h)
    else:
        out["sync_lag_blocks"] = 0 if synced else max(1, settings.MONERO_MAX_SYNC_LAG_BLOCKS + 1)
    out["monero_rpc_stale"] = True
    out["monero_rpc_stale_hint"] = (
        "Height / difficulty / peers below are from the last successful poll; the red message above is the current RPC failure."
    )
    return out


def apply_snapshot(snap: dict[str, Any]) -> None:
    """Atomically replace snapshot so the UI never reads a half-cleared dict."""
    SNAPSHOT.clear()
    SNAPSHOT.update(copy.deepcopy(_SNAPSHOT_BASE))
    SNAPSHOT.update(snap)


def init_snapshot() -> None:
    SNAPSHOT.clear()
    SNAPSHOT.update(copy.deepcopy(_SNAPSHOT_BASE))


init_snapshot()
