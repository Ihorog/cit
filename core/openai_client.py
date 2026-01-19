import os
import json
from core.logger import get_logger

logger = get_logger("openai")

def chat(message):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"reply": "API Key missing", "ok": False}
    # Тут може бути ваш запит через requests/urllib
    return {"reply": f"Echo: {message}", "ok": True, "api": "mock"}
