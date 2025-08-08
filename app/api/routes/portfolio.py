from __future__ import annotations

from typing import Any, List

from fastapi import APIRouter
from app.api.deps import DbSessionDep
from app.services.portfolio.portfolio_service import PortfolioService


router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("/positions")
async def positions(db: DbSessionDep) -> List[dict[str, Any]]:
    return await PortfolioService(db).positions()


@router.get("/orders")
async def orders(db: DbSessionDep) -> List[dict[str, Any]]:
    return await PortfolioService(db).recent_orders()


@router.get("/pnl")
async def pnl(db: DbSessionDep) -> dict[str, float]:
    return await PortfolioService(db).pnl_summary()
