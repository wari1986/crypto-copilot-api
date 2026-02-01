from __future__ import annotations

from datetime import datetime, timezone

from web3 import Web3

from app.core.config import settings
from app.services.dex.base import DexAdapter
from app.services.dex.types import PoolSnapshot

# Minimal ABI fragments for Uniswap V3 Pool
UNIV3_POOL_ABI = [
    {
        "inputs": [],
        "name": "slot0",
        "outputs": [
            {"internalType": "uint160", "name": "sqrtPriceX96", "type": "uint160"},
            {"internalType": "int24", "name": "tick", "type": "int24"},
            {"internalType": "uint16", "name": "observationIndex", "type": "uint16"},
            {"internalType": "uint16", "name": "observationCardinality", "type": "uint16"},
            {
                "internalType": "uint16",
                "name": "observationCardinalityNext",
                "type": "uint16",
            },
            {"internalType": "uint8", "name": "feeProtocol", "type": "uint8"},
            {"internalType": "bool", "name": "unlocked", "type": "bool"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "liquidity",
        "outputs": [{"internalType": "uint128", "name": "", "type": "uint128"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "fee",
        "outputs": [{"internalType": "uint24", "name": "", "type": "uint24"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "tickSpacing",
        "outputs": [{"internalType": "int24", "name": "", "type": "int24"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "token0",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "token1",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
]


class UniswapV3Adapter(DexAdapter):
    dex = "uniswapv3"

    def _web3(self, *, chain: str) -> Web3:
        rpc = settings.rpc_for_chain(chain)
        if not rpc:
            raise RuntimeError(
                "Missing RPC url for chain. Set one of: ETHEREUM_RPC_URL, BASE_RPC_URL, ARBITRUM_RPC_URL."
            )
        return Web3(Web3.HTTPProvider(rpc))

    async def get_pool(self, *, chain: str, address: str) -> PoolSnapshot:
        # This adapter is synchronous web3 calls; keep the API async-safe for now.
        chain_norm = chain.lower().strip()
        if chain_norm in {"eth", "mainnet"}:
            chain_norm = "ethereum"
        if chain_norm == "arb":
            chain_norm = "arbitrum"
        if chain_norm not in {"ethereum", "base", "arbitrum"}:
            raise ValueError("Unsupported chain for Uniswap v3 adapter (ethereum|base|arbitrum)")

        w3 = self._web3(chain=chain_norm)
        if not w3.is_address(address):
            raise ValueError("Invalid pool address")

        pool_addr = w3.to_checksum_address(address)
        contract = w3.eth.contract(address=pool_addr, abi=UNIV3_POOL_ABI)

        slot0 = contract.functions.slot0().call()
        sqrt_price_x96 = int(slot0[0])
        tick = int(slot0[1])

        liquidity = int(contract.functions.liquidity().call())
        fee = int(contract.functions.fee().call())
        tick_spacing = int(contract.functions.tickSpacing().call())
        token0 = str(contract.functions.token0().call())
        token1 = str(contract.functions.token1().call())

        return PoolSnapshot(
            chain=chain_norm,
            address=pool_addr,
            dex=self.dex,
            captured_at=datetime.now(timezone.utc),
            token0=token0,
            token1=token1,
            fee=fee,
            tick_spacing=tick_spacing,
            sqrt_price_x96=sqrt_price_x96,
            tick=tick,
            liquidity=liquidity,
        )
