# AGENTS — app/workers/

Scope: startup tasks, schedulers, and background ingestion behavior.

## Boot Sequence

1. Read [`ai/AGENTS.md`](/Users/Nico/dev/crypto-copilot-api/ai/AGENTS.md).
2. Read [`ai/ARCHITECTURE.md`](/Users/Nico/dev/crypto-copilot-api/ai/ARCHITECTURE.md), [`ai/DECISIONS.md`](/Users/Nico/dev/crypto-copilot-api/ai/DECISIONS.md), [`ai/context.md`](/Users/Nico/dev/crypto-copilot-api/ai/context.md), and the active task brief when one exists.
3. Apply this file for worker-specific rules.

## Worker Rules

- Keep startup behavior explicit and traceable.
- Gate background tasks behind clear settings or feature flags.
- Avoid hiding important side effects in import-time behavior.
- Make failure modes observable through logging and clear control flow.
- Keep worker logic separate from HTTP concerns.

## Operational Practices

- Be conservative with tasks that call external providers repeatedly.
- Prefer idempotent or restart-safe behavior where feasible.
- Document new worker flags or operator expectations in `.env.example`, `RUNBOOK.md`, or task briefs when relevant.

## References

- Global rules: [`ai/AGENTS.md`](/Users/Nico/dev/crypto-copilot-api/ai/AGENTS.md)
- Session runbook: [`ai/runbooks/codex-session-runbook.md`](/Users/Nico/dev/crypto-copilot-api/ai/runbooks/codex-session-runbook.md)
