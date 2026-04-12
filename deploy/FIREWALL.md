# LAN-only firewall notes (gaming PC)

P2Pool stratum (`3333`), XMRig HTTP APIs, and the HashFarm monitor should not face the public Internet. Restrict sources to your home LAN or VPN.

**Stratum bind:** [`scripts/garuda/p2pool-v4.sh`](../scripts/garuda/p2pool-v4.sh) passes `--stratum "${P2POOL_STRATUM_BIND:-0.0.0.0:${P2POOL_STRATUM_PORT:-3333}}"`, so stratum listens on **all interfaces** by default. Miners use `stratum+tcp://<GAMING_PC_LAN_IP>:3333` in XMRig; open **TCP 3333** only from trusted subnets or hosts.

## nftables (192.168.68.0/24 example)

Replace `enp5s0` with your LAN interface name (`ip -br link`) and adjust the subnet if yours differs.

```nft
table inet filter {
  chain input {
    type filter hook input priority 0;
    iif "lo" accept
    iif != "enp5s0" accept
    tcp dport 22 ip saddr 192.168.68.0/24 accept
    tcp dport { 3333, 8787, 18060, 18061, 18062 } ip saddr 192.168.68.0/24 accept
    reject with icmp type port-unreachable
  }
}
```

Apply with `sudo nft -f firewall.nft`. Adjust ports to match `.env` (`P2POOL_STRATUM_PORT`, `MONITOR_PORT`, `XMRIG_API_PORT` on each rig).

## nftables (single laptop only)

If only one miner (e.g. laptop `192.168.68.50`) should reach stratum:

```nft
    tcp dport 3333 ip saddr 192.168.68.50 accept
```

Place that rule (or an equivalent) before your generic reject; combine with other `tcp dport` lines as needed.

## ufw (192.168.68.0/24)

```bash
sudo ufw default deny incoming
sudo ufw allow from 192.168.68.0/24 to any port 3333 proto tcp comment 'P2Pool stratum LAN'
sudo ufw allow from 192.168.68.0/24 to any port 8787 proto tcp comment 'HashFarm monitor'
sudo ufw allow from 192.168.68.0/24 to any port 18060:18062 proto tcp comment 'XMRig HTTP APIs'
sudo ufw enable
```

**Single laptop** (replace with your machine’s address):

```bash
sudo ufw allow from 192.168.68.50 to any port 3333 proto tcp comment 'P2Pool stratum laptop'
```

## firewalld (zone + rich rule example)

```bash
sudo firewall-cmd --permanent --zone=home --add-source=192.168.68.0/24
sudo firewall-cmd --permanent --zone=home --add-port=3333/tcp
sudo firewall-cmd --reload
```

## Older example (192.168.1.0/24)

```bash
sudo ufw allow from 192.168.1.0/24 to any port 3333 proto tcp
```

Keep `monerod` JSON-RPC (`18081`) bound to `127.0.0.1` only (default in these scripts).
