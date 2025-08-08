from __future__ import annotations

from typing import Any, Dict

from app.schemas.llm_contract import Plan
from app.services.llm_decider.client import LlmClient
from app.services.llm_decider.validators import validate_plan


class DeciderService:
    def __init__(self) -> None:
        self._client = LlmClient()

    async def decide(self, context: Dict[str, Any]) -> Plan:
        raw = await self._client.propose_plan(context)
        plan = Plan.model_validate(raw)
        validate_plan(plan)
        return plan
