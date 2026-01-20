import json
import os

db_path = "storage/ci_asset_db.json"

# Створюємо папку, якщо вона зникла
if not os.path.exists("storage"):
    os.makedirs("storage")

# Створюємо файл, якщо він порожній або відсутній
if not os.path.exists(db_path) or os.stat(db_path).st_size == 0:
    with open(db_path, "w", encoding="utf-8") as f:
        json.dump({"state": "init", "possibilities": []}, f)

with open(db_path, "r+", encoding="utf-8") as f:
    try:
        data = json.load(f)
    except json.JSONDecodeError:
        data = {}
        
    data["possibilities"] = [
        {"title": "Мобільна ініціація", "logic": "Створення нових вузлів через сенсорний інтерфейс."},
        {"title": "Синхронізація снів", "logic": "Автоматичне оновлення бази під час нічного спокою."},
        {"title": "Голос Системи", "logic": "Інтеграція мікрофона для диктування канону."}
    ]
    f.seek(0)
    json.dump(data, f, ensure_ascii=False, indent=4)
    f.truncate()
print("--- [TERMUX] ЛЕГЕНДУ ОНОВЛЕНО УСПІШНО ---")
