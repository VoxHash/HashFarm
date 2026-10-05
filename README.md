# HashFarm

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/VoxHash/HashFarm/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/VoxHash/HashFarm/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/VoxHash/HashFarm)](https://github.com/VoxHash/HashFarm/releases)
[![GitHub](https://img.shields.io/badge/GitHub-VoxHash%2FHashFarm-181717?logo=github)](https://github.com/VoxHash/HashFarm)

**VoxHash Technologies** — Monero **P2Pool** mining stack for a PC (pruned `monerod` + P2Pool + optional local XMRig) with additional **XMRig** rigs (Laptop, macOS Apple Silicon) and a **FastAPI** monitor on the PC.

## Features

- Pruned `monerod` launcher with optional data-dir and block-sync tuning for slow disks
- P2Pool v4 install/run with LAN stratum (`0.0.0.0:3333` by default) and firewall guidance
- XMRig helpers for Linux and Apple Silicon, optional NVIDIA CUDA plugin build
- Live FastAPI dashboard: sync lag, pool health, per-rig hashrate, profitability hints
- `/health`, `/ready`, Prometheus `/metrics`, and SQLite poll history
- CI: `ruff`, `pytest`, `shellcheck`

## Quick start

```bash
git clone https://github.com/VoxHash/HashFarm.git
cd HashFarm
cp scripts/common/env.template .env
# edit .env — WALLET_MAIN, GAMING_PC_IP, XMRIG_API_URLS, XMRIG_API_TOKEN, power numbers

# Gaming PC (after monerod + P2Pool are installed):
./scripts/garuda/monerod-pruned.sh
./scripts/garuda/p2pool-v4.sh run
./scripts/garuda/xmrig-cpu.sh run

cd monitor && python -m venv .venv && .venv/bin/pip install -r requirements.txt
../scripts/garuda/run-monitor.sh
# open http://127.0.0.1:8787/
```

Full path: [docs/quick-start.md](docs/quick-start.md) · install details: [docs/installation.md](docs/installation.md).

## Configuration

Copy [`scripts/common/env.template`](scripts/common/env.template) to `.env` at the repository root. Required operator values:

| Variable | Purpose |
| -------- | ------- |
| `WALLET_MAIN` | Mainnet primary address for P2Pool / XMRig user |
| `GAMING_PC_IP` | LAN IP of the node hosting P2Pool stratum |
| `XMRIG_API_URLS` | Comma-separated XMRig HTTP API base URLs |
| `XMRIG_API_TOKEN` | Bearer token matching each miner’s `http.access-token` |
| `MONERO_RPC_URL` | Local `monerod` JSON-RPC (default `http://127.0.0.1:18081/json_rpc`) |
| `P2POOL_STRATUM_URL` | Local P2Pool HTTP (default `http://127.0.0.1:3333`) |

See [docs/configuration.md](docs/configuration.md) for the full table (timeouts, metrics, SMTP, CUDA, safety caps).

## Usage

1. **PC:** run `monerod` → P2Pool → XMRig (scripts under [`scripts/garuda/`](scripts/garuda/)).
2. **Other rigs:** [`scripts/garuda/xmrig-cpu.sh`](scripts/garuda/xmrig-cpu.sh) / [`scripts/macos/xmrig-m1.sh`](scripts/macos/xmrig-m1.sh) with distinct `XMRIG_RIG_ID` / `XMRIG_API_PORT`.
3. **Checks:** [`scripts/common/verify-stack.sh`](scripts/common/verify-stack.sh).
4. **Monitor:** [`monitor/README.md`](monitor/README.md); systemd under [`deploy/systemd/`](deploy/systemd/); firewall in [`deploy/FIREWALL.md`](deploy/FIREWALL.md).

### Fixed difficulty

Set `P2POOL_NO_AUTODIFF=1` in `.env`, run P2Pool via `scripts/garuda/p2pool-v4.sh run`. Set `FIXED_DIFF` and regenerate XMRig configs so the pool user is `WALLET+FIXED_DIFF`.

### LAN stratum and firewall

P2Pool defaults to **`--stratum 0.0.0.0:3333`** (override with **`P2POOL_STRATUM_BIND`**). Open **TCP 3333** only from your LAN — see [`deploy/FIREWALL.md`](deploy/FIREWALL.md). Confirm with `ss -tlnp | grep 3333` after `monerod` is synchronized.

### CUDA / GPU mining

CPU-only by default. For NVIDIA RandomX see [`docs/cuda-mining.md`](docs/cuda-mining.md) and `scripts/garuda/build-xmrig-cuda.sh`.

## Development / tests

```bash
cd monitor
python -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/ruff check .
HASHFARM_SKIP_LIFESPAN=1 .venv/bin/pytest -q
```

## Community

- [Docs index](docs/index.md) · [Contributing](CONTRIBUTING.md) · [Architecture](docs/architecture.md) · [Roadmap](ROADMAP.md) · [Changelog](CHANGELOG.md)
- [Code of Conduct](CODE_OF_CONDUCT.md) · [Security](SECURITY.md) · [Support](SUPPORT.md)
- Contact: [contact@voxhash.dev](mailto:contact@voxhash.dev)

## License

MIT — see [LICENSE](LICENSE).
