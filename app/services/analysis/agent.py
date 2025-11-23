from __future__ import annotations

import math
import statistics
from datetime import UTC, datetime
from typing import Any, Callable

from app.core.config import settings
from app.schemas.analysis import (
    AnalysisResult,
    FlowMetrics,
    Levels,
    LiquidityMetrics,
    SymbolAnalysis,
    VolatilityMetrics,
)
from app.services.llm_decider.client import LlmClient
from app.services.market_data.cache import (
    OrderbookSnapshot,
    atr,
    spread_depth_stats,
    volatility_regime,
)
from app.services.market_data.ccxt_adapter import CcxtAdapter


class AnalysisAgent:
    """Collects market data and produces an LLM-based analysis."""

    def __init__(self) -> None:
        self._ccxt = CcxtAdapter(settings.exchange)
        self._llm = LlmClient()
        self._latest: AnalysisResult | None = None

    async def _gather_context(self, symbols: list[str]) -> dict[str, Any]:
        ctx: dict[str, Any] = {"symbols": {}, "sentiment": await self._fetch_sentiment()}
        for sym in symbols:
            ctx["symbols"][sym] = await self._build_symbol_context(sym)
        return ctx

    async def _fetch_sentiment(self) -> str:
        # Placeholder for real market sentiment API
        return "neutral"

    async def _build_symbol_context(self, symbol: str) -> dict[str, Any]:
        ctx: dict[str, Any] = {"symbol": symbol}

        ohlcv_1h = await self._safe_fetch(lambda: self._ccxt.fetch_ohlcv(symbol, timeframe="1h", limit=200))
        ohlcv_15m = await self._safe_fetch(lambda: self._ccxt.fetch_ohlcv(symbol, timeframe="15m", limit=200))
        ohlcv_1d = await self._safe_fetch(lambda: self._ccxt.fetch_ohlcv(symbol, timeframe="1d", limit=90))

        closes = [float(row["close"]) for row in ohlcv_1h] if ohlcv_1h else []
        highs = [float(row["high"]) for row in ohlcv_1h] if ohlcv_1h else []
        lows = [float(row["low"]) for row in ohlcv_1h] if ohlcv_1h else []

        ctx["close"] = closes[-1] if closes else None
        ctx["trend"] = self._trend_metrics(closes)
        ctx["volatility"] = self._volatility_metrics(ohlcv_1h or [], closes, highs, lows)
        ctx["levels"] = self._levels(ohlcv_1h or [], ohlcv_1d or [])

        ob = await self._safe_fetch(lambda: self._ccxt.fetch_orderbook(symbol, depth=settings.ws_orderbook_levels))
        ctx["orderbook"] = self._orderbook_metrics(ob or {})

        trades = await self._safe_fetch(lambda: self._ccxt.fetch_trades(symbol, limit=300))
        ctx["trade_flow"] = self._trade_flow_metrics(trades or [])

        funding = await self._safe_fetch(lambda: self._ccxt.fetch_funding_rate(symbol))
        ctx["funding_rate"] = float(funding) if funding is not None else None

        closes_15 = [float(row["close"]) for row in ohlcv_15m] if ohlcv_15m else []
        ctx["ltf_trend"] = self._trend_metrics(closes_15)

        return ctx

    async def _safe_fetch(self, fn: Callable[[], Any]):
        try:
            return await fn()
        except Exception:
            return None

    def _orderbook_metrics(self, ob: dict[str, Any]) -> dict[str, float | None]:
        # Normalize decimals to floats to avoid mixed-type math
        bids = [(float(px), float(qty)) for px, qty in (ob.get("bids") or [])]
        asks = [(float(px), float(qty)) for px, qty in (ob.get("asks") or [])]
        snapshot = OrderbookSnapshot(bids=bids, asks=asks)
        stats = spread_depth_stats(snapshot)
        best_bid = bids[0][0] if bids else None
        best_ask = asks[0][0] if asks else None
        mid = (best_bid + best_ask) / 2 if best_bid and best_ask else None
        spread_bps = stats.get("spread_bps")
        depth_10bps = stats.get("depth_at_10bps")
        liquidity_ok = None
        if spread_bps is not None and depth_10bps is not None:
            liquidity_ok = spread_bps <= 10 and depth_10bps >= 5_000
        return {
            "mid": mid,
            "spread_bps": spread_bps,
            "depth_10bps": depth_10bps,
            "depth_50bps": stats.get("depth_at_50bps"),
            "liquidity_ok": liquidity_ok,
        }

    def _trade_flow_metrics(self, trades: list[dict[str, Any]]) -> dict[str, float]:
        buy_quote = sell_quote = 0.0
        large_buy = large_sell = 0
        for t in trades:
            notional = float(t["px"]) * float(t["qty"])
            side = (t.get("side") or "").lower()
            is_large = notional >= 50_000
            if side == "buy":
                buy_quote += notional
                if is_large:
                    large_buy += 1
            elif side == "sell":
                sell_quote += notional
                if is_large:
                    large_sell += 1
        total = buy_quote + sell_quote
        large_trade_side = None
        if large_buy > large_sell:
            large_trade_side = "buy"
        elif large_sell > large_buy:
            large_trade_side = "sell"
        return {
            "buy_quote": buy_quote,
            "sell_quote": sell_quote,
            "net_flow_quote": buy_quote - sell_quote,
            "flow_imbalance": (buy_quote - sell_quote) / total if total else 0.0,
            "large_trade_count": large_buy + large_sell,
            "large_trade_side": large_trade_side,
        }

    def _volatility_metrics(
        self,
        ohlcv: list[dict[str, Any]],
        closes: list[float],
        highs: list[float],
        lows: list[float],
    ) -> dict[str, float | str]:
        if not closes:
            return {"atr": None, "realized_vol": None, "regime": "quiet"}
        returns = [
            math.log(closes[i] / closes[i - 1]) for i in range(1, len(closes)) if closes[i - 1] != 0
        ]
        realized_vol = statistics.pstdev(returns) * math.sqrt(24) if len(returns) > 1 else 0.0
        candles_for_atr = [
            {"high": h, "low": l, "close": c} for h, l, c in zip(highs, lows, closes)
        ]
        atr_val = atr(candles_for_atr, period=14)
        regime = volatility_regime(candles_for_atr)
        return {"atr": atr_val, "realized_vol": realized_vol, "regime": regime}

    def _levels(self, ohlcv_1h: list[dict[str, Any]], ohlcv_1d: list[dict[str, Any]]) -> dict[str, float | None]:
        highs = [float(r["high"]) for r in ohlcv_1h[-60:]] if ohlcv_1h else []
        lows = [float(r["low"]) for r in ohlcv_1h[-60:]] if ohlcv_1h else []
        recent_high = max(highs) if highs else None
        recent_low = min(lows) if lows else None
        daily_highs = [float(r["high"]) for r in ohlcv_1d[-30:]] if ohlcv_1d else []
        daily_lows = [float(r["low"]) for r in ohlcv_1d[-30:]] if ohlcv_1d else []
        support = min(daily_lows) if daily_lows else recent_low
        resistance = max(daily_highs) if daily_highs else recent_high
        return {"recent_high": recent_high, "recent_low": recent_low, "support": support, "resistance": resistance}

    def _trend_metrics(self, closes: list[float]) -> dict[str, Any]:
        if not closes:
            return {"bias": "neutral", "sma_short": None, "sma_long": None}
        sma_short = statistics.fmean(closes[-5:]) if closes else None
        sma_long = statistics.fmean(closes[-20:]) if closes else None
        bias = "neutral"
        if sma_short is not None and sma_long is not None:
            if sma_short > sma_long:
                bias = "up"
            elif sma_short < sma_long:
                bias = "down"
        return {"bias": bias, "sma_short": sma_short, "sma_long": sma_long}

    async def run(self, symbols: list[str] | None = None) -> AnalysisResult:
        symbols = symbols or settings.symbols_list
        context = await self._gather_context(symbols)
        result = await self._llm.market_analysis(context)
        if result is None:
            result = self._deterministic_result(context)
        else:
            result.source = result.source or "openai"
        self._latest = result
        return result

    def _deterministic_result(self, context: dict[str, Any]) -> AnalysisResult:
        symbol_entries: list[SymbolAnalysis] = []
        risks: list[str] = []
        for sym, data in context.get("symbols", {}).items():
            bias, confidence, risk_notes = self._bias_and_risks(data)
            risks.extend(risk_notes)
            symbol_entries.append(
                SymbolAnalysis(
                    symbol=sym,
                    bias=bias,
                    confidence=confidence,
                    summary=self._build_summary(sym, data, bias),
                    trend=data.get("trend", {}).get("bias"),
                    close=data.get("close"),
                    volatility=VolatilityMetrics(**data.get("volatility", {})) if data.get("volatility") else None,
                    liquidity=LiquidityMetrics(**data.get("orderbook", {})) if data.get("orderbook") else None,
                    flow=FlowMetrics(**data.get("trade_flow", {})) if data.get("trade_flow") else None,
                    levels=Levels(**data.get("levels", {})) if data.get("levels") else None,
                    funding_rate=data.get("funding_rate"),
                    risks=risk_notes,
                ),
            )
        return AnalysisResult(
            generated_at=datetime.now(UTC),
            summary="; ".join([f"{s.symbol}: {s.bias} (conf {s.confidence:.2f})" for s in symbol_entries]),
            symbols=symbol_entries,
            risks=list({r for r in risks if r}),
            source="fallback",
        )

    def _bias_and_risks(self, data: dict[str, Any]) -> tuple[str, float, list[str]]:
        risks: list[str] = []
        bias = "neutral"
        confidence = 0.4
        trend_bias = data.get("trend", {}).get("bias")
        ltf_bias = data.get("ltf_trend", {}).get("bias")
        flow = data.get("trade_flow", {})
        ob = data.get("orderbook", {})
        vol = data.get("volatility", {})
        if trend_bias == ltf_bias and trend_bias in {"up", "down"}:
            bias = "long" if trend_bias == "up" else "short"
            confidence += 0.2
        if abs(flow.get("flow_imbalance", 0)) > 0.1:
            confidence += 0.1
        if not ob.get("liquidity_ok", True):
            risks.append("Liquidity thin (wide spread or shallow depth)")
            confidence -= 0.1
        if vol.get("regime") == "expansion":
            risks.append("High volatility regime")
        return bias, max(0.0, min(confidence, 1.0)), risks

    def _build_summary(self, symbol: str, data: dict[str, Any], bias: str) -> str:
        parts = [f"{symbol}: bias {bias}"]
        trend = data.get("trend", {})
        if trend:
            parts.append(f"trend {trend.get('bias')}")
        ob = data.get("orderbook", {})
        if ob:
            spread = ob.get("spread_bps")
            parts.append(f"spread {spread:.2f}bps" if spread is not None else "spread n/a")
        flow = data.get("trade_flow", {})
        if flow:
            imb = flow.get("flow_imbalance")
            parts.append(f"flow imb {imb:.2f}" if imb is not None else "flow n/a")
        return " | ".join(parts)

    def latest(self) -> AnalysisResult | None:
        return self._latest


analysis_agent = AnalysisAgent()
