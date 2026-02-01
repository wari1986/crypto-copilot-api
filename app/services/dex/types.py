from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class PoolSnapshot:
    chain: str
    address: str
    dex: str
    captured_at: datetime

    # Uniswap v3-style fields (also useful generically for concentrated liquidity AMMs)
    token0: str | None = None
    token1: str | None = None
    fee: int | None = None  # in hundredths of a bip (e.g. 500, 3000, 10000)
    tick_spacing: int | None = None

    # slot0
    sqrt_price_x96: int | None = None
    tick: int | None = None

    # state
    liquidity: int | None = None

    # Adapter-specific payload (keep stable schema while MVP evolves)
    extra: dict[str, object] | None = None
