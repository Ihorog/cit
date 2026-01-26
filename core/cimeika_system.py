import os
import json
import sys
from pathlib import Path

# Імпорт модуля аудиту
try:
    from audit import get_audit_instance
    AUDIT_ENABLED = True
except ImportError:
    AUDIT_ENABLED = False

class CimeikaSystem:
    def __init__(self):
        self.base_path = os.path.expanduser("~/cit")
        self.registry_path = os.path.join(self.base_path, "storage/registry/cit_core.json")
        self.init_system()

    def init_system(self):
        """Забезпечує функціональність сховищ"""
        folders = ["storage/gallery", "storage/cinema", "storage/texts", "storage/registry"]
        for folder in folders:
            os.makedirs(os.path.join(self.base_path, folder), exist_ok=True)

    def scan_resources(self):
        """Автоматична індексація всіх медіа та текстів з використанням модуля аудиту"""
        if AUDIT_ENABLED:
            # Використовуємо новий модуль аудиту
            audit = get_audit_instance(os.path.join(self.base_path, "storage"))
            result = audit.audit_resources()
            
            # Зберігаємо у старому форматі для сумісності
            manifest = {
                "gallery_count": result["resources"].get("gallery", {}).get("count", 0),
                "cinema_count": result["resources"].get("cinema", {}).get("count", 0),
                "texts_count": result["resources"].get("texts", {}).get("count", 0),
                "last_audit": result["timestamp"]
            }
        else:
            # Старий метод (fallback)
            manifest = {
                "gallery_count": len(os.listdir(os.path.join(self.base_path, "storage/gallery"))) if os.path.exists(os.path.join(self.base_path, "storage/gallery")) else 0,
                "cinema_count": len(os.listdir(os.path.join(self.base_path, "storage/cinema"))) if os.path.exists(os.path.join(self.base_path, "storage/cinema")) else 0,
                "texts_count": len(os.listdir(os.path.join(self.base_path, "storage/texts"))) if os.path.exists(os.path.join(self.base_path, "storage/texts")) else 0,
                "last_audit": os.popen('date').read().strip()
            }
        
        # Зберігаємо у registry для сумісності
        with open(self.registry_path, "w") as f:
            json.dump(manifest, f, indent=2)
        return manifest

if __name__ == "__main__":
    sys_ci = CimeikaSystem()
    print(f"Системний Сімейка: Контроль встановлено. {sys_ci.scan_resources()}")
