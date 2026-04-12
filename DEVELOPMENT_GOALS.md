# Development goals

Quality and process targets for HashFarm development (2026).

## Testing

- [ ] Introduce `monitor/tests/` with pytest for `settings`, `state.merge_stale_monero`, and collector edge cases.
- [ ] CI runs pytest on every pull request to `main`.
- [ ] Shell: optional `shellcheck` job on `scripts/**/*.sh`.

## Code quality

- **Python:** keep compatible with supported Python versions on Garuda and current macOS Homebrew; prefer explicit types on new public functions.
- **Shell:** `shellcheck`-clean scripts where practical.
- **Dependencies:** pin upper bounds cautiously; review security advisories for `httpx`, `fastapi`, `uvicorn`.

## Documentation

- README remains the **quick path**; deeper material in `docs/` and (optionally) the GitHub Wiki per [docs/wiki-outline.md](docs/wiki-outline.md).
- Every operator-facing env var appears in `scripts/common/env.template` with a comment.

## Accessibility (monitor UI)

- Dashboard uses structured headings; new blocks should too.
- Do not rely on color alone for critical status (errors already use text + CSS class).
- Target WCAG **AA** contrast for body text on default theme.

## Security

- No credentials in committed files; `.env` always gitignored.
- SECURITY.md process followed for vulnerability reports.
- Document attack surface: local RPC, XMRig API, SMTP.

## Performance

- Monitor poll interval should remain modest (single-digit seconds) to avoid overloading `monerod` during sync.
- HTTP client uses configurable Monero RPC read timeout; document tuning for slow disks.

## Releases

- Tag semantically (`v0.2.0`, …) and attach release notes from `CHANGELOG.md`.
