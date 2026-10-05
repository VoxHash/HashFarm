# CLI reference

All scripts expect a repository-root **`.env`** (from `scripts/common/env.template`) unless noted. They use `set -euo pipefail` and exit non-zero on missing config.

## `scripts/common/verify-stack.sh`

Read-only health check: `monerod` `get_info`, P2Pool `/local/stratum`, each XMRig summary API, aggregate hashrate.

```bash
./scripts/common/verify-stack.sh
```

Fails if `.env` is missing or required vars are unset.

## `scripts/garuda/monerod-pruned.sh`

Starts pruned `monerod` with RPC/ZMQ settings for P2Pool. Uses `MONEROD_BIN` when `monerod` is not on `PATH`. Honors `MONERO_DATA_DIR` and optional `MONERO_BLOCK_SYNC_SIZE`.

```bash
./scripts/garuda/monerod-pruned.sh
```

## `scripts/garuda/p2pool-v4.sh`

| Subcommand | Action |
| ---------- | ------ |
| `install` | Download/install official P2Pool v4 Linux build |
| `run` | Start P2Pool against local `monerod` (stratum bind from env) |

```bash
./scripts/garuda/p2pool-v4.sh install
./scripts/garuda/p2pool-v4.sh run
```

Requires `WALLET_MAIN`. Passes `--no-autodiff` when `P2POOL_NO_AUTODIFF=1`.

## `scripts/garuda/xmrig-cpu.sh`

| Subcommand | Action |
| ---------- | ------ |
| `build` | Build/install XMRig to `~/.local/bin/xmrig` (typical) |
| `config` | Write JSON for P2Pool + HTTP API |
| `run` | Regenerate config and start miner |

```bash
./scripts/garuda/xmrig-cpu.sh config
./scripts/garuda/xmrig-cpu.sh run
```

Respects `XMRIG_BINARY`, `XMRIG_ENABLE_CUDA`, API port/token from `.env`.

## `scripts/garuda/build-xmrig-cuda.sh`

Builds `libxmrig-cuda.so` from `xmrig-cuda` (default tag `v6.22.1`). Set `XMRIG_CUDA_ARCH` (e.g. `86`). See [cuda-mining.md](cuda-mining.md).

```bash
./scripts/garuda/build-xmrig-cuda.sh
```

## `scripts/garuda/run-monitor.sh`

Loads `.env`, requires `monitor/.venv` with uvicorn, binds `MONITOR_BIND`:`MONITOR_PORT`.

```bash
./scripts/garuda/run-monitor.sh
```

## `scripts/macos/xmrig-m1.sh`

Apple Silicon counterpart to `xmrig-cpu.sh` (`build` / `config` / `run`). Same `.env` contract for wallet, stratum, and API token.
