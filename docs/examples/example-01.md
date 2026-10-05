# Example 01 — Single PC CPU stack

Run pruned `monerod`, P2Pool, one XMRig, and the monitor on the same Linux gaming PC.

## 1. Environment

```bash
cp scripts/common/env.template .env
```

Set real values (illustrative LAN layout):

```bash
WALLET_MAIN=<your_mainnet_primary_address>
GAMING_PC_IP=192.168.68.10
P2POOL_STRATUM_PORT=3333
XMRIG_API_URLS=http://192.168.68.10:18060
XMRIG_API_TOKEN=<long_random_secret>
XMRIG_RIG_LABELS=gaming_pc
WATTS_GAMING_PC=350
ELECTRICITY_USD_PER_KWH=0.12
MONITOR_PORT=8787
```

## 2. Start stack

```bash
./scripts/garuda/monerod-pruned.sh
./scripts/garuda/p2pool-v4.sh install   # once
./scripts/garuda/p2pool-v4.sh run
./scripts/garuda/xmrig-cpu.sh config
./scripts/garuda/xmrig-cpu.sh run
```

## 3. Monitor

```bash
cd monitor
python -m venv .venv
.venv/bin/pip install -r requirements.txt
../scripts/garuda/run-monitor.sh
```

Open `http://127.0.0.1:8787/`. Confirm `/health` → `{"status":"ok"}` and `/api/snapshot` shows non-error Monero fields once synced.

## 4. Verify

```bash
./scripts/common/verify-stack.sh
```

You should see height/target from `monerod`, stratum JSON from P2Pool, and a positive aggregate hashrate once XMRig is hashing.
