from __future__ import annotations

import asyncio

from app import price_feed, settings


def test_price_feed_fallback_and_cache(monkeypatch) -> None:
    calls = {"cg": 0, "kr": 0}
    price_feed._CACHE.update(  # type: ignore[attr-defined]
        {"price": None, "source": None, "updated_at_monotonic": 0.0, "last_error": None}
    )
    monkeypatch.setattr(settings, "XMR_USD_SOURCES", ["coingecko", "kraken"])
    monkeypatch.setattr(settings, "XMR_USD_CACHE_TTL_SEC", 300.0)
    monkeypatch.setattr(settings, "XMR_USD_SOURCE_TIMEOUT_SEC", 1.0)

    async def bad(*_args, **_kwargs) -> float:
        calls["cg"] += 1
        raise RuntimeError("rate limited")

    async def good(*_args, **_kwargs) -> float:
        calls["kr"] += 1
        return 321.5

    monkeypatch.setattr(price_feed, "_from_coingecko", bad)
    monkeypatch.setattr(price_feed, "_from_kraken", good)
    monkeypatch.setitem(price_feed._PROVIDERS, "coingecko", bad)  # type: ignore[attr-defined]
    monkeypatch.setitem(price_feed._PROVIDERS, "kraken", good)  # type: ignore[attr-defined]

    got1 = asyncio.run(price_feed.get_xmr_usd(None))  # type: ignore[arg-type]
    assert got1["price"] == 321.5
    assert got1["source"] == "kraken"
    assert got1["cached"] is False
    assert calls == {"cg": 1, "kr": 1}

    got2 = asyncio.run(price_feed.get_xmr_usd(None))  # type: ignore[arg-type]
    assert got2["price"] == 321.5
    assert got2["cached"] is True
    assert calls == {"cg": 1, "kr": 1}


def test_price_feed_reports_error_when_all_fail(monkeypatch) -> None:
    price_feed._CACHE.update(  # type: ignore[attr-defined]
        {"price": None, "source": None, "updated_at_monotonic": 0.0, "last_error": None}
    )
    monkeypatch.setattr(settings, "XMR_USD_SOURCES", ["coingecko"])
    monkeypatch.setattr(settings, "XMR_USD_CACHE_TTL_SEC", 1.0)
    monkeypatch.setattr(settings, "XMR_USD_SOURCE_TIMEOUT_SEC", 1.0)

    async def bad(*_args, **_kwargs) -> float:
        raise RuntimeError("boom")

    monkeypatch.setattr(price_feed, "_from_coingecko", bad)
    monkeypatch.setitem(price_feed._PROVIDERS, "coingecko", bad)  # type: ignore[attr-defined]

    got = asyncio.run(price_feed.get_xmr_usd(None))  # type: ignore[arg-type]
    assert got["price"] is None
    assert got["source"] is None
    assert "coingecko" in str(got["error"])
