"""Pytest loads this before test modules; skip the background collector in tests."""

from __future__ import annotations

import os

os.environ.setdefault("HASHFARM_SKIP_LIFESPAN", "1")
