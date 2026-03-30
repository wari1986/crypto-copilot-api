from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_health_and_ready(client: AsyncClient) -> None:
    root = await client.get("/")
    assert root.status_code == 200
    assert root.json()["status"] == "ok"

    health = await client.get("/api/v1/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    ready = await client.get("/api/v1/ready")
    assert ready.status_code == 200
    assert ready.json()["status"] == "ok"
