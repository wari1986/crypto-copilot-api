from __future__ import annotations

from typing import Any, Dict, List, Optional

import ccxt.async_support as ccxt

from app.core.config import settings


class CcxtAdapter:
    def __init__(self, exchange: str = "bybit") -> None:
        klass = getattr(ccxt, exchange)
        self._client = klass(
            {"enableRateLimit": settings.ccxt_rate_limit, "options": {"defaultType": "spot"}}
        )

    async def close(self) -> None:
        await self._client.close()

    async def list_instruments(self, symbols: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        markets = await self._client.load_markets()
        instruments: List[Dict[str, Any]] = []
        for symbol, m in markets.items():
            if symbols and symbol not in symbols:
                continue
            instruments.append(
                {
                    "symbol": symbol,
                    "base": m.get("base"),
                    "quote": m.get("quote"),
                    "active": m.get("active", True),
                    "tick_size": m.get("precision", {}).get("price"),
                    "step_size": m.get("precision", {}).get("amount"),
                }
            )
        return instruments

    async def latest_ticker(self, symbol: str) -> Dict[str, Any]:
        return await self._client.fetch_ticker(symbol)

    async def historical_candles(
        self, symbol: str, timeframe: str, since: Optional[int] = None, limit: int = 500
    ) -> List[Dict[str, Any]]:
        candles = await self._client.fetch_ohlcv(
            symbol, timeframe=timeframe, since=since, limit=limit
        )
        return [
            {"ts": c[0], "open": c[1], "high": c[2], "low": c[3], "close": c[4], "volume": c[5]}
            for c in candles
        ]
