from __future__ import annotations

import re
from pathlib import Path
from typing import Any

# P2P sync progress lines, e.g. "Synced 2492624/3650893 (68%, …"
_SYNC_RE = re.compile(rb"Synced (\d+)/(\d+)")


def _tail_bytes(path: Path, max_bytes: int) -> bytes:
    if not path.is_file():
        return b""
    with path.open("rb") as f:
        f.seek(0, 2)
        size = f.tell()
        f.seek(max(0, size - max_bytes))
        return f.read()


def sync_heights_from_bitmonero_log(data_dir: str, *, max_read_bytes: int = 512_000) -> dict[str, Any] | None:
    """
    When monerod JSON-RPC returns an empty body for extended periods (common on HDD during sync),
    the last 'Synced height/target' line in bitmonero.log still reflects real progress.
    """
    root = Path(data_dir).expanduser()
    log_path = root / "bitmonero.log"
    chunk = _tail_bytes(log_path, max_read_bytes)
    if not chunk:
        return None
    matches = list(_SYNC_RE.finditer(chunk))
    if not matches:
        return None
    last = matches[-1]
    height = int(last.group(1))
    target = int(last.group(2))
    if height <= 0 or target <= 0:
        return None
    lag = max(0, target - height)
    return {
        "height": height,
        "target_height": target,
        "sync_lag_blocks": lag,
        "synchronized_flag": lag == 0,
    }
