from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/llm", tags=["LLM"])


# @router.post("/decide", response_model=Plan)
# async def decide(context: dict[str, Any], db: DbSessionDep) -> Plan:
#     """
#     Makes a decision based on the given context using the LLM model.
#     """
#     return await DeciderService(db).decide(context)
