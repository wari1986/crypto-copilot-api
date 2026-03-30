from __future__ import annotations

from datetime import UTC, datetime, timedelta
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
        raw = await self._client.fetch_l2_order_book(symbol, limit=limit)
        bids = [
            {"price": Decimal(str(price)), "qty": Decimal(str(qty))}
            for price, qty in raw.get("bids", [])
        ]
        asks = [
            {"price": Decimal(str(price)), "qty": Decimal(str(qty))}
            for price, qty in raw.get("asks", [])
        ]
        best_bid = bids[0]["price"] if bids else None
        best_ask = asks[0]["price"] if asks else None
        mid = None
        if best_bid is not None and best_ask is not None:
            mid = (best_bid + best_ask) / Decimal(2)
        return {
            "symbol": symbol,
            "best_bid": best_bid,
            "best_ask": best_ask,
            "mid": mid,
            "bids": bids,
            "asks": asks,
        }

    async def fetch_trades(
        self,
        symbol: str,
        since: datetime | None = None,
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        since_ms = int(since.timestamp() * 1000) if since else None
        trades = await self._client.fetch_trades(symbol, since=since_ms, limit=limit)
        out: list[dict[str, Any]] = []
        for trade in trades:
            timestamp = trade.get("timestamp")
            price = trade.get("price")
            amount = trade.get("amount")
            if timestamp is None or price is None or amount is None:
                continue
            out.append(
                {
                    "trade_id": str(trade.get("id") or trade.get("trade_id") or ""),
                    "ts": datetime.fromtimestamp(timestamp / 1000, tz=UTC),
                    "price": Decimal(str(price)),
                    "qty": Decimal(str(amount)),
                    "side": str(trade.get("side") or "buy").lower(),
                },
            )
        return out

    async def backfill_ohlcv_1m(self, symbol: str, lookback_days: int) -> list[dict[str, Any]]:
        cursor = datetime.now(UTC) - timedelta(days=lookback_days)
        rows: list[dict[str, Any]] = []
        while True:
            batch = await self.fetch_ohlcv(symbol, timeframe="1m", since=cursor, limit=1000)
            if not batch:
                break
            for row in batch:
                if not rows or row["ts"] > rows[-1]["ts"]:
                    rows.append(row)
            if len(batch) < 1000:
                break
            cursor = batch[-1]["ts"] + timedelta(minutes=1)
        return rows
