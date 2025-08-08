from __future__ import annotations

from app.schemas.llm_contract import OrderType, Plan, ProposedTrade


class ValidationError(Exception):
    pass


def validate_plan(plan: Plan) -> None:
    for action in plan.actions:
        if isinstance(action, ProposedTrade):
            _validate_trade(action)


def _validate_trade(trade: ProposedTrade) -> None:
    if trade.qty <= 0:
        raise ValidationError("qty must be positive")
    if trade.order_type == OrderType.MARKET and trade.price is not None:
        raise ValidationError("market orders must not include price")
    if trade.max_slippage_bps < 0 or trade.max_slippage_bps > 10_000:
        raise ValidationError("max_slippage_bps out of bounds")
