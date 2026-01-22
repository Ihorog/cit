import os
import json

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
        """Автоматична індексація всіх медіа та текстів"""
        manifest = {
            "gallery_count": len(os.listdir(os.path.join(self.base_path, "storage/gallery"))),
            "cinema_count": len(os.listdir(os.path.join(self.base_path, "storage/cinema"))),
            "texts_count": len(os.listdir(os.path.join(self.base_path, "storage/texts"))),
            "last_audit": os.popen('date').read().strip()
        }
        with open(self.registry_path, "w") as f:
            json.dump(manifest, f, indent=2)
        return manifest

if __name__ == "__main__":
    sys_ci = CimeikaSystem()
    print(f"Системний Сімейка: Контроль встановлено. {sys_ci.scan_resources()}")
