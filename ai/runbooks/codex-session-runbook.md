# Codex Session Runbook

Operational guidance lives here so `ai/AGENTS.md` can stay focused on behavior and design rules.

## Pre-Flight Checklist

- Read the boot files in order before making changes.
- Confirm the task scope and the modules being touched.
- Start with the smallest coherent fix before considering a refactor.
- Check whether config, migrations, or external provider assumptions are part of the change.

## Local Commands

- Install deps: `uv sync --all-extras`
- Run app: `make run`
- Run migrations: `make migrate`
- Run tests: `make test`
- Run lint and type checks: `make lint`
- Apply formatting: `make fmt`

## Troubleshooting Workflow

1. Reproduce the issue with minimal scope.
2. Verify local env assumptions, settings, and feature flags.
3. Inspect the relevant route, service, schema, and DB boundaries before editing.
4. Prefer root-cause fixes over symptom patches.
5. If background tasks or provider integrations are involved, verify startup and config assumptions explicitly.

## Validation And Readiness

- Run the narrowest meaningful validation first, then widen if the change touches multiple layers.
- For behavior changes, prefer targeted tests plus lint/type checks.
- If contracts or settings change, update docs and examples in the same patch.
- If you cannot run validation, state that explicitly.

## Safety Notes

- Do not introduce real-trading behavior.
- Do not weaken schema or risk validation around LLM-driven flows.
- Never commit secrets or operator-specific credentials.
