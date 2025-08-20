from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query

from app.api.deps import DbSessionDep
from app.db.repositories.instruments import InstrumentsRepository

router = APIRouter(prefix="/instruments", tags=["Instruments"])


# @router.get("/")
# async def list_instruments(db: DbSessionDep, exchange: str | None = Query(default=None)) -> list[dict[str, Any]]:
#     """List all instruments, optionally filtered by exchange."""
#     repo = InstrumentsRepository(db)
#     instruments = await repo.get_all(exchange_filter=exchange)
#     return [
#         {
#             "symbol": i.symbol,
#             "exchange": i.exchange,
#             "base_asset": i.base_asset,
#             "quote_asset": i.quote_asset,
#             "price_precision": i.price_precision,
#             "qty_precision": i.qty_precision,
#             "min_qty": str(i.min_qty),
#             "max_qty": str(i.max_qty),
#             "margin_enabled": i.margin_enabled,
#         }
#         for i in instruments
#     ]


# @router.get("/{symbol}")
# async def get_instrument(symbol: str, db: DbSessionDep) -> dict[str, Any] | None:
#     """Fetch a single instrument by symbol."""
#     repo = InstrumentsRepository(db)
#     instrument = await repo.get_by_symbol(symbol)
#     if not instrument:
#         return None
#     return {
#         "symbol": instrument.symbol,
#         "exchange": instrument.exchange,
#         "base_asset": instrument.base_asset,
#         "quote_asset": instrument.quote_asset,
#         "price_precision": instrument.price_precision,
#         "qty_precision": instrument.qty_precision,
#         "min_qty": str(instrument.min_qty),
#         "max_qty": str(instrument.max_qty),
#         "margin_enabled": instrument.margin_enabled,
#     }
