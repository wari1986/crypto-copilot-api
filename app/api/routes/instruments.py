from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query

router = APIRouter(prefix="/instruments", tags=["instruments"])


@router.get("")
async def list_instruments(exchange: str | None = Query(default=None)) -> list[dict[str, Any]]:
    # Stub: return empty list to satisfy endpoint shape
    _ = exchange
    return []
