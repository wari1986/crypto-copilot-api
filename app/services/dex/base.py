from __future__ import annotations

from abc import ABC, abstractmethod

from app.services.dex.types import PoolSnapshot


class DexAdapter(ABC):
    """Interface for DEX adapters.

    Adapters should return normalized pool snapshots that downstream LP math and
    strategy engines can consume.
    """

    @abstractmethod
    async def get_pool(self, *, chain: str, address: str) -> PoolSnapshot:
        raise NotImplementedError
