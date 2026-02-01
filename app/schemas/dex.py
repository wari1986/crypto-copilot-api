from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class PoolSnapshotOut(BaseModel):
    chain: str
    address: str
    dex: str
    captured_at: datetime

    token0: str | None = None
    token1: str | None = None
    fee: int | None = Field(default=None, description="Uniswap v3 fee (e.g. 500, 3000, 10000)")
    tick_spacing: int | None = None

    sqrt_price_x96: int | None = None
    tick: int | None = None
    liquidity: int | None = None
