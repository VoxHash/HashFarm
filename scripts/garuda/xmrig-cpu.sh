#!/usr/bin/env bash
# Configure or build XMRig (CPU) on Garuda for RandomX -> local P2Pool stratum.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# shellcheck source=/dev/null
[[ -f "${ROOT}/.env" ]] && source "${ROOT}/.env"

WALLET_MAIN="${WALLET_MAIN:?Set WALLET_MAIN in .env}"
GAMING_PC_IP="${GAMING_PC_IP:?Set GAMING_PC_IP in .env}"
PORT="${P2POOL_STRATUM_PORT:-3333}"
RIG_ID="${XMRIG_RIG_ID:-garuda}"
API_PORT="${XMRIG_API_PORT:-18060}"
API_TOKEN="${XMRIG_API_TOKEN:?Set XMRIG_API_TOKEN in .env}"
CONFIG_OUT="${XMRIG_CONFIG_PATH:-${HOME}/.config/xmrig/config-p2pool.json}"
POOL_USER="${WALLET_MAIN}"
if [[ -n "${FIXED_DIFF:-}" ]]; then
  POOL_USER="${WALLET_MAIN}+${FIXED_DIFF}"
fi

POOL_URL="stratum+tcp://${GAMING_PC_IP}:${PORT}"
XMRIG_BIN="${XMRIG_BINARY:-${HOME}/.local/bin/xmrig}"

build_xmrig() {
  local src="${HOME}/src/xmrig"
  sudo pacman -S --needed --noconfirm base-devel cmake git libuv openssl hwloc >/dev/null 2>&1 || true
  mkdir -p "${HOME}/src"
  if [[ ! -d "${src}/.git" ]]; then
    git clone --depth 1 https://github.com/xmrig/xmrig.git "${src}"
  else
    git -C "${src}" pull --ff-only || true
  fi
  cmake -S "${src}" -B "${src}/build" -DCMAKE_BUILD_TYPE=Release -DWITH_HWLOC=ON
  cmake --build "${src}/build" -j"$(nproc)"
  install -Dm0755 "${src}/build/xmrig" "${HOME}/.local/bin/xmrig"
  echo "Built ${HOME}/.local/bin/xmrig"
}

write_config() {
  mkdir -p "$(dirname "${CONFIG_OUT}")"
  umask 077
  cat > "${CONFIG_OUT}" <<JSON
{
  "autosave": true,
  "cpu": {
    "enabled": true,
    "huge-pages": true,
    "huge-pages-jit": true,
    "hw-aes": null,
    "priority": null,
    "memory-pool": false,
    "yield": true,
    "max-threads-hint": 100,
    "asm": true
  },
  "randomx": {
    "mode": "auto",
    "1gb-pages": true,
    "rdmsr": true,
    "wrmsr": true,
    "cache_qos": false,
    "numa": true
  },
  "opencl": false,
  "cuda": false,
  "pools": [
    {
      "algo": "rx/0",
      "url": "${POOL_URL}",
      "user": "${POOL_USER}",
      "pass": "${RIG_ID}",
      "keepalive": true,
      "enabled": true,
      "tls": false
    }
  ],
  "http": {
    "enabled": true,
    "host": "0.0.0.0",
    "port": ${API_PORT},
    "access-token": "${API_TOKEN}",
    "restricted": true
  }
}
JSON
  chmod 0600 "${CONFIG_OUT}"
  echo "Wrote ${CONFIG_OUT}"
  echo "Optional: echo madvise | sudo tee /sys/kernel/mm/transparent_hugepage/enabled"
  echo "Optional MSR: sudo modprobe msr && sudo setcap cap_sys_rawio=ep ${HOME}/.local/bin/xmrig"
}

cmd="${1:-config}"
case "${cmd}" in
  build) build_xmrig ;;
  config) write_config ;;
  run)
    write_config >/dev/null
    [[ -x "${XMRIG_BIN}" ]] || {
      echo "XMRig not executable at ${XMRIG_BIN}. Run: $0 build   or set XMRIG_BINARY in .env" >&2
      exit 1
    }
    exec "${XMRIG_BIN}" -c "${CONFIG_OUT}"
    ;;
  *)
    echo "Usage: $0 {build|config|run}" >&2
    exit 1
    ;;
esac
