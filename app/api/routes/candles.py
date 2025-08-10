from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel

from app.api.deps import DbSessionDep
from app.db.repositories.ohlcv import OhlcvRepository

router = APIRouter(prefix="/candles", tags=["candles"])


class BackfillRequest(BaseModel):
    symbol: str
    interval: str
    start: datetime
    end: datetime


@router.post("/backfill")
async def backfill(_: BackfillRequest) -> dict[str, str]:
    return {"status": "enqueued"}


@router.get("/1m")
async def get_ohlcv_1m(
    symbol: str,
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int = 1000,
    db: DbSessionDep = None,  # type: ignore[assignment]
):
    # FastAPI injects DbSessionDep; ignore typing default for linter.
    rows = await OhlcvRepository(db).fetch_ohlcv_1m(symbol, start, end, limit)
    return [
        {
            "ts": r.ts,
            "open": str(r.open),
            "high": str(r.high),
            "low": str(r.low),
            "close": str(r.close),
            "volume_base": str(r.volume_base),
            "turnover_quote": str(r.turnover_quote) if r.turnover_quote is not None else None,
        }
        for r in rows
    ]
