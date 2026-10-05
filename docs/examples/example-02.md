# Example 02 — LAN multi-rig + firewall

Gaming PC hosts `monerod` + P2Pool; a laptop and an Apple Silicon Mac mine over the LAN.

## 1. Gaming PC `.env`

```bash
WALLET_MAIN=<your_mainnet_primary_address>
GAMING_PC_IP=192.168.68.10
P2POOL_STRATUM_BIND=0.0.0.0:3333
XMRIG_API_URLS=http://192.168.68.10:18060,http://192.168.68.20:18061,http://192.168.68.30:18062
XMRIG_API_TOKEN=<same_token_on_every_rig>
XMRIG_RIG_LABELS=gaming_pc,laptop,mac_mini_m1
WATTS_GAMING_PC=350
WATTS_LAPTOP=80
WATTS_MAC_MINI=40
```

## 2. Firewall (gaming PC only)

Allow TCP **3333** from `192.168.68.0/24` (or each miner IP). Concrete **nftables** / **ufw** / **firewalld** snippets: [`deploy/FIREWALL.md`](../../deploy/FIREWALL.md).

Confirm: `ss -tlnp | grep 3333` shows `0.0.0.0:3333` after sync.

## 3. Miners

**Laptop (Linux):** copy repo or only the scripts + `.env` with the same wallet/token; set a distinct API port in the generated config (e.g. `18061`), then:

```bash
./scripts/garuda/xmrig-cpu.sh config
./scripts/garuda/xmrig-cpu.sh run
```

**Mac:**

```bash
./scripts/macos/xmrig-m1.sh config
./scripts/macos/xmrig-m1.sh run
```

Stratum URL on remote rigs: `stratum+tcp://192.168.68.10:3333`.

## 4. Monitor on the gaming PC

Keep `XMRIG_API_URLS` listing every rig. Start `./scripts/garuda/run-monitor.sh` and check the dashboard for three labeled hashrates.

## 5. Verify from the PC

```bash
./scripts/common/verify-stack.sh
```

Aggregate hashrate should sum all reachable APIs. If one rig is `401`, fix that host’s `access-token` to match `XMRIG_API_TOKEN`.
