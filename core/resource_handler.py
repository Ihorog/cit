import os
import json
import shutil
from datetime import datetime

# Шлях до сховища на роутері Keenetic (має бути змонтований у Termux)
KEENETIC_STORAGE = "/sdcard/keenetic_drive/cit_media" 

def process_new_file(file_path, category="general"):
    """Визначає долю файлу та реєструє його"""
    file_name = os.path.basename(file_path)
    timestamp = datetime.now().isoformat()
    
    # 1. Визначення цільової папки
    dest_dir = os.path.join(KEENETIC_STORAGE, category)
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, file_name)

    # 2. Переміщення у сховище Keenetic
    try:
        shutil.move(file_path, dest_path)
        
        # 3. Реєстрація в Базі Даних (Registry of Truth)
        db_path = os.path.expanduser("~/cit/storage/registry/cit_core.json")
        with open(db_path, "r+") as f:
            db = json.load(f)
            new_component = {
                "id": f"comp_{int(datetime.now().timestamp())}",
                "name": file_name,
                "path": dest_path,
                "type": category,
                "added": timestamp
            }
            db.setdefault("components", []).append(new_component)
            f.seek(0)
            json.dump(db, f, indent=2)
            
        return f"Ci: Компонент {file_name} прийнято та збережено на Keenetic."
    except Exception as e:
        return f"Ci: Помилка збереження: {str(e)}"
