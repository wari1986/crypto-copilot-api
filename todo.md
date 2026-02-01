# TODO (local notes)

## Security / Hygiene

- [ ] **Do not commit secrets.** Keep real credentials out of `todo.md` and the repo.
- [ ] Use `.env` / `.env.local` and make sure `.env` is gitignored.
- [ ] Rotate any leaked tokens/DB URLs.

## Environment

- `DATABASE_URL=` (set this locally; example below)

Example local Postgres:

```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/crypto_copilot
```
