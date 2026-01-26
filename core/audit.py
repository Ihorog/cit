#!/usr/bin/env python3
"""
Модуль аудиту CIT (Cimeika Interface Terminal)
Централізований аудит для системних ресурсів, API запитів, та безпеки
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class CITAudit:
    """Централізована система аудиту для CIT"""
    
    def __init__(self, storage_path: str = None):
        """
        Ініціалізація системи аудиту
        
        Args:
            storage_path: Шлях до директорії storage (за замовчуванням ~/cit/storage)
        """
        if storage_path is None:
            storage_path = os.path.join(os.path.expanduser("~"), "cit", "storage")
        
        self.storage_path = Path(storage_path)
        self.registry_path = self.storage_path / "registry"
        self.audit_log_path = self.storage_path / "audit_logs"
        self.audit_log_path.mkdir(parents=True, exist_ok=True)
        
    def _get_timestamp(self) -> str:
        """Отримати поточний timestamp в ISO формації"""
        return datetime.now().isoformat()
    
    def _write_log_entry(self, category: str, entry: Dict[str, Any]):
        """Записати запис аудиту до файлу"""
        log_file = self.audit_log_path / f"audit_{category}.jsonl"
        entry["timestamp"] = self._get_timestamp()
        
        with open(log_file, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    def audit_resources(self) -> Dict[str, Any]:
        """
        Аудит системних ресурсів (файли, сховища)
        
        Returns:
            Словник з результатами аудиту ресурсів
        """
        result = {
            "audit_type": "resources",
            "timestamp": self._get_timestamp(),
            "resources": {}
        }
        
        # Аудит медіа-ресурсів
        resource_dirs = ["gallery", "cinema", "texts", "registry", "secure", "knowledge"]
        for dir_name in resource_dirs:
            dir_path = self.storage_path / dir_name
            if dir_path.exists():
                files = list(dir_path.glob("*"))
                result["resources"][dir_name] = {
                    "count": len(files),
                    "total_size": sum(f.stat().st_size for f in files if f.is_file()),
                    "files": [f.name for f in files if f.is_file()]
                }
            else:
                result["resources"][dir_name] = {
                    "count": 0,
                    "total_size": 0,
                    "files": [],
                    "status": "not_found"
                }
        
        # Записати в лог
        self._write_log_entry("resources", result)
        
        # Оновити registry
        self._update_registry_audit(result)
        
        return result
    
    def audit_api_request(self, method: str, path: str, 
                         client_ip: str, user_agent: str,
                         status_code: int = None, 
                         response_time_ms: float = None) -> None:
        """
        Аудит API запиту
        
        Args:
            method: HTTP метод (GET, POST, etc.)
            path: Шлях запиту
            client_ip: IP адреса клієнта
            user_agent: User-Agent заголовок
            status_code: HTTP статус код відповіді
            response_time_ms: Час виконання запиту в мілісекундах
        """
        entry = {
            "audit_type": "api_request",
            "method": method,
            "path": path,
            "client_ip": client_ip,
            "user_agent": user_agent,
            "client_type": self._classify_client(user_agent)
        }
        
        if status_code is not None:
            entry["status_code"] = status_code
        if response_time_ms is not None:
            entry["response_time_ms"] = response_time_ms
        
        self._write_log_entry("api_requests", entry)
    
    def audit_network_request(self, source_node: str, target_url: str, 
                             allowed: bool, reason: str = None) -> Dict[str, Any]:
        """
        Аудит мережевого запиту (GEC-4: Ci Guard)
        
        Args:
            source_node: Ідентифікатор ноди-джерела
            target_url: Цільовий URL
            allowed: Чи дозволений запит
            reason: Причина блокування (якщо заблоковано)
        
        Returns:
            Результат перевірки
        """
        entry = {
            "audit_type": "network_request",
            "source_node": source_node,
            "target_url": target_url,
            "allowed": allowed,
            "action": "ALLOWED" if allowed else "BLOCKED"
        }
        
        if reason:
            entry["reason"] = reason
        
        self._write_log_entry("network_security", entry)
        
        return entry
    
    def audit_security_check(self, check_type: str, status: str, 
                            details: Dict[str, Any] = None) -> None:
        """
        Аудит перевірки безпеки
        
        Args:
            check_type: Тип перевірки (GEC-2, GEC-3, GEC-4)
            status: Статус (passed, failed, warning)
            details: Додаткові деталі
        """
        entry = {
            "audit_type": "security_check",
            "check_type": check_type,
            "status": status
        }
        
        if details:
            entry["details"] = details
        
        self._write_log_entry("security", entry)
    
    def get_audit_summary(self, category: str = None, 
                          hours: int = 24) -> Dict[str, Any]:
        """
        Отримати звіт аудиту
        
        Args:
            category: Категорія аудиту (resources, api_requests, network_security, security)
                     None = всі категорії
            hours: Кількість годин для звіту (за замовчуванням 24)
        
        Returns:
            Звіт аудиту
        """
        cutoff_time = datetime.now().timestamp() - (hours * 3600)
        summary = {
            "report_generated": self._get_timestamp(),
            "period_hours": hours,
            "categories": {}
        }
        
        categories = [category] if category else ["resources", "api_requests", "network_security", "security"]
        
        for cat in categories:
            log_file = self.audit_log_path / f"audit_{cat}.jsonl"
            if not log_file.exists():
                summary["categories"][cat] = {"count": 0, "entries": []}
                continue
            
            entries = []
            with open(log_file, "r") as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        entry_time = datetime.fromisoformat(entry["timestamp"]).timestamp()
                        if entry_time >= cutoff_time:
                            entries.append(entry)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        continue
            
            summary["categories"][cat] = {
                "count": len(entries),
                "entries": entries[-100:]  # Останні 100 записів
            }
        
        return summary
    
    def _classify_client(self, user_agent: str) -> str:
        """Класифікувати тип клієнта за User-Agent"""
        ua_lower = user_agent.lower()
        if any(x in ua_lower for x in ["python", "curl", "wget", "httpie"]):
            return "CLI_TOOL"
        elif any(x in ua_lower for x in ["gpt", "gemini", "claude", "ai"]):
            return "AI_AGENT"
        elif any(x in ua_lower for x in ["mozilla", "chrome", "safari", "firefox"]):
            return "WEB_BROWSER"
        else:
            return "UNKNOWN"
    
    def _update_registry_audit(self, audit_result: Dict[str, Any]) -> None:
        """Оновити registry з інформацією про останній аудит"""
        registry_file = self.registry_path / "cit_core.json"
        
        try:
            if registry_file.exists():
                with open(registry_file, "r") as f:
                    data = json.load(f)
            else:
                data = {}
            
            data["last_audit"] = audit_result["timestamp"]
            data["last_audit_type"] = audit_result["audit_type"]
            
            # Зберегти короткі метрики
            if "resources" in audit_result:
                data["resource_summary"] = {
                    dir_name: info["count"] 
                    for dir_name, info in audit_result["resources"].items()
                }
            
            with open(registry_file, "w") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except (IOError, json.JSONDecodeError) as e:
            # Не блокувати роботу системи при помилках registry
            pass


# Глобальний інстанс для використання в інших модулях
_audit_instance = None

def get_audit_instance(storage_path: str = None) -> CITAudit:
    """Отримати глобальний інстанс аудиту (singleton pattern)"""
    global _audit_instance
    if _audit_instance is None:
        _audit_instance = CITAudit(storage_path)
    return _audit_instance


if __name__ == "__main__":
    # Тестовий запуск
    audit = CITAudit()
    
    print("=== Аудит ресурсів ===")
    resources = audit.audit_resources()
    print(json.dumps(resources, indent=2, ensure_ascii=False))
    
    print("\n=== Симуляція API запиту ===")
    audit.audit_api_request("GET", "/health", "127.0.0.1", "curl/7.68.0", 200, 5.2)
    
    print("\n=== Симуляція перевірки безпеки ===")
    audit.audit_network_request("NODE-TG-BOT", "https://api.telegram.org", True)
    audit.audit_network_request("NODE-TG-BOT", "https://evil-server.com", False, "Not in authorized_links")
    
    print("\n=== Звіт аудиту (остання година) ===")
    summary = audit.get_audit_summary(hours=1)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
