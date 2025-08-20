from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter

from app.api.deps import DbSessionDep
from app.services.market_data.ccxt_adapter import CcxtAdapter

# router = APIRouter(prefix="/marketdata", tags=["Market Data"])
router = APIRouter(prefix="/marketdata", tags=["Market Data"])


# @router.get("/ticker/latest")
# async def ticker_latest(symbol: str, db: DbSessionDep) -> dict[str, Any] | None:
#     """Fetch the latest ticker for a symbol."""
#     repo = TickerRepository(db)
#     return await repo.get_latest_ticker(symbol)


@router.get("/orderbook")
async def orderbook_l2(symbol: str, limit: int = 50, db: DbSessionDep = None) -> dict[str, Any]:  # type: ignore[assignment]
    """Fetch the latest L2 order book for a symbol."""
    # if db:
    #     repo = OrderBookRepository(db)
    #     # Attempt to fetch from DB first
    #     orderbook = await repo.get_latest_orderbook(symbol)
    #     if orderbook:
    #         return orderbook
    # Fallback to CCXT if not in DB or DB not available
    return await CcxtAdapter().fetch_l2_orderbook(symbol, limit)


@router.get("/trades")
async def trades(
    symbol: str,
    limit: int = 200,
    since: datetime | None = None,
    db: DbSessionDep = None,
):  # type: ignore[assignment]
    """Fetch recent trades for a symbol."""
    # if db:
    #     repo = TradesRepository(db)
    #     trades_data = await repo.get_trades(symbol, limit, since)
    #     if trades_data:
    #         return trades_data
    # Fallback to CCXT
    return await CcxtAdapter().fetch_trades(symbol, since, limit)
