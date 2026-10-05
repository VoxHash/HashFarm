# Installation

## Clone

```bash
git clone https://github.com/VoxHash/HashFarm.git
cd HashFarm
```

## System dependencies

### Gaming PC (Linux)

| Component | How to obtain |
| --------- | ------------- |
| `monerod` | [getmonero.org downloads](https://www.getmonero.org/downloads/) CLI/GUI, or distro package. Put on `PATH` or set `MONEROD_BIN` in `.env`. |
| P2Pool | `./scripts/garuda/p2pool-v4.sh install` (official Linux x64 release) |
| XMRig | `./scripts/garuda/xmrig-cpu.sh build` → `~/.local/bin/xmrig`, or set `XMRIG_BINARY` to a prebuilt binary |
| Python 3.11+ | Distro `python` / `python3` |
| `curl`, `ss` | Usually preinstalled; used by verify and health checks |

Optional CUDA plugin: NVIDIA driver, `nvcc` (`/opt/cuda` or `CUDA_HOME`), see [cuda-mining.md](cuda-mining.md).

### macOS miners

- Xcode CLT / Homebrew for building XMRig via `scripts/macos/xmrig-m1.sh build`
- Or set `XMRIG_BINARY` to a prebuilt Apple Silicon release

## Monitor Python environment

```bash
cd monitor
python -m venv .venv
.venv/bin/pip install -r requirements.txt
```

For contributors (lint + tests):

```bash
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/ruff check .
HASHFARM_SKIP_LIFESPAN=1 .venv/bin/pytest -q
```

## systemd (optional)

Unit examples live under [`deploy/systemd/`](../deploy/systemd/). Copy and adjust paths to your clone and user, then `systemctl --user enable --now …` (or system units with care).

## Disk layout

Point large dirs at a fast Linux filesystem (ext4/xfs) in `.env`:

```bash
MONERO_DATA_DIR=/path/to/hashfarm/bitmonero
P2POOL_DATA_API_DIR=/path/to/hashfarm/p2pool-data-api
```

Avoid NTFS/exFAT for LMDB if you can—slow disks amplify RPC timeouts.
