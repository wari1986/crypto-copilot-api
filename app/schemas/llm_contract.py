from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, PositiveFloat, model_validator


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    LIMIT = "limit"
    MARKET = "market"
    POST_ONLY = "post_only"
    IOC = "ioc"


class TimeInForce(str, Enum):
    GTC = "GTC"
    IOC = "IOC"
    FOK = "FOK"


class ActionType(str, Enum):
    PROPOSED_TRADE = "ProposedTrade"
    CANCEL = "Cancel"
    MOVE_STOP = "MoveStop"
    FLATTEN = "Flatten"


class CancelAction(BaseModel):
    action: Literal[ActionType.CANCEL] = Field(default=ActionType.CANCEL)
    client_order_id: str


class MoveStopAction(BaseModel):
    action: Literal[ActionType.MOVE_STOP] = Field(default=ActionType.MOVE_STOP)
    instrument_symbol: str
    stop: PositiveFloat


class FlattenAction(BaseModel):
    action: Literal[ActionType.FLATTEN] = Field(default=ActionType.FLATTEN)
    instrument_symbol: str


class ProposedTrade(BaseModel):
    action: Literal[ActionType.PROPOSED_TRADE] = Field(default=ActionType.PROPOSED_TRADE)
    instrument_symbol: str
    side: OrderSide
    order_type: OrderType
    qty: PositiveFloat
    price: PositiveFloat | None = None
    time_in_force: TimeInForce = TimeInForce.GTC
    max_slippage_bps: int = Field(ge=0, le=10_000, default=50)
    stop: PositiveFloat | None = None
    take_profit: PositiveFloat | None = None
    rationale: str | None = None

    @model_validator(mode="after")
    def validate_market_price(self) -> ProposedTrade:
        if self.order_type == OrderType.MARKET and self.price is not None:
            raise ValueError("price must be omitted for market orders")
        if self.order_type != OrderType.MARKET and self.price is None:
            # For limit/post-only/IOC a price is typically required
            raise ValueError("price is required for non-market orders")
        return self


PlanAction = ProposedTrade | CancelAction | MoveStopAction | FlattenAction


class ConstraintsChecked(BaseModel):
    risk: bool
    liquidity: bool
    exposure: bool
    drawdown: bool


class Plan(BaseModel):
    actions: list[PlanAction]
    risk_summary: str
    constraints_checked: ConstraintsChecked
    decision_id: str = Field(pattern=r"^[0-9a-fA-F-]{36}$")


def get_json_schema() -> dict:
    return Plan.model_json_schema()
