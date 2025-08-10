from __future__ import annotations

from typing import Any
from datetime import datetime, timezone, timedelta
from decimal import Decimal

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
                }
            )
        return rows

    async def backfill_ohlcv_1m(self, symbol: str, lookback_days: int, page_limit: int = 1000) -> list[dict[str, Any]]:
        now = datetime.now(timezone.utc)
        since = int((now - timedelta(days=lookback_days)).timestamp() * 1000)
        out: list[dict[str, Any]] = []
        while True:
            candles = await self._client.fetch_ohlcv(symbol, timeframe="1m", since=since, limit=page_limit)
            if not candles:
                break
            for c in candles:
                ts = datetime.fromtimestamp(c[0] / 1000, tz=timezone.utc)
                o, h, l, cl, vol = map(lambda x: Decimal(str(x)), c[1:6])
                out.append(
                    {
                        "ts": ts,
                        "open": o,
                        "high": h,
                        "low": l,
                        "close": cl,
                        "volume_base": vol,
                        "turnover_quote": vol * cl,
                    }
                )
            since = candles[-1][0] + 1
        return out
