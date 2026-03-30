from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ModelDecision
from app.services.llm_decider.client import LlmClient
from app.services.market_data.ccxt_adapter import CcxtAdapter


async def _fake_close(self: CcxtAdapter) -> None:
    return None


async def _fake_fetch_ohlcv(
    self: CcxtAdapter,
    symbol: str,
    timeframe: str = "1m",
    since: datetime | None = None,
    limit: int | None = 1000,
) -> list[dict[str, object]]:
    _ = (self, symbol, timeframe, since, limit)
    return [
        {
            "ts": datetime(2025, 1, 1, tzinfo=UTC),
            "open": Decimal("100"),
            "high": Decimal("105"),
            "low": Decimal("99"),
            "close": Decimal("104"),
            "volume_base": Decimal("12"),
            "turnover_quote": Decimal("1248"),
        },
    ]


async def _fake_fetch_l2_orderbook(
    self: CcxtAdapter,
    symbol: str,
    limit: int = 50,
) -> dict[str, object]:
    _ = (self, limit)
    return {
        "symbol": symbol,
        "best_bid": Decimal("103"),
        "best_ask": Decimal("104"),
        "mid": Decimal("103.5"),
        "bids": [
            {"price": Decimal("103"), "qty": Decimal("2")},
            {"price": Decimal("102.5"), "qty": Decimal("5")},
        ],
        "asks": [
            {"price": Decimal("104"), "qty": Decimal("2")},
            {"price": Decimal("104.5"), "qty": Decimal("5")},
        ],
    }


async def _fake_fetch_trades(
    self: CcxtAdapter,
    symbol: str,
    since: datetime | None = None,
    limit: int = 200,
) -> list[dict[str, object]]:
    _ = (self, symbol, since, limit)
    return [
        {
            "trade_id": "t-1",
            "ts": datetime(2025, 1, 1, tzinfo=UTC),
            "price": Decimal("104"),
            "qty": Decimal("0.5"),
            "side": "buy",
        },
    ]


@pytest.mark.asyncio
async def test_llm_decide_happy_path(client: AsyncClient, db_session: AsyncSession, monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_propose_plan(self: LlmClient, context: dict[str, object]) -> tuple[dict[str, object], str]:
        assert context["symbol"] == "BTC/USDT"
        return (
            {
                "actions": [
                    {
                        "action": "ProposedTrade",
                        "instrument_symbol": "BTC/USDT",
                        "side": "buy",
                        "order_type": "limit",
                        "qty": 0.5,
                        "price": 103.0,
                        "time_in_force": "GTC",
                        "max_slippage_bps": 50,
                        "rationale": "Tight spread and rising tape.",
                    },
                ],
                "risk_summary": "Risk remains bounded by max_notional_usd.",
                "constraints_checked": {
                    "risk": True,
                    "liquidity": True,
                    "exposure": True,
                    "drawdown": True,
                },
                "decision_id": "11111111-1111-1111-1111-111111111111",
            },
            "fake-openai-model",
        )

    monkeypatch.setattr(CcxtAdapter, "close", _fake_close)
    monkeypatch.setattr(CcxtAdapter, "fetch_ohlcv", _fake_fetch_ohlcv)
    monkeypatch.setattr(CcxtAdapter, "fetch_l2_orderbook", _fake_fetch_l2_orderbook)
    monkeypatch.setattr(CcxtAdapter, "fetch_trades", _fake_fetch_trades)
    monkeypatch.setattr(LlmClient, "propose_plan", fake_propose_plan)

    response = await client.post(
        "/api/v1/llm/decide",
        headers={"X-Demo-Api-Key": "test-demo-key"},
        json={"symbol": "BTC/USDT", "max_notional_usd": 500},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["validation_status"] == "validated"
    assert body["plan"]["actions"][0]["instrument_symbol"] == "BTC/USDT"
    assert body["market_snapshot"]["orderbook"]["mid"] == "103.5"

    decisions = await db_session.execute(select(ModelDecision))
    rows = decisions.scalars().all()
    assert len(rows) == 1
    assert rows[0].valid is True


@pytest.mark.asyncio
async def test_llm_decide_rejects_invalid_model_output(
    client: AsyncClient,
    db_session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_propose_plan(self: LlmClient, context: dict[str, object]) -> tuple[dict[str, object], str]:
        _ = context
        return (
            {
                "actions": [
                    {
                        "action": "ProposedTrade",
                        "instrument_symbol": "BTC/USDT",
                        "side": "buy",
                        "order_type": "market",
                        "qty": 0.5,
                        "price": 103.0,
                        "time_in_force": "GTC",
                        "max_slippage_bps": 50,
                    },
                ],
                "risk_summary": "Invalid because market order includes price.",
                "constraints_checked": {
                    "risk": True,
                    "liquidity": True,
                    "exposure": True,
                    "drawdown": True,
                },
                "decision_id": "22222222-2222-2222-2222-222222222222",
            },
            "fake-openai-model",
        )

    monkeypatch.setattr(CcxtAdapter, "close", _fake_close)
    monkeypatch.setattr(CcxtAdapter, "fetch_ohlcv", _fake_fetch_ohlcv)
    monkeypatch.setattr(CcxtAdapter, "fetch_l2_orderbook", _fake_fetch_l2_orderbook)
    monkeypatch.setattr(CcxtAdapter, "fetch_trades", _fake_fetch_trades)
    monkeypatch.setattr(LlmClient, "propose_plan", fake_propose_plan)

    response = await client.post(
        "/api/v1/llm/decide",
        headers={"X-Demo-Api-Key": "test-demo-key"},
        json={"symbol": "BTC/USDT", "max_notional_usd": 500},
    )
    assert response.status_code == 502
    assert "failed validation" in response.json()["detail"]

    decisions = await db_session.execute(select(ModelDecision))
    rows = decisions.scalars().all()
    assert len(rows) == 1
    assert rows[0].valid is False


@pytest.mark.asyncio
async def test_exec_sim_requires_demo_key(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/exec-sim/submit",
        json={
            "trade": {
                "action": "ProposedTrade",
                "instrument_symbol": "BTC/USDT",
                "side": "buy",
                "order_type": "market",
                "qty": 0.5,
                "time_in_force": "GTC",
                "max_slippage_bps": 50,
            },
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_exec_sim_happy_path(client: AsyncClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(CcxtAdapter, "close", _fake_close)
    monkeypatch.setattr(CcxtAdapter, "fetch_l2_orderbook", _fake_fetch_l2_orderbook)

    response = await client.post(
        "/api/v1/exec-sim/submit",
        headers={"X-Demo-Api-Key": "test-demo-key"},
        json={
            "trade": {
                "action": "ProposedTrade",
                "instrument_symbol": "BTC/USDT",
                "side": "buy",
                "order_type": "market",
                "qty": 0.5,
                "time_in_force": "GTC",
                "max_slippage_bps": 200,
            },
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "accepted"
    assert body["filled_qty"] == 0.5
    assert body["reference_price"] == "103.5"
