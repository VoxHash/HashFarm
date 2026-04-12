from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env", override=False)
# If uvicorn is started with cwd=monitor/, repo .env may still be one level up (override=False keeps existing vars).
_cwd = Path.cwd()
for _extra in (_cwd / ".env", _cwd.parent / ".env"):
    if _extra.is_file():
        load_dotenv(_extra, override=False)


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


MONERO_RPC_URL = os.getenv("MONERO_RPC_URL", "http://127.0.0.1:18081/json_rpc")
MONERO_RPC_TIMEOUT_SEC = max(5.0, min(300.0, float(os.getenv("MONERO_RPC_TIMEOUT_SEC", "60"))))
MONERO_RPC_STALE_TTL_SEC = max(30.0, min(3600.0, float(os.getenv("MONERO_RPC_STALE_TTL_SEC", "300"))))
P2POOL_STRATUM_URL = os.getenv("P2POOL_STRATUM_URL", "http://127.0.0.1:3333").rstrip("/")
WALLET_MAIN = os.getenv("WALLET_MAIN", "")

XMRIG_API_URLS = [u.strip() for u in os.getenv("XMRIG_API_URLS", "").split(",") if u.strip()]
_labels = [x.strip() for x in os.getenv("XMRIG_RIG_LABELS", "").split(",") if x.strip()]
XMRIG_RIG_LABELS = _labels + [f"rig_{i}" for i in range(len(_labels), len(XMRIG_API_URLS))]
XMRIG_API_TOKEN = os.getenv("XMRIG_API_TOKEN", "")

ELECTRICITY_USD_PER_KWH = float(os.getenv("ELECTRICITY_USD_PER_KWH", "0.12"))
WATTS = [
    _f("WATTS_GAMING_PC", 0.0) or 0.0,
    _f("WATTS_LAPTOP", 0.0) or 0.0,
    _f("WATTS_MAC_MINI", 0.0) or 0.0,
]

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
