# AGENTS — CIT

## Operating mode
You are working in a production-adjacent local service repo.
Default approach: minimal diffs, reversible changes, stable endpoints.

## Before coding
- Identify the exact acceptance criteria from the issue.
- Locate the exact files to edit (usually `server/cit_server.py`, or scripts/docs).
- Avoid repo-wide sweeping changes.

## Implementation rules
- Prefer stdlib Python solutions.
- Add small helper functions rather than new modules unless necessary.
- Keep handlers deterministic and JSON outputs stable.

## Testing (manual)
Always include at least:
- `curl http://127.0.0.1:8790/health`
- `curl -s -X POST http://127.0.0.1:8790/chat -H 'Content-Type: application/json' -d '{"message":"ping"}'`

## Output policy
- Never print secrets.
- Log only operationally necessary info.
