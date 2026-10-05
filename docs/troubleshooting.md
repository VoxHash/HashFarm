# Troubleshooting

## Missing `.env`

**Symptom:** scripts exit with “Missing …/.env” or `WALLET_MAIN: Set WALLET_MAIN in .env`.

**Fix:** `cp scripts/common/env.template .env` and edit real values.

## `monerod` not found

**Symptom:** `monerod not found (install monerod or set MONEROD_BIN…)`.

**Fix:** Install Monero CLI/GUI and put `monerod` on `PATH`, or set `MONEROD_BIN` to the absolute binary path.

## P2Pool stratum connection refused on `:3333`

**Symptom:** `ss` shows nothing on 3333 while `p2pool` is running.

**Cause:** P2Pool often does not bind stratum until `monerod` is synchronized.

**Fix:** Wait for chain height near target; watch `logs/p2pool.log`. Then `curl http://127.0.0.1:3333/local/stratum`.

## Monitor shows zero hashrate

**Causes:** XMRig HTTP API disabled (`http.enabled: false` in stock configs), wrong port, or token mismatch.

**Fix:** Run `xmrig-*.sh config` so API is enabled on `0.0.0.0` with matching `XMRIG_API_TOKEN`. Verify:

```bash
curl -sS -H "Authorization: Bearer YOUR_TOKEN" "http://RIG_IP:18060/2/summary" | head
```

## XMRig `401 UNAUTHORIZED`

Token in `.env` must equal `"access-token"` in every polled miner config. HashFarm uses one token for all `XMRIG_API_URLS`.

## Monero RPC timeouts

Increase `MONERO_RPC_TIMEOUT_SEC` (up to 600). Set `MONERO_DATA_DIR` so the monitor can parse height from `bitmonero.log` during LMDB stalls. Prefer ext4/xfs on a responsive disk; optional `MONERO_BLOCK_SYNC_SIZE` during catch-up.

## `/ready` returns 503

No recent collector snapshot (`READY_MAX_SNAPSHOT_AGE_SEC`). Confirm the monitor process is running without `HASHFARM_SKIP_LIFESPAN`, and that the collector loop is not crashing on startup. `/health` can still be `200`.

## Firewall blocks LAN miners

Open TCP 3333 only from your LAN (see [`deploy/FIREWALL.md`](../deploy/FIREWALL.md)). Confirm `P2POOL_STRATUM_BIND` is `0.0.0.0:3333` or the PC’s LAN IP—not only `127.0.0.1`.

## Browser console noise

Messages like “SES Removing unpermitted intrinsics” usually come from browser extensions, not the dashboard.
