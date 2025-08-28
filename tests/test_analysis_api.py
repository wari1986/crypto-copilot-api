from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.services.analysis import analysis_agent


@pytest.mark.asyncio
async def test_analysis_endpoints(monkeypatch: pytest.MonkeyPatch) -> None:
    analysis_agent._latest = None

    async def fake_run() -> str:
        analysis_agent._latest = "ai says hi"
        return "ai says hi"

    monkeypatch.setattr(analysis_agent, "run", fake_run)

    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")

    resp = await client.get("/api/v1/llm/analysis")
    assert resp.status_code == 404

    resp = await client.post("/api/v1/llm/analyze")
    assert resp.status_code == 200
    assert resp.json()["analysis"] == "ai says hi"

    resp = await client.get("/api/v1/llm/analysis")
    assert resp.status_code == 200
    assert resp.json()["analysis"] == "ai says hi"

    await client.aclose()
