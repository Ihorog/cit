# CLAUDE.md - AI Assistant Guide for CIT

This document provides comprehensive guidance for AI assistants working with the CIT (Ci Interface Terminal) codebase.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Codebase Structure](#codebase-structure)
3. [Core Architecture](#core-architecture)
4. [Development Conventions](#development-conventions)
5. [File-by-File Guide](#file-by-file-guide)
6. [Common Development Tasks](#common-development-tasks)
7. [Testing and Deployment](#testing-and-deployment)
8. [Important Constraints](#important-constraints)
9. [AI Assistant Guidelines](#ai-assistant-guidelines)

---

## Project Overview

**CIT (Ci Interface Terminal)** is a lightweight HTTP API gateway designed to run on Android devices via Termux. It provides a minimal HTTP interface that proxies chat requests to OpenAI's API.

### Key Characteristics

- **Zero external dependencies** - Uses only Python 3 standard library
- **Termux-optimized** - Designed for Android deployment
- **Minimalist design** - 328 lines of production Python code
- **Embedded web UI** - Full-featured chat interface with STT/TTS
- **Ukrainian language support** - UI and voice features in Ukrainian

### Primary Use Case

Enables an Android phone to act as a personal AI gateway server, accessible via:
- Local network (LAN)
- Tailscale VPN for secure remote access

---

## Codebase Structure

```
cit/
├── README.md                    # User-facing documentation
├── CLAUDE.md                    # This file - AI assistant guide
├── .gitignore                   # Git ignore patterns
├── docs/
│   ├── ARCHITECTURE.md          # System architecture details
│   └── SECURE_ACCESS.md         # Tailscale VPN setup guide
├── server/
│   └── cit_server.py            # Main HTTP server (328 lines)
├── ui/
│   └── index.html               # Legacy standalone UI (deprecated)
└── scripts/
    ├── termux_bootstrap.sh      # Initial Termux setup (23 lines)
    └── termux_boot/
        └── cit_start.sh         # Auto-start script (25 lines)
```

### File Statistics

- **Total lines of code**: ~440 lines
- **Main server**: 328 lines (including embedded UI)
- **Scripts**: 48 lines combined
- **Documentation**: 3 markdown files

---

## Core Architecture

### HTTP Endpoints

The server (`cit_server.py`) exposes four endpoints:

1. **`GET /` or `GET /ui`** → Embedded web chat interface (HTML)
2. **`GET /health`** → Health check: `{"ok": true, "model": "...", "ts": "..."}`
3. **`POST /chat`** → Chat proxy to OpenAI
4. **`OPTIONS /*`** → CORS preflight handling

### Request Flow

```
Client → CIT Server → OpenAI API → CIT Server → Client
         (port 8790)   (Responses API or Chat Completions)
```

### Dual API Strategy

The server uses a **two-tier fallback approach**:

1. **Primary**: OpenAI Responses API (`/v1/responses`)
   - Payload: `{"model": "...", "input": "user message"}`
   - Extracts: `response.output_text`

2. **Fallback**: OpenAI Chat Completions API (`/v1/chat/completions`)
   - Payload: `{"model": "...", "messages": [{"role": "user", "content": "..."}]}`
   - Extracts: `response.choices[0].message.content`

See `call_openai()` function in `server/cit_server.py:247-277`.

### Configuration

All configuration via **environment variables**:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | ✓ Yes | _(none)_ | OpenAI API authentication |
| `CIT_MODEL` | No | `gpt-4o-mini` | OpenAI model to use |
| `CIT_PORT` | No | `8790` | HTTP server port |

**No config files** - Environment-only configuration simplifies deployment.

### Web UI Features

The embedded UI (lines 25-195 in `cit_server.py`) includes:

- **Dark theme** optimized for mobile
- **STT (Speech-to-Text)** via Web Speech API (`uk-UA` locale)
- **TTS (Text-to-Speech)** via Web Speech Synthesis API
- **Health monitoring** (polls `/health` every 4 seconds)
- **Ukrainian language** interface

---

## Development Conventions

### Code Style

1. **Minimalism First**
   - No dependencies outside Python stdlib
   - No frameworks or libraries
   - Flat, simple structure

2. **Python Patterns**
   - Module-level constants: `MODEL`, `PORT`, `OPENAI_API_KEY`
   - Private helper functions: `_json_bytes()`, `_read_json()`, `_send_json()`, `_openai_request()`
   - Public API: `call_openai()`, `Handler` class, `main()`

3. **Error Handling**
   - Return error dicts rather than raising exceptions
   - Format: `{"error": "description", "body": "..."}`
   - No logging of sensitive data (API keys, full request bodies)

4. **CORS**
   - Always include CORS headers on all responses
   - Wildcard origin: `Access-Control-Allow-Origin: *`
   - Supports `OPTIONS` preflight requests

### Git Workflow

- **Branch naming**: Feature branches start with `claude/` (e.g., `claude/claude-md-mjrsxje6fz1p871t-dE7uo`)
- **Commit messages**: Concise, imperative mood (e.g., "Add feature X", "Fix bug in Y")
- **No .env files in repo**: API keys stay out of version control
- **Keep commits atomic**: One logical change per commit

### File Organization

- **Documentation**: `/docs/` for architecture and guides
- **Source code**: `/server/` for Python code
- **Scripts**: `/scripts/` for setup and automation
- **UI**: Currently embedded in Python; legacy `/ui/index.html` exists but is deprecated

---

## File-by-File Guide

### `server/cit_server.py` (328 lines)

**The core of the project.** Single-file HTTP server with embedded UI.

#### Key Sections

| Lines | Section | Description |
|-------|---------|-------------|
| 1-23 | Module docstring & imports | Documentation and stdlib imports |
| 21-23 | Configuration | Environment variable loading |
| 25-195 | `UI_HTML` constant | Embedded web interface (HTML/CSS/JS) |
| 197-245 | Helper functions | JSON handling, CORS, OpenAI requests |
| 247-277 | `call_openai()` | Dual API strategy (Responses → Chat Completions) |
| 279-318 | `Handler` class | HTTP request routing |
| 320-328 | `main()` | Server startup |

#### Important Functions

**`_openai_request(url, payload) -> dict`** (lines 222-245)
- Makes HTTP POST to OpenAI
- Handles HTTPError and generic exceptions
- Returns error dicts on failure

**`call_openai(message) -> dict`** (lines 247-277)
- Primary: Tries Responses API
- Fallback: Tries Chat Completions API
- Returns: `{"reply": "...", "raw": {...}, "api": "responses"|"chat.completions"}`

**`Handler.do_POST()`** (lines 304-318)
- Parses JSON body: `{"message": "user text"}`
- Calls `call_openai()`
- Returns: `{"reply": "...", "api": "...", "raw": {...}}`

#### UI Embedded in Python

The `UI_HTML` constant (lines 25-195) is served on `GET /` and `GET /ui`. This is **intentional** - keeps deployment simple by avoiding separate static file serving.

**When modifying the UI:**
1. Edit the string constant in Python
2. Preserve Ukrainian language strings
3. Maintain dark theme styling
4. Test STT/TTS functionality in a real browser

### `scripts/termux_bootstrap.sh` (23 lines)

**One-time setup script** for fresh Termux installation.

- Updates packages: `pkg update && pkg upgrade`
- Installs: `git python termux-services`
- Clones repo if not present
- Reminds user to set `OPENAI_API_KEY`

**Usage**: Run once after installing Termux.

### `scripts/termux_boot/cit_start.sh` (25 lines)

**Auto-start script** for Termux Boot app.

- Sources `.env` if present
- Starts server with `nohup python server/cit_server.py &`
- Logs PID to stdout

**Deployment**:
1. Install Termux Boot app
2. Copy script to `~/.termux/boot/`
3. Create `.env` file with `OPENAI_API_KEY`

### `ui/index.html` (64 lines)

**Legacy standalone UI** - no longer actively maintained.

- Uses old API contract: `POST /chat` with `messages` array
- Does not match current server implementation
- Keep for reference but prefer embedded UI

**Important**: The embedded UI in `cit_server.py` is the **canonical** version.

### Documentation Files

#### `README.md`

- User-facing quick start guide
- Installation instructions
- API examples with curl
- Repository layout

#### `docs/ARCHITECTURE.md`

- High-level system design
- Component descriptions
- Data flow diagrams
- Security considerations
- Versioning (currently v0)

#### `docs/SECURE_ACCESS.md`

- Tailscale VPN setup instructions
- Android installation steps
- Security best practices

---

## Common Development Tasks

### Adding a New Endpoint

1. **Add handler in `Handler.do_GET()` or `Handler.do_POST()`**
   ```python
   if self.path.startswith("/new-endpoint"):
       data = _read_json(self)
       result = process_data(data)
       _send_json(self, 200, result)
       return
   ```

2. **Always include CORS headers** (use `_send_json()` helper)

3. **Update module docstring** (lines 1-12) with new endpoint

### Modifying the UI

1. **Edit the `UI_HTML` constant** in `server/cit_server.py` (lines 25-195)

2. **Preserve language**: Keep Ukrainian strings (e.g., `"Напиши або натисни..."`)

3. **Test in browser**:
   ```bash
   export OPENAI_API_KEY=sk-...
   python server/cit_server.py
   # Open http://127.0.0.1:8790/ui
   ```

4. **Test STT/TTS**: Use Chrome/Edge (best Web Speech API support)

### Adding Environment Variables

1. **Read in module-level code** (lines 21-23):
   ```python
   NEW_VAR = os.getenv("CIT_NEW_VAR", "default_value")
   ```

2. **Update docstring** (lines 8-11)

3. **Document in `docs/ARCHITECTURE.md`**

4. **Update `scripts/termux_boot/cit_start.sh`** if needed for defaults

### Changing the OpenAI API Call

The `call_openai()` function (lines 247-277) implements the dual API strategy.

**To modify**:
1. Locate the function
2. Adjust payload structure for primary API
3. Adjust fallback API if needed
4. Update response parsing
5. Test with both success and error cases

---

## Testing and Deployment

### Local Testing

```bash
# Set environment
export OPENAI_API_KEY=sk-proj-...
export CIT_MODEL=gpt-4o-mini  # optional
export CIT_PORT=8790          # optional

# Run server
python server/cit_server.py

# Test health endpoint
curl http://127.0.0.1:8790/health

# Test chat endpoint
curl -X POST http://127.0.0.1:8790/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'

# Test UI in browser
open http://127.0.0.1:8790/ui
```

### Termux Deployment

**Fresh installation**:
```bash
# Run bootstrap script
bash scripts/termux_bootstrap.sh

# Create .env file
echo "OPENAI_API_KEY=sk-..." > ~/cit/.env

# Test manually
cd ~/cit
python server/cit_server.py
```

**Auto-start setup**:
```bash
# Install Termux Boot from Play Store
# Copy boot script
mkdir -p ~/.termux/boot
cp scripts/termux_boot/cit_start.sh ~/.termux/boot/

# Reboot device and verify
curl http://127.0.0.1:8790/health
```

### Secure Remote Access

**Tailscale VPN** (recommended):
1. Install Tailscale app on Android
2. Sign in and note Tailscale IP (e.g., `100.x.x.x`)
3. Install Tailscale on other devices
4. Access CIT via `http://100.x.x.x:8790/ui`

See `docs/SECURE_ACCESS.md` for detailed setup.

---

## Important Constraints

### Design Constraints

1. **No external dependencies**
   - Must work with Python stdlib only
   - No `pip install` required
   - Ensures Termux compatibility

2. **Single-file server**
   - Keep `cit_server.py` self-contained
   - Embed UI as string constant
   - Simplifies deployment

3. **Zero configuration files**
   - All config via environment variables
   - Optional `.env` file for convenience
   - No JSON/YAML config

4. **Minimal resource usage**
   - Must run efficiently on Android
   - No background threads or processes
   - Simple request/response model

### Security Constraints

1. **Never commit secrets**
   - API keys stay in environment
   - `.env` files excluded via `.gitignore`
   - No hardcoded credentials

2. **No authentication built-in**
   - Relies on network-level security (LAN or VPN)
   - Not designed for public internet exposure
   - Use Tailscale for remote access

3. **No request logging**
   - Don't log API keys or user messages
   - Minimal stdout logging (startup messages only)
   - Errors returned as JSON, not logged

### Compatibility Constraints

1. **Termux-first**
   - Primary target: Android via Termux
   - Secondary: Any Python 3 environment
   - Avoid Termux-specific paths in core code

2. **Python 3 only**
   - No Python 2 compatibility needed
   - Use modern stdlib features
   - Assume Python 3.7+ (Termux default)

3. **Cross-platform**
   - Server should work on Linux/macOS/Windows
   - Scripts are Bash (Termux/Linux only)
   - UI works in any modern browser

---

## AI Assistant Guidelines

### When Working on This Project

1. **Preserve minimalism**
   - Don't add dependencies unless absolutely critical
   - Don't suggest frameworks or libraries
   - Keep solutions simple and stdlib-only

2. **Respect the design philosophy**
   - Single-file server is intentional
   - Embedded UI is intentional
   - Environment-only config is intentional

3. **Maintain Ukrainian language support**
   - Don't change UI text to English
   - Preserve `uk-UA` locale in STT/TTS
   - Comments and docs can be English

4. **Test on constraints**
   - Always consider Termux environment
   - Assume limited resources (mobile device)
   - Prefer stdlib over external packages

5. **Document changes**
   - Update docstrings if changing endpoints
   - Update `docs/ARCHITECTURE.md` for architectural changes
   - Keep `README.md` user-friendly

### Code Modification Guidelines

**DO:**
- Use stdlib modules only
- Return error dicts instead of raising exceptions
- Include CORS headers on all responses
- Test with both OpenAI APIs (Responses and Chat Completions)
- Preserve existing code style and formatting

**DON'T:**
- Add pip dependencies
- Split the server into multiple files
- Remove the embedded UI
- Change the dual API strategy without good reason
- Add complex logging or monitoring
- Introduce authentication (network-level security preferred)

### Common Pitfalls to Avoid

1. **Dependency creep**
   - Resist suggesting Flask/FastAPI/aiohttp
   - `http.server` is sufficient for this use case

2. **Over-engineering**
   - Don't add database support
   - Don't add user management
   - Don't add complex state management

3. **Breaking Termux compatibility**
   - Avoid packages that require compilation
   - Test environment variable handling
   - Don't assume root access

4. **UI separation**
   - Don't suggest extracting UI to separate files
   - Embedded UI simplifies deployment in Termux

5. **Configuration files**
   - Don't create `config.json` or `settings.yaml`
   - Environment variables are the only config method

### Understanding the Codebase

**Entry points**:
- Server: `python server/cit_server.py`
- Bootstrap: `bash scripts/termux_bootstrap.sh`
- Auto-start: `bash scripts/termux_boot/cit_start.sh`

**Key functions**:
- `call_openai()`: Dual API strategy
- `Handler.do_GET()`: Routing for GET requests
- `Handler.do_POST()`: Routing for POST requests
- `_send_json()`: CORS-enabled JSON responses

**Important constants**:
- `UI_HTML`: Complete web interface
- `MODEL`, `PORT`, `OPENAI_API_KEY`: Configuration

### When Debugging Issues

1. **Check environment variables** first
   - Is `OPENAI_API_KEY` set?
   - Are `CIT_MODEL` and `CIT_PORT` valid?

2. **Test OpenAI APIs independently**
   - Try Responses API directly
   - Try Chat Completions API directly
   - Check API key permissions

3. **Verify CORS**
   - Check browser console for CORS errors
   - Verify `Access-Control-Allow-Origin` header
   - Test `OPTIONS` preflight

4. **Test in multiple browsers**
   - STT/TTS support varies
   - Chrome/Edge have best Web Speech API support
   - Test on actual Android device

### Repository Patterns

**Git branches**:
- Main branch: Production-ready code
- Feature branches: Start with `claude/`
- Push with: `git push -u origin <branch-name>`

**Commit workflow**:
1. Make atomic changes
2. Write clear commit message
3. Test before committing
4. Push to feature branch
5. Create PR when ready

**Documentation updates**:
- Code changes → Update docstrings
- API changes → Update `docs/ARCHITECTURE.md`
- User-facing changes → Update `README.md`
- This file → Update when patterns change

---

## Version History

- **v0 (current)**: Initial release with Responses API + Chat Completions fallback
- Embedded web UI with STT/TTS
- Termux-optimized deployment
- Zero external dependencies

---

## Quick Reference

### File Locations

| File | Purpose |
|------|---------|
| `server/cit_server.py` | Main HTTP server (single file) |
| `scripts/termux_bootstrap.sh` | One-time Termux setup |
| `scripts/termux_boot/cit_start.sh` | Auto-start on boot |
| `docs/ARCHITECTURE.md` | System architecture |
| `docs/SECURE_ACCESS.md` | Tailscale setup |
| `README.md` | User quick start |
| `.gitignore` | Excludes `.env`, cache, editor files |

### Environment Variables

```bash
export OPENAI_API_KEY=sk-...     # Required
export CIT_MODEL=gpt-4o-mini     # Optional (default: gpt-4o-mini)
export CIT_PORT=8790             # Optional (default: 8790)
```

### API Endpoints

```bash
GET  /          → Web UI (HTML)
GET  /ui        → Web UI (HTML)
GET  /health    → {"ok": true, "model": "...", "ts": "..."}
POST /chat      → {"message": "..."} → {"reply": "...", "api": "...", "raw": {...}}
OPTIONS /*      → CORS preflight
```

### Testing Commands

```bash
# Health check
curl http://127.0.0.1:8790/health

# Chat request
curl -X POST http://127.0.0.1:8790/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'

# Start server
python server/cit_server.py
```

---

**Last Updated**: 2025-12-29
**Project Version**: v0
**Python Version**: 3.7+
**Primary Platform**: Android (Termux)
