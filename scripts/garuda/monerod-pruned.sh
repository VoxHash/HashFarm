#!/usr/bin/env bash
# Pruned monerod on Garuda Linux with ZMQ pub for P2Pool (gaming PC).
# Requires: monero-cli / monerod from distro or https://www.getmonero.org/downloads/
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# shellcheck source=/dev/null
[[ -f "${ROOT}/.env" ]] && source "${ROOT}/.env"
MONERO_DATA_DIR="${MONERO_DATA_DIR:-${HOME}/.bitmonero}"
RPC_BIND="${MONERO_RPC_BIND:-127.0.0.1}"
RPC_PORT="${MONERO_RPC_PORT:-18081}"
ZMQ_PUB="${MONERO_ZMQ_PUB:-tcp://127.0.0.1:18083}"
OUT_PEERS="${MONERO_OUT_PEERS:-64}"
IN_PEERS="${MONERO_IN_PEERS:-64}"

mkdir -p "${MONERO_DATA_DIR}"

MONEROD_BIN="${MONEROD_BIN:-monerod}"
MONEROD_RESOLVED=""
if command -v "${MONEROD_BIN}" >/dev/null 2>&1; then
  MONEROD_RESOLVED="$(command -v "${MONEROD_BIN}")"
elif [[ -x "${MONEROD_BIN}" ]]; then
  MONEROD_RESOLVED="${MONEROD_BIN}"
else
  for c in "${HOME}/.local/opt/monero-cli"*/monerod /usr/bin/monerod /usr/local/bin/monerod; do
    if [[ -x "${c}" ]]; then
      MONEROD_RESOLVED="${c}"
      break
    fi
  done
fi
if [[ -z "${MONEROD_RESOLVED}" ]]; then
  echo "monerod not found (install monerod or set MONEROD_BIN in .env to the full path)." >&2
  exit 1
fi

exec "${MONEROD_RESOLVED}" \
  --data-dir "${MONERO_DATA_DIR}" \
  --prune-blockchain \
  --rpc-bind-ip "${RPC_BIND}" \
  --rpc-bind-port "${RPC_PORT}" \
  --zmq-pub "${ZMQ_PUB}" \
  --out-peers "${OUT_PEERS}" \
  --in-peers "${IN_PEERS}" \
  --non-interactive \
  "$@"
