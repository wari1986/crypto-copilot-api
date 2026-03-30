from __future__ import annotations

from app.schemas.market import CandleOut, MarketSnapshot, OrderBookLevelOut, OrderBookOut, TradeOut
from app.services.market_data.ccxt_adapter import CcxtAdapter


class MarketDataService:
    def __init__(self, adapter: CcxtAdapter | None = None) -> None:
        self._adapter = adapter or CcxtAdapter()

    async def build_snapshot(
        self,
        *,
        symbol: str,
        timeframe: str,
        candles_limit: int,
        orderbook_limit: int,
        trades_limit: int,
    ) -> MarketSnapshot:
        candles_raw = await self._adapter.fetch_ohlcv(
            symbol,
            timeframe=timeframe,
            limit=candles_limit,
        )
        orderbook_raw = await self._adapter.fetch_l2_orderbook(symbol, limit=orderbook_limit)
        trades_raw = await self._adapter.fetch_trades(symbol, limit=trades_limit)

        return MarketSnapshot(
            symbol=symbol,
            timeframe=timeframe,
            candles=[CandleOut.model_validate(row) for row in candles_raw],
            orderbook=OrderBookOut(
                symbol=orderbook_raw["symbol"],
                best_bid=orderbook_raw["best_bid"],
                best_ask=orderbook_raw["best_ask"],
                mid=orderbook_raw["mid"],
                bids=[OrderBookLevelOut.model_validate(level) for level in orderbook_raw["bids"]],
                asks=[OrderBookLevelOut.model_validate(level) for level in orderbook_raw["asks"]],
            ),
            trades=[TradeOut.model_validate(row) for row in trades_raw],
        )

    async def close(self) -> None:
        await self._adapter.close()
