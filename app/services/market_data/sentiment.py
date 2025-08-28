from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import httpx


async def fetch_fear_greed_index() -> dict[str, Any]:
    """Fetch the latest Crypto Fear & Greed Index."""
    url = "https://api.alternative.me/fng/?limit=1"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=10.0)
        resp.raise_for_status()
        payload = resp.json().get("data", [])
        if not payload:
            return {}
        entry = payload[0]
        ts = datetime.fromtimestamp(int(entry["timestamp"]), tz=UTC)
        return {
            "value": int(entry["value"]),
            "classification": entry["value_classification"],
            "ts": ts,
        }
