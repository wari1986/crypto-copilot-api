from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable


async def run_periodic(task: Callable[[], Awaitable[None]], interval_seconds: int) -> None:
    while True:
        try:
            await task()
        except Exception:
            pass
        await asyncio.sleep(interval_seconds)
