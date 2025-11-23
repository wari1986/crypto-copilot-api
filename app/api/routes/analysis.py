from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.analysis import analysis_agent

router = APIRouter(prefix="/analysis", tags=["Analysis"])


class RunRequest(BaseModel):
    symbols: list[str] | None = None


@router.get("/latest")
async def latest_analysis() -> dict:
    """Return the latest cached analysis."""
    res = analysis_agent.latest()
    return res.as_dict() if res else {"message": "no analysis yet"}


@router.post("/run")
async def run_analysis(payload: RunRequest) -> dict:
    """Force a fresh analysis run (optional symbols override)."""
    res = await analysis_agent.run(symbols=payload.symbols)
    return res.as_dict()
