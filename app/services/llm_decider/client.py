from __future__ import annotations

import json
import logging
from json import JSONDecodeError
from typing import Any

from openai import AsyncOpenAI

from app.core.config import settings
from app.schemas.analysis import AnalysisResult

logger = logging.getLogger(__name__)


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

    async def market_analysis(self, context: dict[str, Any]) -> AnalysisResult | None:
        """Return a structured market analysis; None signals fallback should be used."""
        if not settings.openai_api_key:
            return None
        try:
            symbols = list(context.get("symbols", {}).keys())
            logger.info("Calling OpenAI market analysis", extra={"model": self._model, "symbols": symbols})
            completion = await self._client.chat.completions.create(
                model=self._model,
                timeout=self._timeout,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Act as a crypto trading desk analyst. "
                            "Use only the provided data. "
                            "Return JSON matching the AnalysisResult schema with: "
                            "summary, generated_at (ISO datetime), risks, "
                            "and per symbol: bias (long/short/neutral), confidence 0-1, "
                            "short summary, trend, close, volatility, liquidity, flow, levels, funding_rate, risks. "
                            "Be concise, avoid speculation, never hallucinate missing fields."
                        ),
                    },
                    {"role": "user", "content": json.dumps(context)},
                ],
            )
            content = completion.choices[0].message.content if completion.choices else None
            if not content:
                logger.warning("OpenAI returned empty content, using fallback")
                return None
            try:
                data = json.loads(content)
                # Normalize symbols: if returned as a dict keyed by symbol, convert to list
                symbols_raw = data.get("symbols")
                if isinstance(symbols_raw, dict):
                    data["symbols"] = [
                        {"symbol": sym, **(payload if isinstance(payload, dict) else {})}
                        for sym, payload in symbols_raw.items()
                    ]
                # Normalize risks: ensure list
                risks_raw = data.get("risks")
                if isinstance(risks_raw, str):
                    data["risks"] = [risks_raw]
                elif risks_raw is None:
                    data["risks"] = []
            except JSONDecodeError as exc:
                logger.warning("OpenAI returned non-JSON content, falling back", exc_info=exc)
                return None
            result = AnalysisResult.model_validate(data)
            result.source = "openai"
            return result
        except Exception as exc:
            logger.warning("OpenAI market analysis failed, falling back", exc_info=exc)
            return None
