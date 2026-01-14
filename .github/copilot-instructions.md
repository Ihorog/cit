# Copilot Instructions — CIT (Ci Interface Terminal)

## 0) What this repo is
CIT is a lightweight local/LAN HTTP service running on Android (Samsung Tab) via Termux.
It exposes minimal endpoints for health and chat; it must remain stable, predictable, and safe.

Primary runtime is Termux on Android.
Keep everything minimal, stdlib-first, and reproducible.

## 1) Hard constraints (non-negotiable)
- **Python stdlib-only** for the server. Do not introduce pip dependencies unless explicitly requested.
- Must run in Termux without compiling native deps (no Rust/Cargo build steps).
- Default service port: `8790`.
- Keep logs and secrets out of git.
- Do not change product intent: CIT = single entry point / gateway for Ci chat & later integrations.

## 2) Known environment (facts)
- Device: Samsung Galaxy Tab (Android) + Termux
- Base dir: `$HOME/cimeika/cit` (typical Termux path: `/data/data/com.termux/files/home/cimeika/cit`)
- Server: `server/cit_server.py`
- Logs: `logs/`
- Local health check: `http://127.0.0.1:8790/health`
- LAN usage exists (service may bind `0.0.0.0`)

## 3) API contract (keep stable)
- `GET /health` -> JSON with `{ ok, service, time, port, model, openai }`
- `POST /chat` -> request JSON `{ message, system? }`, response JSON `{ ok, cit, time, model, reply }`

Notes:
- If `message` empty -> return a short "CIT online …" hint response.
- On upstream error -> return `502` with structured error payload.

## 4) Source-of-truth files & structure
Repository layout should remain:
- `server/` — HTTP server and handler logic
- `scripts/` — Termux bootstrap, boot scripts, operational helpers
- `docs/` — architecture, ops, security notes
- `data/` — runtime data (ignored by git)
- `logs/` — runtime logs (ignored by git)

If you add files, keep them in the correct area above.

## 5) Security & secrets
- Never commit `.env` or any key material.
- Ensure `.gitignore` includes `.env`, `logs/`, `data/`, `__pycache__/`.
- Avoid writing sensitive data into logs (no API keys, tokens, headers).

## 6) How to run locally (Termux)
Preferred:
- `cd $HOME/cimeika/cit`
- `export $(grep -v '^#' .env | xargs) || true`
- `python server/cit_server.py`

Or background:
- `nohup python server/cit_server.py > logs/cit_8790.log 2>&1 &`

## 7) Change policy (how to work on tasks)
When implementing an issue:
- Make the smallest change that satisfies acceptance criteria.
- Update docs when behavior changes.
- Add a quick manual test command snippet to the PR description.

Do not do broad refactors unless the issue explicitly requests it.

## 8) PR rules & iteration
- Expect iteration via PR review comments. If you are asked to change something, implement exactly that and push again.
- Batch review comments where possible (avoid many tiny cycles).

Important:
- Copilot coding agent pushes only to `copilot/*` branches. Do not assume direct pushes to main. (GitHub policy)

## 9) Quality gates (must pass)
- Server still starts with Python stdlib only.
- `/health` returns expected JSON.
- `/chat` returns `{ reply }` for a normal prompt.
- Error paths return structured JSON and non-200 status.

## 10) What NOT to do
- Do not add frameworks (FastAPI/Flask) unless explicitly requested.
- Do not add heavy frontends or UI scaffolding unless the issue is specifically "/ui".
- Do not change API shapes without a versioning decision documented in `docs/`.
