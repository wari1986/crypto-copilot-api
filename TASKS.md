# Crypto Copilot API — Concrete Plan (get it running ASAP)

Goal: ship an end-to-end **working** system quickly:

- ingest news (Yahoo Finance first)
- ingest market data + compute TradingView-like indicators (start with CCXT candles)
- ingest at least **one** DEX source (start with Uniswap v3 pools via a single adapter)
- generate **LP + perps advice** with hard guardrails
- expose everything through a single API that Moltbot (Telegram) can call

## Principle

**Back-end first, paper-only.** LLM proposes, deterministic services compute, risk layer blocks. Execution stays in simulator until everything is stable.

---

## Phase 0 — Boot & sanity (30–60 min)

**Outcome:** API boots locally, DB works, you can hit `/health`.

- [ ] Create `.env` from `.env.example`
- [ ] Ensure `DATABASE_URL` points to a local Postgres (docker) for consistent JSONB behavior
- [ ] `uv sync --all-extras` (or your preferred install path)
- [ ] `make migrate`
- [ ] `make run`
- [ ] Confirm:
  - GET `/api/v1/health`
  - OpenAPI docs load

Deliverable:
- a short `RUNBOOK.md` (how to run dev + docker) (add if missing)

---

## Phase 1 — Minimal “market context” endpoint (same day)

**Outcome:** one endpoint returns a usable snapshot for an LLM prompt.

Add a single endpoint:

- `GET /api/v1/context?symbol=BTC/USDT&exchange=bybit&tf=1h`

Returns:
- latest candles (N=200)
- computed indicators (RSI, EMA20/50/200, MACD, ATR, BBands)
- simple regime flags (trend up/down, volatility high/low)

Tasks:
- [ ] Ensure candles backfill actually fetches via CCXT (not stub)
- [ ] Store candles in DB + cache
- [ ] Implement indicator computation in `app/services/market_data/indicators.py` (or existing file)
- [ ] Add schema: `MarketContext`
- [ ] Add tests for indicator determinism

---

## Phase 2 — Yahoo Finance news polling + summarization (same day → next day)

**Outcome:** API can list headlines and return a short structured summary.

Endpoints:
- `GET /api/v1/news?query=BTC&limit=50`
- `POST /api/v1/news/summarize` (input: `url` or `article_id`)

Implementation:
- Start with RSS-like feeds / known public endpoints (avoid fragile scraping if possible).
- Store:
  - `articles(id, source, title, url, published_at, raw_content?, extracted_text?, hash)`
  - optional: `summary`, `summary_model`, `summary_at`

Tasks:
- [ ] Implement news fetcher worker in `app/workers/`
- [ ] Implement article extraction (fallback: title + snippet if extraction fails)
- [ ] Add summarizer (can reuse the existing LLM client pattern)
- [ ] Add a `NewsDigest` prompt template (system prompt + strict output schema)

---

## Phase 3 — DEX market data (start with one adapter) (1–2 days)

**Outcome:** you can pull pool state + compute LP range advice.

Pick **one** first:
- Uniswap v3 (best documented + mature tooling)

Minimal data you need for LP advice:
- pool price (sqrtPriceX96)
- current tick
- tick spacing
- liquidity
- fee tier
- recent volume/fees (if available)

Endpoints:
- `GET /api/v1/dex/univ3/pools/{chain}/{poolAddress}`
- `POST /api/v1/lp/advice` (inputs: pool + deposit amounts + horizon)

Tasks:
- [ ] Build adapter interface: `DexAdapter` (univ3 first)
- [ ] Implement on-chain reads via a provider (Alchemy/Infura/etc)
- [ ] Normalize output into `PoolSnapshot`
- [ ] Implement LP math helpers:
  - price↔tick conversion
  - position value within range
  - fee APR estimate (start simple)
  - IL scenario table (coarse but useful)
- [ ] Implement recommendation:
  - range suggestion (wide/medium/tight presets based on vol)
  - rebalance trigger rules

---

## Phase 4 — Strategy + risk engine (paper-only) (1–2 days)

**Outcome:** advice is constrained; execution stays simulated.

- [ ] Add `RiskConfig` (max leverage, max position size, allowlists for venues)
- [ ] Validate every proposed action:
  - schema validation (already exists)
  - risk checks (new)
  - “paper-only” flag must be true

---

## Phase 5 — Moltbot integration (Telegram) (same day)

**Outcome:** chat becomes a real operator console.

### Integration pattern (recommended)

Moltbot should be **UI + orchestration**.

- Moltbot receives Telegram message
- Moltbot calls `crypto-copilot-api` endpoints to fetch context + compute advice
- Moltbot replies with:
  - short recommendation
  - key numbers + assumptions
  - “Approve?” flow for simulated execution

API additions:
- [ ] `POST /api/v1/chat/answer` (optional) to centralize prompt-building
- [ ] `POST /api/v1/actions/preview` (dry-run)
- [ ] `POST /api/v1/actions/execute` (paper, requires explicit confirmation token)

### Notifications

Add a scheduler job that emits events Moltbot can push:
- range out of band
- funding spike
- volatility regime change
- news headline matching watchlist

---

## What to do next (my recommendation)

1) Phase 0 today.
2) Phase 1 + Phase 2 tomorrow.
3) Uniswap v3 adapter as the first DEX integration.
4) Use Moltbot as the first UI (skip web UI until the backend is solid).
