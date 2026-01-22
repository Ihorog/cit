import os
import json
import sys

def check_system():
    print("--- [Ciт] ПЕРЕВІРКА ЦІЛІСНОСТІ GEC-2 ---")
    
    # 1. Перевірка Реєстру Істини
    matrix_path = "docs/wiki/registry/matrix.json"
    if not os.path.exists(matrix_path):
        print(f"[ERROR] Registry not found at {matrix_path}")
        return False
        
    # 2. Перевірка Паспорта Вузла
    passport_path = "storage/secure/device_identity.json"
    if not os.path.exists(passport_path):
        print(f"[ERROR] Node Passport not found at {passport_path}")
        return False
        
    print("[OK] Базові компоненти на місці.")
    return True

if __name__ == "__main__":
    if "--check" in sys.argv:
        if not check_system():
            sys.exit(1)
        sys.exit(0)
