# AGENTS — app/services/

Scope: domain services, external integrations, simulator logic, market-data logic, and LLM orchestration.

## Boot Sequence

1. Read [`ai/AGENTS.md`](/Users/Nico/dev/crypto-copilot-api/ai/AGENTS.md).
2. Read [`ai/ARCHITECTURE.md`](/Users/Nico/dev/crypto-copilot-api/ai/ARCHITECTURE.md), [`ai/DECISIONS.md`](/Users/Nico/dev/crypto-copilot-api/ai/DECISIONS.md), [`ai/context.md`](/Users/Nico/dev/crypto-copilot-api/ai/context.md), and the active task brief when one exists.
3. Apply this file for service-specific rules.

## Service Rules

- Keep services focused on one domain responsibility at a time.
- Prefer explicit constructor or method dependencies over hidden global lookups.
- Keep service entrypoints typed and easy to test in isolation.
- Put integration-specific logic in the appropriate service subtree instead of broad shared helpers.
- Preserve deterministic validation around model-generated outputs.

## Python Practices

- Prefer small classes or focused functions with explicit inputs and outputs.
- Avoid `Any` when a stable domain type can be defined.
- Keep async I/O async; do not block event-loop paths with sync network or DB behavior.
- Raise meaningful exceptions or translate them at boundaries instead of swallowing failures.

## Domain-Specific Rules

- Exchange, DEX, and market-data code should normalize external inputs before returning them to callers.
- Simulator logic must stay paper-only.
- LLM services must preserve schema validation and post-processing guardrails.
- Risk-sensitive logic should remain deterministic and inspectable.

## References

- Global rules: [`ai/AGENTS.md`](/Users/Nico/dev/crypto-copilot-api/ai/AGENTS.md)
- Architecture map: [`ai/ARCHITECTURE.md`](/Users/Nico/dev/crypto-copilot-api/ai/ARCHITECTURE.md)
