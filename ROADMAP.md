# Roadmap

**Vision:** A small, auditable toolkit to run Monero P2Pool at home with clear observability and safe defaults.

**Organization:** [VoxHash Labs](https://github.com/VoxHash-Labs) — repository: [HashFarm](https://github.com/VoxHash-Labs/HashFarm).

## Current status (2026-Q2)

Shipped: pruned node script, P2Pool v4 installer/runner, CPU XMRig helpers (Linux + macOS), FastAPI monitor (dashboard + JSON API), env template, verify script, systemd examples, RPC timeout / stale snapshot UX, documentation for large-disk paths and prebuilt XMRig.

## Milestones

### Phase A — Operator polish (short term)

- [ ] GitHub Actions: lint/test gate for `monitor/` (ruff or flake8 + pytest skeleton).
- [ ] Versioned releases with GitHub Release notes mirroring `CHANGELOG.md`.
- [ ] Optional `docs_improvement` issue template if the community files many doc issues.

### Phase B — Observability (mid term)

- [ ] Persist minimal time-series (SQLite or Prometheus export) for hashrate and sync lag.
- [ ] Health endpoint for Kubernetes / systemd `ExecStartPost` style checks.

### Phase C — Advanced mining (optional)

- [ ] Documented or scripted path for **paired** XMRig + CUDA builds (no version skew), still optional vs CPU-first story.
- [ ] Optional Tor / remote RPC tunnel documentation (no default insecure exposure).

## Non-goals

- Custodial wallet services or cloud control of private keys.
- Replacing official `monerod`, P2Pool, or XMRig upstreams.

See [DEVELOPMENT_GOALS.md](DEVELOPMENT_GOALS.md) for quality and testing targets.
