from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Instrument, TradeRT


class TradesRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def insert_trades(self, instrument_id: int, rows: Iterable[dict]) -> None:
        values = [
            {
                "instrument_id": instrument_id,
                "ts": r["ts"],
                "px": r["px"],
                "qty": r["qty"],
                "side": r["side"],
                "trade_id": r["trade_id"],
            }
            for r in rows
        ]
        if not values:
            return
        stmt = insert(TradeRT).values(values)
        stmt = stmt.on_conflict_do_nothing(constraint="uq_trade_rt_unique")
        await self._db.execute(stmt)
        await self._db.commit()

    async def get_recent(
        self, symbol: str, limit: int = 200, since_ts: datetime | None = None,
    ) -> list[TradeRT]:
        sub = select(Instrument.id).where(Instrument.symbol == symbol).scalar_subquery()
        q = select(TradeRT).where(TradeRT.instrument_id == sub)
        if since_ts is not None:
            q = q.where(TradeRT.ts >= since_ts)
        q = q.order_by(TradeRT.ts.desc()).limit(limit)
        res = await self._db.execute(q)
        return list(res.scalars().all())


