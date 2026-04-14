from __future__ import annotations

import asyncio

from app import safety_controller, settings


def test_reduce_on_sustained_breach_then_restore(monkeypatch) -> None:
    safety_controller._RIG_STATE.clear()  # type: ignore[attr-defined]
    actions: list[tuple[str, str]] = []

    async def fake_json_rpc(_client, base_url: str, method: str) -> None:
        actions.append((base_url, method))

    monkeypatch.setattr(safety_controller, "_json_rpc", fake_json_rpc)
    monkeypatch.setattr(settings, "SAFETY_ENABLE_AUTOMATION", True)
    monkeypatch.setattr(settings, "SAFETY_DRY_RUN", False)
    monkeypatch.setattr(settings, "SAFETY_BREACH_CONSEC_SEC", 0)
    monkeypatch.setattr(settings, "SAFETY_RECOVERY_CONSEC_SEC", 0)
    monkeypatch.setattr(settings, "SAFETY_ACTION_COOLDOWN_SEC", 0)
    monkeypatch.setattr(settings, "SAFETY_MISSING_TELEMETRY_CONSEC_SEC", 999999)
    monkeypatch.setattr(settings, "SAFETY_MAX_CPU_TEMP_C", [80.0])
    monkeypatch.setattr(settings, "SAFETY_MAX_GPU_TEMP_C", [])
    monkeypatch.setattr(settings, "SAFETY_MAX_POWER_W", [])

    snap = {
        "rigs": [
            {
                "label": "rig_a",
                "url": "http://127.0.0.1:18060",
                "cpu_temp_c": 90.0,
                "telemetry_stale": False,
                "telemetry_error": None,
            }
        ]
    }
    asyncio.run(safety_controller.apply_policy(None, snap))  # type: ignore[arg-type]
    assert actions == [("http://127.0.0.1:18060", "pause")]
    assert snap["rigs"][0]["safety_mode"] == "reduced"

    snap["rigs"][0]["cpu_temp_c"] = 60.0
    asyncio.run(safety_controller.apply_policy(None, snap))  # type: ignore[arg-type]
    assert actions[-1] == ("http://127.0.0.1:18060", "resume")
    assert snap["rigs"][0]["safety_mode"] == "normal"


def test_reduce_on_missing_telemetry(monkeypatch) -> None:
    safety_controller._RIG_STATE.clear()  # type: ignore[attr-defined]
    monkeypatch.setattr(settings, "SAFETY_ENABLE_AUTOMATION", True)
    monkeypatch.setattr(settings, "SAFETY_DRY_RUN", True)
    monkeypatch.setattr(settings, "SAFETY_BREACH_CONSEC_SEC", 999999)
    monkeypatch.setattr(settings, "SAFETY_RECOVERY_CONSEC_SEC", 999999)
    monkeypatch.setattr(settings, "SAFETY_ACTION_COOLDOWN_SEC", 0)
    monkeypatch.setattr(settings, "SAFETY_MISSING_TELEMETRY_CONSEC_SEC", 0)
    monkeypatch.setattr(settings, "SAFETY_MAX_CPU_TEMP_C", [])
    monkeypatch.setattr(settings, "SAFETY_MAX_GPU_TEMP_C", [])
    monkeypatch.setattr(settings, "SAFETY_MAX_POWER_W", [])

    snap = {
        "rigs": [
            {
                "label": "rig_missing",
                "url": "http://127.0.0.1:18061",
                "telemetry_stale": True,
                "telemetry_error": "timeout",
            }
        ]
    }
    asyncio.run(safety_controller.apply_policy(None, snap))  # type: ignore[arg-type]
    assert snap["rigs"][0]["safety_mode"] == "reduced"
    assert "dry-run" in str(snap["rigs"][0]["safety_last_action"])
