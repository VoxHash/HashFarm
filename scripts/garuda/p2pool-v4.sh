#!/usr/bin/env bash
# Install or run P2Pool v4+ on Garuda Linux (x64). Downloads official release and verifies SHA256 from signed checksum file.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# shellcheck source=/dev/null
[[ -f "${ROOT}/.env" ]] && source "${ROOT}/.env"

P2POOL_VERSION="${P2POOL_VERSION:-v4.14}"
P2POOL_ASSET="p2pool-${P2POOL_VERSION}-linux-x64.tar.gz"
INSTALL_DIR="${P2POOL_INSTALL_DIR:-${HOME}/.local/opt/p2pool}"
SHA_URL="https://github.com/SChernykh/p2pool/releases/download/${P2POOL_VERSION}/sha256sums.txt.asc"
DL_URL="https://github.com/SChernykh/p2pool/releases/download/${P2POOL_VERSION}/${P2POOL_ASSET}"

WALLET_MAIN="${WALLET_MAIN:?Set WALLET_MAIN in .env}"
MONERO_HOST="${MONERO_HOST:-127.0.0.1}"
MONERO_RPC_PORT="${MONERO_RPC_PORT:-18081}"
MONERO_ZMQ_PORT="${MONERO_ZMQ_PORT:-18083}"
STRATUM_ADDR="${P2POOL_STRATUM_BIND:-0.0.0.0:${P2POOL_STRATUM_PORT:-3333}}"
P2P_ADDR="${P2POOL_P2P_BIND:-0.0.0.0:37889}"
DATA_API_DIR="${P2POOL_DATA_API_DIR:-${HOME}/.local/share/p2pool-data-api}"
NO_AUTODIFF_FLAG=()
if [[ "${P2POOL_NO_AUTODIFF:-0}" == "1" ]]; then
  NO_AUTODIFF_FLAG=(--no-autodiff)
fi

install_release() {
  mkdir -p "${INSTALL_DIR}" "${DATA_API_DIR}"
  local tmp
  tmp="$(mktemp -d)"
  echo "Downloading ${DL_URL}"
  curl -fsSL -o "${tmp}/${P2POOL_ASSET}" "${DL_URL}"
  curl -fsSL -o "${tmp}/sha256sums.txt.asc" "${SHA_URL}"
  local expected
  expected="$(
    P2POOL_ASSET="${P2POOL_ASSET}" SUM="${tmp}/sha256sums.txt.asc" python3 <<'PY'
import os, re, pathlib
text = pathlib.Path(os.environ["SUM"]).read_text(errors="replace")
name = os.environ["P2POOL_ASSET"]
m = re.search(r"Name:\s*" + re.escape(name) + r"\b.*?SHA256:\s*([0-9a-fA-F]+)", text, re.S)
print(m.group(1).lower() if m else "")
PY
  )"
  [[ -n "${expected}" ]] || { rm -rf "${tmp}"; echo "Could not parse SHA256 for ${P2POOL_ASSET}" >&2; exit 1; }
  ( cd "${tmp}" && echo "${expected}  ${P2POOL_ASSET}" | sha256sum -c - )
  tar -xzf "${tmp}/${P2POOL_ASSET}" -C "${tmp}"
  local bin
  bin="$(find "${tmp}" -type f -name p2pool 2>/dev/null | head -1)"
  [[ -n "${bin}" ]] || { rm -rf "${tmp}"; echo "p2pool binary not found in archive" >&2; exit 1; }
  install -m 0755 "${bin}" "${INSTALL_DIR}/p2pool-${P2POOL_VERSION}"
  ln -sfn "p2pool-${P2POOL_VERSION}" "${INSTALL_DIR}/p2pool"
  rm -rf "${tmp}"
  echo "Installed ${INSTALL_DIR}/p2pool"
}

cmd="${1:-run}"
case "${cmd}" in
  install)
    install_release
    ;;
  run)
    if [[ ! -x "${INSTALL_DIR}/p2pool" ]]; then
      echo "P2Pool not found; run: $0 install" >&2
      exit 1
    fi
    exec "${INSTALL_DIR}/p2pool" \
      --host "${MONERO_HOST}" \
      --rpc-port "${MONERO_RPC_PORT}" \
      --zmq-port "${MONERO_ZMQ_PORT}" \
      --wallet "${WALLET_MAIN}" \
      --stratum "${STRATUM_ADDR}" \
      --p2p "${P2P_ADDR}" \
      --data-api "${DATA_API_DIR}" \
      --local-api \
      "${NO_AUTODIFF_FLAG[@]}" \
      "${@:2}"
    ;;
  *)
    echo "Usage: $0 {install|run} [extra p2pool args]" >&2
    exit 1
    ;;
esac
