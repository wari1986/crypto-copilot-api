from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

import ccxt.async_support as ccxt

from app.core.config import settings


def to_ws_symbol(ccxt_symbol: str) -> str:
    return ccxt_symbol.replace("/", "")


def to_ccxt_symbol(ws_symbol: str) -> str:
    return ws_symbol[:-4] + "/" + ws_symbol[-4:]


class CcxtAdapter:
    def __init__(self, exchange: str = "bybit") -> None:
        klass = getattr(ccxt, exchange)
        self._client = klass(
            {"enableRateLimit": settings.ccxt_rate_limit, "options": {"defaultType": "spot"}},
        )

    async def close(self) -> None:
        await self._client.close()

    async def list_instruments(self, symbols: list[str] | None = None) -> list[dict[str, Any]]:
        markets = await self._client.load_markets()
        instruments: list[dict[str, Any]] = []
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
                },
            )
        return instruments

    async def latest_ticker(self, symbol: str) -> dict[str, Any]:
        return await self._client.fetch_ticker(symbol)

    async def fetch_markets_spot(self) -> list[dict[str, Any]]:
        markets = await self._client.load_markets()
        rows: list[dict[str, Any]] = []
        for symbol, m in markets.items():
            if not m.get("spot"):
                continue
            precision = m.get("precision", {})
            price_scale = precision.get("price")
            qty_scale = precision.get("amount")
            tick_size = Decimal(10) ** Decimal(-(price_scale or 0))
            lot_size = Decimal(10) ** Decimal(-(qty_scale or 0))
            maker = Decimal(str(m.get("maker", 0))) * Decimal(10_000)
            taker = Decimal(str(m.get("taker", 0))) * Decimal(10_000)
            settlement = m.get("quote")
            min_cost = m.get("limits", {}).get("cost", {}).get("min")
            min_amt = m.get("limits", {}).get("amount", {}).get("min")
            last = m.get("info", {}).get("lastPrice") or 0
            min_notional = None
            if min_cost is not None:
                min_notional = Decimal(str(min_cost))
            elif min_amt is not None and last:
                min_notional = Decimal(str(min_amt)) * Decimal(str(last))
            rows.append(
                {
                    "symbol": symbol,
                    "venue": settings.exchange,
                    "type": "spot",
                    "settlement": settlement,
                    "tick_size": tick_size,
                    "lot_size": lot_size,
                    "min_notional": min_notional,
                    "contract_size": None,
                    "price_scale": price_scale,
                    "qty_scale": qty_scale,
                    "maker_fee_bps": maker,
                    "taker_fee_bps": taker,
                    "max_leverage": None,
                },
            )
        return rows

    async def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1m",
        since: datetime | None = None,
        limit: int | None = 1000,
    ) -> list[dict[str, Any]]:
        since_ms = int(since.timestamp() * 1000) if since else None
        candles = await self._client.fetch_ohlcv(
            symbol,
            timeframe=timeframe,
            since=since_ms,
            limit=limit,
        )
        if not candles:
            return []

        out: list[dict[str, Any]] = []
        for c in candles:
            ts = datetime.fromtimestamp(c[0] / 1000, tz=UTC)
            o, h, low, cl, vol = map(lambda x: Decimal(str(x)), c[1:6])
            out.append(
                {
                    "ts": ts,
                    "open": o,
                    "high": h,
                    "low": low,
                    "close": cl,
                    "volume_base": vol,
                    "turnover_quote": vol * cl,
                },
            )
        return out

    async def fetch_l2_orderbook(self, symbol: str, limit: int = 50) -> dict[str, Any]:
        """Fetch level 2 order book depth for a symbol."""
        book = await self._client.fetch_order_book(symbol, limit=limit)
        ts = book.get("timestamp")
        ts_dt = (
            datetime.fromtimestamp(ts / 1000, tz=UTC) if ts is not None else datetime.now(UTC)
        )

        def _convert(rows: list[list[float]]) -> list[dict[str, Decimal]]:
            return [
                {"price": Decimal(str(p)), "volume": Decimal(str(v))} for p, v in rows
            ]

        bids = _convert(book.get("bids", [])[:limit])
        asks = _convert(book.get("asks", [])[:limit])
        return {"symbol": symbol, "ts": ts_dt, "bids": bids, "asks": asks}

    async def fetch_trades(
        self, symbol: str, since: datetime | None = None, limit: int = 200,
    ) -> list[dict[str, Any]]:
        """Fetch recent trades for a symbol."""
        since_ms = int(since.timestamp() * 1000) if since else None
        trades = await self._client.fetch_trades(symbol, since=since_ms, limit=limit)
        out: list[dict[str, Any]] = []
        for t in trades:
            ts = datetime.fromtimestamp(t.get("timestamp", 0) / 1000, tz=UTC)
            out.append(
                {
                    "ts": ts,
                    "price": Decimal(str(t.get("price"))),
                    "qty": Decimal(str(t.get("amount"))),
                    "side": t.get("side"),
                },
            )
        return out
