from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from . import alerts, collector, settings, state

_templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    stop = asyncio.Event()

    async def loop() -> None:
        # trust_env=False avoids broken localhost polling when HTTP(S)_PROXY is set.
        async with httpx.AsyncClient(trust_env=False) as client:
            while not stop.is_set():
                try:
                    snap = await collector.build_snapshot(client)
                    state.apply_snapshot(snap)
                    await alerts.evaluate(snap)
                except Exception as e:
                    state.apply_snapshot(
                        {
                            "updated_at": None,
                            "last_error": str(e),
                            "monero": state.monero_collector_failure(str(e)),
                        }
                    )
                try:
                    await asyncio.wait_for(stop.wait(), timeout=settings.POLL_INTERVAL_SEC)
                except asyncio.TimeoutError:
                    continue

    task = asyncio.create_task(loop())
    yield
    stop.set()
    await task


app = FastAPI(title="HashFarm P2Pool Monitor", lifespan=lifespan)


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
