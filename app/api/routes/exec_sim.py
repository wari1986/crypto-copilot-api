from __future__ import annotations

from fastapi import APIRouter

from app.schemas.llm_contract import ProposedTrade

router = APIRouter(prefix="/exec-sim", tags=["exec-sim"])


@router.post("/submit")
async def submit(trade: ProposedTrade) -> dict[str, str]:
    # Stub: accept and acknowledge
    return {"status": "accepted"}
