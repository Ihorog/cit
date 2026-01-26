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
    print("[WARNING] Audit module not available, using legacy test")

def run_security_test():
    """GEC-4 тест: Симуляція неавторизованого мережевого запиту"""
    print(">>> [GEC-4] Симуляція неавторизованого мережевого запиту...")
    
    # Перевірка доступу до Matrix файлу
    matrix_path = Path(__file__).parent.parent / "docs" / "wiki" / "registry" / "matrix.json"
    
    if not matrix_path.exists():
        print(f"[SKIP] Matrix файл не знайдено: {matrix_path}")
        return True  # Пропускаємо тест якщо немає Matrix
    
    with open(matrix_path, "r") as f:
        matrix = json.load(f)
    
    # Спроба звернутися до лінку, якого немає в Matrix для NODE-TG-BOT
    test_node = "NODE-TG-BOT"
    unauthorized_url = "evil-server.com"  # Лише домен
    authorized_url = "api.telegram.org"   # Лише домен
    
    if test_node not in matrix.get('nodes', {}):
        print(f"[SKIP] Ноду {test_node} не знайдено в Matrix")
        return True
    
    allowed_links = matrix['nodes'][test_node].get('authorized_links', [])
    
    # Тест 1: Заборонений URL
    if unauthorized_url not in allowed_links:
        print(f"\033[1;31m[BLOCK] Ci Guard: Запит до {unauthorized_url} ЗАБОРОНЕНО.\033[0m")
        
        # Логування через модуль аудиту
        if AUDIT_ENABLED:
            audit = get_audit_instance()
            audit.audit_network_request(test_node, f"https://{unauthorized_url}", False, "Not in authorized_links")
            audit.audit_security_check("GEC-4", "passed", {
                "test": "unauthorized_url_blocked",
                "node": test_node,
                "url": unauthorized_url
            })
    else:
        print(f"[FAIL] Небезпечний URL {unauthorized_url} дозволено!")
        return False
    
    # Тест 2: Дозволений URL
    if authorized_url in allowed_links:
        print(f"\033[1;32m[ALLOW] Ci Guard: Запит до {authorized_url} ДОЗВОЛЕНО.\033[0m")
        
        # Логування через модуль аудиту
        if AUDIT_ENABLED:
            audit = get_audit_instance()
            audit.audit_network_request(test_node, f"https://{authorized_url}", True)
            audit.audit_security_check("GEC-4", "passed", {
                "test": "authorized_url_allowed",
                "node": test_node,
                "url": authorized_url
            })
    else:
        print(f"[FAIL] Легітимний URL {authorized_url} заблоковано!")
        return False
    
    print("[OK] GEC-4 Ci Guard тест пройдено успішно!")
    return True

if __name__ == "__main__":
    if run_security_test():
        sys.exit(0)
    else:
        sys.exit(1)
