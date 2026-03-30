# AGENTS — app/db/

Scope: SQLAlchemy base, sessions, models, and repository helpers.

## Boot Sequence

1. Read [`ai/AGENTS.md`](/Users/Nico/dev/crypto-copilot-api/ai/AGENTS.md).
2. Read [`ai/ARCHITECTURE.md`](/Users/Nico/dev/crypto-copilot-api/ai/ARCHITECTURE.md), [`ai/DECISIONS.md`](/Users/Nico/dev/crypto-copilot-api/ai/DECISIONS.md), [`ai/context.md`](/Users/Nico/dev/crypto-copilot-api/ai/context.md), and the active task brief when one exists.
3. Apply this file for DB-layer rules.

## Persistence Rules

- Keep session lifecycle in the existing async SQLAlchemy flow.
- Keep ORM models, repository code, and API schemas separated.
- Prefer repository helpers or focused DB modules when persistence logic is repeated or non-trivial.
- Avoid sprinkling raw SQL or engine setup across unrelated modules.
- Make transaction boundaries explicit when write behavior becomes more than a single simple operation.

## Data Modeling

- Preserve model clarity over convenience shortcuts.
- Keep field naming and typing aligned with existing model patterns.
- When persistence changes affect API or LLM contracts, update schemas and tests in the same change.

## References

- Global rules: [`ai/AGENTS.md`](/Users/Nico/dev/crypto-copilot-api/ai/AGENTS.md)
- Architecture map: [`ai/ARCHITECTURE.md`](/Users/Nico/dev/crypto-copilot-api/ai/ARCHITECTURE.md)
