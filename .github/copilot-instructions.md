# CIT — GitHub Copilot Instructions

## PURPOSE
These instructions define mandatory rules for GitHub Copilot working on the CIT (Ci Interface Terminal) repository, part of the Cimeika ecosystem.

**CIT Overview**: Lightweight API gateway bridging Cimeika devices to OpenAI API, designed for Android/Termux with **zero external dependencies in core**. Version 2.1 implements unified modular architecture consolidating 5 repositories following the **111 density principle**: 1 Core, 1 Registry, 1 Entry Point.

Goal:
- eliminate repeated actions,
- enforce a single execution path,
- ensure all changes flow through PR → verification → human approval.

Copilot acts as a controlled execution agent, not an autonomous decision-maker.

**Core Philosophy**: Minimal diffs, reversible changes, stable endpoints. This is production-adjacent.

---

## CIT-SPECIFIC RULES (READ FIRST)
**Before any code changes**, read [AGENTS.md](../AGENTS.md):
- Operating mode: production-adjacent local service
- Default approach: minimal diffs, reversible changes, stable endpoints
- Implementation: stdlib Python, small helper functions, deterministic handlers
- Testing: Always include manual curl tests for `/health` and `/chat`
- Output: Never print secrets, log only operational info

---

## CIT ARCHITECTURE ESSENTIALS

### Entry Points
- **Flask server**: [server/cit_server.py](../server/cit_server.py) — Production API (port 8790/5000)
- **Standalone server**: [ci.py](../ci.py) — Single-file HTTP server with embedded UI (port 8790)
- **Modular engine**: [core/engine.py](../core/engine.py) — Module runtime with CLI (`build`, `run`, `module`)

### Key Components
- **OpenAI Client**: [server/openai_client.py](../server/openai_client.py) — Autonomous client with intelligent routing (Responses API → Chat Completions fallback)
- **Plugin System** (optional): [core/plugin_loader.py](../core/plugin_loader.py) — Dynamic module registration

### Critical Files
- [AGENTS.md](../AGENTS.md) — Operating rules for AI agents (READ FIRST)
- [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) — Technical architecture and data flows
- [docs/UNIFICATION.md](../docs/UNIFICATION.md) — Modular architecture and 111 principle
- [README.md](../README.md) — Feature overview and quick start

---

## DEVELOPER WORKFLOWS

### Testing API Endpoints (MANDATORY)
Always test with these commands after changes:
```bash
# Health check
curl http://127.0.0.1:8790/health

# Chat endpoint
curl -X POST http://127.0.0.1:8790/chat \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"ping"}]}'
```

### Running Tests
```bash
python tests/test_v21_components.py      # OpenAI client, job manager
python tests/test_modular_engine.py      # Plugin system, manifests
python tests/test_api_endpoints.py       # API endpoints
```

### Starting the Server
```bash
# Required: Set API key
export OPENAI_API_KEY="sk-..."

# Option 1: Flask server (preferred for production)
python server/cit_server.py

# Option 2: Standalone server with UI
python ci.py

# Option 3: Modular engine
python core/engine.py run
```

### Building and Validating Modules (Optional)
```bash
python core/engine.py module <id>      # Run specific module
```

---

## PROJECT-SPECIFIC CONVENTIONS

### Code Style
- **Python stdlib first**: Prefer standard library over external dependencies
- **No secrets in code**: Read from environment (`OPENAI_API_KEY`, `CIT_MODEL`)
- **Ukrainian comments**: Core comments in Ukrainian, docs/public-facing in English
- **Small helpers**: Add helper functions rather than new modules unless necessary

### Environment Variables
```bash
OPENAI_API_KEY          # Required: OpenAI API key
CIT_MODEL / OPENAI_MODEL # Optional: Model name (default: gpt-4o-mini)
CIT_PORT / PORT         # Optional: Server port (default: 8790 or 5000)
HOST                    # Optional: Bind address (default: 0.0.0.0)
```

### API Response Patterns
Endpoints return consistent JSON: status field + data/error. See [server/cit_server.py](../server/cit_server.py) for exact schemas.

---

## COMMON PITFALLS
1. **Don't add external deps to core**: Flask server can have deps, but `ci.py` and core modules must use stdlib only
2. **Port conflicts**: Default is 8790 for `ci.py`, 5000 for Flask. Check running processes
3. **Environment setup**: Always export `OPENAI_API_KEY` before starting servers
4. **Deployment**: Example deployment is Android/Termux (Samsung device)

---

## BEFORE IMPLEMENTING CHANGES
Before any changes, read [AGENTS.md](../AGENTS.md) — contains critical operating rules.

---

- **Ecosystem**: Repository `ciwiki` (canonical reference for ecosystem)
- **This Repo**: `cit` (technical implementation)
- **Integration**: Changes must align with `ciwiki` documentation

If something is not defined here:
- do NOT guess,
- create a documentation PR in `ciwiki`,
- wait for approval.

---

## SCOPE (REPOSITORIES)
Copilot instructions apply to:
- `ciwiki` — Canonical documentation and conceptual framework
- `cit` — This repository: API gateway and modular engine
- `cimeika-unified` — Unified system integration
- `citt` — Telegram bot integration
- `media` (restricted: docs only)

Repository `cit_versel`:
- strictly frozen,
- no changes,
- no deployment,
- no workflows.

---

## HARD CONSTRAINTS
- No direct commits to `main`.
- All changes go through branches and Pull Requests.
- No deployment, no production actions.
- No secrets committed to repository.
- No architectural rewrites unless explicitly authorized.

---

## ANTI-REPEAT PRINCIPLE (CORE RULE)
Any repeated action is a system failure.

A repeat includes:
- the same manual command executed more than once,
- the same error occurring more than once,
- the same sequence of steps repeated to achieve a standard outcome.

When a repeat is detected, Copilot MUST:
1. identify the root cause,
2. introduce a mechanism that prevents repetition,
3. document the resolution,
4. ensure the issue cannot reoccur under the same conditions.

Repeats must be eliminated permanently unless system conditions change.

---

## STANDARD INTENT CLASSES
Copilot MUST use only standard intent categories.
No custom magic words or invented markers.

Allowed intents:
- status
- health
- analyze
- fix
- refactor
- document
- sync
- run_tests
- make_pr

Each intent must have:
- clear trigger condition,
- deterministic outcome,
- explicit approval boundary.

---

## EXECUTION FLOW (SINGLE PATH)
All work must follow this sequence:

1. Plan (what and why).
2. Implement in a branch.
3. Verify (tests / checks / validation).
4. Create Pull Request.
5. Await human approval.
6. Merge.

There are no alternative paths.

---

## PULL REQUEST REQUIREMENTS
Each PR must include:
- What changed
- Why it changed (root cause)
- How it was verified
- Risk assessment
- Rollback plan

PRs without verification or explanation are invalid.

---

## DOCUMENTATION FIRST
If behavior, process, or contract is unclear:
- update documentation in `ciwiki` first,
- only then proceed to implementation.

---

## SECURITY & SAFETY
- Principle of least privilege.
- Secrets only via GitHub Secrets or environment configuration.
- No credentials in code or markdown.

---

## MINIMALISM RULE
Change only what is necessary.
Do not refactor broadly.
Do not rewrite systems without explicit authorization.

But: always eliminate repetition when found.

---

## FINAL AUTHORITY
Human approval is mandatory before any merge.

Copilot prepares.
Human decides.

END OF INSTRUCTIONS
