# GitHub Wiki outline

Use this outline when enabling the [GitHub Wiki](https://docs.github.com/en/communities/documenting-your-project-with-wikis/about-wikis) for **VoxHash-Labs/HashFarm**. Create pages in any order; keep the sidebar linked to the sections below.

## Suggested pages

1. **Home** — One-paragraph project summary + link to repo README and `docs/`.
2. **Hardware checklist** — Gaming PC RAM/SSD notes, pruned disk sizing, optional large mount for `MONERO_DATA_DIR`.
3. **Garuda first-time setup** — Order: `monerod` → P2Pool install → P2Pool run → XMRig `build`/`config`/`run` → monitor venv.
4. **macOS rig** — Homebrew deps, `xmrig-m1.sh`, firewall for API port.
5. **Environment reference** — Table of every `env.template` variable with safe defaults.
6. **Troubleshooting** — RPC timeouts, stratum `:3333` refused during sync, zero hashrate (HTTP API off), SMTP failures.
7. **systemd** — How to adapt `deploy/systemd/*.service` paths and user accounts.
8. **Security hardening** — LAN-only RPC, tokens, no `.env` in backups to cloud without encryption.
9. **Upgrades** — Bumping P2Pool `P2POOL_VERSION`, Monero fork checklist, XMRig rebuild.
10. **FAQ** — P2Pool vs solo, pruned vs full, why RandomX GPU is optional.

## Sidebar (example)

- Home  
- Hardware checklist  
- Garuda setup  
- macOS rig  
- Environment reference  
- Troubleshooting  
- systemd  
- Security  
- Upgrades  
- FAQ  

## Maintenance

- When wiki and `docs/` disagree, treat the **repo `docs/` and README** as canonical unless the wiki explicitly documents machine-specific runbooks.
