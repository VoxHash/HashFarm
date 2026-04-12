# Optional: XMRig + CUDA (paired builds)

HashFarm’s shell-generated configs are **CPU-first** (`cuda: false`, `opencl: false`). If you want **NVIDIA CUDA** RandomX on the gaming PC, treat it as an **advanced** path: use an **XMRig** build and an **`xmrig-cuda`** plugin that share a **compatible plugin API** (see [CudaLib::load in XMRig](https://github.com/xmrig/xmrig/blob/v6.26.0/src/backend/cuda/wrappers/CudaLib.cpp): API **3 or 4**).

## Rules of thumb

1. Prefer an **official XMRig release** (e.g. **6.26.0**) plus **`libxmrig-cuda.so`** built from the **`xmrig-cuda`** tag recommended by that ecosystem—today **`v6.22.1`** is the current plugin release and declares **API v4**, which **6.26.x** accepts. The plugin’s **`APP_VERSION` string does not have to equal XMRig’s**; what matters is **API / symbols** (including optional **`rxUpdateDataset`** for RandomX).
2. Do **not** mix **stale** or **random** plugin builds (old tree without `rxUpdateDataset`, wrong **CUDA arch**, or wrong **SO** for your OS): you will see load failures, “plugin outdated”, or bad hashrate.
3. After enabling CUDA in JSON, keep the **HTTP API** block (`host`, `port`, `access-token`) aligned with `.env` so the HashFarm monitor can still read `hashrate.total`.

## Hardware check (this machine)

Recorded on the operator workstation:

| Item | Value |
|------|--------|
| GPU | NVIDIA GeForce **RTX 3070 Ti**, 8192 MiB, driver **595.58.03**, compute capability **8.6** |
| CPU sample | **AMD Ryzen 7 8700G** (XMRig **6.26.0** `rx/0` benchmark ~**2.5 kH/s** on a 60s window; MSR mod was not applied, so CPU hashrate is **not** representative of a tuned box) |

**Worth CUDA for Monero RandomX?** On this class of PC the **CPU usually dominates** RandomX; the **3070 Ti** adds modest **GPU** H/s at extra power and VRAM use. Use **`xmrig --bench=… --algo=rx/0`** with **`libxmrig-cuda.so`** installed next to `xmrig` and compare **GPU-only** vs **CPU-only** before leaving GPU mining on 24/7.

## Build the CUDA plugin (Garuda / Arch)

1. Install the **CUDA toolkit** (Arch: `sudo pacman -S cuda`). **`nvcc`** lives at **`/opt/cuda/bin/nvcc`** and is **not** on the default shell `PATH`; [`scripts/garuda/build-xmrig-cuda.sh`](../scripts/garuda/build-xmrig-cuda.sh) prepends **`/opt/cuda/bin`** (or **`$CUDA_HOME/bin`**) automatically when that file exists. For manual CMake, run `export PATH="/opt/cuda/bin:$PATH"` first.
2. From the HashFarm repo (with `.env` containing **`XMRIG_BINARY`** if you use a Desktop `xmrig`):

   ```bash
   export XMRIG_CUDA_SRC=/path/to/xmrig-cuda-6.22.1
   export XMRIG_CUDA_ARCH=86   # required: xmrig-cuda CMake uses -DCUDA_ARCH (not defaults: they include 50, dropped in CUDA 12+)
   ./scripts/garuda/build-xmrig-cuda.sh
   ```

   Override **`XMRIG_CUDA_TAG`** (default **`v6.22.1`**), **`XMRIG_CUDA_SO_DEST`**, or **`XMRIG_CUDA_ARCH`** (same as numeric **`CMAKE_CUDA_ARCHITECTURES`**, e.g. **`75`** for Turing, **`89`** for some Ada). The script **removes `build/`** each run unless **`XMRIG_CUDA_KEEP_BUILD=1`**, so a failed configure does not stick with bad **`CUDA_ARCH`** cache.

   **CUDA 13+:** `nvcc` removed **`cudaDeviceProp.clockRate`** fields used by xmrig-cuda **v6.22.1**. The build script applies [`scripts/garuda/patches/xmrig-cuda-v6.22.1-cuda13-device-clocks.patch`](../scripts/garuda/patches/xmrig-cuda-v6.22.1-cuda13-device-clocks.patch) when **`nvcc`** reports major **≥ 13** and the tree is still unpatched. Set **`XMRIG_CUDA_SKIP_PATCH=1`** to skip (e.g. custom fork that already fixed this).

3. The script installs **`libxmrig-cuda.so`** next to **`XMRIG_BINARY`** when that path is set and executable.

## HashFarm integration

1. Set **`XMRIG_BINARY`** in `.env` to your **6.26.0** `xmrig` (see `scripts/common/env.template`).
2. After the plugin is beside that binary, enable CUDA in generated config:

   ```bash
   export XMRIG_ENABLE_CUDA=1
   ./scripts/garuda/xmrig-cpu.sh config
   ./scripts/garuda/xmrig-cpu.sh run
   ```

3. Tune **`threads` / `bfactor`** in `config.json` per [XMRig CUDA docs](https://xmrig.com/docs/miner/config/cuda); the script only enables a minimal **`{ "enabled": true, "nvml": true }`** block.

## Contributing a PR to `xmrig/xmrig-cuda`

Open a pull request only for an **upstream-worthy** change (bug fix, algorithm support, build fix, documentation). **Bumping the version label alone** does not create compatibility.

1. **Fork** [xmrig/xmrig-cuda](https://github.com/xmrig/xmrig-cuda) on GitHub.
2. **Clone your fork** and add `upstream`:  
   `git remote add upstream https://github.com/xmrig/xmrig-cuda.git`
3. **Branch** from current default:  
   `git fetch upstream && git checkout -b your-topic upstream/master`
4. **Commit** a minimal change with a clear message.
5. **Build** `libxmrig-cuda.so` and test loading it under **your XMRig** version (e.g. **6.26.0**), RandomX path, and regression check when CUDA is disabled.
6. **Push** and open **Compare & pull request** against **`xmrig/xmrig-cuda` `master`**.
7. In the PR description: problem, reproduction, **GPU model**, **driver / CUDA**, test logs, and risk notes. Follow maintainer feedback (CI, DCO, etc., if required).

For **HashFarm-only** mining you typically **do not** need an upstream PR—only a **correct local build** and config.
