from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter

from app.schemas.market import CandleOut
from app.services.market_data.ccxt_adapter import CcxtAdapter

router = APIRouter(prefix="/candles", tags=["candles"])


@router.get("/", response_model=list[CandleOut])
async def candles(
    symbol: str,
    timeframe: str,
    limit: int = 100,
    since: datetime | None = None,
) -> list[CandleOut]:
    adapter = CcxtAdapter()
    try:
        rows = await adapter.fetch_ohlcv(symbol, timeframe, since, limit)
        return [CandleOut.model_validate(row) for row in rows]
    finally:
        await adapter.close()
