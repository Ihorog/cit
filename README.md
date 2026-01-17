<p align="center">
  <img src="https://raw.githubusercontent.com/Ihorog/cit/main/ui/icons/icon-512.png" alt="CIT Logo" width="180" />
</p>

# CIT (Ci Interface Terminal)

[![Vercel Deployment](https://github.com/Ihorog/cit/actions/workflows/vercel-deploy.yml/badge.svg)](https://github.com/Ihorog/cit/actions/workflows/vercel-deploy.yml)

CIT (Ci Interface Terminal) is a lightweight API gateway that sits between your Cimeika devices and the OpenAI API.  
It exposes a minimal HTTP interface and forwards chat requests to OpenAI using Python's standard library.  
The service is designed to run locally on Android through Termux and can be connected to other systems over a LAN.  

> **Note:** For conceptual understanding of Ci and its underlying framework, see the [Legend Ci documentation](LEGEND_CI.md) (canonical source: [ciwiki/Legend ci](https://github.com/Ihorog/ciwiki/tree/main/Legend%20ci)). This README focuses on technical implementation.

## Features

* **Health check** – `GET /health` returns a simple JSON object to verify the service is running.  
* **Web UI** – `GET /ui` (or `/`) provides a browser-based chat interface with Speech-to-Text (STT) and Text-to-Speech (TTS) support.
* **Chat proxy** – `POST /chat` forwards your chat messages to OpenAI and returns the response.  
* **Intelligent API routing** – uses OpenAI's Responses API with automatic fallback to Chat Completions API.
* **No external dependencies** – implemented with Python's built‑in modules, so it works out of the box in Termux.  
* **Simple deployment** – start the server with a single script or integrate it into Termux Boot for auto‑start.

## Quick start in Termux

Follow these three steps to install and run CIT on your Android device using Termux:

1. **Install Termux packages**
   ```bash
   pkg update -y && pkg upgrade -y
   pkg install -y git python termux-services
   ```

2. **Clone the repository**
   ```bash
   git clone https://github.com/Ihorog/cit.git ~/cit
   cd ~/cit
   ```

3. **Run the server**
   ```bash
   # Export your OpenAI API key (required)
   export OPENAI_API_KEY="your-api-key-here"
   # Optional: Export your HuggingFace token for ML model access
   export HUGGINGFACE_API_TOKEN="your-token-here"
   # Start the server on port 8790
   python server/cit_server.py
   ```

The service will listen on all interfaces (port `8790` by default).  
You can add the start command to `scripts/termux_boot/cit_start.sh` and enable Termux Boot to run CIT automatically after a reboot.

Access the Web UI at `http://127.0.0.1:8790/ui` in your browser to use the chat interface with voice capabilities.

## Example requests

### Web UI

Open your browser and navigate to:
```
http://127.0.0.1:8790/ui
```

The Web UI provides:
- Text input with "Send" button
- 🎙️ STT button for voice input (Ukrainian language)
- 🔊 TTS button to hear the assistant's response
- Real-time health status indicator
- Dark theme optimized for mobile

### API Endpoints

Check that CIT is running:

```bash
curl http://127.0.0.1:8790/health
# → {"ok": true, "model": "gpt-4o-mini", "ts": "2026-01-01T22:04:59.584648+00:00"}
```

Send a chat message to OpenAI via CIT:

```bash
curl -X POST http://127.0.0.1:8790/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello, world!"}'

# Example response:
# {
#   "reply": "Hello! How can I assist you today?",
#   "api": "chat.completions",
#   "raw": {
#     "id": "chatcmpl-abc123",
#     "object": "chat.completion",
#     "created": 1735756800,
#     "model": "gpt-4.1-mini",
#     "choices": [
#       {
#         "index": 0,
#         "message": {
#           "role": "assistant",
#           "content": "Hello! How can I assist you today?"
#         },
#         "finish_reason": "stop"
#       }
#     ]
#   }
# }
```

Or open the Web UI in your browser:

```bash
# Open http://127.0.0.1:8790/ui in your browser
# Features:
# - Interactive chat interface
# - 🎙️ Speech-to-Text (STT) for voice input
# - 🔊 Text-to-Speech (TTS) to hear responses
# - Dark theme optimized for mobile
```

## Repository check

Run a lightweight repo verification (syntax + /health probe) without external dependencies:

```bash
./scripts/repo_check.sh
```

The script starts a temporary server on port `8979` by default. Set `OPENAI_API_KEY` if you want to include the `/chat` smoke test.

## Repository layout

```
cit/
├── README.md             # this file
├── .gitignore            # common ignores (.env, Python cache)
├── docs/
│   └── ARCHITECTURE.md   # high‑level architecture description
├── server/
│   └── cit_server.py     # main HTTP server implementation
└── scripts/
    ├── termux_bootstrap.sh    # optional helper to set up Termux environment
    └── termux_boot/cit_start.sh # script run by Termux Boot
```

> **Note:** Operational scripts have been organized into `scripts/ops/` and vault/sync scripts into `scripts/vault/`. See README files in those directories for details.

## Web Interface (Cimeika)

In addition to the embedded UI served by the CIT server, there's a modern **Next.js PWA** interface called **Cimeika** in the `/web` directory.

**Features:**
- 🎨 Beautiful dark theme optimized for mobile
- 💬 Full-featured chat interface with AI
- 🎙️ Speech-to-Text (Ukrainian)
- 🔊 Text-to-Speech (Ukrainian)  
- 📱 PWA support (install as app)
- 🎯 Menu system with multiple sections
- 📊 Real-time health monitoring

**Quick start:**
```bash
# Start CIT server (required)
export OPENAI_API_KEY="your-api-key-here"
python server/cit_server.py

# In another terminal, start web app
cd web
npm install
npm run dev
# Open http://localhost:3000
```

See [`web/README_WEB.md`](web/README_WEB.md) for detailed documentation, deployment guides, and PWA setup.

## 🚀 Автоматичне розгортання

Веб-інтерфейс автоматично розгортається на Vercel при кожному push до `main` гілки.

### Швидкий старт

1. **Налаштуйте Vercel токени** — див. [docs/VERCEL_SETUP.md](docs/VERCEL_SETUP.md)
2. **Push код** — деплой відбудеться автоматично
3. **Створіть PR** — отримаєте preview URL для тестування

### Локальне тестування

```bash
# Перевірити що збірка працює
./scripts/test-vercel-deploy.sh

# Деплой вручну (потрібен Vercel CLI)
npm install -g vercel
vercel --prod
```

Детальна документація: [docs/VERCEL_SETUP.md](docs/VERCEL_SETUP.md)

## Copilot

GitHub Copilot development follows the canonical instructions defined in the [ciwiki repository](https://github.com/Ihorog/ciwiki/blob/main/.github/copilot-instructions.md).

Key principles:
- Anti-repeat: eliminate repeated actions
- Single execution path through PR → verification → approval
- Documentation first

See [.github/copilot-instructions.md](.github/copilot-instructions.md) for the full instructions synchronized from ciwiki.

## License

This project is released under the MIT License.  See `LICENSE` for details.
