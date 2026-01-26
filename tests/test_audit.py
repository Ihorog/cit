#!/usr/bin/env python3
"""
Тести для модуля аудиту CIT
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# Додати core до шляху
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from audit import CITAudit


def test_audit_initialization():
    """Тест: Ініціалізація системи аудиту"""
    print("=== Тест 1: Ініціалізація ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        audit = CITAudit(tmpdir)
        
        # Перевірка створення директорій
        assert audit.audit_log_path.exists(), "Директорія логів не створена"
        assert audit.storage_path.exists(), "Директорія storage не існує"
        
        print("✓ Ініціалізація пройшла успішно")
        return True


def test_resource_audit():
    """Тест: Аудит ресурсів"""
    print("\n=== Тест 2: Аудит ресурсів ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        audit = CITAudit(tmpdir)
        
        # Створити тестові файли
        test_dir = audit.storage_path / "gallery"
        test_dir.mkdir(parents=True, exist_ok=True)
        (test_dir / "test1.jpg").write_text("test content")
        (test_dir / "test2.png").write_text("test content 2")
        
        # Виконати аудит
        result = audit.audit_resources()
        
        # Перевірити результати
        assert result["audit_type"] == "resources", "Невірний тип аудиту"
        assert "timestamp" in result, "Відсутній timestamp"
        assert result["resources"]["gallery"]["count"] == 2, "Невірна кількість файлів"
        
        # Перевірити що лог створено
        log_file = audit.audit_log_path / "audit_resources.jsonl"
        assert log_file.exists(), "Файл логу не створено"
        
        print("✓ Аудит ресурсів пройшов успішно")
        return True


def test_api_request_audit():
    """Тест: Аудит API запитів"""
    print("\n=== Тест 3: Аудит API запитів ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        audit = CITAudit(tmpdir)
        
        # Логувати кілька запитів
        audit.audit_api_request("GET", "/health", "127.0.0.1", "curl/7.68.0", 200, 5.2)
        audit.audit_api_request("POST", "/chat", "192.168.1.100", "Mozilla/5.0", 200, 150.5)
        audit.audit_api_request("GET", "/audit", "10.0.0.1", "python-requests/2.28", 200, 10.3)
        
        # Перевірити що логи створені
        log_file = audit.audit_log_path / "audit_api_requests.jsonl"
        assert log_file.exists(), "Файл логу API запитів не створено"
        
        # Прочитати логи
        with open(log_file) as f:
            lines = f.readlines()
            assert len(lines) == 3, "Невірна кількість записів логу"
            
            # Перевірити класифікацію клієнтів
            entry1 = json.loads(lines[0])
            assert entry1["client_type"] == "CLI_TOOL", "Невірна класифікація curl"
            
            entry2 = json.loads(lines[1])
            assert entry2["client_type"] == "WEB_BROWSER", "Невірна класифікація браузера"
        
        print("✓ Аудит API запитів пройшов успішно")
        return True


def test_network_security_audit():
    """Тест: Аудит мережевої безпеки (GEC-4)"""
    print("\n=== Тест 4: Аудит мережевої безпеки ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        audit = CITAudit(tmpdir)
        
        # Логувати дозволений запит
        result1 = audit.audit_network_request(
            "NODE-TG-BOT", 
            "https://api.telegram.org", 
            True
        )
        assert result1["allowed"] == True, "Дозволений запит не пройшов"
        assert result1["action"] == "ALLOWED", "Невірна дія"
        
        # Логувати заборонений запит
        result2 = audit.audit_network_request(
            "NODE-TG-BOT", 
            "https://evil-server.com", 
            False, 
            "Not in authorized_links"
        )
        assert result2["allowed"] == False, "Заборонений запит не заблоковано"
        assert result2["action"] == "BLOCKED", "Невірна дія"
        assert "reason" in result2, "Відсутня причина блокування"
        
        # Перевірити логи
        log_file = audit.audit_log_path / "audit_network_security.jsonl"
        assert log_file.exists(), "Файл логу мережевої безпеки не створено"
        
        print("✓ Аудит мережевої безпеки пройшов успішно")
        return True


def test_security_check_audit():
    """Тест: Аудит перевірок безпеки"""
    print("\n=== Тест 5: Аудит перевірок безпеки ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        audit = CITAudit(tmpdir)
        
        # Логувати різні перевірки
        audit.audit_security_check("GEC-2", "passed", {"test": "integrity_check"})
        audit.audit_security_check("GEC-3", "warning", {"repair": "auto_fixed"})
        audit.audit_security_check("GEC-4", "passed", {"network": "validated"})
        
        # Перевірити логи
        log_file = audit.audit_log_path / "audit_security.jsonl"
        assert log_file.exists(), "Файл логу безпеки не створено"
        
        with open(log_file) as f:
            lines = f.readlines()
            assert len(lines) == 3, "Невірна кількість записів"
        
        print("✓ Аудит перевірок безпеки пройшов успішно")
        return True


def test_audit_summary():
    """Тест: Генерація звіту аудиту"""
    print("\n=== Тест 6: Генерація звіту ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        audit = CITAudit(tmpdir)
        
        # Створити тестові дані
        audit.audit_api_request("GET", "/health", "127.0.0.1", "curl", 200, 5)
        audit.audit_network_request("NODE-TG-BOT", "https://api.telegram.org", True)
        audit.audit_security_check("GEC-4", "passed")
        
        # Отримати звіт
        summary = audit.get_audit_summary(hours=1)
        
        assert "report_generated" in summary, "Відсутній час генерації звіту"
        assert "categories" in summary, "Відсутні категорії"
        assert "api_requests" in summary["categories"], "Відсутня категорія API запитів"
        
        # Перевірити що дані присутні
        assert summary["categories"]["api_requests"]["count"] > 0, "Немає записів API запитів"
        assert summary["categories"]["network_security"]["count"] > 0, "Немає записів безпеки"
        
        print("✓ Генерація звіту пройшла успішно")
        return True


def test_client_classification():
    """Тест: Класифікація типів клієнтів"""
    print("\n=== Тест 7: Класифікація клієнтів ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        audit = CITAudit(tmpdir)
        
        test_cases = [
            ("curl/7.68.0", "CLI_TOOL"),
            ("python-requests/2.28.0", "CLI_TOOL"),
            ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0", "WEB_BROWSER"),
            ("Mozilla/5.0 (iPhone; CPU iPhone OS 14_6)", "WEB_BROWSER"),
            ("GPT-4 Agent", "AI_AGENT"),
            ("Unknown-Agent", "UNKNOWN"),
        ]
        
        for user_agent, expected_type in test_cases:
            result = audit._classify_client(user_agent)
            assert result == expected_type, f"Невірна класифікація для {user_agent}: {result} != {expected_type}"
        
        print("✓ Класифікація клієнтів пройшла успішно")
        return True


def run_all_tests():
    """Запустити всі тести"""
    print("=" * 60)
    print("ТЕСТУВАННЯ МОДУЛЯ АУДИТУ CIT")
    print("=" * 60)
    
    tests = [
        test_audit_initialization,
        test_resource_audit,
        test_api_request_audit,
        test_network_security_audit,
        test_security_check_audit,
        test_audit_summary,
        test_client_classification,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"✗ Тест провалився: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ Помилка тесту: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"РЕЗУЛЬТАТИ: {passed} пройдено, {failed} провалено")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
