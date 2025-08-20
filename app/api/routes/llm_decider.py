from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter

from app.api.deps import DbSessionDep
from app.db.models import ModelDecision
from app.schemas.llm_contract import Plan
from app.services.llm_decider.decider import DeciderService

router = APIRouter(prefix="/llm", tags=["LLM"])


# @router.post("/decide", response_model=Plan)
# async def decide(context: dict[str, Any], db: DbSessionDep) -> Plan:
#     """
#     Makes a decision based on the given context using the LLM model.
#     """
#     return await DeciderService(db).decide(context)
