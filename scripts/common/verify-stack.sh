#!/usr/bin/env bash
# Read-only checks: monerod sync, P2Pool stratum HTTP, XMRig APIs, aggregate hashrate.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="${ROOT}/.env"
if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Missing ${ENV_FILE}. Copy scripts/common/env.template to .env and edit." >&2
  exit 1
fi
# shellcheck source=/dev/null
source "${ENV_FILE}"

MONERO_RPC_URL="${MONERO_RPC_URL:-http://127.0.0.1:18081/json_rpc}"
P2POOL_STRATUM_URL="${P2POOL_STRATUM_URL:-http://127.0.0.1:3333}"
XMRIG_API_URLS="${XMRIG_API_URLS:?Set XMRIG_API_URLS in .env}"
XMRIG_API_TOKEN="${XMRIG_API_TOKEN:-}"

rpc() {
  local method="$1"
  local params="${2:-{}}"
  curl -sS -X POST "${MONERO_RPC_URL}" -H 'Content-Type: application/json' \
    -d "{\"jsonrpc\":\"2.0\",\"id\":\"v\",\"method\":\"${method}\",\"params\":${params}}"
}

echo "=== monerod ${MONERO_RPC_URL} ==="
INFO="$(rpc get_info)"
echo "${INFO}" | python3 -c 'import json,sys; j=json.load(sys.stdin); r=j.get("result")or{}; \
assert "error" not in j, j.get("error"); \
print("height", r.get("height"), "target_height", r.get("target_height"), "difficulty", r.get("difficulty")); \
print("status", r.get("status"), "incoming_connections", r.get("incoming_connections_count"))'

echo ""
echo "=== P2Pool local stratum ${P2POOL_STRATUM_URL}/local/stratum ==="
curl -sS -m 5 "${P2POOL_STRATUM_URL}/local/stratum" | python3 -m json.tool 2>/dev/null || echo "(unavailable)"

echo ""
echo "=== XMRig miners (hashrate.total) ==="
IFS=',' read -r -a URLS <<< "${XMRIG_API_URLS}"
total=0
for base in "${URLS[@]}"; do
  base="${base// /}"
  [[ -z "${base}" ]] && continue
  hdr=()
  if [[ -n "${XMRIG_API_TOKEN}" ]]; then
    hdr=(-H "Authorization: Bearer ${XMRIG_API_TOKEN}")
  fi
  body=""
  for path in /2/summary /1/summary; do
    if body="$(curl -sS -m 3 "${hdr[@]}" "${base}${path}" 2>/dev/null)"; then
      if echo "${body}" | python3 -c "import json,sys; json.load(sys.stdin)" 2>/dev/null; then
        echo "${base}${path}"
        echo "${body}" | python3 -m json.tool 2>/dev/null | head -n 40
        h="$(echo "${body}" | python3 -c "import json,sys; d=json.load(sys.stdin); print(int(d.get('hashrate',{}).get('total',[0])[0] or 0))" 2>/dev/null || echo 0)"
        total=$((total + h))
        break
      fi
    fi
  done
done
echo ""
echo "Aggregate hashrate.total[0] (H/s): ${total}"
