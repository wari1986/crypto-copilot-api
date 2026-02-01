from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env",), env_prefix="", case_sensitive=False)

    env: Literal["dev", "prod", "test"] = Field(default="dev", alias="ENV")
    api_port: int = Field(default=8000, alias="API_PORT")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO",
        alias="LOG_LEVEL",
    )

    # Default to in-memory SQLite for local dev/tests to avoid requiring Postgres at import time
    database_url: str = Field(default="sqlite+aiosqlite:///:memory:", alias="DATABASE_URL")

    # Database pool configuration (tuned for serverless Postgres like Supabase)
    db_pool_size: int = Field(default=5, alias="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=5, alias="DB_MAX_OVERFLOW")
    db_pool_timeout: int = Field(default=30, alias="DB_POOL_TIMEOUT")
    db_pool_recycle_seconds: int = Field(default=1800, alias="DB_POOL_RECYCLE_SECONDS")

    ccxt_rate_limit: bool = Field(default=True, alias="CCXT_RATE_LIMIT")

    bybit_api_key: str | None = Field(default=None, alias="BYBIT_API_KEY")
    bybit_api_secret: str | None = Field(default=None, alias="BYBIT_API_SECRET")
    bybit_testnet: bool = Field(default=True, alias="BYBIT_TESTNET")

    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-5", alias="OPENAI_MODEL")
    openai_timeout_seconds: int = Field(default=60, alias="OPENAI_TIMEOUT_SECONDS")

    # Market data configuration (legacy exchange plumbing kept; not the focus)
    exchange: str = Field(default="bybit", alias="EXCHANGE")
    spot_only: bool = Field(default=True, alias="SPOT_ONLY")
    symbols: str = Field(default="BTC/USDT,ETH/USDT,SOL/USDT", alias="SYMBOLS")
    ws_orderbook_levels: int = Field(default=50, alias="WS_ORDERBOOK_LEVELS")
    ws_snapshot_interval_sec: int = Field(default=30, alias="WS_SNAPSHOT_INTERVAL_SEC")
    backfill_lookback_days: int = Field(default=120, alias="BACKFILL_LOOKBACK_DAYS")
    ws_public_url: str = Field(
        default="wss://stream.bybit.com/v5/public/spot", alias="WS_PUBLIC_URL"
    )

    # DEX / on-chain providers
    ethereum_rpc_url: str | None = Field(default=None, alias="ETHEREUM_RPC_URL")
    # Alias (shorter) for the same value; if both are set, ETHEREUM_RPC_URL wins.
    eth_rpc_url: str | None = Field(default=None, alias="ETH_RPC_URL")

    # Ingestion/worker feature flags
    enable_market_data_tasks: bool = Field(default=False, alias="ENABLE_MARKET_DATA_TASKS")
    enable_backfill_on_startup: bool = Field(default=False, alias="ENABLE_BACKFILL_ON_STARTUP")

    @property
    def symbols_list(self) -> list[str]:
        return [s.strip() for s in self.symbols.split(",") if s.strip()]

    @property
    def ethereum_rpc(self) -> str | None:
        return self.ethereum_rpc_url or self.eth_rpc_url


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
