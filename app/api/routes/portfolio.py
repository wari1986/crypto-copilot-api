from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from app.api.deps import DbSessionDep
from app.services.portfolio.portfolio_service import PortfolioService

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])


# @router.get("/positions")
# async def positions(db: DbSessionDep) -> list[dict[str, Any]]:
#     """Fetch current positions."""
#     return await PortfolioService(db).get_positions()


# @router.get("/orders")
# async def orders(db: DbSessionDep) -> list[dict[str, Any]]:
#     """Fetch recent orders."""
#     return await PortfolioService(db).get_orders()


# @router.get("/pnl")
# async def pnl(db: DbSessionDep) -> dict[str, float]:
#     """Fetch profit and loss."""
#     return await PortfolioService(db).get_pnl()
