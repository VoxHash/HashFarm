from __future__ import annotations

import asyncio
import smtplib
import time
from email.message import EmailMessage
from typing import Any

from . import settings

_last_sent_at: dict[str, float] = {}
_rig_low_since: dict[str, float] = {}


def _can_send(key: str) -> bool:
    now = time.monotonic()
    last = _last_sent_at.get(key, 0.0)
    if now - last < settings.ALERT_EMAIL_COOLDOWN_SEC:
        return False
    _last_sent_at[key] = now
    return True


def _send_email(subject: str, body: str) -> None:
    if not settings.SMTP_HOST or not settings.ALERT_TO:
        return
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_USER or "hashfarm-monitor"
    msg["To"] = settings.ALERT_TO
    msg.set_content(body)
    if settings.SMTP_STARTTLS:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=30) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            if settings.SMTP_USER not in (None, ""):
                smtp.login(settings.SMTP_USER, settings.SMTP_PASS)
            smtp.send_message(msg)
    else:
        with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=30) as smtp:
            if settings.SMTP_USER not in (None, ""):
                smtp.login(settings.SMTP_USER, settings.SMTP_PASS)
            smtp.send_message(msg)


async def send_email_async(subject: str, body: str) -> None:
    await asyncio.to_thread(_send_email, subject, body)


async def evaluate(snapshot: dict[str, Any]) -> None:
    if not settings.ALERT_TO or not settings.SMTP_HOST:
        return
    now = time.monotonic()
    monero = snapshot.get("monero") or {}
    lag = int(monero.get("sync_lag_blocks") or 999)
    if monero.get("_error"):
        key = "monero_down"
        if _can_send(key):
            await send_email_async("HashFarm: monerod RPC error", str(monero.get("_error")))
    elif lag > settings.MONERO_MAX_SYNC_LAG_BLOCKS:
        key = "monero_lag"
        if _can_send(key):
            await send_email_async(
                "HashFarm: monerod sync lag",
                f"sync_lag_blocks={lag} (threshold {settings.MONERO_MAX_SYNC_LAG_BLOCKS})",
            )
    p2 = snapshot.get("p2pool") or {}
    if p2.get("error"):
        key = "p2pool_down"
        if _can_send(key):
            await send_email_async("HashFarm: P2Pool API unreachable", str(p2.get("error")))
    min_h = settings.ALERT_MIN_HASHRATE_HS
    if min_h > 0:
        for rig in snapshot.get("rigs") or []:
            label = str(rig.get("label") or "rig")
            hr = float(rig.get("hashrate_hs") or 0.0)
            if hr < min_h:
                since = _rig_low_since.setdefault(label, now)
                if now - since >= settings.ALERT_LOW_HASHRATE_CONSEC_SEC:
                    k = f"lowhr_{label}"
                    if _can_send(k):
                        await send_email_async(
                            f"HashFarm: low hashrate {label}",
                            f"hashrate_hs={hr} threshold={min_h} for >= {settings.ALERT_LOW_HASHRATE_CONSEC_SEC}s",
                        )
                        _rig_low_since[label] = now
            else:
                _rig_low_since.pop(label, None)
