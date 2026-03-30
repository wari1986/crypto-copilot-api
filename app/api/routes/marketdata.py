from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter

from app.schemas.market import OrderBookOut, TradeOut
from app.services.market_data.ccxt_adapter import CcxtAdapter

router = APIRouter(prefix="/marketdata", tags=["Market Data"])


@router.get("/orderbook", response_model=OrderBookOut)
async def orderbook_l2(symbol: str, limit: int = 50) -> OrderBookOut:
    adapter = CcxtAdapter()
    try:
        return OrderBookOut.model_validate(await adapter.fetch_l2_orderbook(symbol, limit))
    finally:
        await adapter.close()


@router.get("/trades", response_model=list[TradeOut])
async def trades(
    symbol: str,
    limit: int = 200,
    since: datetime | None = None,
) -> list[TradeOut]:
    adapter = CcxtAdapter()
    try:
        rows = await adapter.fetch_trades(symbol, since, limit)
        return [TradeOut.model_validate(row) for row in rows]
    finally:
        await adapter.close()
