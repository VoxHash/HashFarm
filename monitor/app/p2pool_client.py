from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

import httpx

from . import settings


def _stratum_bases() -> list[str]:
    primary = settings.P2POOL_STRATUM_URL.rstrip("/")
    bases = [primary]
    try:
        u = urlparse(primary)
        if u.hostname in ("localhost", "::1"):
            alt = primary.replace(f"{u.scheme}://{u.hostname}", f"{u.scheme}://127.0.0.1", 1)
            if alt not in bases:
                bases.append(alt)
    except Exception:
        pass
    return bases


async def _get_json(client: httpx.AsyncClient, base: str, path: str) -> dict[str, Any]:
    url = f"{base}{path}"
    r = await client.get(url, timeout=8.0)
    r.raise_for_status()
    return r.json()


async def fetch_p2pool(client: httpx.AsyncClient) -> dict[str, Any]:
    out: dict[str, Any] = {"stratum": None, "p2p": None, "error": None, "http_base": None}
    last_err: str | None = None
    base_ok: str | None = None
    for base in _stratum_bases():
        try:
            out["stratum"] = await _get_json(client, base, "/local/stratum")
            base_ok = base
            break
        except Exception as e:
            last_err = f"{base}/local/stratum: {e}"
    if base_ok is None and last_err:
        out["error"] = (
            f"P2Pool HTTP unreachable ({last_err}). "
            "Ensure P2Pool is running with --local-api and that nothing blocks port 3333. "
            "If this dashboard is not on the mining PC, set P2POOL_STRATUM_URL in .env to that machine's LAN IP."
        )
    if base_ok:
        out["http_base"] = base_ok
        try:
            out["p2p"] = await _get_json(client, base_ok, "/local/p2p")
        except Exception:
            out["p2p"] = None
    return out
