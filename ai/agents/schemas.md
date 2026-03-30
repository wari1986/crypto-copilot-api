# AGENTS — app/schemas/

Scope: Pydantic models for API contracts, LLM contracts, and typed boundaries.

## Boot Sequence

1. Read [`ai/AGENTS.md`](/Users/Nico/dev/crypto-copilot-api/ai/AGENTS.md).
2. Read [`ai/ARCHITECTURE.md`](/Users/Nico/dev/crypto-copilot-api/ai/ARCHITECTURE.md), [`ai/DECISIONS.md`](/Users/Nico/dev/crypto-copilot-api/ai/DECISIONS.md), [`ai/context.md`](/Users/Nico/dev/crypto-copilot-api/ai/context.md), and the active task brief when one exists.
3. Apply this file for schema-specific rules.

## Contract Rules

- Prefer explicit Pydantic models over unstructured dictionaries.
- Keep API contracts and model-facing contracts stable and readable.
- Treat schema changes as interface changes that may require route, service, and test updates.
- Do not relax validation just to accommodate uncertain upstream or LLM behavior.
- Reuse shared domain types when it improves consistency.

## FastAPI And Pydantic Practices

- Use Pydantic v2 patterns consistently.
- Keep field names, defaults, and optionality intentional.
- Use clear names that map to business meaning, not implementation accidents.
- When a contract is safety-sensitive, choose strictness over convenience.

## References

- Global rules: [`ai/AGENTS.md`](/Users/Nico/dev/crypto-copilot-api/ai/AGENTS.md)
- Decision log: [`ai/DECISIONS.md`](/Users/Nico/dev/crypto-copilot-api/ai/DECISIONS.md)
