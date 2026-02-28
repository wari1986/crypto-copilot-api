# RUNBOOK — crypto-copilot-api

## Objective
Bring up the API reliably, verify health/readiness, and run quality checks.

## Prerequisites
- Python 3.11+
- `uv` installed
- Docker Desktop (for containerized path)

## Path A: Local (fast iteration)

1. Install dependencies
```bash
cat > .env << 'EOF'
DATABASE_URL=sqlite+aiosqlite:///:memory:
EOF
uv sync --all-extras
```

2. Run migrations
```bash
make migrate
```

3. Start API
```bash
make run
```

4. Smoke-check
```bash
./scripts/smoke_local.sh
```

## Path B: Docker (most reproducible)

1. Build and start
```bash
cat > .env << 'EOF'
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/crypto_copilot
EOF
docker compose up -d --build
```

2. Run migrations
```bash
docker compose exec api sh -lc "uv run alembic upgrade head"
```

3. Smoke-check
```bash
./scripts/smoke_local.sh
```

## Quality Gates
```bash
make fmt
make lint
make test
```

## Troubleshooting
- `Cannot connect to Docker daemon`: start Docker Desktop and retry.
- `uv: command not found`: install uv from https://docs.astral.sh/uv/.
- DB readiness fails: confirm `DATABASE_URL` in `.env` and rerun migrations.

## Notes
- `/api/v1/health` is liveness and does not require DB.
- `/api/v1/ready` checks DB connectivity.
