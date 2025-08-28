from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import settings
from app.db.repositories.instruments import InstrumentsRepository
from app.db.repositories.ohlcv import OhlcvRepository
from app.db.session import get_session_factory
from app.services.market_data.cache import MarketCache
from app.services.market_data.ccxt_adapter import CcxtAdapter
from app.services.market_data.ws_bybit import BybitWs
from app.services.analysis import analysis_agent


async def run_periodic(task: Callable[[], Awaitable[None]], interval_seconds: int) -> None:
    while True:
        try:
            await task()
        except Exception:
            pass
        await asyncio.sleep(interval_seconds)


async def start_market_data_tasks(
    session_factory: async_sessionmaker[AsyncSession] | None = None,
) -> None:
    # Gate background ingestion by flag to avoid exhausting DB resources unintentionally
    if not settings.enable_market_data_tasks:
        return
    session_factory = session_factory or get_session_factory()
    cache = MarketCache()
    ccxt = CcxtAdapter(settings.exchange)

    # Upsert instruments
    async with session_factory() as db:  # type: ignore[misc]
        markets = await ccxt.fetch_markets_spot()
        wanted = set(settings.symbols_list)
        markets = [m for m in markets if m["symbol"] in wanted]
        await InstrumentsRepository(db).upsert_many(markets)

    # Backfill OHLCV in the background only if explicitly enabled
    if settings.enable_backfill_on_startup:

        async def backfill_all() -> None:
            async with session_factory() as db:  # type: ignore[misc]
                for sym in settings.symbols_list:
                    rows = await ccxt.backfill_ohlcv_1m(sym, settings.backfill_lookback_days)
                    from sqlalchemy import select

                    from app.db.models import Instrument

                    res = await db.execute(select(Instrument.id).where(Instrument.symbol == sym))
                    inst_id = res.scalar_one_or_none()
                    if inst_id is None:
                        continue
                    await OhlcvRepository(db).insert_ohlcv_rows(inst_id, rows)

        asyncio.create_task(backfill_all())

    # Start WS tasks
    ws = BybitWs(cache)
    asyncio.create_task(ws.start_tickers(settings.symbols_list, session_factory))
    asyncio.create_task(
        ws.start_orderbook(settings.symbols_list, settings.ws_orderbook_levels, session_factory),
    )
    asyncio.create_task(ws.start_trades(settings.symbols_list, session_factory))

    async def _run_analysis() -> None:
        await analysis_agent.run()

    asyncio.create_task(run_periodic(_run_analysis, 4 * 60 * 60))
