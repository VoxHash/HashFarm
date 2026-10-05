# Quick start

End-to-end path on the **gaming PC** after cloning [VoxHash/HashFarm](https://github.com/VoxHash/HashFarm).

## 1. Configure

```bash
cp scripts/common/env.template .env
```

Edit `.env` and set at least:

- `WALLET_MAIN` — your mainnet primary address
- `GAMING_PC_IP` — this machine’s LAN IP
- `XMRIG_API_URLS` — e.g. `http://<LAN_IP>:18060`
- `XMRIG_API_TOKEN` — long random secret (same value in every miner config)

## 2. Node and pool

```bash
# monerod on PATH, or set MONEROD_BIN in .env
./scripts/garuda/monerod-pruned.sh

# first time: install; then run
./scripts/garuda/p2pool-v4.sh install
./scripts/garuda/p2pool-v4.sh run
```

Wait until `monerod` is near network height. Confirm stratum: `ss -tlnp | grep 3333`.

## 3. Miner

```bash
./scripts/garuda/xmrig-cpu.sh config
./scripts/garuda/xmrig-cpu.sh run
```

## 4. Monitor

```bash
cd monitor
python -m venv .venv
.venv/bin/pip install -r requirements.txt
../scripts/garuda/run-monitor.sh
```

Open `http://127.0.0.1:8787/` (or your `MONITOR_BIND` / `MONITOR_PORT`).

## 5. Verify

```bash
./scripts/common/verify-stack.sh
```

Expect JSON from `monerod` `get_info`, P2Pool `/local/stratum`, and XMRig `/2/summary` (or `/1/summary`).

## Next

- Multi-rig LAN: [examples/example-02.md](examples/example-02.md)
- CUDA: [cuda-mining.md](cuda-mining.md)
- Firewall: [../deploy/FIREWALL.md](../deploy/FIREWALL.md)
