from __future__ import annotations

from typing import Any

from app.services.exchanges.exchange_base import ExchangeBase


class BybitExchange(ExchangeBase):
    async def place_order(
        self, symbol: str, side: str, type_: str, qty: float, price: float | None = None,
    ) -> dict[str, Any]:
        return {"client_order_id": "stub", "status": "new"}

    async def cancel_order(self, client_order_id: str) -> bool:
        return True

    async def get_open_orders(self, symbol: str | None = None) -> list[dict[str, Any]]:
        _ = symbol
        return []

    async def get_positions(self) -> list[dict[str, Any]]:
        return []

    async def get_balance(self) -> dict[str, float]:
        return {"USDT": 0.0}
