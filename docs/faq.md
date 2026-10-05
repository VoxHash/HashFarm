# FAQ

## Is HashFarm a mining pool?

No. It is a **self-hosted toolkit** that runs your own `monerod` + **P2Pool** + XMRig and a local monitor. Payouts follow P2Pool rules to `WALLET_MAIN`.

## Do I need a GPU?

No. Default configs are **CPU RandomX**. NVIDIA CUDA is optional—see [cuda-mining.md](cuda-mining.md).

## Can I expose the monitor to the internet?

Not recommended without a reverse proxy and authentication. Default bind is `0.0.0.0:8787`; prefer localhost or a trusted LAN and firewall. See [remote-rpc-tor.md](remote-rpc-tor.md) for remote access patterns.

## Why keep the name HashFarm?

It accurately describes a home **hashrate farm** for Monero. There is no conflicting upstream product under this name; branding stays **HashFarm** under VoxHash Technologies.

## Where do I report security issues?

Email [contact@voxhash.dev](mailto:contact@voxhash.dev)—do not open a public issue. See [SECURITY.md](../SECURITY.md).

## Which Python version?

CI uses **Python 3.12**. Local smoke has also been run on newer CPython (e.g. 3.14) for the monitor venv; use 3.11+ in practice.

## How do I update?

```bash
git pull
cd monitor && .venv/bin/pip install -r requirements.txt
# regenerate miner configs if env.template gained new keys
```

Check [CHANGELOG.md](../CHANGELOG.md) and GitHub Releases for breaking notes.
