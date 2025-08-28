from __future__ import annotations

import json
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

    async def market_analysis(self, context: dict[str, Any]) -> str:
        """Return a market analysis based on the provided context."""
        if settings.openai_api_key:
            try:
                resp = await self._client.responses.create(
                    model=self._model,
                    timeout=self._timeout,
                    reasoning={"effort": "medium"},
                    input=[
                        {
                            "role": "system",
                            "content": "You are a crypto market analyst.",
                        },
                        {"role": "user", "content": json.dumps(context)},
                    ],
                )
                content = resp.output_text
                if content:
                    return content
            except Exception:
                pass
        # Fallback simple summary
        parts = []
        for sym, data in context.get("symbols", {}).items():
            price = data.get("close")
            sma_short = data.get("sma_short")
            sma_long = data.get("sma_long")
            trend = "up" if sma_short and sma_long and sma_short > sma_long else "down"
            parts.append(f"{sym}: price {price:.2f}, trend {trend}")
        sentiment = context.get("sentiment")
        if sentiment:
            parts.append(f"Sentiment: {sentiment}")
        return " | ".join(parts)
