from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class CandleOut(BaseModel):
    ts: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume_base: Decimal
    turnover_quote: Decimal | None = None


class OrderBookLevelOut(BaseModel):
    price: Decimal
    qty: Decimal


class OrderBookOut(BaseModel):
    symbol: str
    best_bid: Decimal | None = None
    best_ask: Decimal | None = None
    mid: Decimal | None = None
    bids: list[OrderBookLevelOut] = Field(default_factory=list)
    asks: list[OrderBookLevelOut] = Field(default_factory=list)


class TradeOut(BaseModel):
    trade_id: str
    ts: datetime
    price: Decimal
    qty: Decimal
    side: Literal["buy", "sell"]


class MarketSnapshot(BaseModel):
    symbol: str
    timeframe: str
    candles: list[CandleOut] = Field(default_factory=list)
    orderbook: OrderBookOut
    trades: list[TradeOut] = Field(default_factory=list)
