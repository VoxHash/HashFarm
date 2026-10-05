# Getting started

HashFarm helps you run a **self-hosted Monero P2Pool** layout: a pruned `monerod`, P2Pool v4, one or more XMRig miners, and a FastAPI monitor on the gaming PC.

## Who it is for

Home or lab operators who already understand Monero wallets and want LAN mining with clear sync/hashrate visibility—not a custodial pool or cloud miner.

## What you need

| Dependency | Role | Notes |
| ---------- | ---- | ----- |
| Linux (Garuda/Arch-like) or macOS (miners) | Host OS | Scripts under `scripts/garuda/` and `scripts/macos/` |
| `monerod` (Monero CLI or GUI bundle) | Full node | Must sync; pruned mode supported |
| P2Pool v4 | Decentralized pool | Installed via `scripts/garuda/p2pool-v4.sh` |
| XMRig 6.26.x | Miner | CPU default; CUDA optional |
| Python 3.11+ | Monitor | `monitor/requirements.txt` |
| Wallet primary address | Payouts | Set `WALLET_MAIN` in `.env` — never commit `.env` |

Optional: NVIDIA GPU + CUDA toolkit for [`cuda-mining.md`](cuda-mining.md); SMTP for alerts; systemd for boot persistence.

## Suggested order

1. [Installation](installation.md)
2. [Configuration](configuration.md)
3. [Quick start](quick-start.md) or [Usage](usage.md)
4. [Verify](cli.md#verify-stacksh) with `scripts/common/verify-stack.sh`

## Support

See [SUPPORT.md](../SUPPORT.md) or email [contact@voxhash.dev](mailto:contact@voxhash.dev).
