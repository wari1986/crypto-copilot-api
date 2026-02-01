from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas.dex import PoolSnapshotOut
from app.services.dex.meteora import MeteoraAdapter

router = APIRouter(prefix="/dex/meteora", tags=["DEX: Meteora"])


@router.get("/pools/{chain}/{pool_address}", response_model=PoolSnapshotOut)
async def get_meteora_pool(chain: str, pool_address: str) -> PoolSnapshotOut:
    """Fetch a minimal Meteora pool/account snapshot (Solana).

    Notes:
    - Supports `chain` = solana
    - Requires `SOLANA_RPC_URL`
    """

    try:
        snap = await MeteoraAdapter().get_pool(chain=chain, address=pool_address)
        return PoolSnapshotOut(
            chain=snap.chain,
            address=snap.address,
            dex=snap.dex,
            captured_at=snap.captured_at,
            token0=snap.token0,
            token1=snap.token1,
            fee=snap.fee,
            tick_spacing=snap.tick_spacing,
            sqrt_price_x96=snap.sqrt_price_x96,
            tick=snap.tick,
            liquidity=snap.liquidity,
            extra=snap.extra,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Meteora fetch failed: {e}") from e
