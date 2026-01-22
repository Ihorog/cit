import os
import json
import sys

def run_security_test():
    print(">>> [GEC-4] Симуляція неавторизованого мережевого запиту...")
    with open("docs/wiki/registry/matrix.json", "r") as f:
        matrix = json.load(f)
    
    # Спроба звернутися до лінку, якого немає в Matrix для NODE-TG-BOT
    unauthorized_url = "https://evil-server.com"
    allowed_links = matrix['nodes']['NODE-TG-BOT']['authorized_links']
    
    if unauthorized_url not in allowed_links:
        print(f"\033[1;31m[BLOCK] Ci Guard: Запит до {unauthorized_url} ЗАБОРОНЕНО.\033[0m")
        return True # Тест пройдено (захист спрацював)
    return False

if __name__ == "__main__":
    if run_security_test():
        sys.exit(0)
    else:
        sys.exit(1)
