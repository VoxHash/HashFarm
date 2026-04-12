# Security policy

## Supported versions

Security-sensitive fixes are applied to the latest `main` branch. Use the newest tagged release when running in production.

| Version / branch | Supported |
| ---------------- | --------- |
| `main` (latest)  | Yes       |
| Older tags       | Best effort |

## Reporting a vulnerability

**Do not** open a public GitHub issue for undisclosed security problems.

Email **[contact@voxhash.dev](mailto:contact@voxhash.dev)** with:

- A clear description of the issue and affected components (monitor, scripts, deployment)
- Steps to reproduce
- Potential impact (e.g., credential leak, SSRF, auth bypass)
- Affected versions or commit SHA if known

We aim to acknowledge within **72 hours** and coordinate disclosure after a fix is available.

## Operational security (operators)

This project orchestrates **real mining infrastructure**. Treat these as high sensitivity and keep them out of git:

- Repository root **`.env`** (wallet addresses, API tokens, SMTP credentials, LAN layout)
- **`monerod` / wallet** files under your configured `MONERO_DATA_DIR`
- **XMRig** HTTP API tokens
- **TLS keys** or RPC passwords if you enable non-default `monerod` RPC auth

Use `scripts/common/env.template` as a reference only; copy to **`.env`** locally and never commit `.env`.

## Dependency updates

The Python monitor pins dependencies in `monitor/requirements.txt`. Review release notes when upgrading `fastapi`, `httpx`, `uvicorn`, and related packages.
