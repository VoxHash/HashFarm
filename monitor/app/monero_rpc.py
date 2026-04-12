from __future__ import annotations

import asyncio
import json
from typing import Any

import httpx

from . import settings


def _format_rpc_failure(exc: BaseException) -> str:
    if isinstance(exc, httpx.ConnectError):
        return (
            f"Cannot connect to monerod at {settings.MONERO_RPC_URL!r} ({exc}). "
            "Start monerod or fix MONERO_RPC_URL in .env."
        )
    if isinstance(exc, httpx.TimeoutException):
        return (
            f"monerod RPC timed out ({settings.MONERO_RPC_URL!r}, read timeout {settings.MONERO_RPC_TIMEOUT_SEC}s). "
            "The daemon may be overloaded during sync—increase MONERO_RPC_TIMEOUT_SEC in .env if needed."
        )
    if isinstance(exc, httpx.HTTPStatusError):
        return f"monerod HTTP {exc.response.status_code} from {settings.MONERO_RPC_URL!r}: {exc}"
    if isinstance(exc, RuntimeError):
        return str(exc)
    return f"monerod RPC error: {type(exc).__name__}: {exc}"


def _rpc_timeout() -> httpx.Timeout:
    r = float(settings.MONERO_RPC_TIMEOUT_SEC)
    return httpx.Timeout(connect=10.0, read=r, write=30.0, pool=10.0)


async def _post_rpc_once(client: httpx.AsyncClient, method: str, params: dict[str, Any] | None) -> dict[str, Any]:
    body = {"jsonrpc": "2.0", "id": "hf", "method": method, "params": params or {}}
    r = await client.post(settings.MONERO_RPC_URL, json=body, timeout=_rpc_timeout())
    r.raise_for_status()
    raw = r.content
    if not raw or not raw.strip():
        raise RuntimeError(
            "Empty HTTP body from monerod (common while the node is busy syncing or under disk load). "
            "See p2pool.log for similar get_info messages; retry shortly."
        )
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise RuntimeError(f"Invalid JSON from monerod: {e}") from e
    if data.get("error"):
        raise RuntimeError(str(data["error"]))
    return data.get("result") or {}


async def _rpc(
    client: httpx.AsyncClient,
    method: str,
    params: dict[str, Any] | None = None,
    *,
    transient_retries: int = 0,
) -> dict[str, Any]:
    """JSON-RPC to monerod. transient_retries: extra attempts for empty body / transport blips (get_info)."""
    backoff = (0.2, 0.5, 0.8)
    last: BaseException | None = None
    total = 1 + max(0, transient_retries)
    for attempt in range(total):
        try:
            return await _post_rpc_once(client, method, params)
        except (httpx.HTTPError, OSError, RuntimeError) as e:
            last = e
            if attempt >= total - 1:
                break
            delay = backoff[min(attempt, len(backoff) - 1)]
            await asyncio.sleep(delay)
    assert last is not None
    raise RuntimeError(_format_rpc_failure(last)) from last


async def fetch_daemon_snapshot(client: httpx.AsyncClient) -> dict[str, Any]:
    info = await _rpc(client, "get_info", transient_retries=3)
    height = int(info.get("height") or 0)
    target = int(info.get("target_height") or 0)
    diff = float(info.get("difficulty") or 0)
    synced = bool(info.get("synchronized"))
    if target > 0 and height > 0:
        lag = max(0, target - height)
    else:
        lag = 0 if synced else max(1, settings.MONERO_MAX_SYNC_LAG_BLOCKS + 1)
    tpl: dict[str, Any] = {}
    if settings.WALLET_MAIN:
        try:
            tpl = await _rpc(
                client,
                "get_block_template",
                {"wallet_address": settings.WALLET_MAIN, "reserve_size": 60},
                transient_retries=0,
            )
        except Exception:
            tpl = {}
    expected_atomic = 0
    if tpl:
        try:
            expected_atomic = int(tpl.get("expected_reward") or 0)
        except (TypeError, ValueError):
            expected_atomic = 0
    return {
        "height": height,
        "target_height": target,
        "difficulty": diff,
        "status": info.get("status"),
        "incoming_connections": info.get("incoming_connections_count"),
        "outgoing_connections": info.get("outgoing_connections_count"),
        "sync_lag_blocks": lag,
        "synchronized_flag": synced,
        "expected_reward_atomic": expected_atomic,
        "raw_info_subset": {
            k: info.get(k)
            for k in ("version", "offline", "nettype", "top_block_hash", "tx_count")
            if k in info
        },
    }
