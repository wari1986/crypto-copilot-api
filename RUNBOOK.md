# RUNBOOK — crypto-copilot-api

## Local (fastest)

Prereqs:
- Python 3.11+
- `uv` installed (https://docs.astral.sh/uv/)
- Postgres (recommended) or accept in-memory SQLite for quick tests

### 1) Install

```bash
uv sync --all-extras
```

### 2) Configure env

```bash
cp .env.example .env
# edit .env
```

Recommended local Postgres:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/crypto_copilot
```

### 3) Migrate + run

```bash
make migrate
make run
```

### 4) Verify

- `GET http://localhost:8000/` → `{ "status": "ok" }`
- `GET http://localhost:8000/api/v1/health` → status + version
- `GET http://localhost:8000/api/v1/ready` → checks DB connectivity

---

## Docker (recommended for consistency)

```bash
cp .env.example .env
# set OPENAI_API_KEY etc.

docker compose up -d --build
```

Run migrations inside the API container:

```bash
docker compose exec api sh -lc "uv run alembic upgrade head"
```

Then verify:

```bash
curl -s http://localhost:8000/api/v1/health
curl -s http://localhost:8000/api/v1/ready
```

---

## Notes

- Bybit/CCXT logic is kept in the repo, but the current roadmap is DEX LP + perps.
- Keep secrets in `.env` (never commit).
