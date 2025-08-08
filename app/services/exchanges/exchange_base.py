from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class ExchangeBase(ABC):
    @abstractmethod
    async def place_order(
        self, symbol: str, side: str, type_: str, qty: float, price: float | None = None
    ) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def cancel_order(self, client_order_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def get_open_orders(self, symbol: str | None = None) -> List[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    async def get_positions(self) -> List[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    async def get_balance(self) -> Dict[str, float]:
        raise NotImplementedError
