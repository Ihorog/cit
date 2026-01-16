# GitHub Copilot Instructions — Ihorog/cit (CIT Family Assistant)

## Role of this repository

This repository is the canonical runtime for the CIT Family Assistant. It contains server/API, PWA/UI, storage, and orchestration scripts.

## Non-negotiable rules (hard constraints)

1. **Do NOT change overall architecture** unless explicitly requested in a Task Spec.

2. **Do NOT add dependencies** unless the Task Spec explicitly allows it.

3. **Do NOT commit or output secrets/tokens/keys.** Never hardcode secrets.

4. **Do NOT introduce a second runtime/server elsewhere** (e.g., in toolbox repos).

5. **Do NOT change API behavior without versioning.**

## Code boundaries

- **Server/API:** `server/`
- **UI/PWA:** `ui/`, `ui_dashboard/`, `web/`
- **Storage/logs/artifacts:** `storage/`
- **Orchestration:** `scripts/`, `bin/`
- **CI:** `.github/workflows/`

## API standards

- Use versioned endpoints under `/v1/...` for new functionality.
- Long-running operations MUST be implemented as Jobs (queue/store + status + logs).
- Every response must include `ok` and `request_id`.

## Preferred implementation style

- Minimal, readable changes; smallest viable diff.
- Prefer standard library over new dependencies.
- Keep backward compatibility; if legacy endpoints exist, preserve them.
- Ensure deterministic behavior; avoid hidden side effects.

## Testing & validation requirements

- Provide a short checklist to verify changes.
- If you add new code paths, add minimal smoke tests or validation steps.
- Do not propose "TODO" placeholders unless the Task Spec allows it.

## Output format for every task

- List of edited files
- Unified diff (or patch-like excerpt)
- Acceptance checklist
- Short changelog
