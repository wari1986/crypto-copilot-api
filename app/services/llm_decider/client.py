from __future__ import annotations

import json
from typing import Any

from openai import AsyncOpenAI

from app.core.config import settings
from app.schemas.llm_contract import get_json_schema


class LlmClient:
    def __init__(self) -> None:
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        self._model = settings.openai_model
        self._timeout = settings.openai_timeout_seconds

    async def propose_plan(self, context: dict[str, Any]) -> tuple[dict[str, Any], str]:
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required for /api/v1/llm/decide.")

        schema = json.dumps(get_json_schema(), sort_keys=True)
        completion = await self._client.chat.completions.create(
            model=self._model,
            temperature=0.2,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a risk-aware crypto trading copilot. "
                        "Return JSON only. The response must satisfy this schema: "
                        f"{schema}. "
                        "Prefer zero or one actions. Use only the symbol in context. "
                        "Never suggest live execution; this is simulation-only."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(context, sort_keys=True, default=str),
                },
            ],
            timeout=self._timeout,
        )
        content = completion.choices[0].message.content
        if not content:
            raise RuntimeError("OpenAI returned an empty completion.")
        return json.loads(content), (completion.model or self._model)
