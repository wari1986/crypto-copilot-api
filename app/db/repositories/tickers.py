from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Instrument, TickerRT


class TickersRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def insert_ticker(self, instrument_id: int, row: dict) -> None:
        rec = TickerRT(
            instrument_id=instrument_id,
            ts=row["ts"],
            last=row["last"],
            bid=row["bid"],
            ask=row["ask"],
            mid=row["mid"],
            spread_bps=row["spread_bps"],
            day_vol_quote=row.get("day_vol_quote"),
            mark=row.get("mark"),
            index=row.get("index"),
        )
        self._db.add(rec)
        await self._db.commit()

    async def get_latest(self, symbol: str) -> TickerRT | None:
        sub = select(Instrument.id).where(Instrument.symbol == symbol).scalar_subquery()
        res = await self._db.execute(
            select(TickerRT).where(TickerRT.instrument_id == sub).order_by(TickerRT.ts.desc()).limit(1)
        )
        return res.scalar_one_or_none()


