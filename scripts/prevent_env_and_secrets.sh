#!/usr/bin/env bash
set -euo pipefail

staged_files="$(git diff --cached --name-only)"

if [ -n "$staged_files" ]; then
  if echo "$staged_files" | rg -n '(^|/)\.env($|[._].*)' >/dev/null; then
    allowed='(^|/)\.env\.example$'
    blocked="$(echo "$staged_files" | rg '(^|/)\.env($|[._].*)' | rg -v "$allowed" || true)"
    if [ -n "$blocked" ]; then
      echo "Blocked: committing env files is not allowed."
      echo "$blocked"
      echo "Keep secrets in local runtime env or secret manager."
      exit 1
    fi
  fi
fi

# Scan only newly added lines in staged diffs for obvious credential patterns.
added_lines="$(git diff --cached -U0 --no-color | rg '^\+' | rg -v '^\+\+\+' || true)"
if [ -n "$added_lines" ]; then
  if echo "$added_lines" | rg -n -i \
    '(api[_-]?key\s*[:=]\s*\S+|secret\s*[:=]\s*\S+|token\s*[:=]\s*\S+|password\s*[:=]\s*\S+|postgres(ql|\+asyncpg)?://[^:@\s]+:[^@\s]+@|mongodb(\+srv)?://[^:@\s]+:[^@\s]+@|redis://[^:@\s]+:[^@\s]+@|amqp://[^:@\s]+:[^@\s]+@|-----BEGIN (RSA|EC|OPENSSH) PRIVATE KEY-----|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{82,}|xox[baprs]-[A-Za-z0-9-]+|sk-[A-Za-z0-9]{20,})' \
    >/dev/null; then
    echo "Blocked: detected potential secrets in staged changes."
    echo "Please replace with placeholders and load real values from local env/secret manager."
    exit 1
  fi
fi

exit 0
