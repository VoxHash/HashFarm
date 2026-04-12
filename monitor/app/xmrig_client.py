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
    headers: dict[str, str] = {}
    token = (settings.XMRIG_API_TOKEN or "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    last_err: str | None = None
    for path in ("/2/summary", "/1/summary"):
        try:
            r = await client.get(f"{base}{path}", headers=headers, timeout=5.0)
            if r.status_code == 401:
                # XMRig returns 401 when access-token is set but Authorization is missing or invalid shape.
                if not token:
                    last_err = (
                        "401 UNAUTHORIZED: monitor has no XMRIG_API_TOKEN — set it in the gaming PC .env "
                        "to the same string as each XMRig config http.access-token (see monitor/README.md)"
                    )
                else:
                    last_err = (
                        "401 UNAUTHORIZED: XMRig did not accept the request (missing/invalid auth on its side). "
                        "Confirm http.access-token in this rig's config matches XMRIG_API_TOKEN and upgrade XMRig "
                        "if needed; wrong secrets normally return 403 on current XMRig."
                    )
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
