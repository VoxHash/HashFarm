#!/usr/bin/env bash
# Build libxmrig-cuda.so from xmrig/xmrig-cuda for use with XMRig 6.26+ (plugin API v4).
# Requires: NVIDIA driver, CUDA toolkit with nvcc (e.g. Arch: sudo pacman -S cuda).
# After build, copies the .so next to your xmrig binary unless XMRIG_CUDA_SO_DEST is set.
set -euo pipefail

_REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# shellcheck source=/dev/null
[[ -f "${_REPO}/.env" ]] && source "${_REPO}/.env"

TAG="${XMRIG_CUDA_TAG:-v6.22.1}"
SRC="${XMRIG_CUDA_SRC:-}"
BUILD_DIR=""
OUT_SO=""

# Arch / pacman "cuda" installs nvcc under /opt/cuda/bin (not on default PATH).
_cuda_bin_prepend() {
  local d=""
  if [[ -n "${CUDA_HOME:-}" && -x "${CUDA_HOME}/bin/nvcc" ]]; then
    d="${CUDA_HOME}/bin"
  elif [[ -n "${CUDA_PATH:-}" && -x "${CUDA_PATH}/bin/nvcc" ]]; then
    d="${CUDA_PATH}/bin"
  elif [[ -x /opt/cuda/bin/nvcc ]]; then
    d="/opt/cuda/bin"
  fi
  if [[ -n "${d}" ]]; then
    export PATH="${d}:${PATH}"
  fi
}
_cuda_bin_prepend

if [[ -z "${SRC}" ]]; then
  echo "Set XMRIG_CUDA_SRC to your plugin source tree (e.g. /home/you/Desktop/xmrig-cuda-6.22.1)." >&2
  echo "Optional: XMRIG_CUDA_TAG=${TAG} (git tag to checkout when SRC is a clone)." >&2
  exit 1
fi

if ! command -v nvcc >/dev/null 2>&1; then
  echo "nvcc not found. Install CUDA (e.g. sudo pacman -S cuda) and/or set CUDA_HOME to the toolkit root." >&2
  echo "On Arch, nvcc is usually /opt/cuda/bin/nvcc — this script prepends that path when it exists." >&2
  exit 1
fi

# xmrig-cuda uses -DCUDA_ARCH (semicolon list, e.g. 75;86), NOT CMAKE_CUDA_ARCHITECTURES, for nvcc
# --generate-code. Its default list includes 50; CUDA 12+ nvcc dropped sm_50 → "Unsupported gpu architecture 'compute_50'".
# sm_86 = RTX 30x0 (except some 3050s), A4000, etc.
ARCH="${XMRIG_CUDA_ARCH:-${CMAKE_CUDA_ARCHITECTURES:-86}}"
if [[ ! -d "${SRC}/.git" ]] && [[ ! -f "${SRC}/CMakeLists.txt" ]]; then
  echo "Not a valid xmrig-cuda source directory: ${SRC}" >&2
  exit 1
fi

# Tarball trees often have no .git; only fetch/checkout when this is a real clone.
if git -C "${SRC}" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git -C "${SRC}" fetch --tags origin 2>/dev/null || true
  if ! git -C "${SRC}" checkout -f "${TAG}" 2>/dev/null; then
    echo "Note: could not checkout ${TAG}; building sources as they are on disk." >&2
  fi
fi

# CUDA 13+ removed cudaDeviceProp::clockRate / memoryClockRate (nvcc error on v6.22.1 sources).
_nv_major="$(nvcc --version 2>/dev/null | sed -n 's/.*release \([0-9][0-9]*\)\..*/\1/p' | head -1)"
_patch="${_REPO}/scripts/garuda/patches/xmrig-cuda-v6.22.1-cuda13-device-clocks.patch"
if [[ "${XMRIG_CUDA_SKIP_PATCH:-0}" != "1" ]] && [[ "${_nv_major:-0}" -ge 13 ]] && [[ -f "${_patch}" ]]; then
  if ! grep -q 'cudaDevAttrClockRate' "${SRC}/src/cuda_extra.cu" 2>/dev/null; then
    echo "Applying CUDA ${_nv_major}.x device clock patch (cudaDeviceGetAttribute) to xmrig-cuda sources…"
    patch -d "${SRC}" -p1 -N < "${_patch}" || {
      echo "Patch failed; if sources differ from v6.22.1, set XMRIG_CUDA_SKIP_PATCH=1 or fix cuda_extra.cu manually." >&2
      exit 1
    }
  fi
fi

BUILD_DIR="${SRC}/build"
if [[ "${XMRIG_CUDA_KEEP_BUILD:-0}" != "1" ]]; then
  rm -rf "${BUILD_DIR}"
fi
cmake -S "${SRC}" -B "${BUILD_DIR}" -DCMAKE_BUILD_TYPE=Release \
  "-DCUDA_ARCH=${ARCH}" \
  "-DCMAKE_CUDA_ARCHITECTURES=${ARCH}"
cmake --build "${BUILD_DIR}" -j"$(nproc)"

OUT_SO="${BUILD_DIR}/libxmrig-cuda.so"
[[ -f "${OUT_SO}" ]] || {
  echo "Expected ${OUT_SO} missing after build." >&2
  exit 1
}

DEST="${XMRIG_CUDA_SO_DEST:-}"
if [[ -z "${DEST}" ]]; then
  XBIN="${XMRIG_BINARY:-${HOME}/.local/bin/xmrig}"
  if [[ -x "${XBIN}" ]]; then
    DEST="$(cd "$(dirname "${XBIN}")" && pwd)/libxmrig-cuda.so"
  else
    echo "Built ${OUT_SO}. Set XMRIG_BINARY or XMRIG_CUDA_SO_DEST to copy the plugin next to xmrig." >&2
    exit 0
  fi
fi

install -Dm0755 "${OUT_SO}" "${DEST}"
echo "Installed CUDA plugin to ${DEST}"
echo "Run: XMRIG_ENABLE_CUDA=1 ${_REPO}/scripts/garuda/xmrig-cpu.sh config   then ${_REPO}/scripts/garuda/xmrig-cpu.sh run"
