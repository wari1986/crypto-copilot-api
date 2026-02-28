# Security Policy

## Reporting a Vulnerability
Please report vulnerabilities privately via GitHub Security Advisories or direct contact before opening a public issue.

Include:
- impact summary
- reproduction steps
- affected endpoints/files
- proposed remediation (if available)

## Secret Handling Rules
- Never commit secrets, tokens, private keys, or credentialed connection strings.
- Use `.env` locally and a secret manager in deployed environments.
- Do not track `.env*` files in git.

## Leak Response Playbook
1. Revoke/rotate exposed credentials immediately.
2. Remove leaked files/content from the current branch.
3. Rewrite git history to purge leaked material if it was committed.
4. Force-push rewritten history and notify collaborators to resync.
5. Review logs and access patterns for misuse.

## Preventive Controls in This Repo
- Pre-commit hook blocks `.env*` files.
- Pre-commit hook scans staged additions for high-signal secret patterns.
- CI runs automated secret scanning on pushes and pull requests.
