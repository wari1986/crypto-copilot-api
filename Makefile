PY ?= uv run
UV ?= uv

.PHONY: dev test lint fmt migrate run smoke hooks

dev: run

test:
	$(PY) pytest -q

lint:
	$(PY) ruff check .
	$(PY) mypy .

fmt:
	$(PY) black .
	$(PY) ruff check . --fix

migrate:
	$(PY) alembic upgrade head

run:
	$(PY) uvicorn app.main:app --host 0.0.0.0 --port $${API_PORT:-8000} --reload

smoke:
	./scripts/smoke_local.sh

hooks:
	$(PY) pre-commit install
