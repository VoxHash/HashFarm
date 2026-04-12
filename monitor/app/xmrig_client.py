from __future__ import annotations

from typing import Any

import httpx

from . import settings


def _pick_hashrate_hs(summary: dict[str, Any]) -> float:
    hr = summary.get("hashrate") or {}
    total = hr.get("total")
    if isinstance(total, list) and total:
        try:
            return float(total[0] or 0)
        except (TypeError, ValueError):
            return 0.0
    if isinstance(total, (int, float)):
        return float(total)
    return 0.0


async def fetch_summary(client: httpx.AsyncClient, base_url: str) -> dict[str, Any]:
    base = base_url.rstrip("/")
    headers = {}
    if settings.XMRIG_API_TOKEN:
        headers["Authorization"] = f"Bearer {settings.XMRIG_API_TOKEN}"
    last_err: str | None = None
    for path in ("/2/summary", "/1/summary"):
        try:
            r = await client.get(f"{base}{path}", headers=headers, timeout=5.0)
            if r.status_code == 401:
                last_err = "unauthorized"
                continue
            r.raise_for_status()
            data = r.json()
            return {"path": path, "hashrate_hs": _pick_hashrate_hs(data), "raw": data}
        except Exception as e:
            last_err = str(e)
            continue
    return {"path": None, "hashrate_hs": 0.0, "error": last_err or "unavailable", "raw": {}}


async def fetch_all_rigs(client: httpx.AsyncClient) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for i, url in enumerate(settings.XMRIG_API_URLS):
        label = settings.XMRIG_RIG_LABELS[i] if i < len(settings.XMRIG_RIG_LABELS) else f"rig_{i}"
        row = await fetch_summary(client, url)
        row["label"] = label
        row["url"] = url
        watts = settings.WATTS[i] if i < len(settings.WATTS) else 0.0
        row["watts_assumed"] = watts
        out.append(row)
    return out
