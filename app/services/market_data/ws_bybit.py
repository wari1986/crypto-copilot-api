from __future__ import annotations

import asyncio
from typing import Any, AsyncIterator, Dict, List


class BybitWsClient:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._running = False
        self._last_heartbeat: float | None = None

    async def subscribe_trades(self, symbol: str) -> AsyncIterator[Dict[str, Any]]:
        _ = symbol
        # Stub stream
        while False:
            yield {}

    async def subscribe_orderbook(self, symbol: str) -> AsyncIterator[Dict[str, Any]]:
        _ = symbol
        # Stub stream
        while False:
            yield {}

    def last_heartbeat(self) -> float | None:
        return self._last_heartbeat
