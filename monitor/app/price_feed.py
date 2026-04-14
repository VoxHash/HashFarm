from __future__ import annotations

import time
from typing import Any

import httpx

from . import settings

_CACHE: dict[str, Any] = {
    "price": None,
    "source": None,
    "updated_at_monotonic": 0.0,
    "last_error": None,
}


def _cache_age_sec(now: float) -> float | None:
    ts = float(_CACHE.get("updated_at_monotonic") or 0.0)
    if ts <= 0:
        return None
    return max(0.0, now - ts)


def _cache_valid(now: float) -> bool:
    age = _cache_age_sec(now)
    if age is None:
        return False
    return age <= float(settings.XMR_USD_CACHE_TTL_SEC)


async def _from_coingecko(client: httpx.AsyncClient, timeout_sec: float) -> float:
    r = await client.get(
        "https://api.coingecko.com/api/v3/simple/price",
        params={"ids": "monero", "vs_currencies": "usd"},
        timeout=timeout_sec,
    )
    r.raise_for_status()
    data = r.json()
    v = data.get("monero", {}).get("usd")
    if v is None:
        raise ValueError("coingecko: missing monero.usd")
    return float(v)


async def _from_kraken(client: httpx.AsyncClient, timeout_sec: float) -> float:
    r = await client.get(
        "https://api.kraken.com/0/public/Ticker",
        params={"pair": "XMRUSD"},
        timeout=timeout_sec,
    )
    r.raise_for_status()
    data = r.json()
    if data.get("error"):
        raise ValueError(f"kraken: {data.get('error')}")
    result = data.get("result") or {}
    if not result:
        raise ValueError("kraken: empty result")
    first = next(iter(result.values()))
    close = (first or {}).get("c") or []
    if not close:
        raise ValueError("kraken: missing close")
    return float(close[0])


async def _from_cryptocompare(client: httpx.AsyncClient, timeout_sec: float) -> float:
    r = await client.get(
        "https://min-api.cryptocompare.com/data/price",
        params={"fsym": "XMR", "tsyms": "USD"},
        timeout=timeout_sec,
    )
    r.raise_for_status()
    data = r.json()
    v = data.get("USD")
    if v is None:
        raise ValueError("cryptocompare: missing USD")
    return float(v)


_PROVIDERS: dict[str, Any] = {
    "coingecko": _from_coingecko,
    "kraken": _from_kraken,
    "cryptocompare": _from_cryptocompare,
}


async def get_xmr_usd(client: httpx.AsyncClient) -> dict[str, Any]:
    now = time.monotonic()
    age = _cache_age_sec(now)
    if _cache_valid(now):
        return {
            "price": _CACHE["price"],
            "source": _CACHE["source"],
            "cached": True,
            "age_sec": age,
            "error": None,
        }

    timeout_sec = float(settings.XMR_USD_SOURCE_TIMEOUT_SEC)
    errors: list[str] = []
    for source in settings.XMR_USD_SOURCES:
        fn = _PROVIDERS.get(source)
        if fn is None:
            errors.append(f"{source}: unsupported source")
            continue
        try:
            price = float(await fn(client, timeout_sec))
            _CACHE["price"] = price
            _CACHE["source"] = source
            _CACHE["updated_at_monotonic"] = now
            _CACHE["last_error"] = None
            return {
                "price": price,
                "source": source,
                "cached": False,
                "age_sec": 0.0,
                "error": None,
            }
        except Exception as e:
            errors.append(f"{source}: {e}")

    if _CACHE.get("price") is not None and _cache_valid(now):
        return {
            "price": _CACHE["price"],
            "source": _CACHE["source"],
            "cached": True,
            "age_sec": _cache_age_sec(now),
            "error": "; ".join(errors) if errors else "all price sources failed",
        }

    _CACHE["last_error"] = "; ".join(errors) if errors else "all price sources failed"
    return {
        "price": None,
        "source": None,
        "cached": False,
        "age_sec": age,
        "error": _CACHE["last_error"],
    }
