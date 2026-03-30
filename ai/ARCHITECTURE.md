# Crypto Copilot API Architecture

This file is the canonical architecture map for `crypto-copilot-api`.
Behavior and workflow rules stay in [`ai/AGENTS.md`](/Users/Nico/dev/crypto-copilot-api/ai/AGENTS.md). Historical rationale stays in [`ai/DECISIONS.md`](/Users/Nico/dev/crypto-copilot-api/ai/DECISIONS.md).

## System Overview

- Runtime: FastAPI application assembled in `app/main.py`.
- Primary goal: expose a backend API for market data, portfolio context, DEX integrations, paper execution, and LLM-backed trading advice with strict validation.
- Current stack: Python 3.11, FastAPI, Pydantic v2, async SQLAlchemy, Alembic, Postgres or SQLite, CCXT, OpenAI SDK, Web3/WebSocket integrations.
- Operational posture: backend-first, paper-trading only, with deterministic validation between model output and execution paths.

## Design Boundaries

These boundaries are design-level rules, not framework-specific accidents:

- transport stays thin
- business logic lives outside request handlers
- persistence is isolated from HTTP orchestration
- configuration is centralized
- safety checks sit between intelligence and execution

If the language or framework changes later, keep those boundaries intact unless there is a strong reason not to.

## Top-Level Module Map

- [`app/main.py`](/Users/Nico/dev/crypto-copilot-api/app/main.py): application assembly, router registration, startup tasks.
- [`app/api/`](/Users/Nico/dev/crypto-copilot-api/app/api): HTTP layer, dependencies, and route modules.
- [`app/core/`](/Users/Nico/dev/crypto-copilot-api/app/core): config, logging, security, exception handling, app-wide setup.
- [`app/db/`](/Users/Nico/dev/crypto-copilot-api/app/db): SQLAlchemy base, session wiring, models, repositories.
- [`app/schemas/`](/Users/Nico/dev/crypto-copilot-api/app/schemas): typed API and contract boundaries.
- [`app/services/`](/Users/Nico/dev/crypto-copilot-api/app/services): business logic, exchange adapters, DEX integrations, simulation, LLM services.
- [`app/workers/`](/Users/Nico/dev/crypto-copilot-api/app/workers): scheduled/background startup tasks.
- [`tests/`](/Users/Nico/dev/crypto-copilot-api/tests): smoke tests and contract-oriented tests.

## Data And Control Flow

1. FastAPI routes accept requests under `/api/v1`.
2. Dependencies provide DB sessions and shared runtime context.
3. Services perform domain logic, external API calls, simulation, and validation.
4. Repositories or DB helpers persist state through async SQLAlchemy.
5. Schemas define the contracts at API and LLM boundaries.
6. Workers run optional startup or ingestion workflows behind explicit settings.

## Architectural Conventions

- Route files should parse input, call dependencies, delegate to services, and return typed output.
- DEX, exchange, market-data, simulator, and LLM logic belong in `app/services/**`.
- New settings belong in `app/core/config.py`.
- Request/response and model-facing contracts belong in `app/schemas/**`.
- Repeated or non-trivial persistence logic belongs behind DB-layer helpers or repositories.
- Safety-critical validation must happen before any simulated execution effect is persisted or returned as actionable advice.

## Architecture-Relevant Commands

- App boot: `make run`
- Migrations: `make migrate`
- Tests: `make test`
- Lint + type-check: `make lint`
- Formatting: `make fmt`

## Related Documents

- Workflow and guardrails: [`ai/AGENTS.md`](/Users/Nico/dev/crypto-copilot-api/ai/AGENTS.md)
- Decision history: [`ai/DECISIONS.md`](/Users/Nico/dev/crypto-copilot-api/ai/DECISIONS.md)
- Operational context: [`ai/context.md`](/Users/Nico/dev/crypto-copilot-api/ai/context.md)
- Session runbook: [`ai/runbooks/codex-session-runbook.md`](/Users/Nico/dev/crypto-copilot-api/ai/runbooks/codex-session-runbook.md)
