from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_health_smoke(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")
    resp = await client.get("/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
    health = await client.get("/api/v1/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    await client.aclose()
