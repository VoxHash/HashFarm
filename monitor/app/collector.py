from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlparse

import httpx

from . import earnings, monero_rpc, p2pool_client, settings, state, xmrig_client


def _annotate_p2pool_stratum_vs_sync(monero: dict[str, Any], p2: dict[str, Any]) -> None:
    """P2Pool often does not listen on :3333 until monerod is healthy; explain vs wrong URL / LAN."""
    if not p2.get("error"):
        return
    parts: list[str] = [str(p2["error"])]
    err_p2_l = parts[0].lower()
    u = urlparse(settings.P2POOL_STRATUM_URL)
    port = u.port or 3333

    if monero.get("_error"):
        refused = (
            "connection refused" in err_p2_l
            or "all connection attempts failed" in err_p2_l
            or "connecterror" in err_p2_l
            or "actively refused" in err_p2_l
        )
        if refused:
            p2["stratum_pending_sync"] = True
        parts.append(
            "P2Pool uses the same monerod as this dashboard. When JSON-RPC to monerod times out or fails, "
            "P2Pool may also stall and stratum HTTP on this host often stays closed—that is not fixed by "
            "changing P2POOL_STRATUM_URL on localhost. Restore monerod responsiveness first (check bitmonero.log, "
            "disk load, and optional monerod tuning such as --max-concurrency), then stratum should open once the node is healthy."
        )

    th = int(monero.get("target_height") or 0)
    h = int(monero.get("height") or 0)
    if th > 0 and h > 0:
        behind = max(0, th - h)
        if behind > settings.MONERO_MAX_SYNC_LAG_BLOCKS:
            p2["stratum_pending_sync"] = True
            parts.append(
                f"P2Pool typically does not open stratum HTTP on port {port} while monerod is still catching up "
                f"(~{behind:,} blocks behind the network). The `p2pool` process may still be running and logging "
                "\"not synchronized\" / \"busy syncing\". This is not a wrong LAN IP on the mining PC—wait for "
                "`monerod` to finish syncing, then `/local/stratum` should respond."
            )

    p2["error"] = " ".join(parts)


async def _xmr_spot_usd(client: httpx.AsyncClient) -> float | None:
    try:
        r = await client.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "monero", "vs_currencies": "usd"},
            timeout=10.0,
        )
        r.raise_for_status()
        data = r.json()
        v = data.get("monero", {}).get("usd")
        return float(v) if v is not None else None
    except Exception:
        return None


async def build_snapshot(client: httpx.AsyncClient) -> dict[str, Any]:
    snap: dict[str, Any] = {"updated_at": datetime.now(UTC).isoformat()}
    snap["endpoints"] = {
        "monero_rpc": settings.MONERO_RPC_URL,
        "p2pool_http": settings.P2POOL_STRATUM_URL,
    }
    monero: dict[str, Any] = {}
    try:
        monero = await monero_rpc.fetch_daemon_snapshot(client)
        state.record_last_good_monero(monero)
    except Exception as e:
        monero = state.merge_stale_monero(state.monero_collector_failure(str(e)))
    snap["monero"] = monero

    p2 = await p2pool_client.fetch_p2pool(client)
    _annotate_p2pool_stratum_vs_sync(monero, p2)
    snap["p2pool"] = p2

    rigs = await xmrig_client.fetch_all_rigs(client)
    snap["rigs"] = rigs
    agg = sum(float(r.get("hashrate_hs") or 0.0) for r in rigs)
    snap["aggregate_hashrate_hs"] = agg

    diff = float(monero.get("difficulty") or 0.0)
    atomic = int(monero.get("expected_reward_atomic") or 0)
    snap["estimated_mainchain_solo_xmr_per_day"] = earnings.estimate_mainchain_solo_xmr_per_day(
        agg, diff, atomic, settings.BLOCK_TIME_SEC
    )

    tw = sum(float(r.get("watts_assumed") or 0.0) for r in rigs)
    snap["total_watts"] = tw
    snap["daily_power_usd"] = earnings.daily_power_cost_usd(tw, settings.ELECTRICITY_USD_PER_KWH)
    snap["xmr_usd"] = await _xmr_spot_usd(client)
    snap["net_usd_per_day"] = earnings.net_usd_per_day(
        snap["estimated_mainchain_solo_xmr_per_day"],
        snap["xmr_usd"],
        snap["daily_power_usd"],
    )
    snap["wallet_main"] = settings.WALLET_MAIN
    snap["last_error"] = None
    return snap
