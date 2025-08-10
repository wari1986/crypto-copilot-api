from __future__ import annotations

from datetime import datetime
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Instrument, OBSide, OrderBookL2


class OrderBookRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def write_snapshot(
        self,
        instrument_id: int,
        snapshot_id: str,
        bids: list[tuple],
        asks: list[tuple],
        ts: datetime,
    ) -> None:
        # Remove previous levels at the same snapshot? We keep append-only rows for history.
        for px, qty in bids:
            self._db.add(
                OrderBookL2(
                    instrument_id=instrument_id,
                    ts=ts,
                    side=OBSide.bid,
                    px=px,
                    qty=qty,
                    snapshot_id=snapshot_id,
                )
            )
        for px, qty in asks:
            self._db.add(
                OrderBookL2(
                    instrument_id=instrument_id,
                    ts=ts,
                    side=OBSide.ask,
                    px=px,
                    qty=qty,
                    snapshot_id=snapshot_id,
                )
            )
        await self._db.commit()

    async def write_delta(
        self, instrument_id: int, update_id: int | None, side: str, px, qty, ts: datetime
    ) -> None:
        self._db.add(
            OrderBookL2(
                instrument_id=instrument_id,
                ts=ts,
                side=OBSide(side),
                px=px,
                qty=qty,
                update_id=update_id,
            )
        )
        await self._db.commit()

    async def get_latest_snapshot(self, symbol: str, limit_per_side: int) -> dict:
        sub = select(Instrument.id).where(Instrument.symbol == symbol).scalar_subquery()
        # Find latest snapshot timestamp for this instrument
        res = await self._db.execute(
            select(OrderBookL2.ts)
            .where(OrderBookL2.instrument_id == sub, OrderBookL2.snapshot_id.is_not(None))
            .order_by(OrderBookL2.ts.desc())
            .limit(1)
        )
        latest_ts = res.scalar_one_or_none()
        if latest_ts is None:
            return {"bids": [], "asks": [], "ts": None}

        bids = await self._db.execute(
            select(OrderBookL2)
            .where(
                OrderBookL2.instrument_id == sub,
                OrderBookL2.ts == latest_ts,
                OrderBookL2.side == OBSide.bid,
            )
            .order_by(OrderBookL2.px.desc())
            .limit(limit_per_side)
        )
        asks = await self._db.execute(
            select(OrderBookL2)
            .where(
                OrderBookL2.instrument_id == sub,
                OrderBookL2.ts == latest_ts,
                OrderBookL2.side == OBSide.ask,
            )
            .order_by(OrderBookL2.px.asc())
            .limit(limit_per_side)
        )
        return {
            "bids": [(r.px, r.qty) for r in bids.scalars().all()],
            "asks": [(r.px, r.qty) for r in asks.scalars().all()],
            "ts": latest_ts,
        }


