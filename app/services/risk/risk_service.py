from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RiskSettings:
    per_trade_risk_pct: float = 1.0
    daily_loss_limit: float = 5.0


class RiskService:
    def __init__(self, settings: RiskSettings | None = None) -> None:
        self._settings = settings or RiskSettings()

    def check_per_trade_risk(self, notional: float, equity: float) -> bool:
        if equity <= 0:
            return False
        return (notional / equity) * 100.0 <= self._settings.per_trade_risk_pct
