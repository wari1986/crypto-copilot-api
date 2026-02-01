from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas.dex import PoolSnapshotOut
from app.services.dex.uniswap_v3 import UniswapV3Adapter

router = APIRouter(prefix="/dex/uniswapv3", tags=["DEX: Uniswap v3"])


@router.get("/pools/{chain}/{pool_address}", response_model=PoolSnapshotOut)
async def get_uniswapv3_pool(chain: str, pool_address: str) -> PoolSnapshotOut:
    """Fetch a normalized Uniswap v3 pool snapshot.

    Notes:
    - Supports `chain` in {ethereum|base|arbitrum}.
    - Requires the matching RPC url env var:
      - ETHEREUM_RPC_URL
      - BASE_RPC_URL
      - ARBITRUM_RPC_URL
    """

    try:
        snap = await UniswapV3Adapter().get_pool(chain=chain, address=pool_address)
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
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Uniswap v3 fetch failed: {e}") from e
