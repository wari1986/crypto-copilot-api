from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query
from app.api.deps import DbSessionDep
from app.db.repositories.instruments import InstrumentsRepository

router = APIRouter(prefix="/instruments", tags=["instruments"])


@router.get("")
async def list_instruments(db: DbSessionDep, exchange: str | None = Query(default=None)) -> list[dict[str, Any]]:
    _ = exchange
    repo = InstrumentsRepository(db)
    instruments = await repo.get_all_spot()
    return [
        {
            "symbol": i.symbol,
            "venue": i.venue,
            "type": i.type,
            "settlement": i.settlement,
            "price_scale": i.price_scale,
            "qty_scale": i.qty_scale,
        }
        for i in instruments
    ]


@router.get("/{symbol}")
async def get_instrument(symbol: str, db: DbSessionDep) -> dict[str, Any] | None:
    inst = await InstrumentsRepository(db).get_by_symbol(symbol)
    if inst is None:
        return None
    return {
        "symbol": inst.symbol,
        "venue": inst.venue,
        "type": inst.type,
        "settlement": inst.settlement,
        "price_scale": inst.price_scale,
        "qty_scale": inst.qty_scale,
    }
