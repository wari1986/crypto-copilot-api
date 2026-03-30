from __future__ import annotations

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, PositiveFloat

from app.schemas.llm_contract import Plan, ProposedTrade
from app.schemas.market import MarketSnapshot


class DecisionRequest(BaseModel):
    symbol: str = Field(description="CCXT symbol such as BTC/USDT")
    timeframe: str = Field(default="1m")
    candles_limit: int = Field(default=20, ge=5, le=200)
    orderbook_limit: int = Field(default=10, ge=1, le=50)
    trades_limit: int = Field(default=20, ge=1, le=100)
    max_notional_usd: PositiveFloat = Field(default=1_000)
    thesis: str | None = None


class DecisionResponse(BaseModel):
    plan: Plan
    market_snapshot: MarketSnapshot
    model: str
    simulated_only: bool = True
    validation_status: Literal["validated"]


class SimulationRequest(BaseModel):
    trade: ProposedTrade
    orderbook_limit: int = Field(default=10, ge=1, le=50)


class SimulationResponse(BaseModel):
    status: Literal["accepted", "partial", "rejected"]
    symbol: str
    side: str
    order_type: str
    requested_qty: float
    filled_qty: float
    reference_price: Decimal | None = None
    simulated_avg_fill_price: Decimal | None = None
    simulated_slippage_bps: Decimal | None = None
    notional_quote: Decimal | None = None
    reason: str | None = None
