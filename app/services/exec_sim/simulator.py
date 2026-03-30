from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.schemas.llm_contract import OrderSide, OrderType, ProposedTrade
from app.schemas.market import OrderBookOut


@dataclass
class SimulationResult:
    status: str
    filled_qty: float
    avg_fill_price: Decimal | None
    reference_price: Decimal | None
    simulated_slippage_bps: Decimal | None
    notional_quote: Decimal | None
    reason: str | None = None


def simulate_trade(trade: ProposedTrade, orderbook: OrderBookOut) -> SimulationResult:
    reference_price = orderbook.mid or orderbook.best_ask or orderbook.best_bid
    if reference_price is None:
        return SimulationResult(
            status="rejected",
            filled_qty=0.0,
            avg_fill_price=None,
            reference_price=None,
            simulated_slippage_bps=None,
            notional_quote=None,
            reason="No reference price available.",
        )

    if trade.side == OrderSide.BUY:
        levels = orderbook.asks
        def executable(price: Decimal) -> bool:
            return trade.order_type == OrderType.MARKET or (
                trade.price is not None and price <= Decimal(str(trade.price))
            )
    else:
        levels = orderbook.bids
        def executable(price: Decimal) -> bool:
            return trade.order_type == OrderType.MARKET or (
                trade.price is not None and price >= Decimal(str(trade.price))
            )

    remaining = Decimal(str(trade.qty))
    filled = Decimal("0")
    notional = Decimal("0")

    for level in levels:
        if remaining <= 0:
            break
        if not executable(level.price):
            continue
        take_qty = min(remaining, level.qty)
        filled += take_qty
        notional += take_qty * level.price
        remaining -= take_qty

    if filled == 0:
        return SimulationResult(
            status="rejected",
            filled_qty=0.0,
            avg_fill_price=None,
            reference_price=reference_price,
            simulated_slippage_bps=None,
            notional_quote=None,
            reason="No executable liquidity at the requested price.",
        )

    avg_fill_price = notional / filled
    slippage_bps = abs(avg_fill_price - reference_price) / reference_price * Decimal("10000")
    if slippage_bps > Decimal(trade.max_slippage_bps):
        return SimulationResult(
            status="rejected",
            filled_qty=0.0,
            avg_fill_price=avg_fill_price,
            reference_price=reference_price,
            simulated_slippage_bps=slippage_bps,
            notional_quote=notional,
            reason="Simulated slippage exceeds max_slippage_bps.",
        )

    status = "accepted" if remaining == 0 else "partial"
    return SimulationResult(
        status=status,
        filled_qty=float(filled),
        avg_fill_price=avg_fill_price,
        reference_price=reference_price,
        simulated_slippage_bps=slippage_bps,
        notional_quote=notional,
    )
