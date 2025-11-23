from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class VolatilityMetrics(BaseModel):
    atr: float | None = None
    realized_vol: float | None = None
    regime: str | None = None


class LiquidityMetrics(BaseModel):
    mid: float | None = None
    spread_bps: float | None = None
    depth_10bps: float | None = None
    depth_50bps: float | None = None
    liquidity_ok: bool | None = None


class FlowMetrics(BaseModel):
    buy_quote: float | None = None
    sell_quote: float | None = None
    net_flow_quote: float | None = None
    flow_imbalance: float | None = None
    large_trade_count: int | None = None
    large_trade_side: str | None = None


class Levels(BaseModel):
    recent_high: float | None = None
    recent_low: float | None = None
    support: float | None = None
    resistance: float | None = None


class SymbolAnalysis(BaseModel):
    symbol: str
    bias: str
    confidence: float = Field(ge=0.0, le=1.0)
    summary: str
    trend: str | None = None
    close: float | None = None
    volatility: VolatilityMetrics | None = None
    liquidity: LiquidityMetrics | None = None
    flow: FlowMetrics | None = None
    levels: Levels | None = None
    funding_rate: float | None = None
    risks: list[str] = Field(default_factory=list)


class AnalysisResult(BaseModel):
    generated_at: datetime
    summary: str
    symbols: list[SymbolAnalysis]
    risks: list[str] = Field(default_factory=list)
    source: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return self.model_dump()
