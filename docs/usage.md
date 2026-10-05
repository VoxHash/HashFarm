# Usage

## Daily operator loop

1. Confirm `monerod` is running and syncing (`./scripts/common/verify-stack.sh` or monitor dashboard).
2. Confirm P2Pool stratum is bound (`ss -tlnp | grep 3333`) after the node is healthy.
3. Keep XMRig configs regenerated after `.env` changes: `./scripts/garuda/xmrig-cpu.sh config` then `run`.
4. Leave the monitor up (`./scripts/garuda/run-monitor.sh` or a systemd unit).

## Starting components

| Step | Command |
| ---- | ------- |
| Node | `./scripts/garuda/monerod-pruned.sh` |
| Pool install | `./scripts/garuda/p2pool-v4.sh install` |
| Pool run | `./scripts/garuda/p2pool-v4.sh run` |
| Miner config/run | `./scripts/garuda/xmrig-cpu.sh config` / `run` |
| macOS miner | `./scripts/macos/xmrig-m1.sh config` / `run` |
| Monitor | `./scripts/garuda/run-monitor.sh` |
| Verify | `./scripts/common/verify-stack.sh` |

## Reading the monitor

- Browser: `http://127.0.0.1:8787/` (or `MONITOR_PORT`)
- JSON: `GET /api/snapshot`
- Probes: `GET /health`, `GET /ready`
- Scrapers: `GET /metrics`

Hashrate stays at zero if XMRig HTTP API is disabled or the token mismatches—see [troubleshooting.md](troubleshooting.md).

## LAN miners

Point remote XMRig at `stratum+tcp://<GAMING_PC_IP>:3333`. Open TCP 3333 only for your LAN ([`deploy/FIREWALL.md`](../deploy/FIREWALL.md)). Use a unique `XMRIG_API_PORT` / rig id per machine and list every API URL in `XMRIG_API_URLS`.

## CUDA

Build `libxmrig-cuda.so` with `scripts/garuda/build-xmrig-cuda.sh`, set `XMRIG_ENABLE_CUDA=1`, regenerate config. Details: [cuda-mining.md](cuda-mining.md).
