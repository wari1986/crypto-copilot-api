from __future__ import annotations

from functools import lru_cache
from typing import Literal, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env",), env_prefix="", case_sensitive=False)

    env: Literal["dev", "prod", "test"] = Field(default="dev", alias="ENV")
    api_port: int = Field(default=8000, alias="API_PORT")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO", alias="LOG_LEVEL"
    )

    # Default to in-memory SQLite for local dev/tests to avoid requiring Postgres at import time
    database_url: str = Field(default="sqlite+aiosqlite:///:memory:", alias="DATABASE_URL")

    ccxt_rate_limit: bool = Field(default=True, alias="CCXT_RATE_LIMIT")

    bybit_api_key: Optional[str] = Field(default=None, alias="BYBIT_API_KEY")
    bybit_api_secret: Optional[str] = Field(default=None, alias="BYBIT_API_SECRET")
    bybit_testnet: bool = Field(default=True, alias="BYBIT_TESTNET")

    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-5", alias="OPENAI_MODEL")
    openai_timeout_seconds: int = Field(default=60, alias="OPENAI_TIMEOUT_SECONDS")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
