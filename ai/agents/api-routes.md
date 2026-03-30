# AGENTS — app/api/routes/

Scope: FastAPI route modules and API-layer dependency wiring.

## Boot Sequence

1. Read [`ai/AGENTS.md`](/Users/Nico/dev/crypto-copilot-api/ai/AGENTS.md).
2. Read [`ai/ARCHITECTURE.md`](/Users/Nico/dev/crypto-copilot-api/ai/ARCHITECTURE.md), [`ai/DECISIONS.md`](/Users/Nico/dev/crypto-copilot-api/ai/DECISIONS.md), [`ai/context.md`](/Users/Nico/dev/crypto-copilot-api/ai/context.md), and the active task brief when one exists.
3. Apply this file for route-layer constraints.

## Core Rules

- Keep route handlers thin.
- Validate and parse input at the API boundary.
- Reuse dependency wiring from `app/api/deps.py`.
- Delegate orchestration to services rather than embedding domain logic in routes.
- Return typed responses when practical.
- Do not put exchange logic, DEX math, simulator logic, or LLM orchestration directly in route functions.

## FastAPI Practices

- Prefer explicit request and response schemas over loose JSON payloads.
- Keep status codes and error mapping consistent with the existing app behavior.
- Do not leak secrets, internal exceptions, or raw provider errors.
- Keep route modules grouped by domain, not by technical helper type.

## References

- Global rules: [`ai/AGENTS.md`](/Users/Nico/dev/crypto-copilot-api/ai/AGENTS.md)
- Session runbook: [`ai/runbooks/codex-session-runbook.md`](/Users/Nico/dev/crypto-copilot-api/ai/runbooks/codex-session-runbook.md)
