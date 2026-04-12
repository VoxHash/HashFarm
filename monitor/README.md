# HashFarm monitor (FastAPI)

Runs on the **gaming PC**. Polls `monerod`, P2Pool `/local/*` HTTP, each XMRig summary API, and CoinGecko for XMR/USD.

## Setup

From repository root:

```bash
cd monitor
python -m venv .venv
.venv/bin/pip install -r requirements.txt
cp ../scripts/common/env.template ../.env
# edit ../.env — set WALLET_MAIN, GAMING_PC_IP, XMRIG_API_URLS, tokens, SMTP, etc.
../scripts/garuda/run-monitor.sh
```

Open `http://127.0.0.1:8787/` (or your `MONITOR_BIND` / `MONITOR_PORT`).

Each rig URL in **`XMRIG_API_URLS`** must expose XMRig’s HTTP API with **`Authorization: Bearer <XMRIG_API_TOKEN>`** (see repo root `.env`). Prebuilt configs with the API disabled will not contribute hashrate to the dashboard.

### `401 UNAUTHORIZED` from XMRig

XMRig’s HTTP daemon returns **401** when **`http.access-token` is set** in the miner’s `config.json` but the client sends **no** `Authorization: Bearer …` header ([source: `Httpd::auth`](https://github.com/xmrig/xmrig/blob/master/src/base/api/Httpd.cpp)).

**Fix (most common):** On the **machine that runs the monitor**, set **`XMRIG_API_TOKEN`** in `.env` to the **exact same string** as `"access-token"` under `"http"` in **each** XMRig config you poll. HashFarm sends **one** token for every URL in `XMRIG_API_URLS`, so every rig must use that same secret (or remove `access-token` on miners you intentionally want open on localhost only).

Then regenerate or edit miner configs and restart XMRig, for example:

```bash
# On each Linux rig (from repo root after .env is correct)
./scripts/garuda/xmrig-cpu.sh config && ./scripts/garuda/xmrig-cpu.sh run
```

Quick check from the monitor host:

```bash
curl -sS -H "Authorization: Bearer YOUR_TOKEN" "http://RIG_IP:18060/2/summary" | head
```

## Browser devtools noise

Messages such as **SES Removing unpermitted intrinsics** or **`runtime.lastError: The message port closed before a response was received`** almost always come from **browser extensions** (wallets, script blockers, “security” injectors), not from this dashboard. Test in a clean profile or disable extensions if you need a quiet console.

## API

- `GET /` — HTML dashboard
- `GET /api/snapshot` — JSON for scripting
- `GET /health` — liveness (always `200` if the process is up)
- `GET /ready` — readiness (`503` until a recent collector snapshot exists; tune `READY_MAX_SNAPSHOT_AGE_SEC` in `.env`)
- `GET /metrics` — Prometheus text gauges from the latest snapshot (for scrapers)

## Time-series (SQLite)

When `METRICS_ENABLED=1` (default), each poll appends a row to `METRICS_SQLITE_PATH` (default under `monitor/data/`). Rows older than `METRICS_RETENTION_DAYS` are pruned automatically.

## Development / CI

```bash
cd monitor
python -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
HASHFARM_SKIP_LIFESPAN=1 .venv/bin/pytest -q   # conftest sets this by default
.venv/bin/ruff check .
```

`HASHFARM_SKIP_LIFESPAN` disables the background collector loop (used by pytest); do **not** set it in production.
