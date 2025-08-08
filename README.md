# Crypto Trading Copilot — API

FastAPI + SQLAlchemy (async) backend for a crypto trading copilot. Week 1 scope: data access, risk guardrails, paper execution simulator, and LLM decision validation/persistence. No real-money trading.

## Tech
- Python 3.11+
- FastAPI
- SQLAlchemy 2.x (async) + Alembic
- Postgres (Supabase)
- Pydantic v2
- CCXT
- WebSockets (async)
- OpenAI SDK

## Architecture (Week 1)
```
+------------------+    +----------------+     +-------------------+
|  API (FastAPI)   | -> |  Services      |  -> |  Repositories/DB  |
|  /api/v1/...     |    |  (market,risk, |     |  (SQLAlchemy)     |
|  health, llm, .. |    |  portfolio,    |     |  Postgres         |
+------------------+    |  exec-sim)     |     +-------------------+
          |              +----------------+                |
          v                        |                        v
  LLM Decider (OpenAI) ----> Validators ----> model_decisions table
```

## Quickstart (Local)
```bash
uv sync --all-extras
cp .env.example .env
make migrate
make run
```

## Configuration (.env)
See `.env.example` for all keys. Use your Supabase Postgres URI in `DATABASE_URL`.

## Migrations
```bash
make migrate  # creates DB and runs alembic migrations
```

## API Reference (Week 1)
- GET `/api/v1/health`
- GET `/api/v1/instruments?exchange=BYBIT`
- POST `/api/v1/candles/backfill`
- GET `/api/v1/portfolio/positions`
- GET `/api/v1/portfolio/orders`
- GET `/api/v1/portfolio/pnl`
- POST `/api/v1/exec-sim/submit`
- POST `/api/v1/llm/decide`

## LLM Decision Contract
Strict Pydantic v2 models with JSON Schema export. See `app/schemas/llm_contract.py` and `tests/test_llm_contract.py`.

## Contributing
- Formatter: black
- Linter: ruff
- Typing: mypy
- Use `pre-commit install`

## License
MIT
