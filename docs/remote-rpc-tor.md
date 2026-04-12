# Remote RPC access and Tor (documentation only)

`monerod` JSON-RPC in HashFarm defaults to **loopback** (`127.0.0.1:18081`). That is the safest default: the monitor and P2Pool talk locally without exposing wallet or chain control to the LAN or internet.

## If you must reach RPC from another machine

Prefer **SSH port forwarding** instead of opening `18081` on the LAN:

```bash
ssh -N -L 18081:127.0.0.1:18081 user@gaming-pc
```

Point `MONERO_RPC_URL` on the client to `http://127.0.0.1:18081/json_rpc` through the tunnel.

If you bind RPC to a non-loopback address, use **`--rpc-login`** (user:hash) or restrict with **firewall** rules and VPN membership. Never expose unauthenticated JSON-RPC to the public internet.

## Tor hidden service (advanced)

Some operators publish `monerod` RPC as an **onion service** for remote wallet or monitoring. That is outside HashFarm’s scripts: follow upstream Monero hardening guidance, use authentication, and understand latency implications for the monitor’s polling loop.

**Non-goals for this repo:** shipping Tor unit files, `.onion` templates, or automated RPC exposure patterns.

## P2Pool note

P2Pool still needs reliable **ZMQ** and **RPC** to the same `monerod` instance. Remote tunnels add failure modes; keep the gaming PC’s stack local when possible.
