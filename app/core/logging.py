from __future__ import annotations

import logging
import sys
from contextvars import ContextVar

_request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)


def set_request_id(request_id: str | None) -> None:
    _request_id_ctx.set(request_id)


class RequestIdFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:  # noqa: D401
        request_id = _request_id_ctx.get()
        record.request_id = request_id or "-"  # type: ignore[attr-defined]
        return super().format(record)


def configure_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(stream=sys.stdout)
    formatter = RequestIdFormatter(
        fmt=(
            "%(asctime)s %(levelname)s [%(name)s] [req=%(request_id)s] "
            "%(message)s"
        ),
    )
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
