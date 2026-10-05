# Roadmap

**Vision:** A small, auditable toolkit to run Monero P2Pool at home with clear observability and safe defaults.

**Organization:** [VoxHash Technologies](https://voxhash.dev) — repository: [VoxHash/HashFarm](https://github.com/VoxHash/HashFarm).

## Current status (2026-Q4)

Shipped through **v0.2.0**: pruned node script, P2Pool v4 installer/runner, CPU XMRig helpers (Linux + macOS), optional CUDA build helper + docs, FastAPI monitor (dashboard, JSON API, `/health` `/ready` `/metrics`, SQLite metrics), env template, verify script, systemd examples, RPC timeout / log-height fallback UX, firewall notes, CI (`ruff` + `pytest` + `shellcheck`), and a complete operator docs kit under `docs/`.

## Milestones

### Phase A — Operator polish (done)

- [x] GitHub Actions: lint/test gate for `monitor/` (ruff + pytest) and shellcheck for `scripts/`.
- [x] Versioned releases with GitHub Release notes mirroring `CHANGELOG.md` (`v0.1.0`, `v0.2.0`).
- [x] Optional `docs_improvement` issue template for documentation feedback.
- [x] Standard documentation kit (install, configure, use, API, FAQ, troubleshooting, examples).

### Phase B — Observability (done)

- [x] Persist minimal time-series (SQLite) for hashrate / sync lag / height; Prometheus text from `/metrics`.
- [x] Health (`/health`) and readiness (`/ready`) endpoints for orchestration probes.

### Phase C — Advanced mining (done)

- [x] Documented path for **paired** XMRig + CUDA builds — [docs/cuda-mining.md](docs/cuda-mining.md).
- [x] Remote RPC / Tor pointers — [docs/remote-rpc-tor.md](docs/remote-rpc-tor.md) (no default insecure exposure).

### Phase D — Operator UX (next)

- [ ] Dashboard charts from SQLite metrics (hashrate and sync lag over retention window).
- [ ] Optional webhook / Pushover alerts alongside SMTP.
- [ ] Packaging helpers: one-command “bootstrap monitor venv” script and clearer first-run checklist in README.
- [ ] Documented Apple Silicon + Linux dual-rig verify recipe using real LAN IPs from `.env`.

### Phase E — Hardening (later)

- [ ] Optional basic auth or reverse-proxy notes for exposing the monitor beyond localhost.
- [ ] Expand pytest coverage for collector merge paths and XMRig 401 messaging.
- [ ] Keep `shellcheck`-clean scripts and review dependency advisories for `httpx` / `fastapi` / `uvicorn` each minor release.

## Quality targets (ongoing)

- **Python:** compatible with current Garuda and Homebrew Python; prefer explicit types on new public functions.
- **Shell:** `set -euo pipefail`, quote variables, `shellcheck`-clean where practical.
- **Docs:** every operator-facing env var appears in `scripts/common/env.template` with a comment.
- **Security:** no credentials in git; treat `.env`, RPC, and XMRig API tokens as high sensitivity.
- **Performance:** keep poll intervals modest; tune `MONERO_RPC_TIMEOUT_SEC` for slow disks.

## Non-goals

- Custodial wallet services or cloud control of private keys.
- Replacing official `monerod`, P2Pool, or XMRig upstreams.
