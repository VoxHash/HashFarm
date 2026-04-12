# Contributing (detailed)

HashFarm combines **Bash** deployment scripts, a **Python/FastAPI** monitor, and optional **systemd** units. Contributions are welcome from miners who script, Python developers, and DevOps folks.

## Repository layout

| Path | Role |
| ---- | ---- |
| `scripts/` | `monerod`, P2Pool, XMRig helpers; `common/env.template`, `verify-stack.sh` |
| `monitor/app/` | FastAPI app, collectors, templates |
| `deploy/` | systemd examples, firewall notes |
| `docs/` | Long-form technical documentation |

## Development setup (monitor)

```bash
cd monitor
python -m venv .venv
.venv/bin/pip install -r requirements.txt
cp ../scripts/common/env.template ../.env   # then edit ../.env — never commit it
../scripts/garuda/run-monitor.sh
```

Point `.env` at a working local stack or mocks are **not** used in production paths; use a testnet wallet / lab machine if you need isolated testing.

## Coding standards

- **Python:** match existing style (type hints where already used, `ruff`/`black` if introduced later in CI). Prefer small, readable functions.
- **Shell:** `set -euo pipefail`, quote variables, keep scripts POSIX-friendly where feasible.
- **Security:** never log tokens, SMTP passwords, or seeds. Redact wallet addresses in public issue screenshots if you prefer privacy.

## Branch and PR workflow

1. Fork [VoxHash-Labs/HashFarm](https://github.com/VoxHash-Labs/HashFarm) and clone your fork.
2. Create a branch: `feat/…`, `fix/…`, or `docs/…`.
3. Commit with [Conventional Commits](https://www.conventionalcommits.org/) messages.
4. Push and open a PR against `main` using `.github/PULL_REQUEST_TEMPLATE.md`.
5. Update **CHANGELOG.md** (`[Unreleased]`) for anything operators care about.

## Tests

Run from `monitor/` after `pip install -r requirements-dev.txt`:

```bash
.venv/bin/pytest -q
.venv/bin/ruff check .
```

`tests/conftest.py` sets **`HASHFARM_SKIP_LIFESPAN=1`** so the FastAPI lifespan does not start the background collector loop. Do **not** set that variable in production.

When adding logic, extend **`monitor/tests/`** and document new behavior in the PR.

## Accessibility (dashboard)

The HTML dashboard should remain readable without relying on color alone (status classes already distinguish states). New UI should use semantic headings and sufficient contrast.

## License

By contributing, you agree your contributions are licensed under the [MIT License](../LICENSE).
