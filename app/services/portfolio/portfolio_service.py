from __future__ import annotations

from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Order, Position


class PortfolioService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def positions(self) -> List[Dict[str, Any]]:
        res = await self._db.execute(select(Position))
        return [
            {
                "instrument_id": p.instrument_id,
                "side": p.side.value,
                "qty": p.qty,
                "avg_price": p.avg_price,
                "unrealized_pnl": p.unrealized_pnl,
                "realized_pnl": p.realized_pnl,
            }
            for p in res.scalars().all()
        ]

    async def recent_orders(self, limit: int = 100) -> List[Dict[str, Any]]:
        res = await self._db.execute(select(Order).order_by(Order.id.desc()).limit(limit))
        return [
            {
                "client_order_id": o.client_order_id,
                "status": o.status.value,
                "qty": o.qty,
                "price": o.price,
            }
            for o in res.scalars().all()
        ]

    async def pnl_summary(self) -> Dict[str, float]:
        res = await self._db.execute(select(Position))
        positions = res.scalars().all()
        realized = sum(p.realized_pnl for p in positions)
        unrealized = sum(p.unrealized_pnl for p in positions)
        return {"realized": realized, "unrealized": unrealized}
