from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from sqlalchemy import text

from app.api.deps import DbSessionDep
from app.core.config import settings

router = APIRouter()


# @router.get("/health")
# async def health(db: DbSessionDep) -> dict[str, Any]:
#     """Health check endpoint."""
#     # Check DB connection
#     await db.execute(text("SELECT 1"))
#     return {"status": "ok", "version": settings.version, "name": settings.project_name}
