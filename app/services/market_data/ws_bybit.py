from __future__ import annotations

import asyncio
import json
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

import websockets

from app.core.config import settings
from app.db.repositories.orderbook import OrderBookRepository
from app.db.repositories.tickers import TickersRepository
from app.db.repositories.trades import TradesRepository
from app.services.market_data.cache import MarketCache, OrderbookSnapshot
from app.services.market_data.ccxt_adapter import to_ccxt_symbol


class BybitWs:
    def __init__(self, cache: MarketCache) -> None:
        self._cache = cache
        self._closing = asyncio.Event()

    async def _connect(self):
        return await websockets.connect(settings.ws_public_url, ping_interval=20, ping_timeout=20)

    async def _run(self, topics: list[str], handler) -> None:
        backoff = 1
        while not self._closing.is_set():
            try:
                async with await self._connect() as ws:
                    await ws.send(json.dumps({"op": "subscribe", "args": topics}))
                    async for raw in ws:
                        msg = json.loads(raw)
                        await handler(msg)
                        if self._closing.is_set():
                            break
                backoff = 1
            except Exception:
                await asyncio.sleep(min(backoff, 30))
                backoff *= 2

    async def start_tickers(self, symbols: list[str], db_session_factory) -> None:
        topics = [f"tickers.{s.replace('/', '')}" for s in symbols]

        async def on_ticker(msg: dict[str, Any]) -> None:
            data = msg.get("data")
            if isinstance(data, list):
                for d in data:
                    await self._process_ticker(d, db_session_factory)
            elif isinstance(data, dict):
                await self._process_ticker(data, db_session_factory)

        await self._run(topics, on_ticker)

    async def _process_ticker(self, d: dict[str, Any], db_session_factory) -> None:
        symbol_ws = d.get("symbol")
        if not symbol_ws:
            return
        symbol = to_ccxt_symbol(symbol_ws)
        bid = Decimal(d.get("bid1Price") or d.get("bidPrice") or 0)
        ask = Decimal(d.get("ask1Price") or d.get("askPrice") or 0)
        last = Decimal(d.get("lastPrice") or 0)
        mid = (bid + ask) / Decimal(2) if bid and ask else last
        spread_bps = (ask - bid) / mid * Decimal(10_000) if bid and ask and mid else Decimal(0)
        ts = datetime.now(UTC)
        row = {
            "ts": ts,
            "last": last,
            "bid": bid,
            "ask": ask,
            "mid": mid,
            "spread_bps": spread_bps,
            "day_vol_quote": None,
        }
        await self._cache.set_ticker(symbol, row)
        async with db_session_factory() as db:  # type: ignore[misc]
            from sqlalchemy import select

            from app.db.models import Instrument

            res = await db.execute(select(Instrument.id).where(Instrument.symbol == symbol))
            inst_id = res.scalar_one_or_none()
            if inst_id is None:
                return
            await TickersRepository(db).insert_ticker(inst_id, row)

    async def start_orderbook(self, symbols: list[str], depth: int, db_session_factory) -> None:
        topics = [f"orderbook.{depth}.{s.replace('/', '')}" for s in symbols]

        async def on_ob(msg: dict[str, Any]) -> None:
            data = msg.get("data")
            ts = datetime.now(UTC)
            if not data:
                return
            if isinstance(data, dict) and data.get("type") == "snapshot":
                await self._process_ob_snapshot(data, ts, db_session_factory)
            elif isinstance(data, dict):
                await self._process_ob_delta(data, ts, db_session_factory)

        await self._run(topics, on_ob)

    async def _process_ob_snapshot(self, data: dict[str, Any], ts: datetime, db_session_factory) -> None:
        symbol = to_ccxt_symbol(data.get("s") or data.get("symbol"))
        bids = [(Decimal(px), Decimal(qty)) for px, qty in data.get("b", [])]
        asks = [(Decimal(px), Decimal(qty)) for px, qty in data.get("a", [])]
        snapshot_id = str(uuid.uuid4())
        await self._cache.set_orderbook(symbol, OrderbookSnapshot(bids=bids, asks=asks))
        async with db_session_factory() as db:  # type: ignore[misc]
            from sqlalchemy import select

            from app.db.models import Instrument

            res = await db.execute(select(Instrument.id).where(Instrument.symbol == symbol))
            inst_id = res.scalar_one_or_none()
            if inst_id is None:
                return
            await OrderBookRepository(db).write_snapshot(inst_id, snapshot_id, bids, asks, ts)

    async def _process_ob_delta(self, data: dict[str, Any], ts: datetime, db_session_factory) -> None:
        symbol = to_ccxt_symbol(data.get("s") or data.get("symbol"))
        update_id = data.get("u")
        bids = [(Decimal(px), Decimal(qty)) for px, qty in data.get("b", [])]
        asks = [(Decimal(px), Decimal(qty)) for px, qty in data.get("a", [])]
        async with db_session_factory() as db:  # type: ignore[misc]
            from sqlalchemy import select

            from app.db.models import Instrument

            res = await db.execute(select(Instrument.id).where(Instrument.symbol == symbol))
            inst_id = res.scalar_one_or_none()
            if inst_id is None:
                return
            repo = OrderBookRepository(db)
            for px, qty in bids:
                await repo.write_delta(inst_id, update_id, "bid", px, qty, ts)
            for px, qty in asks:
                await repo.write_delta(inst_id, update_id, "ask", px, qty, ts)

    async def start_trades(self, symbols: list[str], db_session_factory) -> None:
        topics = [f"publicTrade.{s.replace('/', '')}" for s in symbols]

        async def on_trade(msg: dict[str, Any]) -> None:
            data = msg.get("data") or []
            by_sym: dict[str, list[dict[str, Any]]] = {}
            for t in data:
                sym = to_ccxt_symbol(t.get("s") or t.get("symbol"))
                px = Decimal(t.get("p") or t.get("price") or 0)
                qty = Decimal(t.get("q") or t.get("qty") or 0)
                side = (t.get("S") or t.get("side") or "").lower()
                ts = datetime.fromtimestamp((t.get("T") or t.get("ts") or 0) / 1000, tz=UTC)
                trade_id = str(t.get("i") or t.get("tradeId") or t.get("id"))
                by_sym.setdefault(sym, []).append(
                    {"ts": ts, "px": px, "qty": qty, "side": side, "trade_id": trade_id},
                )
            async with db_session_factory() as db:  # type: ignore[misc]
                from sqlalchemy import select

                from app.db.models import Instrument

                for sym, rows in by_sym.items():
                    res = await db.execute(select(Instrument.id).where(Instrument.symbol == sym))
                    inst_id = res.scalar_one_or_none()
                    if inst_id is None:
                        continue
                    await TradesRepository(db).insert_trades(inst_id, rows)

        await self._run(topics, on_trade)

    async def close(self) -> None:
        self._closing.set()
