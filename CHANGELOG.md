# Changelog

All notable changes to **HashFarm** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **`scripts/garuda/build-xmrig-cuda.sh`**: build **`libxmrig-cuda.so`** from **`xmrig-cuda`** tag **`v6.22.1`** (configurable), pass **`-DCUDA_ARCH`** (via **`XMRIG_CUDA_ARCH`** / **`CMAKE_CUDA_ARCHITECTURES`**) so CUDA 12+ does not try to build dropped **`sm_50`** defaults; wipe **`build/`** unless **`XMRIG_CUDA_KEEP_BUILD=1`**. Prepends **`/opt/cuda/bin`** or **`$CUDA_HOME/bin`** to **`PATH`** for **`nvcc`**. On **CUDA 13+**, applies **`scripts/garuda/patches/xmrig-cuda-v6.22.1-cuda13-device-clocks.patch`** for removed **`cudaDeviceProp`** clock fields (opt out with **`XMRIG_CUDA_SKIP_PATCH=1`**).
- **`XMRIG_ENABLE_CUDA=1`** for **`scripts/garuda/xmrig-cpu.sh`** to emit a minimal enabled **`cuda`** block; expanded [docs/cuda-mining.md](docs/cuda-mining.md) (API pairing, RTX 3070 Ti notes, upstream PR steps).

### Changed

- Monitor: **`MONERO_RPC_TIMEOUT_SEC`** may be set up to **600** seconds; when **`MONERO_DATA_DIR`** is set and **`get_info`** fails, **height / target / lag** can be recovered from the latest `Synced …/…` line in **`bitmonero.log`** (typical when LMDB on a slow disk stalls JSON-RPC). **`monerod-pruned.sh`** accepts optional **`MONERO_BLOCK_SYNC_SIZE`** to shorten write bursts during catch-up. The repo **`.env`** is loaded with **`override=True`** so it wins over stale exported shell variables (for example an old **`MONERO_DATA_DIR`**).
- **Firewall docs** for `192.168.68.0/24`, single-laptop allow, and **firewalld**; **env.template** comments for `P2POOL_STRATUM_BIND`. README notes default stratum `0.0.0.0:3333` and `ss` check after sync.
- Clearer XMRig **401 UNAUTHORIZED** hints when `XMRIG_API_TOKEN` is missing or mismatched; monitor README troubleshooting for HTTP API auth.

### Added

- GitHub Actions **CI** (`ruff`, `pytest`, `shellcheck`) for `monitor/` and `scripts/`.
- Monitor **`/health`**, **`/ready`**, and Prometheus **`/metrics`** endpoints.
- **SQLite** append-only poll metrics (`METRICS_*` settings); `monitor/data/` gitignored.
- Pytest suite with `HASHFARM_SKIP_LIFESPAN` test hook; `requirements-dev.txt` and `pyproject.toml` for Ruff/pytest.
- **Phase C** docs: [docs/cuda-mining.md](docs/cuda-mining.md), [docs/remote-rpc-tor.md](docs/remote-rpc-tor.md).
- GitHub **docs improvement** issue template.

## [0.1.0] - 2026-04-12

### Added

- Shell scripts for Garuda: pruned `monerod`, P2Pool v4 install/run, CPU XMRig, stack verification.
- macOS Apple Silicon XMRig helper script.
- FastAPI monitor: dashboard, JSON snapshot API, Monero RPC polling with configurable timeouts, P2Pool local HTTP client, XMRig summary aggregation, optional SMTP alerts.
- `MONERO_RPC_TIMEOUT_SEC`, last-known-good Monero snapshot on transient RPC failure, and clearer P2Pool messaging when RPC is unhealthy.
- Optional `XMRIG_BINARY` for prebuilt XMRig paths; documentation for CUDA version pairing, large-disk data dirs, and Monero GUI bundle vs PATH.
- Example `env.template`, systemd unit examples, and firewall notes.
- Open-source governance: `LICENSE` (MIT), `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `SUPPORT.md`, `ROADMAP.md`, `DEVELOPMENT_GOALS.md`.
- `docs/architecture.md`, `docs/contributing.md`, `docs/index.md`, `docs/wiki-outline.md`.
- GitHub issue and pull request templates under `.github/`.

### Changed

- Expanded `.gitignore` for env files, IDE paths, Python artifacts, logs, and local chain data.
- README community links, badges, and repository topic list for discoverability.

---

## Changelog maintenance

For each release:

1. Move `[Unreleased]` items under a new `## [x.y.z] - YYYY-MM-DD` section.
2. Follow [Conventional Commits](https://www.conventionalcommits.org/) in commit messages to make history scannable.
3. Link GitHub issues and pull requests where relevant.
