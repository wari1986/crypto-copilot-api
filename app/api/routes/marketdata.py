from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Query

from app.api.deps import DbSessionDep
from app.db.repositories.orderbook import OrderBookRepository
from app.db.repositories.tickers import TickersRepository
from app.db.repositories.trades import TradesRepository


router = APIRouter(prefix="/marketdata", tags=["marketdata"])


@router.get("/ticker/latest")
async def ticker_latest(symbol: str, db: DbSessionDep) -> dict[str, Any] | None:
    t = await TickersRepository(db).get_latest(symbol)
    if t is None:
        return None
    return {
        "ts": t.ts,
        "last": str(t.last),
        "bid": str(t.bid),
        "ask": str(t.ask),
        "mid": str(t.mid),
        "spread_bps": str(t.spread_bps),
        "day_vol_quote": str(t.day_vol_quote) if t.day_vol_quote is not None else None,
    }


@router.get("/orderbook/l2")
async def orderbook_l2(symbol: str, limit: int = 50, db: DbSessionDep | None = None) -> dict[str, Any]:
    assert db is not None
    snap = await OrderBookRepository(db).get_latest_snapshot(symbol, limit)
    return {
        "ts": snap["ts"],
        "bids": [(str(px), str(qty)) for px, qty in snap["bids"]],
        "asks": [(str(px), str(qty)) for px, qty in snap["asks"]],
    }


@router.get("/trades")
async def trades(symbol: str, limit: int = 200, since: datetime | None = None, db: DbSessionDep | None = None):
    assert db is not None
    rows = await TradesRepository(db).get_recent(symbol, limit, since)
    return [
        {"ts": r.ts, "px": str(r.px), "qty": str(r.qty), "side": r.side.value, "trade_id": r.trade_id}
        for r in rows
    ]


