from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SimulationResult:
    status: str
    filled_qty: float
    avg_fill_price: float


def simulate_simple_mid_slippage(mid: float, bps: float) -> float:
    return mid * (1 + bps / 10_000)
