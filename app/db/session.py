from __future__ import annotations

import os
import ssl
from collections.abc import AsyncIterator
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import certifi
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

_engine: AsyncEngine | None = None
_session_maker: async_sessionmaker[AsyncSession] | None = None


def _ensure_session_factory() -> async_sessionmaker[AsyncSession]:
    global _engine, _session_maker
    if _engine is None:
        db_url = settings.database_url
        # Normalize SSL params for asyncpg: drop sslmode, ensure ssl=true
        if db_url.startswith("postgresql+asyncpg://"):
            parsed = urlparse(db_url)
            q = parse_qs(parsed.query)
            if "sslmode" in q:
                q.pop("sslmode", None)
            if "ssl" not in q:
                q["ssl"] = ["true"]
            db_url = urlunparse(
                (
                    parsed.scheme,
                    parsed.netloc,
                    parsed.path,
                    parsed.params,
                    urlencode(q, doseq=True),
                    parsed.fragment,
                ),
            )
        connect_args: dict[str, object] = {}
        if db_url.startswith("postgresql+asyncpg://"):
            # Prefer user-provided root cert; fallback to certifi bundle
            cafile = os.getenv("PGSSLROOTCERT") or os.getenv("DB_SSL_ROOT_CERT") or certifi.where()
            verify = os.getenv("DB_SSL_VERIFY", "true").lower() != "false"
            if verify:
                ssl_context = ssl.create_default_context(cafile=cafile)
                ssl_context.check_hostname = True
            else:
                # Insecure: disable verification (dev only)
                ssl_context = ssl._create_unverified_context()
                ssl_context.check_hostname = False
            connect_args["ssl"] = ssl_context
        _engine = create_async_engine(
            db_url,
            pool_pre_ping=True,
            connect_args=connect_args,
            pool_size=settings.db_pool_size if "sqlite" not in db_url else None,  # type: ignore[arg-type]
            max_overflow=settings.db_max_overflow if "sqlite" not in db_url else None,  # type: ignore[arg-type]
            pool_timeout=settings.db_pool_timeout,
            pool_recycle=settings.db_pool_recycle_seconds,
        )
    if _session_maker is None:
        _session_maker = async_sessionmaker(
            _engine,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )
    return _session_maker


async def get_session() -> AsyncIterator[AsyncSession]:
    session_factory = _ensure_session_factory()
    async with session_factory() as session:
        yield session


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the async sessionmaker for background tasks."""
    return _ensure_session_factory()
