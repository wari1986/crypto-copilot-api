from __future__ import annotations

import asyncio
import os

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.mark.asyncio
async def test_health_smoke(monkeypatch: pytest.MonkeyPatch) -> None:
    # Use a dummy DB URL; health will still attempt to ping so this is a smoke test structure.
    # In CI, provide a real DATABASE_URL via docker compose.
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")
    # We don't call /health here because it requires DB. Just ensure root responds.
    resp = await client.get("/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
    await client.aclose()
