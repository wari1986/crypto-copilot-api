from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.api.deps import DbSessionDep, DemoKeyDep
from app.schemas.showcase import DecisionRequest, DecisionResponse
from app.services.llm_decider.decider import DeciderService
from app.services.llm_decider.validators import ValidationError
from app.services.market_data.service import MarketDataService

router = APIRouter(prefix="/llm", tags=["LLM"])


@router.post("/decide", response_model=DecisionResponse)
async def decide(
    request: DecisionRequest,
    db: DbSessionDep,
    _: DemoKeyDep,
) -> DecisionResponse:
    market_data = MarketDataService()
    try:
        snapshot = await market_data.build_snapshot(
            symbol=request.symbol,
            timeframe=request.timeframe,
            candles_limit=request.candles_limit,
            orderbook_limit=request.orderbook_limit,
            trades_limit=request.trades_limit,
        )
    finally:
        await market_data.close()

    context = {
        "symbol": request.symbol,
        "risk_limits": {"max_notional_usd": request.max_notional_usd},
        "thesis": request.thesis,
        "market_snapshot": snapshot.model_dump(mode="json"),
    }
    try:
        result = await DeciderService().decide(context, db)
    except (RuntimeError, ValueError, ValidationError) as exc:
        raise HTTPException(status_code=502, detail=f"Model output failed validation: {exc}") from exc

    return DecisionResponse(
        plan=result.plan,
        market_snapshot=snapshot,
        model=result.model,
        validation_status="validated",
    )
