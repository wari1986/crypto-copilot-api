# syntax=docker/dockerfile:1.7
FROM ghcr.io/astral-sh/uv:python3.11-bookworm AS base
WORKDIR /app
COPY pyproject.toml README.md ./
RUN uv sync --frozen --no-install-project --all-extras

FROM base AS dev
COPY . .
RUN uv sync --all-extras
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM base AS prod
COPY . .
RUN uv sync --no-dev --all-extras
ENV ENV=prod
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
