from __future__ import annotations

import asyncio
from typing import Any

from app.core.config import settings
from app.services.market_data.ccxt_adapter import CcxtAdapter


class MarketSnapshotService:
    """Fetches a full market snapshot for configured symbols."""

    def __init__(self) -> None:
        self._adapter = CcxtAdapter(settings.exchange)
        self._latest: dict[str, Any] | None = None
        self._lock = asyncio.Lock()

    async def refresh(self, symbols: list[str]) -> dict[str, Any]:
        async with self._lock:
            snapshots: dict[str, Any] = {}
            for sym in symbols:
                snapshots[sym] = await self._fetch_symbol(sym)
            self._latest = snapshots
            return snapshots

    async def _fetch_symbol(self, symbol: str) -> dict[str, Any]:
        candle = {}
        try:
            # Grab the most recent closed 1h candle
            candles = await self._adapter.fetch_ohlcv(symbol, timeframe="1h", limit=1)
            candle = candles[-1] if candles else {}
        except Exception:
            candle = {}

        try:
            orderbook = await self._adapter.fetch_orderbook(
                symbol, depth=settings.ws_orderbook_levels,
            )
        except Exception:
            orderbook = {}

        try:
            trades = await self._adapter.fetch_trades(symbol, limit=200)
        except Exception:
            trades = []

        try:
            funding_rate = await self._adapter.fetch_funding_rate(symbol)
        except Exception:
            funding_rate = None

        return {
            "candle_1h": candle,
            "orderbook": orderbook,
            "trades": trades,
            "funding_rate": float(funding_rate) if funding_rate is not None else None,
        }

    def latest(self) -> dict[str, Any] | None:
        return self._latest


market_snapshot_service = MarketSnapshotService()
