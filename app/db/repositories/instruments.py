from __future__ import annotations

from decimal import Decimal
from typing import Any, Iterable, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Instrument


class InstrumentsRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def upsert_many(self, market_rows: Iterable[dict[str, Any]]) -> None:
        for row in market_rows:
            venue = row.get("venue", "bybit")
            symbol = row["symbol"]
            result = await self._db.execute(
                select(Instrument).where(Instrument.venue == venue, Instrument.symbol == symbol)
            )
            inst = result.scalar_one_or_none()
            if inst is None:
                inst = Instrument(
                    symbol=symbol,
                    base_asset=row.get("base_asset") or symbol.split("/")[0],
                    quote_asset=row.get("settlement") or symbol.split("/")[-1],
                    exchange=row.get("exchange") or inst_exchange_default(),
                    status="TRADING",
                    tick_size=0.0,
                    step_size=0.0,
                    min_notional=0.0,
                    venue=venue,
                    type=row.get("type", "spot"),
                    settlement=row.get("settlement"),
                    tick_size_num=row.get("tick_size"),
                    lot_size_num=row.get("lot_size"),
                    min_notional_num=row.get("min_notional"),
                    contract_size=row.get("contract_size"),
                    price_scale=row.get("price_scale"),
                    qty_scale=row.get("qty_scale"),
                    maker_fee_bps=row.get("maker_fee_bps"),
                    taker_fee_bps=row.get("taker_fee_bps"),
                    max_leverage=row.get("max_leverage"),
                )
                self._db.add(inst)
            else:
                await self._db.execute(
                    update(Instrument)
                    .where(Instrument.id == inst.id)
                    .values(
                        settlement=row.get("settlement"),
                        tick_size_num=row.get("tick_size"),
                        lot_size_num=row.get("lot_size"),
                        min_notional_num=row.get("min_notional"),
                        contract_size=row.get("contract_size"),
                        price_scale=row.get("price_scale"),
                        qty_scale=row.get("qty_scale"),
                        maker_fee_bps=row.get("maker_fee_bps"),
                        taker_fee_bps=row.get("taker_fee_bps"),
                        max_leverage=row.get("max_leverage"),
                    )
                )
        await self._db.commit()

    async def get_all_spot(self) -> list[Instrument]:
        res = await self._db.execute(select(Instrument).where(Instrument.type == "spot"))
        return list(res.scalars().all())

    async def get_by_symbol(self, symbol: str) -> Optional[Instrument]:
        res = await self._db.execute(select(Instrument).where(Instrument.symbol == symbol))
        return res.scalar_one_or_none()


def inst_exchange_default():
    # Fallback enum value when creating a new instrument
    from app.db.models import Exchange

    return Exchange.BYBIT


