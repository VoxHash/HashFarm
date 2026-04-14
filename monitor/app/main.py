from __future__ import annotations

import asyncio
import os
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates

from . import alerts, collector, metrics, safety_controller, settings, state

_templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


def _snapshot_age_seconds() -> float | None:
    ua = state.SNAPSHOT.get("updated_at")
    if not ua or not isinstance(ua, str):
        return None
    try:
        raw = ua.replace("Z", "+00:00") if ua.endswith("Z") else ua
        dt = datetime.fromisoformat(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return (datetime.now(UTC) - dt).total_seconds()
    except ValueError:
        return None


async def _record_metrics_row(snap: dict[str, Any]) -> None:
    if not settings.METRICS_ENABLED:
        return
    await asyncio.to_thread(
        metrics.record_snapshot,
        settings.METRICS_SQLITE_PATH,
        snap,
        settings.METRICS_RETENTION_DAYS,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.getenv("HASHFARM_SKIP_LIFESPAN", "").lower() in ("1", "true", "yes"):
        yield
        return

    stop = asyncio.Event()

    async def loop() -> None:
        # trust_env=False avoids broken localhost polling when HTTP(S)_PROXY is set.
        async with httpx.AsyncClient(trust_env=False) as client:
            while not stop.is_set():
                try:
                    snap = await collector.build_snapshot(client)
                    await safety_controller.apply_policy(client, snap)
                    state.apply_snapshot(snap)
                    await _record_metrics_row(snap)
                    await alerts.evaluate(snap)
                except Exception as e:
                    fail_snap = {
                        "updated_at": None,
                        "last_error": str(e),
                        "monero": state.monero_collector_failure(str(e)),
                    }
                    state.apply_snapshot(fail_snap)
                    await _record_metrics_row(fail_snap)
                try:
                    await asyncio.wait_for(stop.wait(), timeout=settings.POLL_INTERVAL_SEC)
                except TimeoutError:
                    continue

    task = asyncio.create_task(loop())
    yield
    stop.set()
    await task


app = FastAPI(title="HashFarm P2Pool Monitor", lifespan=lifespan)


@app.get("/health")
async def health() -> JSONResponse:
    """Liveness: process is up (does not check upstream daemons)."""
    return JSONResponse({"status": "ok"})


@app.get("/ready")
async def ready() -> JSONResponse:
    """Readiness: a collector snapshot exists and is recent enough for orchestration probes."""
    age = _snapshot_age_seconds()
    if age is None or age > float(settings.READY_MAX_SNAPSHOT_AGE_SEC):
        return JSONResponse(
            {
                "ready": False,
                "reason": "no_recent_snapshot",
                "snapshot_age_seconds": age,
                "max_age_seconds": settings.READY_MAX_SNAPSHOT_AGE_SEC,
            },
            status_code=503,
        )
    return JSONResponse({"ready": True, "snapshot_age_seconds": age})


@app.get("/metrics", response_class=PlainTextResponse)
async def prometheus_metrics() -> PlainTextResponse:
    """Prometheus-compatible gauges from the latest in-memory snapshot."""
    body = metrics.prometheus_text(dict(state.SNAPSHOT))
    return PlainTextResponse(body, media_type="text/plain; version=0.0.4; charset=utf-8")


@app.get("/api/snapshot")
async def api_snapshot() -> JSONResponse:
    return JSONResponse(dict(state.SNAPSHOT))


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request) -> HTMLResponse:
    return _templates.TemplateResponse(
        request,
        "dashboard.html",
        {"snap": dict(state.SNAPSHOT), "settings": settings},
    )
