# Monitor API

Base URL defaults to `http://127.0.0.1:8787` (`MONITOR_BIND` / `MONITOR_PORT`). No authentication is built into the app—bind to localhost or put a reverse proxy in front if you expose it.

## `GET /`

HTML dashboard (Jinja2) for sync, pool, rigs, and profitability hints.

## `GET /api/snapshot`

JSON snapshot from the latest collector poll.

Typical top-level fields:

| Field | Meaning |
| ----- | ------- |
| `updated_at` | ISO timestamp of last successful snapshot apply (may be null if the collector loop errored hard) |
| `monero` | Height, target, difficulty, sync lag, RPC error flags |
| `p2pool` | Local stratum/p2p payloads or errors |
| `rigs` | Per-rig hashrate / status |
| `aggregate_hashrate_hs` | Sum of rig hashrates |
| `xmr_usd` / `net_usd_per_day` | Price feed + rough economics |
| `safety` | Reduce-load policy state |
| `last_error` | Last collector exception string, if any |

## `GET /health`

Liveness. Returns `200` with `{"status":"ok"}` if the process is up. Does **not** check `monerod` / P2Pool / XMRig.

## `GET /ready`

Readiness for orchestration. Returns `200` when a recent snapshot exists; otherwise `503` with `reason: no_recent_snapshot` when age exceeds `READY_MAX_SNAPSHOT_AGE_SEC` or no snapshot was applied yet.

## `GET /metrics`

Prometheus text exposition (`text/plain; version=0.0.4`) of gauges derived from the latest snapshot (aggregate hashrate, heights, sync lag, Monero RPC error/stale flags, etc.).

## Collector behavior notes

- Monero RPC uses `MONERO_RPC_TIMEOUT_SEC` (up to 600s).
- On RPC failure with `MONERO_DATA_DIR` set, height/target/lag may be parsed from `bitmonero.log`.
- XMRig calls send `Authorization: Bearer <XMRIG_API_TOKEN>` when the token is set.
- Set `HASHFARM_SKIP_LIFESPAN=1` only for pytest; never in production.
