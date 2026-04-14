from __future__ import annotations

import time
from typing import Any

import httpx

from . import settings

_RIG_STATE: dict[str, dict[str, Any]] = {}


def _cap_at(vals: list[float], idx: int) -> float | None:
    if idx >= len(vals):
        return None
    v = float(vals[idx])
    return v if v > 0 else None


def _state_for(label: str) -> dict[str, Any]:
    if label not in _RIG_STATE:
        _RIG_STATE[label] = {
            "mode": "normal",
            "breach_since": None,
            "recover_since": None,
            "missing_since": None,
            "last_action_ts": 0.0,
            "last_action": None,
            "last_reason": None,
            "last_error": None,
        }
    return _RIG_STATE[label]


def _breach_reason(rig: dict[str, Any], idx: int) -> str | None:
    cpu_cap = _cap_at(settings.SAFETY_MAX_CPU_TEMP_C, idx)
    gpu_cap = _cap_at(settings.SAFETY_MAX_GPU_TEMP_C, idx)
    pwr_cap = _cap_at(settings.SAFETY_MAX_POWER_W, idx)
    cpu = rig.get("cpu_temp_c")
    gpu = rig.get("gpu_temp_c")
    pwr = rig.get("power_w")
    if cpu_cap is not None and isinstance(cpu, (int, float)) and float(cpu) > cpu_cap:
        return f"cpu_temp {cpu:.1f}C > cap {cpu_cap:.1f}C"
    if gpu_cap is not None and isinstance(gpu, (int, float)) and float(gpu) > gpu_cap:
        return f"gpu_temp {gpu:.1f}C > cap {gpu_cap:.1f}C"
    if pwr_cap is not None and isinstance(pwr, (int, float)) and float(pwr) > pwr_cap:
        return f"power {pwr:.1f}W > cap {pwr_cap:.1f}W"
    return None


async def _json_rpc(client: httpx.AsyncClient, base_url: str, method: str) -> None:
    headers = {"Content-Type": "application/json"}
    token = (settings.XMRIG_API_TOKEN or "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    payload = {"jsonrpc": "2.0", "id": "hashfarm", "method": method}
    r = await client.post(
        f"{base_url.rstrip('/')}/json_rpc",
        headers=headers,
        json=payload,
        timeout=float(settings.XMRIG_API_TIMEOUT_SEC),
    )
    r.raise_for_status()


async def _act(client: httpx.AsyncClient, rig: dict[str, Any], action: str, reason: str, st: dict[str, Any]) -> None:
    now = time.monotonic()
    if now - float(st["last_action_ts"] or 0.0) < float(settings.SAFETY_ACTION_COOLDOWN_SEC):
        return
    if settings.SAFETY_DRY_RUN or not settings.SAFETY_ENABLE_AUTOMATION:
        st["last_action_ts"] = now
        st["last_action"] = f"{action} (dry-run)"
        st["last_reason"] = reason
        st["last_error"] = None
        return
    method = "pause" if action == "reduce" else "resume"
    await _json_rpc(client, str(rig.get("url") or ""), method)
    st["last_action_ts"] = now
    st["last_action"] = action
    st["last_reason"] = reason
    st["last_error"] = None


async def apply_policy(client: httpx.AsyncClient, snap: dict[str, Any]) -> None:
    now = time.monotonic()
    reduced = 0
    actions: list[dict[str, str]] = []
    for idx, rig in enumerate(snap.get("rigs") or []):
        label = str(rig.get("label") or f"rig_{idx}")
        st = _state_for(label)
        missing = bool(rig.get("telemetry_stale")) or bool(rig.get("telemetry_error"))
        reason = _breach_reason(rig, idx)
        try:
            if st["mode"] == "normal":
                st["recover_since"] = None
                if missing:
                    st["missing_since"] = st["missing_since"] or now
                    if now - float(st["missing_since"]) >= float(settings.SAFETY_MISSING_TELEMETRY_CONSEC_SEC):
                        await _act(client, rig, "reduce", "telemetry missing too long", st)
                        st["mode"] = "reduced"
                        actions.append({"rig": label, "action": "reduce", "reason": "telemetry missing too long"})
                elif reason:
                    st["missing_since"] = None
                    st["breach_since"] = st["breach_since"] or now
                    if now - float(st["breach_since"]) >= float(settings.SAFETY_BREACH_CONSEC_SEC):
                        await _act(client, rig, "reduce", reason, st)
                        st["mode"] = "reduced"
                        actions.append({"rig": label, "action": "reduce", "reason": reason})
                else:
                    st["missing_since"] = None
                    st["breach_since"] = None
            else:
                reduced += 1
                if missing or reason:
                    st["recover_since"] = None
                else:
                    st["recover_since"] = st["recover_since"] or now
                    if now - float(st["recover_since"]) >= float(settings.SAFETY_RECOVERY_CONSEC_SEC):
                        await _act(client, rig, "restore", "telemetry recovered and under caps", st)
                        st["mode"] = "normal"
                        st["breach_since"] = None
                        st["missing_since"] = None
                        actions.append({"rig": label, "action": "restore", "reason": "recovered"})
        except Exception as e:
            st["last_error"] = str(e)
        rig["safety_mode"] = st["mode"]
        rig["safety_last_action"] = st["last_action"]
        rig["safety_last_reason"] = st["last_reason"]
        rig["safety_error"] = st["last_error"]
    snap["safety"] = {
        "enabled": settings.SAFETY_ENABLE_AUTOMATION,
        "dry_run": settings.SAFETY_DRY_RUN,
        "reduced_rigs": reduced,
        "actions": actions,
    }
