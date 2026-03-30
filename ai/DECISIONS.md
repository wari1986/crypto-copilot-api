# Crypto Copilot API Decision Log

This file records durable engineering decisions for `crypto-copilot-api`.
Dates are best-effort when the exact historical adoption date is unclear.

## 2026-03-30 — AI documentation uses `ai/` as the local control plane

### Decision
Adopt a canonical `ai/` doc set with `AGENTS`, `ARCHITECTURE`, `DECISIONS`, `context`, `tasks/`, `runbooks/`, and folder overlays under `ai/agents/`.

### Context
The repo needed a stable boot sequence for LLM-assisted work and a place to preserve architecture rules, operational context, and change rationale across sessions.

### Consequences
- Sessions now have a defined read order.
- Folder-specific overlays can hold implementation rules without duplicating global policy.
- The design philosophy and current-stack practices are documented separately but consistently.

## Existing convention — Backend stays FastAPI-first with thin routes and service-layer orchestration

### Decision
Keep FastAPI route handlers thin and move most operational logic into `app/services/**`.

### Context
Route-heavy logic becomes difficult to test, easy to duplicate, and harder to evolve safely as integrations grow.

### Consequences
- Routes should mostly validate input, obtain dependencies, call services, and return results.
- Service modules own exchange, DEX, simulator, market-data, and LLM orchestration logic.

## Existing convention — LLM outputs remain schema-bound and validator-gated

### Decision
Treat LLM output as untrusted until it conforms to explicit schemas and validation rules.

### Context
Trading advice is safety-sensitive, and free-form model output cannot be allowed to drive decisions or execution behavior directly.

### Consequences
- Contracts belong in `app/schemas/**`.
- Validators stay in dedicated service logic, not ad hoc route code.
- New model-assisted flows must preserve deterministic validation before any downstream action.

## Existing convention — Execution remains paper-only

### Decision
Keep execution logic simulated and do not introduce real-money trading effects.

### Context
The repository is explicitly framed as a copilot and simulator, not a live trading engine.

### Consequences
- Execution features must stay non-custodial and non-live.
- Code that could place real orders or bypass guardrails should be treated as out of scope unless explicitly requested and reviewed.

## Existing convention — Configuration is centralized in `app/core/config.py`

### Decision
Use the Pydantic settings model in `app/core/config.py` as the authoritative environment/config boundary.

### Context
Scattered environment reads create drift, hidden runtime behavior, and inconsistent defaults.

### Consequences
- New env vars should be added in the settings model.
- `.env.example` should be updated when new operator-facing configuration is introduced.

## Existing convention — Async SQLAlchemy and typed schemas are first-class

### Decision
Keep persistence async and use typed Pydantic models for stable boundaries.

### Context
This repo depends on explicit contracts across API, DB, and LLM integration layers.

### Consequences
- Avoid loose dictionaries at important boundaries.
- Prefer explicit types, repository helpers, and focused tests over convenience shortcuts.
