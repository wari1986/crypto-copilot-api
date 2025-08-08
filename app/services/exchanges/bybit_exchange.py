from __future__ import annotations

from typing import Any, Dict, List

from app.services.exchanges.exchange_base import ExchangeBase


class BybitExchange(ExchangeBase):
    async def place_order(
        self, symbol: str, side: str, type_: str, qty: float, price: float | None = None
    ) -> Dict[str, Any]:
        return {"client_order_id": "stub", "status": "new"}

    async def cancel_order(self, client_order_id: str) -> bool:
        return True

    async def get_open_orders(self, symbol: str | None = None) -> List[Dict[str, Any]]:
        _ = symbol
        return []

    async def get_positions(self) -> List[Dict[str, Any]]:
        return []

    async def get_balance(self) -> Dict[str, float]:
        return {"USDT": 0.0}
