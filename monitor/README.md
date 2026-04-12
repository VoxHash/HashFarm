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

## Browser devtools noise

Messages such as **SES Removing unpermitted intrinsics** or **`runtime.lastError: The message port closed before a response was received`** almost always come from **browser extensions** (wallets, script blockers, “security” injectors), not from this dashboard. Test in a clean profile or disable extensions if you need a quiet console.

## API

- `GET /` — HTML dashboard
- `GET /api/snapshot` — JSON for scripting
