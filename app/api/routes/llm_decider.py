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

router = APIRouter(prefix="/llm", tags=["llm"])


@router.post("/decide", response_model=Plan)
async def decide(context: dict[str, Any], db: DbSessionDep) -> Plan:
    service = DeciderService()
    plan = await service.decide(context)

    ctx_str = json.dumps(context, sort_keys=True, default=str)
    ctx_hash = hashlib.sha256(ctx_str.encode()).hexdigest()

    decision = ModelDecision(
        ts=datetime.now(UTC),
        request_id=plan.decision_id,
        input_context_hash=ctx_hash,
        decision_json=json.loads(plan.model_dump_json()),
        valid=True,
        rejection_reason=None,
        signoff_user=None,
        applied=False,
        applied_ts=None,
    )
    db.add(decision)
    await db.commit()
    return plan
