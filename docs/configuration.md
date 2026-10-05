# Configuration

All operator secrets and host-specific values live in **`.env`** at the repository root (gitignored). Start from the real template:

```bash
cp scripts/common/env.template .env
```

The monitor loads `.env` with **`override=True`** so file values win over stale exported shell variables.

## Required

| Variable | Description |
| -------- | ----------- |
| `WALLET_MAIN` | Mainnet primary address used by P2Pool / XMRig |
| `GAMING_PC_IP` | LAN IP/hostname of the P2Pool host |
| `XMRIG_API_URLS` | Comma-separated XMRig HTTP API bases (no path) |
| `XMRIG_API_TOKEN` | Bearer token; must match each miner `http.access-token` |

## Monero / P2Pool

| Variable | Default / notes |
| -------- | --------------- |
| `MONERO_RPC_URL` | `http://127.0.0.1:18081/json_rpc` |
| `MONERO_RPC_TIMEOUT_SEC` | `60` (max `600`) |
| `MONERO_RPC_STALE_TTL_SEC` | Keep last-good heights after soft RPC failures |
| `MONERO_DATA_DIR` | Chain dir; also enables `bitmonero.log` height fallback |
| `MONERO_BLOCK_SYNC_SIZE` | Optional; smaller batches on slow HDD catch-up |
| `MONEROD_BIN` | Full path if `monerod` is not on `PATH` |
| `P2POOL_STRATUM_URL` | `http://127.0.0.1:3333` (local HTTP API) |
| `P2POOL_STRATUM_BIND` | Default `0.0.0.0:3333` for LAN miners |
| `P2POOL_DATA_API_DIR` | P2Pool `--data-api` directory |
| `P2POOL_STRATUM_PORT` | Port miners use (usually `3333`) |
| `P2POOL_NO_AUTODIFF` / `FIXED_DIFF` | Fixed difficulty mode |

## XMRig / CUDA

| Variable | Notes |
| -------- | ----- |
| `XMRIG_BINARY` | Absolute path to `xmrig` if not using script defaults |
| `XMRIG_RIG_LABELS` | Labels aligned with `XMRIG_API_URLS` order |
| `XMRIG_API_TIMEOUT_SEC` | Per-request timeout |
| `XMRIG_ENABLE_CUDA` | `1` to emit CUDA block in generated config |
| `XMRIG_CUDA_ARCH` / `CMAKE_CUDA_ARCHITECTURES` | GPU SM (e.g. `86` for RTX 3070 Ti) |
| `CUDA_HOME` | Toolkit root if not `/opt/cuda` |

## Monitor / metrics / alerts

| Variable | Notes |
| -------- | ----- |
| `MONITOR_BIND` / `MONITOR_PORT` | Default `0.0.0.0:8787` |
| `METRICS_ENABLED` | SQLite append (default on) |
| `METRICS_SQLITE_PATH` / `METRICS_RETENTION_DAYS` | Storage + prune |
| `READY_MAX_SNAPSHOT_AGE_SEC` | `/ready` freshness window |
| `ELECTRICITY_USD_PER_KWH`, `WATTS_*` | Profitability hints |
| `XMR_USD_SOURCES` | e.g. `coingecko,kraken,cryptocompare` |
| `SMTP_*` / `ALERT_*` | Optional email alerts |
| `SAFETY_*` | Temperature/power reduce-load policy (dry-run default) |
| `RIG_TELEMETRY_URLS` | Optional external temp/power JSON endpoints |

See comments in [`scripts/common/env.template`](../scripts/common/env.template) for every key.
