from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from sqlalchemy import text

from app.api.deps import DbSessionDep

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health(db: DbSessionDep) -> dict[str, Any]:
    # Attempt DB ping; tolerate failure in dev to keep liveness simple
    try:
        await db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "degraded"
    return {"status": "ok", "db": db_status}
