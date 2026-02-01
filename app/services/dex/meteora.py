from __future__ import annotations

from datetime import datetime, timezone

import httpx

from app.core.config import settings
from app.services.dex.base import DexAdapter
from app.services.dex.types import PoolSnapshot


class MeteoraAdapter(DexAdapter):
    """Meteora adapter (Solana).

    MVP scope: fetch and return a minimal snapshot using Solana JSON-RPC `getAccountInfo`.

    Notes:
    - Meteora has multiple program types (DLMM, etc.). Proper decoding will come next.
    - For now we return the raw account info payload in `extra` so downstream code can evolve
      without changing the fetch surface.
    """

    dex = "meteora"

    async def get_pool(self, *, chain: str, address: str) -> PoolSnapshot:
        chain_norm = chain.lower().strip()
        if chain_norm not in {"solana", "sol", "mainnet"}:
            raise ValueError("Unsupported chain for Meteora adapter (solana)")

        rpc = settings.solana_rpc_url
        if not rpc:
            raise RuntimeError("Missing SOLANA_RPC_URL. Required for Meteora reads.")

        # Solana addresses are base58; we do lightweight validation here.
        if not (32 <= len(address) <= 64):
            raise ValueError("Invalid Solana address length")

        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getAccountInfo",
            "params": [address, {"encoding": "base64"}],
        }

        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(rpc, json=payload)
            resp.raise_for_status()
            data = resp.json()

        if "error" in data:
            raise RuntimeError(f"Solana RPC error: {data['error']}")

        return PoolSnapshot(
            chain="solana",
            address=address,
            dex=self.dex,
            captured_at=datetime.now(timezone.utc),
            extra={
                "rpc": rpc,
                "accountInfo": data.get("result"),
            },
        )
