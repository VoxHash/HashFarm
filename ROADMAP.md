# Roadmap

**Vision:** A small, auditable toolkit to run Monero P2Pool at home with clear observability and safe defaults.

**Organization:** [VoxHash Labs](https://github.com/VoxHash-Labs) — repository: [HashFarm](https://github.com/VoxHash-Labs/HashFarm).

## Current status (2026-Q2)

Shipped: pruned node script, P2Pool v4 installer/runner, CPU XMRig helpers (Linux + macOS), FastAPI monitor (dashboard + JSON API), env template, verify script, systemd examples, RPC timeout / stale snapshot UX, documentation for large-disk paths and prebuilt XMRig, **CI (ruff + pytest + shellcheck)**, **SQLite metrics + `/metrics`**, **`/health` + `/ready`**, and **CUDA / remote RPC docs**.

## Milestones

### Phase A — Operator polish (short term)

- [x] GitHub Actions: lint/test gate for `monitor/` (ruff + pytest) and shellcheck for `scripts/`.
- [x] Versioned releases with GitHub Release notes mirroring `CHANGELOG.md` (process established with `v0.1.0`).
- [x] Optional `docs_improvement` issue template for documentation feedback.

### Phase B — Observability (mid term)

- [x] Persist minimal time-series (SQLite) for hashrate / sync lag / height; Prometheus text from `/metrics`.
- [x] Health (`/health`) and readiness (`/ready`) endpoints for orchestration probes.

### Phase C — Advanced mining (optional)

- [x] Documented path for **paired** XMRig + CUDA builds — [docs/cuda-mining.md](docs/cuda-mining.md).
- [x] Remote RPC / Tor pointers — [docs/remote-rpc-tor.md](docs/remote-rpc-tor.md) (no default insecure exposure).

## Non-goals

- Custodial wallet services or cloud control of private keys.
- Replacing official `monerod`, P2Pool, or XMRig upstreams.

See [DEVELOPMENT_GOALS.md](DEVELOPMENT_GOALS.md) for quality and testing targets.
