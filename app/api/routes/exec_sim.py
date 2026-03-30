from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import DemoKeyDep
from app.schemas.market import OrderBookOut
from app.schemas.showcase import SimulationRequest, SimulationResponse
from app.services.exec_sim.simulator import simulate_trade
from app.services.market_data.ccxt_adapter import CcxtAdapter

router = APIRouter(prefix="/exec-sim", tags=["exec-sim"])


@router.post("/submit", response_model=SimulationResponse)
async def submit(request: SimulationRequest, _: DemoKeyDep) -> SimulationResponse:
    adapter = CcxtAdapter()
    try:
        orderbook_raw = await adapter.fetch_l2_orderbook(
            request.trade.instrument_symbol,
            limit=request.orderbook_limit,
        )
    finally:
        await adapter.close()

    result = simulate_trade(request.trade, OrderBookOut.model_validate(orderbook_raw))
    return SimulationResponse(
        status=result.status,
        symbol=request.trade.instrument_symbol,
        side=request.trade.side.value,
        order_type=request.trade.order_type.value,
        requested_qty=float(request.trade.qty),
        filled_qty=result.filled_qty,
        reference_price=result.reference_price,
        simulated_avg_fill_price=result.avg_fill_price,
        simulated_slippage_bps=result.simulated_slippage_bps,
        notional_quote=result.notional_quote,
        reason=result.reason,
    )
