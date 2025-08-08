from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass, field


@dataclass
class OrderbookSnapshot:
    bids: list[tuple[float, float]]  # price, qty
    asks: list[tuple[float, float]]


@dataclass
class MarketCache:
    orderbooks: dict[str, OrderbookSnapshot] = field(default_factory=dict)
    trades: dict[str, deque[tuple[float, float]]] = field(default_factory=dict)  # (price, qty)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    async def set_orderbook(self, symbol: str, snapshot: OrderbookSnapshot) -> None:
        async with self._lock:
            self.orderbooks[symbol] = snapshot

    async def append_trade(self, symbol: str, price: float, qty: float, maxlen: int = 1000) -> None:
        async with self._lock:
            dq = self.trades.setdefault(symbol, deque(maxlen=maxlen))
            dq.append((price, qty))


def atr(candles: list[dict], period: int = 14, method: str = "RMA") -> float:
    if not candles or len(candles) < 2:
        return 0.0
    trs: list[float] = []
    prev_close = candles[0]["close"]
    for c in candles[1:]:
        high, low, close = c["high"], c["low"], c["close"]
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


def volatility_regime(candles: list[dict]) -> str:
    return "quiet" if atr(candles) < 0.01 else "expansion"


def rolling_volume(candles: list[dict], n: int) -> float:
    if not candles:
        return 0.0
    return sum(c.get("volume", 0.0) for c in candles[-n:])


def spread_depth_stats(ob: OrderbookSnapshot) -> dict[str, float]:
    if not ob.bids or not ob.asks:
        return {"spread_bps": 0.0, "depth_at_10bps": 0.0, "depth_at_50bps": 0.0}
    best_bid = ob.bids[0][0]
    best_ask = ob.asks[0][0]
    mid = (best_bid + best_ask) / 2
    spread_bps = (best_ask - best_bid) / mid * 10_000

    def depth_at_bps(bps: float) -> float:
        target_price = mid * (1 + (bps / 10_000))
        depth = 0.0
        for price, qty in ob.asks:
            if price <= target_price:
                depth += qty
            else:
                break
        return depth

    return {
        "spread_bps": spread_bps,
        "depth_at_10bps": depth_at_bps(10),
        "depth_at_50bps": depth_at_bps(50),
    }
