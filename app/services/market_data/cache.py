from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any


@dataclass
class OrderbookSnapshot:
    bids: list[tuple[Decimal, Decimal]]  # price, qty
    asks: list[tuple[Decimal, Decimal]]


@dataclass
class MarketCache:
    orderbooks: dict[str, OrderbookSnapshot] = field(default_factory=dict)
    trades: dict[str, deque[tuple[Decimal, Decimal]]] = field(default_factory=dict)  # (price, qty)
    tickers: dict[str, dict[str, Decimal | None | Any]] = field(default_factory=dict)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    async def set_orderbook(self, symbol: str, snapshot: OrderbookSnapshot) -> None:
        async with self._lock:
            self.orderbooks[symbol] = snapshot

    async def append_trade(self, symbol: str, price: Decimal, qty: Decimal, maxlen: int = 1000) -> None:
        async with self._lock:
            dq = self.trades.setdefault(symbol, deque(maxlen=maxlen))
            dq.append((price, qty))

    async def set_ticker(self, symbol: str, ticker: dict[str, Decimal | None | Any]) -> None:
        async with self._lock:
            self.tickers[symbol] = ticker


def atr(candles: list[dict[str, Decimal]], period: int = 14, method: str = "RMA") -> float:
    if not candles or len(candles) < 2:
        return 0.0
    trs: list[float] = []
    prev_close = float(candles[0]["close"])
    for c in candles[1:]:
        high = float(c["high"])
        low = float(c["low"])
        close = float(c["close"])
        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        trs.append(tr)
        prev_close = close
    if not trs:
        return 0.0
    period = min(period, len(trs))
    # RMA approximation
    rma = sum(trs[:period]) / period
    alpha = 1 / period
    for v in trs[period:]:
        rma = (rma * (1 - alpha)) + (v * alpha)
    return rma


def volatility_regime(candles: list[dict[str, Decimal]]) -> str:
    return "quiet" if atr(candles) < 0.01 else "expansion"


def rolling_volume(candles: list[dict[str, Decimal]], n: int) -> float:
    if not candles:
        return 0.0
    return sum(float(c.get("volume", Decimal("0"))) for c in candles[-n:])


def spread_depth_stats(ob: OrderbookSnapshot) -> dict[str, float]:
    if not ob.bids or not ob.asks:
        return {"spread_bps": 0.0, "depth_at_10bps": 0.0, "depth_at_50bps": 0.0}
    best_bid = ob.bids[0][0]
    best_ask = ob.asks[0][0]
    mid = (best_bid + best_ask) / Decimal(2)
    spread_bps = float((best_ask - best_bid) / mid * Decimal(10_000))

    def depth_at_bps(bps: float) -> float:
        target_price = mid * (Decimal(1) + (Decimal(str(bps)) / Decimal(10_000)))
        depth = 0.0
        for price, qty in ob.asks:
            if price <= target_price:
                depth += float(qty)
            else:
                break
        return depth

    return {
        "spread_bps": spread_bps,
        "depth_at_10bps": depth_at_bps(10),
        "depth_at_50bps": depth_at_bps(50),
    }
