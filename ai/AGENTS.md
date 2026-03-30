# Crypto Copilot API Agent Guide

This file is the session entrypoint for AI work in this repository.

The design philosophy in this repo is intentionally durable and should survive language, framework, or tooling changes. Implementation guidance below is adapted to the current stack: Python 3.11, FastAPI, Pydantic v2, async SQLAlchemy, Alembic, and supporting services around market data, DEX integrations, and LLM validation.

## Scope

These instructions apply to the entire `crypto-copilot-api` repository.

## Boot Sequence

Read these files in order at the start of each session:

1. [`ai/AGENTS.md`](/Users/Nico/dev/crypto-copilot-api/ai/AGENTS.md)
2. [`ai/ARCHITECTURE.md`](/Users/Nico/dev/crypto-copilot-api/ai/ARCHITECTURE.md)
3. [`ai/DECISIONS.md`](/Users/Nico/dev/crypto-copilot-api/ai/DECISIONS.md)
4. [`ai/context.md`](/Users/Nico/dev/crypto-copilot-api/ai/context.md)
5. [`ai/tasks/README.md`](/Users/Nico/dev/crypto-copilot-api/ai/tasks/README.md)
6. Read the active task brief in `ai/tasks/*.md` when the work has a named feature brief.
7. Then load folder-specific overlays when touching those areas.

## Folder Guidance

- If working in `app/api/routes/**` or `app/api/deps.py`, read [`ai/agents/api-routes.md`](/Users/Nico/dev/crypto-copilot-api/ai/agents/api-routes.md).
- If working in `app/services/**`, read [`ai/agents/services.md`](/Users/Nico/dev/crypto-copilot-api/ai/agents/services.md).
- If working in `app/db/**`, read [`ai/agents/db.md`](/Users/Nico/dev/crypto-copilot-api/ai/agents/db.md).
- If working in `app/schemas/**`, read [`ai/agents/schemas.md`](/Users/Nico/dev/crypto-copilot-api/ai/agents/schemas.md).
- If working in `app/workers/**`, read [`ai/agents/workers.md`](/Users/Nico/dev/crypto-copilot-api/ai/agents/workers.md).

## Workflow Rules

- Keep diffs minimal and avoid rewriting unrelated code.
- Prefer `apply_patch` for small targeted edits.
- Use `rg` and `rg --files` for search.
- Preserve the existing service boundaries before introducing new abstractions.
- Keep route handlers thin and move orchestration into services.
- Keep LLM behavior schema-bound and validator-gated.
- Keep execution logic paper-only; do not introduce real-trading side effects.
- Update docs in `ai/` when the working agreement changes.

## Engineering Philosophy

- Clarity over cleverness.
- Preserve abstraction boundaries.
- Favor deterministic computation before probabilistic generation.
- Keep side effects explicit.
- Fix root causes over symptom patches.
- Prefer focused modules over broad utility layers.
- Centralize configuration.
- Make safe behavior the default path.

## Python And FastAPI Standards

- Use explicit typing on public functions, service methods, and schemas.
- Prefer Pydantic models over loose dictionaries for request, response, and LLM contracts.
- Keep async request paths fully async.
- Put environment-backed settings in `app/core/config.py`.
- Keep app setup in `app/core/` and `app/main.py`, not scattered across modules.
- Favor small service entrypoints with explicit dependencies over hidden globals.

## Review And Quality Standards

- Evaluate changes critically against both software design fundamentals and current Python/FastAPI best practices.
- State behavior change clearly: what worked before, what changes now, and why.
- Call out risks to safety boundaries, typing, validation, or persistence behavior.
- When reviewing, focus first on correctness, regressions, and missing tests.

## Canonical References

- Architecture map: [`ai/ARCHITECTURE.md`](/Users/Nico/dev/crypto-copilot-api/ai/ARCHITECTURE.md)
- Decision log: [`ai/DECISIONS.md`](/Users/Nico/dev/crypto-copilot-api/ai/DECISIONS.md)
- Operational context: [`ai/context.md`](/Users/Nico/dev/crypto-copilot-api/ai/context.md)
- Session runbook: [`ai/runbooks/codex-session-runbook.md`](/Users/Nico/dev/crypto-copilot-api/ai/runbooks/codex-session-runbook.md)
- Task brief system: [`ai/tasks/README.md`](/Users/Nico/dev/crypto-copilot-api/ai/tasks/README.md)
