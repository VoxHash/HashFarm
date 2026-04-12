# LAN-only firewall notes (gaming PC)

P2Pool stratum (`3333`), XMRig HTTP APIs, and the HashFarm monitor should not face the public Internet. Restrict sources to your home LAN or VPN.

## nftables (example)

Replace `enp5s0` with your uplink interface and `192.168.1.0/24` with your LAN.

```nft
table inet filter {
  chain input {
    type filter hook input priority 0;
    iif "lo" accept
    iif != "enp5s0" accept
    tcp dport 22 ip saddr 192.168.1.0/24 accept
    tcp dport { 3333, 8787, 18060, 18061, 18062 } ip saddr 192.168.1.0/24 accept
    reject with icmp type port-unreachable
  }
}
```

Apply with `nft -f firewall.nft`. Adjust ports to match `.env` (`P2POOL_STRATUM_PORT`, `MONITOR_PORT`, `XMRIG_API_PORT` on each rig).

## ufw (example)

```bash
sudo ufw default deny incoming
sudo ufw allow from 192.168.1.0/24 to any port 3333 proto tcp
sudo ufw allow from 192.168.1.0/24 to any port 8787 proto tcp
sudo ufw allow from 192.168.1.0/24 to any port 18060:18062 proto tcp
sudo ufw enable
```

Keep `monerod` JSON-RPC (`18081`) bound to `127.0.0.1` only (default in these scripts).
