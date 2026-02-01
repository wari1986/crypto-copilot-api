from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from sqlalchemy import text

from app.api.deps import DbSessionDep
from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, Any]:
    """Liveness check.

    - Does not require the database.
    - Use `/ready` for DB readiness.
    """

    return {
        "status": "ok",
        "env": settings.env,
        "version": "0.1.0",
        "name": "crypto-copilot-api",
    }


@router.get("/ready")
async def ready(db: DbSessionDep) -> dict[str, Any]:
    """Readiness check.

    Verifies the DB connection is usable.
    """

    await db.execute(text("SELECT 1"))
    return {"status": "ok"}
