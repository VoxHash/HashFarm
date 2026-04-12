# Optional: XMRig + CUDA (paired builds)

HashFarm’s shell-generated configs are **CPU-first** (`cuda: false`, `opencl: false`). If you want **NVIDIA CUDA** RandomX on the gaming PC, treat it as an **advanced** path: upstream ships **matching** XMRig and `xmrig-cuda` plugin versions together.

## Rules of thumb

1. Download the **same release family** for both the main `xmrig` binary and the CUDA plugin from the [official XMRig releases](https://github.com/xmrig/xmrig/releases) (or build both from the same tag).
2. Do **not** mix arbitrary versions (for example core **6.26** with CUDA plugin sources **6.22**): the plugin ABI is version-sensitive and you will get confusing load failures or silent misbehavior.
3. After enabling CUDA in JSON, keep the **HTTP API** block (`host`, `port`, `access-token`) aligned with `.env` so the HashFarm monitor can still read `hashrate.total`.

## Operator steps (outline)

1. Install NVIDIA driver and CUDA runtime per distro docs.
2. Place the CUDA plugin library where your `xmrig` build expects it (release archives document layout).
3. Set `XMRIG_BINARY` in `.env` if you are not using `~/.local/bin/xmrig`.
4. Regenerate config (`scripts/garuda/xmrig-cpu.sh config`) and then **manually** set `"cuda": true` and a sane `"threads"` / `"intensity"` profile for your GPU—validate stability before leaving it unattended.

RandomX on **GPU** is often secondary to **CPU** hashrate on Monero; many operators run GPU off or use it only when the PC is idle. This project does not ship a CUDA build script to avoid pinning NVIDIA SDK versions in CI.
