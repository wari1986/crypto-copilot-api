Crypto Copilot API — Week 1 Skeleton

Completed Tasks

- [x] FastAPI app scaffolding with `/api/v1` prefix and root `/` ok response
- [x] Core: config, logging, errors, CORS
- [x] DB session factory (async)
- [x] Migrations: initial tables for instruments, candles, orders, fills, positions, configs, model_decisions
- [x] Basic routes: health, instruments (stub), candles.backfill (stub), portfolio (db-backed), exec-sim (stub), llm.decide (persist decision)
- [x] LLM contract schemas with JSON schema helper
- [x] LLM decider client/validators/decider (minimal)
- [x] Market data stubs (ccxt adapter, ws bybit, cache) + indicators
- [x] Dockerfile + docker-compose
- [x] Makefile targets

In Progress Tasks

- [ ] Tests: flesh out `tests/test_orders_repo.py`, `tests/test_simulator.py`
- [ ] Repositories for each model with async CRUD
- [ ] Risk service checks against configs
- [ ] Improve `/health` readiness (db + ws heartbeat)
- [ ] Seed script content
- [ ] Pre-commit + CI config

Future Tasks

- [ ] Rate limiting middleware
- [ ] OpenAPI docs polish and examples
- [ ] Real CCXT and Bybit ws wiring + cache integration
- [ ] Execution simulator fills + DB updates
- [ ] Admin UI (separate repo) wiring

Relevant Files

- app/main.py — FastAPI app and router wiring ✅
- app/core/config.py — env settings ✅
- app/db/models.py — ORM models ✅
- migrations/versions/0001_initial.py — initial schema ✅
- app/schemas/llm_contract.py — LLM contract ✅
- app/services/llm_decider/\* — client/validators/decider ✅
- app/services/market_data/\* — ccxt/ws/cache + indicators ✅
- app/services/portfolio/portfolio_service.py — portfolio derived state ✅
- app/api/routes/\* — api endpoints ✅
- app/workers/scheduler.py — periodic task helper ✅

Implementation Notes

- Default DB is in-memory SQLite for dev/tests via `DATABASE_URL` default; set Postgres for prod/dev docker.
- JSON fields use Postgres JSONB with SQLite fallback.
- Minimal validators enforce obvious guardrails; risk engine integration TBD.
