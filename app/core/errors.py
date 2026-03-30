from __future__ import annotations

from typing import cast

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.types import ExceptionHandler


class AppError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


def setup_exception_handlers(app: FastAPI) -> None:
    handler = cast(ExceptionHandler, app_error_handler)
    app.add_exception_handler(AppError, handler)
