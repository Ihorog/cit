import sys
import os
from pathlib import Path

# Add parent directory to path for utils imports
sys.path.insert(0, str(Path(__file__).parent))
from utils.json_handler import read_json_file, write_json_file

db_path = "storage/ci_asset_db.json"

# Створюємо папку, якщо вона зникла
if not os.path.exists("storage"):
    os.makedirs("storage")

# Створюємо файл, якщо він порожній або відсутній
data = read_json_file(db_path, default={"state": "init", "possibilities": []})
        
data["possibilities"] = [
    {"title": "Мобільна ініціація", "logic": "Створення нових вузлів через сенсорний інтерфейс."},
    {"title": "Синхронізація снів", "logic": "Автоматичне оновлення бази під час нічного спокою."},
    {"title": "Голос Системи", "logic": "Інтеграція мікрофона для диктування канону."}
]

write_json_file(db_path, data, indent=4)
print("--- [TERMUX] ЛЕГЕНДУ ОНОВЛЕНО УСПІШНО ---")
