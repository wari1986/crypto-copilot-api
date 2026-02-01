# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

# System deps for postgres + builds
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Install uv (fast python package manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Copy project metadata first (better layer caching)
COPY pyproject.toml ./
COPY README.md ./

# Install deps (including extras if declared)
RUN uv sync --all-extras

# Copy the rest
COPY . .

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
