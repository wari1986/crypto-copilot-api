from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Instrument, OHLCV1m


class OhlcvRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def insert_ohlcv_rows(self, instrument_id: int, rows: Iterable[dict]) -> None:
        values = [
            {
                "instrument_id": instrument_id,
                "ts": r["ts"],
                "open": r["open"],
                "high": r["high"],
                "low": r["low"],
                "close": r["close"],
                "volume_base": r["volume_base"],
                "turnover_quote": r.get("turnover_quote"),
            }
            for r in rows
        ]
        if not values:
            return
        stmt = insert(OHLCV1m).values(values)
        stmt = stmt.on_conflict_do_nothing(index_elements=["instrument_id", "ts"])  # type: ignore[attr-defined]
        await self._db.execute(stmt)
        await self._db.commit()

    async def fetch_ohlcv_1m(
        self,
        symbol: str,
        start: datetime | None,
        end: datetime | None,
        limit: int = 1000,
    ) -> list[OHLCV1m]:
        sub = select(Instrument.id).where(Instrument.symbol == symbol).scalar_subquery()
        q = select(OHLCV1m).where(OHLCV1m.instrument_id == sub)
        if start is not None:
            q = q.where(OHLCV1m.ts >= start)
        if end is not None:
            q = q.where(OHLCV1m.ts <= end)
        q = q.order_by(OHLCV1m.ts.asc()).limit(limit)
        res = await self._db.execute(q)
        return list(res.scalars().all())
