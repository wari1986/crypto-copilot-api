from __future__ import annotations

from typing import Annotated

from fastapi import FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings


def setup_cors(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


async def require_demo_api_key(
    x_demo_api_key: Annotated[str | None, Header(alias="X-Demo-Api-Key")] = None,
) -> None:
    if not settings.demo_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="DEMO_API_KEY is not configured for protected endpoints.",
        )
    if x_demo_api_key != settings.demo_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid demo API key.",
        )
