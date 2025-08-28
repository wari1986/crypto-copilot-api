from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.services.llm_decider.client import LlmClient
from app.services.market_data.ccxt_adapter import CcxtAdapter


class AnalysisAgent:
    """Collects market data and produces an LLM-based analysis."""

    def __init__(self) -> None:
        self._ccxt = CcxtAdapter(settings.exchange)
        self._llm = LlmClient()
        self._latest: str | None = None

    async def _gather_context(self) -> dict[str, Any]:
        ctx: dict[str, Any] = {"symbols": {}, "sentiment": await self._fetch_sentiment()}
        for sym in settings.symbols_list:
            ohlcv = await self._ccxt.fetch_ohlcv(sym, timeframe="1h", limit=24)
            closes = [float(row["close"]) for row in ohlcv]
            if not closes:
                continue
            sma_short = sum(closes[-5:]) / min(5, len(closes))
            sma_long = sum(closes[-20:]) / min(20, len(closes))
            ctx["symbols"][sym] = {
                "close": closes[-1],
                "sma_short": sma_short,
                "sma_long": sma_long,
            }
        return ctx

    async def _fetch_sentiment(self) -> str:
        # Placeholder for real market sentiment API
        return "neutral"

    async def run(self) -> str:
        context = await self._gather_context()
        analysis = await self._llm.market_analysis(context)
        self._latest = analysis
        return analysis

    def latest(self) -> str | None:
        return self._latest


analysis_agent = AnalysisAgent()
