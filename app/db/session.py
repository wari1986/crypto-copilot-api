from __future__ import annotations

from collections.abc import AsyncIterator

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
        _engine = create_async_engine(settings.database_url, pool_pre_ping=True)
    if _session_maker is None:
        _session_maker = async_sessionmaker(
            _engine, expire_on_commit=False, autoflush=False, autocommit=False,
        )
    return _session_maker


async def get_session() -> AsyncIterator[AsyncSession]:
    session_factory = _ensure_session_factory()
    async with session_factory() as session:
        yield session
