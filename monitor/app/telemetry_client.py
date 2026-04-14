from __future__ import annotations

from typing import Any
import time

import httpx

from . import settings

_LAST_GOOD: dict[int, dict[str, Any]] = {}


def _walk(obj: Any, out: dict[str, float]) -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            lk = str(k).lower()
            if isinstance(v, (int, float)):
                out[lk] = float(v)
            else:
                _walk(v, out)
    elif isinstance(obj, list):
        for item in obj:
            _walk(item, out)


def _extract_metrics(data: dict[str, Any]) -> dict[str, Any]:
    flat: dict[str, float] = {}
    _walk(data, flat)
    cpu = flat.get("cpu_temp_c")
    if cpu is None:
        cpu = flat.get("cpu_temp")
    if cpu is None:
        cpu = flat.get("temperature_cpu")
    gpu = flat.get("gpu_temp_c")
    if gpu is None:
        gpu = flat.get("gpu_temp")
    if gpu is None:
        gpu = flat.get("temperature_gpu")
    power = flat.get("power_w")
    if power is None:
        power = flat.get("power")
    return {"cpu_temp_c": cpu, "gpu_temp_c": gpu, "power_w": power}


async def fetch_for_rig(client: httpx.AsyncClient, idx: int) -> dict[str, Any]:
    if idx >= len(settings.RIG_TELEMETRY_URLS):
        return {"available": False, "stale": True, "error": "telemetry url not configured"}
    url = settings.RIG_TELEMETRY_URLS[idx].rstrip("/")
    headers: dict[str, str] = {}
    token = (settings.RIG_TELEMETRY_TOKEN or "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        r = await client.get(url, headers=headers, timeout=float(settings.RIG_TELEMETRY_TIMEOUT_SEC))
        r.raise_for_status()
        data = r.json()
        m = _extract_metrics(data if isinstance(data, dict) else {"raw": data})
        got_any = any(m.get(k) is not None for k in ("cpu_temp_c", "gpu_temp_c", "power_w"))
        now = time.monotonic()
        if got_any:
            _LAST_GOOD[idx] = {"ts": now, "metrics": dict(m)}
        return {
            "available": got_any,
            "stale": not got_any,
            "source_url": url,
            "error": None if got_any else "telemetry payload missing cpu/gpu temp and power fields",
            "age_sec": 0.0 if got_any else None,
            **m,
        }
    except Exception as e:
        prev = _LAST_GOOD.get(idx)
        if prev:
            age = max(0.0, time.monotonic() - float(prev.get("ts") or 0.0))
            metrics = dict(prev.get("metrics") or {})
            stale = age > float(settings.RIG_TELEMETRY_STALE_SEC)
            return {
                "available": True,
                "stale": stale,
                "source_url": url,
                "age_sec": age,
                "error": str(e) if stale else None,
                **metrics,
            }
        return {"available": False, "stale": True, "source_url": url, "age_sec": None, "error": str(e)}
