# RUNBOOK — crypto-copilot-api

## Objective

Bring up the showcase API, verify health/readiness, and validate the protected AI + simulation flow.

## Prerequisites

- Python 3.11+
- `uv` installed
- Docker Desktop if using the canonical Postgres path
- `OPENAI_API_KEY` if you want the real `/api/v1/llm/decide` path

## Local Path

1. Create env file.

```bash
cp .env.example .env
```

2. Install dependencies.

```bash
uv sync --all-extras
```

3. Run migrations.

```bash
make migrate
```

4. Start API.

```bash
make run
```

5. Smoke-check.

```bash
./scripts/smoke_local.sh
```

## Docker Path

1. Create env file.

```bash
cp .env.example .env
```

2. Build and start.

```bash
docker compose up -d --build
```

3. Run migrations.

```bash
docker compose exec api sh -lc "uv run alembic upgrade head"
```

4. Smoke-check.

```bash
./scripts/smoke_local.sh
```

## Protected Endpoint Check

The protected endpoints require `X-Demo-Api-Key` and a matching `DEMO_API_KEY` in `.env`.

Simulate a trade:

```bash
curl -s http://localhost:8000/api/v1/exec-sim/submit \
  -H 'Content-Type: application/json' \
  -H "X-Demo-Api-Key: ${DEMO_API_KEY}" \
  -d '{
    "trade": {
      "action": "ProposedTrade",
      "instrument_symbol": "BTC/USDT",
      "side": "buy",
      "order_type": "market",
      "qty": 0.25,
      "time_in_force": "GTC",
      "max_slippage_bps": 100
    }
  }'
```

Generate an AI plan:

```bash
curl -s http://localhost:8000/api/v1/llm/decide \
  -H 'Content-Type: application/json' \
  -H "X-Demo-Api-Key: ${DEMO_API_KEY}" \
  -d '{
    "symbol": "BTC/USDT",
    "max_notional_usd": 500
  }'
```

## Quality Gates

```bash
make lint
make test
```

## Troubleshooting

- `uv: command not found`: install uv from https://docs.astral.sh/uv/
- readiness fails: confirm `DATABASE_URL` and rerun migrations
- `401 Missing or invalid demo API key`: set `DEMO_API_KEY` in `.env` and send the matching `X-Demo-Api-Key` header
- `502 Model output failed validation`: inspect the LLM response and adjust prompt/model settings
- `OPENAI_API_KEY is required`: add a real provider key to `.env`

## Notes

- `/api/v1/health` is liveness
- `/api/v1/ready` checks DB connectivity
- DEX routes are auxiliary read-only endpoints, not the primary showcase flow
