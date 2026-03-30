# Crypto Copilot API

[![CI](https://github.com/wari1986/crypto-copilot-api/actions/workflows/ci.yml/badge.svg)](https://github.com/wari1986/crypto-copilot-api/actions/workflows/ci.yml)

Backend showcase project for a crypto trading copilot prototype. The repo is intentionally scoped to demonstrate strong backend/API engineering judgment, not to ship a production trading platform.

## What It Does Today

This repo now supports one clear end-to-end showcase flow:

1. fetch BYBIT spot market context
2. normalize candles, order book, and recent trades into structured models
3. generate a schema-constrained AI trade plan
4. validate that plan against guardrails
5. simulate execution only

Secondary read-only DEX pool snapshot endpoints are also available for Uniswap v3 and Meteora.

## What It Does Not Do

- no live trading
- no broker/exchange writes
- no user auth or account system
- no frontend/dashboard
- no claim of full production readiness

## Why This Repo Exists

The goal is to showcase:

- typed FastAPI service design
- async SQLAlchemy and migration-backed schema modeling
- market-data normalization and retrieval patterns
- schema-driven AI integration instead of vague text generation
- safe simulation-oriented execution behavior
- practical demo security
- lint/type/test discipline

## Supported API Surface

Public read endpoints:

- `GET /`
- `GET /api/v1/health`
- `GET /api/v1/ready`
- `GET /api/v1/candles?symbol=BTC/USDT&timeframe=1m`
- `GET /api/v1/marketdata/orderbook?symbol=BTC/USDT`
- `GET /api/v1/marketdata/trades?symbol=BTC/USDT`
- `GET /api/v1/dex/uniswapv3/pools/{chain}/{pool_address}`
- `GET /api/v1/dex/meteora/pools/{chain}/{pool_address}`

Protected showcase endpoints:

- `POST /api/v1/llm/decide`
- `POST /api/v1/exec-sim/submit`

Protected endpoints require the `X-Demo-Api-Key` header and a matching `DEMO_API_KEY` in the server environment.

## Quickstart

1. Create a local env file from [`.env.example`](/Users/Nico/dev/crypto-copilot-api/.env.example).

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

4. Start the API.

```bash
make run
```

5. Verify the basics.

```bash
./scripts/smoke_local.sh
```

Open:

- `http://localhost:8000/docs`
- `http://localhost:8000/api/v1/health`

## Canonical Demo Setup

The intended demo path is Postgres-backed.

```bash
cp .env.example .env
docker compose up -d --build
docker compose exec api sh -lc "uv run alembic upgrade head"
./scripts/smoke_local.sh
```

## Example Protected Calls

Generate a structured plan:

```bash
curl -s http://localhost:8000/api/v1/llm/decide \
  -H 'Content-Type: application/json' \
  -H "X-Demo-Api-Key: ${DEMO_API_KEY}" \
  -d '{
    "symbol": "BTC/USDT",
    "max_notional_usd": 500,
    "thesis": "Look for a tight-spread mean-reversion setup."
  }'
```

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

## Developer Workflow

```bash
make fmt
make lint
make test
```

## Security Notes

- keep real credentials out of git
- use `.env` locally and `.env.example` for placeholders only
- `OPENAI_API_KEY` is the provider secret for the AI demo
- `DEMO_API_KEY` protects sensitive API endpoints exposed by this app
- see [SECURITY.md](/Users/Nico/dev/crypto-copilot-api/SECURITY.md) for the disclosure policy

## Repository Notes

- `ai/tasks/task.md` contains the showcase-hardening brief used for this pass
- `ai/tasks/*.md` is the place for persistent task briefs across Codex sessions

## License

MIT
