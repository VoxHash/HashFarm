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

## LAN stratum (`0.0.0.0:3333`) and firewall

P2Pool is started with **`--stratum 0.0.0.0:3333`** by default (override with **`P2POOL_STRATUM_BIND`** in `.env`). That listens on every interface so laptops can use `stratum+tcp://<GAMING_PC_LAN_IP>:3333`.

Open **TCP 3333** only from your LAN (e.g. **`192.168.68.0/24`**) or from the laptop’s single IP—see [`deploy/FIREWALL.md`](deploy/FIREWALL.md) for **nftables**, **ufw**, and **firewalld** examples. Applying firewall rules requires **`sudo`** on the gaming PC.

After `monerod` is synchronized, confirm stratum: `ss -tlnp | grep 3333` (expect `0.0.0.0:3333` or `*:3333`). Until then P2Pool may log “not synchronized” and not bind stratum yet.

## P2Pool “connection refused” on :3333

If `monerod` is still syncing, P2Pool often **does not bind** the stratum HTTP port yet (`ss` shows nothing on `3333` even when `pgrep p2pool` is running). That is normal. Wait until chain height is near the network target and `logs/p2pool.log` shows a healthy connection; then `curl http://127.0.0.1:3333/local/stratum` should return JSON.

## Monero RPC timeouts

If the monitor reports **monerod RPC timed out**, confirm `monerod` is running and listening (`ss -tlnp | grep 18081`). The read timeout is **`MONERO_RPC_TIMEOUT_SEC`** in `.env` (up to 600 seconds; see `scripts/common/env.template`). During catch-up on a slow disk, `get_info` can return an empty body for a long time; the dashboard can still show **height / target / lag** parsed from **`bitmonero.log`** when **`MONERO_DATA_DIR`** is set. If timeouts persist on a healthy disk, review official **monerod** tuning (for example optional **`MONERO_BLOCK_SYNC_SIZE`** in `monerod-pruned.sh`) and keep the chain on a responsive volume.

## Prebuilt XMRig (`XMRIG_BINARY`)

The Garuda and macOS scripts default to **`~/.local/bin/xmrig`** and **`~/bin/xmrig`** after `build`. To use a prebuilt tree (for example an official release unpacked on the Desktop), set **`XMRIG_BINARY`** in `.env` to the full path of the `xmrig` executable.

Still run **`config`** (or `run`, which regenerates the config) so the JSON matches this project: **RandomX to your P2Pool**, and the **HTTP API enabled** with host `0.0.0.0`, **`XMRIG_API_PORT`**, and **`XMRIG_API_TOKEN`**. Stock release `config.json` files often ship with **`http.enabled: false`**, which makes the HashFarm monitor show **zero hashrate** for that rig until you align with the script output.

## CUDA / GPU mining

HashFarm defaults to **CPU-only** JSON (`cuda: false`). For NVIDIA RandomX, use **XMRig 6.26.x** with a **`libxmrig-cuda.so`** built from **`xmrig-cuda` `v6.22.1`** (plugin **API v4**), install the `.so` next to your `xmrig`, then set **`XMRIG_ENABLE_CUDA=1`** and run **`scripts/garuda/xmrig-cpu.sh config`**. Build helper: [`scripts/garuda/build-xmrig-cuda.sh`](scripts/garuda/build-xmrig-cuda.sh) (set **`XMRIG_CUDA_ARCH`** to your GPU’s numeric SM, e.g. **86** for RTX 3070 Ti, so CUDA 12+ does not try deprecated **`sm_50`** defaults; on **CUDA 13+** it also applies a small **`cuda_extra.cu`** patch for removed **`cudaDeviceProp`** clock fields). Full notes, GPU table, and upstream PR workflow: [`docs/cuda-mining.md`](docs/cuda-mining.md).

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
