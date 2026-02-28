#!/usr/bin/env bash
set -euo pipefail

base_url="${BASE_URL:-http://localhost:8000}"

check() {
  local path="$1"
  local expected="$2"
  local body
  body="$(curl -sS "${base_url}${path}")"
  if ! echo "$body" | rg -q "$expected"; then
    echo "Smoke check failed for ${path}. Response: ${body}"
    exit 1
  fi
  echo "ok ${path}"
}

check "/" '"status"'
check "/api/v1/health" '"status"'
check "/api/v1/ready" '"status"'

echo "Smoke checks passed."
