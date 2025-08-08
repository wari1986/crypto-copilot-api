from __future__ import annotations

from typing import Any

from openai import AsyncOpenAI

from app.core.config import settings


class LlmClient:
    def __init__(self) -> None:
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        self._model = settings.openai_model
        self._timeout = settings.openai_timeout_seconds

    async def propose_plan(self, context: dict[str, Any]) -> dict[str, Any]:
        # Minimal stub; real prompt/tooling later
        _ = context
        # Return an empty plan structure that will fail validation unless filled by caller/tests
        return {
            "actions": [],
            "risk_summary": "",
            "constraints_checked": {
                "risk": True,
                "liquidity": True,
                "exposure": True,
                "drawdown": True,
            },
            "decision_id": "00000000-0000-0000-0000-000000000000",
        }
