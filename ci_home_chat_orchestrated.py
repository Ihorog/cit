#!/usr/bin/env python3
"""
CI HOME CHAT ORCHESTRATED
— інтерфейс взаємодії з Ci через локальний оркестратор або API.
"""

import json
import requests
import time

API_LOCAL = "http://127.0.0.1:8790"
API_HF = "https://ihorog-cimeika-api.hf.space"

def check_api(base):
    try:
        r = requests.get(f"{base}/health", timeout=2)
        return r.ok
    except Exception:
        return False

def resolve_api():
    if check_api(API_LOCAL):
        print("🧠 Використовується локальний API (Cimeika).")
        return API_LOCAL
    print("☁️  Використовується Hugging Face API (резерв).")
    return API_HF

API_BASE = resolve_api()

def send_message(message: str):
    payload = {"input": message}
    try:
        r = requests.post(f"{API_BASE}/chat", json=payload, timeout=20)
        if r.ok:
            data = r.json()
            return data.get("response", "(немає відповіді)")
        else:
            return f"❌ Помилка: {r.status_code}"
    except Exception as e:
        return f"⚠️ Помилка з'єднання: {e}"

def main():
    print("\n💬 CI HOME CHAT — інтерактивний режим (введи 'вихід' для завершення)\n")
    while True:
        try:
            msg = input("Ти: ").strip()
            if msg.lower() in ("вихід", "exit", "quit"):
                print("👋 Завершення чату.")
                break
            if not msg:
                continue
            reply = send_message(msg)
            print(f"Ci: {reply}\n")
            time.sleep(0.3)
        except KeyboardInterrupt:
            print("\n👋 Вихід.")
            break

if __name__ == "__main__":
    main()
