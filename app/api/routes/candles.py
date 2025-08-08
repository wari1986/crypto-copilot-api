from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter(prefix="/candles", tags=["candles"])


class BackfillRequest(BaseModel):
    symbol: str
    interval: str
    start: datetime
    end: datetime


@router.post("/backfill")
async def backfill(_: BackfillRequest) -> dict[str, str]:
    return {"status": "enqueued"}
