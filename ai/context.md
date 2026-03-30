# Repository Operational Context

## Current Focus

- Keep `ai/` as the session control plane for consistent AI-assisted development.
- Preserve app behavior by favoring minimal, scoped changes and stable contracts.
- Use existing FastAPI, service, schema, and DB patterns rather than creating parallel abstractions.

## Known Fragile Areas

- Contract drift between routes, schemas, services, and persisted models can break consumers silently.
- Market-data and DEX integrations can fail due to upstream API, RPC, or network assumptions.
- Startup/background tasks can create confusing behavior if feature flags are not understood.
- LLM flows are safety-sensitive because schema drift or weak validation can make advice unreliable.
- Persistence behavior can diverge between in-memory SQLite and Postgres-specific production assumptions.

## Architectural Constraints

- Data flow should remain: route -> dependency -> service -> repository or DB helper -> typed response.
- Config comes from `app/core/config.py`, not scattered environment reads.
- Business logic belongs in `app/services/**`, not in routes.
- LLM outputs must be validated before being treated as advice or execution input.
- Execution remains simulated and guarded.

## Common Mistakes

- Adding business logic directly inside route handlers.
- Returning or accepting loose dictionaries where a typed schema should exist.
- Reading env vars directly in arbitrary modules instead of extending settings.
- Mixing database access, transport logic, and domain logic in the same function.
- Treating model output as trustworthy before schema and risk validation.

## Active Documentation Pattern

- `ai/AGENTS.md` is the boot file.
- `ai/ARCHITECTURE.md` is the canonical structure map.
- `ai/DECISIONS.md` records durable decisions.
- `ai/context.md` holds operational constraints and fragile areas.
- `ai/agents/*.md` contains folder-scoped overlays.
- `ai/runbooks/` contains operational runbooks.
- `ai/tasks/` contains task briefs for multi-session work.

## Notes For Future Sessions

- Read the boot files in order before editing.
- Load the folder overlay matching the scope you touch.
- If a change affects architecture, workflow, or long-lived conventions, update the relevant `ai/` docs in the same patch.
- If a change alters contracts or settings, validate both code behavior and documentation alignment.
