# Contributing to HashFarm

Thank you for helping improve HashFarm. This file is the entry point; the **detailed guide** lives in [docs/contributing.md](docs/contributing.md).

## Quick links

- [Architecture](docs/architecture.md) — how the monitor and scripts fit together
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Security reporting](SECURITY.md)
- [Support](SUPPORT.md)

## Principles

1. **No secrets in git** — use `.env` (gitignored); only edit `scripts/common/env.template` with placeholders.
2. **Scope** — keep pull requests focused (one concern per PR when possible).
3. **Conventional Commits** — e.g. `feat(monitor): …`, `fix(scripts): …`, `docs: …`.

## Pull requests

Use the [pull request template](.github/PULL_REQUEST_TEMPLATE.md). At minimum:

- Describe the change and link issues (`Fixes #123`).
- Note how you tested (manual stack check, unit tests if added).
- Update `CHANGELOG.md` under `[Unreleased]` for user-visible changes.

## Questions

Open a [discussion](https://github.com/VoxHash-Labs/HashFarm/discussions) or an issue (non-security) after checking existing threads.
