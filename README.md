# HashFarm

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/VoxHash-Labs/HashFarm/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/VoxHash-Labs/HashFarm/actions/workflows/ci.yml)
[![GitHub](https://img.shields.io/badge/GitHub-VoxHash%2FHashFarm-181717?logo=github)](https://github.com/VoxHash/HashFarm)

Monero **P2Pool** mining stack for a PC (pruned `monerod` + P2Pool + optional local XMRig) with additional **XMRig** rigs (Laptop, macOS Apple Silicon) and a **FastAPI** monitor on the PC.

## Quick path

1. Copy [`scripts/common/env.template`](scripts/common/env.template) to `.env` at the repository root and set your wallet, LAN IP, API URLs, power numbers, and optional SMTP.
2. **PC (Garuda):** run `monerod` → install/run P2Pool → run XMRig (see [`monitor/README.md`](monitor/README.md) and shell scripts under [`scripts/garuda/`](scripts/garuda/)).
3. **Other rigs:** [`scripts/garuda/xmrig-cpu.sh`](scripts/garuda/xmrig-cpu.sh) (laptop) and [`scripts/macos/xmrig-m1.sh`](scripts/macos/xmrig-m1.sh) (M1) with distinct `XMRIG_RIG_ID` / `XMRIG_API_PORT` per machine.
4. Stack checks: [`scripts/common/verify-stack.sh`](scripts/common/verify-stack.sh).
5. Monitor: [`monitor/README.md`](monitor/README.md); optional **systemd** units under [`deploy/systemd/`](deploy/systemd/) and firewall notes in [`deploy/FIREWALL.md`](deploy/FIREWALL.md).

## Fixed difficulty

Set `P2POOL_NO_AUTODIFF=1` in `.env`, run P2Pool via `scripts/garuda/p2pool-v4.sh run` (script passes `--no-autodiff` when set). Set `FIXED_DIFF` and regenerate XMRig configs so the pool user is `WALLET+FIXED_DIFF`.

## P2Pool “connection refused” on :3333

If `monerod` is still syncing, P2Pool often **does not bind** the stratum HTTP port yet (`ss` shows nothing on `3333` even when `pgrep p2pool` is running). That is normal. Wait until chain height is near the network target and `logs/p2pool.log` shows a healthy connection; then `curl http://127.0.0.1:3333/local/stratum` should return JSON.

## Monero RPC timeouts

If the monitor reports **monerod RPC timed out**, confirm `monerod` is running and listening (`ss -tlnp | grep 18081`). The default read timeout is **`MONERO_RPC_TIMEOUT_SEC`** in `.env` (see `scripts/common/env.template`). If timeouts persist on a healthy disk, review official **monerod** tuning (concurrency, cache) and keep the chain on a responsive volume.

## Prebuilt XMRig (`XMRIG_BINARY`)

The Garuda and macOS scripts default to **`~/.local/bin/xmrig`** and **`~/bin/xmrig`** after `build`. To use a prebuilt tree (for example an official release unpacked on the Desktop), set **`XMRIG_BINARY`** in `.env` to the full path of the `xmrig` executable.

Still run **`config`** (or `run`, which regenerates the config) so the JSON matches this project: **RandomX to your P2Pool**, and the **HTTP API enabled** with host `0.0.0.0`, **`XMRIG_API_PORT`**, and **`XMRIG_API_TOKEN`**. Stock release `config.json` files often ship with **`http.enabled: false`**, which makes the HashFarm monitor show **zero hashrate** for that rig until you align with the script output.

## CUDA / GPU mining

HashFarm shell configs are **CPU-only** (`cuda: false`, `opencl: false`). NVIDIA **CUDA** mining uses a separate **xmrig-cuda** plugin whose **major.minor version must match** the XMRig release you run; mixing unrelated trees (for example XMRig 6.26 with CUDA plugin 6.22 sources) is unsupported upstream. For GPU RandomX you would build or download a **paired** XMRig + CUDA release from the official project, enable `cuda` in config, and keep the same **HTTP API** settings if you want that rig in the dashboard.

## `monerod` from Monero GUI vs packages

[`scripts/garuda/monerod-pruned.sh`](scripts/garuda/monerod-pruned.sh) invokes **`monerod` on your `PATH`**. A **Monero GUI** bundle ships its own `monerod`; you can run that binary by adjusting `PATH` or wrapping the script, but keep **daemon, P2Pool, and XMRig** on versions compatible with the current Monero network (upgrade after hard forks).

## Large disk: chain and P2Pool API data

Pruned **`monerod`** data and P2Pool **`--data-api`** still use significant space. Point them at a larger mount by setting in `.env`:

- **`MONERO_DATA_DIR`** — passed to `monerod --data-dir` (see `env.template`).
- **`P2POOL_DATA_API_DIR`** — used by [`scripts/garuda/p2pool-v4.sh`](scripts/garuda/p2pool-v4.sh) as `--data-api`.

Example layout on a roomy drive (adjust to your mount, e.g. **`/run/media/YourComputer/Disk`**):

```bash
MONERO_DATA_DIR=/run/media/YourComputer/Disk/hashfarm/bitmonero
P2POOL_DATA_API_DIR=/run/media/YourComputer/Disk/hashfarm/p2pool-data-api
```

Use a **Linux-native** filesystem (**ext4** or **xfs**) for `monerod` if you can; NTFS/exFAT on external disks is a poor fit for heavy random I/O and can worsen RPC timeouts.

## Community

- [Contributing](CONTRIBUTING.md) · [Architecture](docs/architecture.md) · [Roadmap](ROADMAP.md) · [Changelog](CHANGELOG.md)
- [Code of Conduct](CODE_OF_CONDUCT.md) · [Security](SECURITY.md) · [Support](SUPPORT.md)
- [GitHub Discussions](https://github.com/VoxHash-Labs/HashFarm/discussions) (when enabled)

Discovery topics are configured on the GitHub **About** section (`monero`, `xmr`, `p2pool`, `xmrig`, `randomx`, `mining`, `stratum`, `python`, `fastapi`, `bash`, `linux`, `macos`, `self-hosted`, `open-source`, `cryptocurrency`, `httpx`, `uvicorn`, `home-server`, `systemd`, `observability`).
