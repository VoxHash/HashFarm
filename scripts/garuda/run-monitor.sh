#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
set -a
# shellcheck source=/dev/null
source "${ROOT}/.env"
set +a
BIND="${MONITOR_BIND:-0.0.0.0}"
PORT="${MONITOR_PORT:-8787}"
if [[ ! -x "${ROOT}/monitor/.venv/bin/uvicorn" ]]; then
  echo "Missing monitor venv. Run: cd \"${ROOT}/monitor\" && python -m venv .venv && .venv/bin/pip install -r requirements.txt" >&2
  exit 1
fi
cd "${ROOT}/monitor"
exec "${ROOT}/monitor/.venv/bin/uvicorn" app.main:app --host "${BIND}" --port "${PORT}"
