from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel

from app.api.deps import DbSessionDep
from app.services.market_data.ccxt_adapter import CcxtAdapter

router = APIRouter(prefix="/candles", tags=["candles"])


class BackfillRequest(BaseModel):
    symbol: str
    interval: str
    start: datetime
    end: datetime


@router.post("/backfill")
async def backfill(_: BackfillRequest) -> dict[str, str]:
    return {"status": "enqueued"}


@router.get("/")
async def candles(
    symbol: str,
    timeframe: str,
    limit: int = 100,
    since: datetime | None = None,
    db: DbSessionDep = None,  # type: ignore[assignment]
):
    # FastAPI injects DbSessionDep; ignore typing default for linter.
    """
    ## OHLCV Candles

    This endpoint retrieves historical OHLCV (Open, High, Low, Close, Volume) data
    for a given symbol and timeframe.

    - **symbol**: Trading pair symbol (e.g., 'BTC/USDT').
    - **timeframe**: Chart timeframe (e.g., '1m', '5m', '1h', '1d').
    - **limit**: Number of candles to retrieve.
    - **since**: Start time for candles.
    - **db**: Database session.
    """
    # if db:
    #     repo = OHLCVRepository(db)
    #     candles = await repo.get_candles(symbol, timeframe, limit, since)
    #     if candles:
    #         return candles
    # Fallback to CCXT if not in DB or DB not available
    adapter = CcxtAdapter()
    return await adapter.fetch_ohlcv(symbol, timeframe, since, limit)
