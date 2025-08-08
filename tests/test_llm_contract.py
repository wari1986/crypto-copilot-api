from __future__ import annotations

import pytest

from app.schemas.llm_contract import OrderSide, OrderType, Plan, ProposedTrade, TimeInForce


def test_plan_valid_schema() -> None:
    trade = ProposedTrade(
        instrument_symbol="BTC/USDT",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        qty=1.0,
        price=50000.0,
        time_in_force=TimeInForce.GTC,
        max_slippage_bps=50,
    )
    plan = Plan(
        actions=[trade],
        risk_summary="ok",
        constraints_checked={"risk": True, "liquidity": True, "exposure": True, "drawdown": True},
        decision_id="00000000-0000-0000-0000-000000000000",
    )
    assert plan.actions[0].qty == 1.0


def test_market_with_price_rejected() -> None:
    with pytest.raises(Exception):
        ProposedTrade(
            instrument_symbol="BTC/USDT",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            qty=1.0,
            price=50000.0,
        )
