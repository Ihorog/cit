# CIT (Ci Interface Terminal)

CIT (Ci Interface Terminal) is a lightweight API gateway that sits between your Cimeika devices and the OpenAI API.  
It exposes a minimal HTTP interface with two endpoints and forwards chat requests to OpenAI using Python's standard library.  
The service is designed to run locally on Android through Termux and can be connected to other systems over a LAN.  

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
   export OPENAI_API_KEY=sk-...
   # Start the server on port 8790
   python server/cit_server.py
   ```

The service will listen on all interfaces (port `8790` by default).  
You can add the start command to `scripts/termux_boot/cit_start.sh` and enable Termux Boot to run CIT automatically after a reboot.

## Example requests

Check that CIT is running:

```bash
curl http://127.0.0.1:8790/health
# → {"ok": true}
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

## License

This project is released under the MIT License.  See `LICENSE` for details.
