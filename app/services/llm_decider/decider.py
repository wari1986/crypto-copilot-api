from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ModelDecision
from app.schemas.llm_contract import Plan
from app.services.llm_decider.client import LlmClient
from app.services.llm_decider.validators import ValidationError, validate_plan


@dataclass
class DecisionResult:
    plan: Plan
    model: str


class DeciderService:
    def __init__(self) -> None:
        self._client = LlmClient()

    async def decide(self, context: dict[str, Any], db: AsyncSession) -> DecisionResult:
        context_payload = jsonable_encoder(context)
        context_hash = hashlib.sha256(
            json.dumps(context_payload, sort_keys=True).encode("utf-8"),
        ).hexdigest()
        raw, model = await self._client.propose_plan(context)

        try:
            plan = Plan.model_validate(raw)
            validate_plan(plan)
        except (ValueError, ValidationError) as exc:
            await self._record_decision(
                db=db,
                request_id=str(raw.get("decision_id") or "invalid-decision"),
                context_hash=context_hash,
                decision_json=raw,
                valid=False,
                rejection_reason=str(exc),
            )
            raise

        await self._record_decision(
            db=db,
            request_id=plan.decision_id,
            context_hash=context_hash,
            decision_json=jsonable_encoder(plan),
            valid=True,
            rejection_reason=None,
        )
        return DecisionResult(plan=plan, model=model)

    async def _record_decision(
        self,
        *,
        db: AsyncSession,
        request_id: str,
        context_hash: str,
        decision_json: dict[str, Any],
        valid: bool,
        rejection_reason: str | None,
    ) -> None:
        db.add(
            ModelDecision(
                ts=datetime.now(UTC),
                request_id=request_id,
                input_context_hash=context_hash,
                decision_json=decision_json,
                valid=valid,
                rejection_reason=rejection_reason,
                applied=False,
            ),
        )
        await db.commit()
