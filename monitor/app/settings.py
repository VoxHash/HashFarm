from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
_repo_env = REPO_ROOT / ".env"
if _repo_env.is_file():
    # Repo .env must win over stray exported vars (e.g. old MONERO_DATA_DIR in a shell profile).
    load_dotenv(_repo_env, override=True)
_cwd = Path.cwd()
for _extra in (_cwd / ".env", _cwd.parent / ".env"):
    if _extra.is_file() and _extra.resolve() != _repo_env.resolve():
        load_dotenv(_extra, override=True)


def _f(name: str, default: float | None = None) -> float | None:
    v = os.getenv(name)
    if v is None or v == "":
        return default
    return float(v)


def _i(name: str, default: int) -> int:
    v = os.getenv(name)
    if v is None or v == "":
        return default
    return int(v)


def _csv(name: str, default: str = "") -> list[str]:
    raw = os.getenv(name, default)
    return [x.strip() for x in raw.split(",") if x.strip()]


def _csv_float(name: str, default: str = "") -> list[float]:
    out: list[float] = []
    for x in _csv(name, default):
        try:
            out.append(float(x))
        except ValueError:
            out.append(0.0)
    return out


MONERO_RPC_URL = os.getenv("MONERO_RPC_URL", "http://127.0.0.1:18081/json_rpc")
MONERO_RPC_TIMEOUT_SEC = max(5.0, min(600.0, float(os.getenv("MONERO_RPC_TIMEOUT_SEC", "60"))))
MONERO_RPC_STALE_TTL_SEC = max(30.0, min(3600.0, float(os.getenv("MONERO_RPC_STALE_TTL_SEC", "300"))))
MONERO_DATA_DIR = (os.getenv("MONERO_DATA_DIR") or "").strip()
P2POOL_STRATUM_URL = os.getenv("P2POOL_STRATUM_URL", "http://127.0.0.1:3333").rstrip("/")
WALLET_MAIN = os.getenv("WALLET_MAIN", "")

XMRIG_API_URLS = [u.strip() for u in os.getenv("XMRIG_API_URLS", "").split(",") if u.strip()]
_labels = [x.strip() for x in os.getenv("XMRIG_RIG_LABELS", "").split(",") if x.strip()]
XMRIG_RIG_LABELS = _labels + [f"rig_{i}" for i in range(len(_labels), len(XMRIG_API_URLS))]
XMRIG_API_TOKEN = os.getenv("XMRIG_API_TOKEN", "")
XMRIG_API_TIMEOUT_SEC = max(1.0, min(20.0, float(os.getenv("XMRIG_API_TIMEOUT_SEC", "5"))))

RIG_TELEMETRY_URLS = _csv("RIG_TELEMETRY_URLS", "")
RIG_TELEMETRY_TOKEN = os.getenv("RIG_TELEMETRY_TOKEN", "")
RIG_TELEMETRY_TIMEOUT_SEC = max(1.0, min(20.0, float(os.getenv("RIG_TELEMETRY_TIMEOUT_SEC", "3"))))
RIG_TELEMETRY_STALE_SEC = max(10.0, min(3600.0, float(os.getenv("RIG_TELEMETRY_STALE_SEC", "45"))))

ELECTRICITY_USD_PER_KWH = float(os.getenv("ELECTRICITY_USD_PER_KWH", "0.12"))
WATTS = [
    _f("WATTS_GAMING_PC", 0.0) or 0.0,
    _f("WATTS_LAPTOP", 0.0) or 0.0,
    _f("WATTS_MAC_MINI", 0.0) or 0.0,
]

XMR_USD_SOURCES = _csv("XMR_USD_SOURCES", "coingecko,kraken,cryptocompare")
XMR_USD_CACHE_TTL_SEC = max(5.0, min(3600.0, float(os.getenv("XMR_USD_CACHE_TTL_SEC", "300"))))
XMR_USD_SOURCE_TIMEOUT_SEC = max(1.0, min(20.0, float(os.getenv("XMR_USD_SOURCE_TIMEOUT_SEC", "8"))))

SAFETY_ENABLE_AUTOMATION = os.getenv("SAFETY_ENABLE_AUTOMATION", "0") == "1"
SAFETY_DRY_RUN = os.getenv("SAFETY_DRY_RUN", "1") == "1"
SAFETY_BREACH_CONSEC_SEC = max(5, _i("SAFETY_BREACH_CONSEC_SEC", 30))
SAFETY_RECOVERY_CONSEC_SEC = max(5, _i("SAFETY_RECOVERY_CONSEC_SEC", 120))
SAFETY_ACTION_COOLDOWN_SEC = max(5, _i("SAFETY_ACTION_COOLDOWN_SEC", 120))
SAFETY_MISSING_TELEMETRY_CONSEC_SEC = max(5, _i("SAFETY_MISSING_TELEMETRY_CONSEC_SEC", 120))
SAFETY_MAX_CPU_TEMP_C = _csv_float("SAFETY_MAX_CPU_TEMP_C", "")
SAFETY_MAX_GPU_TEMP_C = _csv_float("SAFETY_MAX_GPU_TEMP_C", "")
SAFETY_MAX_POWER_W = _csv_float("SAFETY_MAX_POWER_W", "")

MONERO_MAX_SYNC_LAG_BLOCKS = _i("MONERO_MAX_SYNC_LAG_BLOCKS", 2)
ALERT_TO = os.getenv("ALERT_TO", "")
ALERT_MIN_HASHRATE_HS = _f("ALERT_MIN_HASHRATE_HS", 0.0) or 0.0
ALERT_LOW_HASHRATE_CONSEC_SEC = _i("ALERT_LOW_HASHRATE_CONSEC_SEC", 600)
ALERT_EMAIL_COOLDOWN_SEC = _i("ALERT_EMAIL_COOLDOWN_SEC", 900)

SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = _i("SMTP_PORT", 587)
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
SMTP_STARTTLS = os.getenv("SMTP_STARTTLS", "1") == "1"

POLL_INTERVAL_SEC = _i("POLL_INTERVAL_SEC", 5)

BLOCK_TIME_SEC = 120.0

# Time-series (Phase B): append-only SQLite under monitor/data/ by default
METRICS_ENABLED = os.getenv("METRICS_ENABLED", "1") == "1"
METRICS_SQLITE_PATH = os.getenv(
    "METRICS_SQLITE_PATH",
    str(REPO_ROOT / "monitor" / "data" / "metrics.sqlite"),
)
METRICS_RETENTION_DAYS = _i("METRICS_RETENTION_DAYS", 7)

# /ready returns 503 if snapshot is older than this (seconds)
READY_MAX_SNAPSHOT_AGE_SEC = _i("READY_MAX_SNAPSHOT_AGE_SEC", max(60, POLL_INTERVAL_SEC * 6))
