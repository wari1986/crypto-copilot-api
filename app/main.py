from __future__ import annotations

from fastapi import FastAPI

from app.api.routes.candles import router as candles_router
from app.api.routes.exec_sim import router as exec_sim_router
from app.api.routes.health import router as health_router
from app.api.routes.instruments import router as instruments_router
from app.api.routes.llm_decider import router as llm_router
from app.api.routes.marketdata import router as marketdata_router
from app.api.routes.portfolio import router as portfolio_router
from app.core.config import settings
from app.core.errors import setup_exception_handlers
from app.core.logging import configure_logging
from app.core.security import setup_cors

configure_logging(settings.log_level)
app = FastAPI(title="Crypto Copilot API", version="0.1.0", openapi_url="/openapi.json")
setup_cors(app)
setup_exception_handlers(app)

app.include_router(health_router, prefix="/api/v1")
app.include_router(instruments_router, prefix="/api/v1")
app.include_router(candles_router, prefix="/api/v1")
app.include_router(portfolio_router, prefix="/api/v1")
app.include_router(exec_sim_router, prefix="/api/v1")
app.include_router(llm_router, prefix="/api/v1")
app.include_router(marketdata_router, prefix="/api/v1")


@app.get("/")
async def root() -> dict[str, str]:
    return {"status": "ok"}
