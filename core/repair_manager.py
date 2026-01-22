import os
import subprocess

class RepairManager:
    def __init__(self):
        self.repair_tools = {
            "storage_mount": "scripts/mount_keenetic.sh",
            "db_recovery": "recovery.sh",
            "network_reset": "scripts/reset_network.sh"
        }

    def identify_and_fix(self, error_type):
        """Протокол ідентифікації та виклику засобів ремонту"""
        print(f"Ci: Ідентифіковано збій: {error_type}. Запуск засобів ремонту...")
        
        if "mount" in error_type or "Permission denied" in error_type:
            return self.run_tool("storage_mount")
        elif "json" in error_type or "registry" in error_type:
            return self.run_tool("db_recovery")
        
        return "Ci: Необхідна ескалація до Архітектора (GEC-3)."

    def run_tool(self, tool_name):
        script = self.repair_tools.get(tool_name)
        if script and os.path.exists(script):
            subprocess.run(["bash", script])
            return True
        return False

if __name__ == "__main__":
    # Автономний запуск діагностики
    pass
