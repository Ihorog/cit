# CIT Architecture

The Ci Interface Terminal (CIT) is designed to be the simplest possible bridge between a local Cimeika device and remote AI services.  The current version (v0) includes an embedded Web UI and exposes HTTP endpoints that forward chat requests to OpenAI using only Python's standard library.

## Components

- **Android device (Termux)** – The server runs on an Android phone using the Termux terminal emulator.  Termux provides a full Linux environment for installing Python and running services.  A companion app (Termux Boot) can automatically launch CIT on startup.

- **CIT server** – A lightweight HTTP server implemented in `server/cit_server.py`.  It listens on port `8790` and provides:
  - `GET /` or `GET /ui` – Serves an embedded Web UI with a full-featured chat interface. The UI includes:
    - Dark theme optimized for mobile devices
    - Speech-to-Text (STT) for voice input using Web Speech API (Ukrainian language)
    - Text-to-Speech (TTS) for reading responses aloud
    - Real-time health monitoring with model display
    - Message history with clear functionality
  - `GET /health` – Returns server status with model name and timestamp: `{"ok": true, "model": "gpt-4o-mini", "ts": "2026-01-01T..."}`
  - `POST /chat` – Proxies chat requests to OpenAI. Accepts `{"message": "text"}` and returns `{"reply": "...", "api": "responses|chat.completions", "raw": {...}}`

- **OpenAI API** – CIT uses Python's `urllib.request` to call OpenAI APIs with a dual-strategy approach:
  1. Primary: Responses API (`https://api.openai.com/v1/responses`) for simplified interaction
  2. Fallback: Chat Completions API (`https://api.openai.com/v1/chat/completions`) if Responses API fails
  
  The `OPENAI_API_KEY` environment variable must be set; CIT does not read or store secrets from files.  All errors from the upstream API are surfaced as JSON.

- **WebDAV / rclone (optional)** – If the device has rclone configured to a WebDAV backend (e.g., Keenetic router), you can mount or sync your local chat logs and other data.  CIT itself does not perform any file operations, but it is structured to coexist with rclone services (started separately via `scripts/termux_bootstrap.sh`).

- **Future gateways** – The architecture anticipates additional connectors to systems like GitHub, Hugging Face, Figma, or other AI models.  These would operate as separate modules communicating over HTTP or through a message bus.  The core CIT API remains unchanged: external services integrate by consuming or extending the `/chat` endpoint.

## Data flow

1. A client on the Android device (or another host on the LAN) sends a request to the device's IP on port 8790:
   - `GET /` or `GET /ui` → Web UI (chat interface)
   - `GET /health` → Server status check
   - `POST /chat` → Chat request

2. The CIT server receives the request and processes it:
   - For `/` or `/ui`, it returns the embedded HTML interface with Ukrainian language support.
   - For `/health`, it returns `{"ok": true, "model": "gpt-4o-mini", "ts": "2026-01-01T..."}`.
   - For `/chat`, it validates the JSON body (`{"message": "text"}`), reads the `OPENAI_API_KEY` environment variable, and forwards to OpenAI:
     1. First tries Responses API (`/v1/responses`) with `{"model": "...", "input": "text"}`
     2. Falls back to Chat Completions API (`/v1/chat/completions`) with `{"model": "...", "messages": [{"role": "user", "content": "text"}]}`

3. The response is normalized and returned as `{"reply": "...", "api": "responses|chat.completions", "raw": {...}}`.  The Web UI extracts the `reply` field and displays it in the chat log.

### Extended services

Although the current implementation is deliberately minimal, CIT is designed to support extended services via separate scripts or companion daemons:

- **rclone rc** – Running an rclone remote control server (e.g., `rclone rcd --rc-web-gui --rc-addr=127.0.0.1:5572`) allows other devices on the LAN to upload/download data via WebDAV.  Integrate CIT with rclone by adding a service entry in `termux_bootstrap.sh`.

- **GitHub / Hugging Face / Figma** – Future versions may proxy GitHub or other APIs.  These should be implemented as separate endpoints (e.g., `/repo` or `/huggingface`) and should avoid introducing heavy dependencies.  Keep the core CIT server lean and modular.

## Security considerations

- **Environment variables** – Never hard‑code API keys in source code.  Read `OPENAI_API_KEY` from the environment.  You can add a `.env` file locally, but it must be excluded from version control via `.gitignore`.

- **Local access only** – By default, Termux binds the service to `0.0.0.0` so it is accessible from any device on the local network.  Configure your firewall or router if you want to restrict access.  Do not expose CIT directly to the internet without a proper reverse proxy and authentication.

- **Logging** – This implementation prints startup messages to stdout.  It does not log request bodies or API keys.  For production use, consider implementing proper logging with sensitive data redaction.

## Versioning

This document describes CIT **v0**.  The API surface is intentionally small to make it easy to test and extend.  Future versions should maintain backward compatibility for `/health` and `/chat` or introduce versioned endpoints.
