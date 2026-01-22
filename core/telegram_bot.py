import os
import json
import requests
from datetime import datetime

# Налаштування доступу (використовуйте свої змінні середовища)
TELEGRAM_TOKEN = os.getenv("TG_TOKEN")
ADMIN_CHAT_ID = os.getenv("TG_ADMIN_ID")

def send_to_admin(message):
    """Надсилає сервісне повідомлення власнику системи"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": ADMIN_CHAT_ID,
        "text": f"⚠️ [Ciт GEC-3 REPORT]\n{message}",
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Помилка ескалації: {e}")

def handle_repair_signal(signal_path="storage/last_repair_request.json"):
    """Перевіряє наявність нових запитів на ремонт"""
    if os.path.exists(signal_path):
        with open(signal_path, "r") as f:
            data = json.load(f)
        
        report = (
            f"*Вузол:* {data['node_id']}\n"
            f"*Статус:* {data['status']}\n"
            f"*Помилка:* `{data['error']}`\n"
            f"*Дія:* {data['action']}"
        )
        send_to_admin(report)
        # Архівуємо запит після обробки
        os.rename(signal_path, f"storage/archive/repair_{datetime.now().timestamp()}.json")

if __name__ == "__main__":
    print(f"--- [Ciт] БОТ АКТИВОВАНО: {datetime.now()} ---")
    # Тут запускається основний цикл бота
