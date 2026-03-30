from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_demo_api_key
from app.db.session import get_session

DbSessionDep = Annotated[AsyncSession, Depends(get_session)]
DemoKeyDep = Annotated[None, Depends(require_demo_api_key)]
