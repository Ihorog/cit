# Система аудиту CIT

## Огляд

Система аудиту CIT забезпечує централізоване логування та моніторинг всіх важливих подій у системі, включаючи:

- 📊 **Аудит ресурсів** - моніторинг файлів та сховищ
- 🔐 **Аудит API запитів** - логування всіх HTTP запитів
- 🛡️ **Аудит мережевої безпеки (GEC-4)** - контроль мережевих з'єднань
- ✅ **Аудит перевірок безпеки** - логування результатів GEC перевірок

## Архітектура

Система аудиту побудована на модульному підході з використанням патерну Singleton для глобального доступу.

### Компоненти

1. **core/audit.py** - Основний модуль аудиту
   - `CITAudit` - головний клас системи аудиту
   - `get_audit_instance()` - отримання глобального інстансу

2. **Інтеграція з ci.py** - Автоматичне логування API запитів
3. **Інтеграція з core/cimeika_system.py** - Аудит ресурсів
4. **Інтеграція з core/audit_test.py** - GEC-4 перевірки безпеки

## API Endpoints

### GET /audit

Отримати повний звіт аудиту за вказаний період.

**Query Parameters:**
- `hours` (необов'язковий) - кількість годин для звіту (за замовчуванням: 24)

**Приклад:**
```bash
curl "http://127.0.0.1:8790/audit?hours=1"
```

**Відповідь:**
```json
{
  "report_generated": "2026-01-26T01:00:00.000000",
  "period_hours": 1,
  "categories": {
    "resources": {
      "count": 5,
      "entries": [...]
    },
    "api_requests": {
      "count": 120,
      "entries": [...]
    },
    "network_security": {
      "count": 8,
      "entries": [...]
    },
    "security": {
      "count": 3,
      "entries": [...]
    }
  }
}
```

### GET /audit/resources

Виконати аудит системних ресурсів (файлів та сховищ).

**Приклад:**
```bash
curl http://127.0.0.1:8790/audit/resources
```

**Відповідь:**
```json
{
  "audit_type": "resources",
  "timestamp": "2026-01-26T01:00:00.000000",
  "resources": {
    "gallery": {
      "count": 42,
      "total_size": 1234567,
      "files": ["image1.jpg", "image2.png", ...]
    },
    "cinema": {...},
    "texts": {...},
    "registry": {...},
    "secure": {...},
    "knowledge": {...}
  }
}
```

## Програмний доступ

### Ініціалізація

```python
from core.audit import get_audit_instance

# Отримати глобальний інстанс аудиту
audit = get_audit_instance()

# Або створити новий з власним шляхом
from core.audit import CITAudit
audit = CITAudit(storage_path="/custom/path/storage")
```

### Аудит ресурсів

```python
# Виконати аудит ресурсів
result = audit.audit_resources()

print(f"Знайдено файлів: {result['resources']['gallery']['count']}")
print(f"Розмір сховища: {result['resources']['gallery']['total_size']} байт")
```

### Логування API запитів

```python
# Залогувати API запит
audit.audit_api_request(
    method="GET",
    path="/health",
    client_ip="127.0.0.1",
    user_agent="curl/7.68.0",
    status_code=200,
    response_time_ms=5.2
)
```

### Аудит мережевих запитів (GEC-4)

```python
# Перевірити і залогувати мережевий запит
result = audit.audit_network_request(
    source_node="NODE-TG-BOT",
    target_url="https://api.telegram.org",
    allowed=True
)

# Заблокований запит
result = audit.audit_network_request(
    source_node="NODE-TG-BOT",
    target_url="https://evil-server.com",
    allowed=False,
    reason="Not in authorized_links"
)
```

### Логування перевірок безпеки

```python
# Залогувати результат перевірки безпеки
audit.audit_security_check(
    check_type="GEC-4",
    status="passed",
    details={
        "test": "network_authorization",
        "node": "NODE-TG-BOT"
    }
)
```

### Отримання звіту

```python
# Отримати звіт за останні 24 години
summary = audit.get_audit_summary(hours=24)

# Отримати звіт тільки по API запитах
api_summary = audit.get_audit_summary(category="api_requests", hours=12)

print(f"Всього API запитів: {summary['categories']['api_requests']['count']}")
```

## Формат логів

Всі логи зберігаються у форматі JSONL (JSON Lines) для легкого парсингу та аналізу.

### Розташування логів

```
~/cit/storage/audit_logs/
├── audit_api_requests.jsonl      # API запити
├── audit_network_security.jsonl  # Мережева безпека
├── audit_resources.jsonl         # Аудит ресурсів
└── audit_security.jsonl          # Перевірки безпеки
```

### Приклад запису логу

```json
{
  "audit_type": "api_request",
  "method": "GET",
  "path": "/health",
  "client_ip": "127.0.0.1",
  "user_agent": "curl/7.68.0",
  "client_type": "CLI_TOOL",
  "status_code": 200,
  "response_time_ms": 5.2,
  "timestamp": "2026-01-26T01:00:00.000000"
}
```

## Типи клієнтів

Система автоматично класифікує клієнтів за User-Agent:

- `CLI_TOOL` - curl, wget, python-requests, httpie
- `AI_AGENT` - GPT, Gemini, Claude, AI
- `WEB_BROWSER` - Mozilla, Chrome, Safari, Firefox
- `UNKNOWN` - невідомі клієнти

## Інтеграція з GEC

Система аудиту повністю інтегрована з фреймворком GEC (Governance, Escalation, Control):

### GEC-2: Strict Least Privilege
- Аудит доступу до ресурсів
- Контроль data_scopes

### GEC-3: Automated Repair
- Логування результатів автоматичного ремонту
- Ескалація помилок

### GEC-4: Push Protection (Ci Guard)
- Аудит мережевих з'єднань
- Перевірка authorized_links з Matrix
- Блокування неавторизованих запитів

## Тестування

Запустити тести:

```bash
# Тести модуля аудиту
python tests/test_audit.py

# Тест GEC-4 безпеки
python core/audit_test.py

# Тест CimeikaSystem з аудитом
python core/cimeika_system.py
```

## Приклади використання

### Моніторинг активності системи

```python
from core.audit import get_audit_instance

audit = get_audit_instance()

# Отримати активність за останню годину
summary = audit.get_audit_summary(hours=1)

print(f"API запитів: {summary['categories']['api_requests']['count']}")
print(f"Перевірок безпеки: {summary['categories']['security']['count']}")
```

### Аналіз типів клієнтів

```python
import json
from pathlib import Path

log_file = Path.home() / "cit" / "storage" / "audit_logs" / "audit_api_requests.jsonl"

client_types = {}
with open(log_file) as f:
    for line in f:
        entry = json.loads(line)
        ct = entry.get("client_type", "UNKNOWN")
        client_types[ct] = client_types.get(ct, 0) + 1

print("Статистика клієнтів:")
for ct, count in sorted(client_types.items(), key=lambda x: -x[1]):
    print(f"  {ct}: {count}")
```

### Пошук повільних запитів

```python
import json
from pathlib import Path

log_file = Path.home() / "cit" / "storage" / "audit_logs" / "audit_api_requests.jsonl"

slow_requests = []
with open(log_file) as f:
    for line in f:
        entry = json.loads(line)
        if entry.get("response_time_ms", 0) > 100:  # > 100ms
            slow_requests.append(entry)

print(f"Знайдено {len(slow_requests)} повільних запитів")
for req in slow_requests[:5]:
    print(f"  {req['method']} {req['path']}: {req['response_time_ms']:.1f}ms")
```

## Конфігурація

### Власний шлях до storage

```python
from core.audit import CITAudit

# Використовувати custom storage
audit = CITAudit(storage_path="/mnt/external/cit/storage")
```

### Період зберігання логів

За замовчуванням логи зберігаються необмежено. Для автоматичного очищення старих логів можна використовувати cron:

```bash
# Видалити логи старіші 30 днів
find ~/cit/storage/audit_logs -name "*.jsonl" -mtime +30 -delete
```

## Безпека

- Логи не містять секретів (API ключів, паролів)
- Чутливі дані (IP адреси) логуються тільки для внутрішнього використання
- Доступ до /audit endpoints можна обмежити за IP/авторизацією

## Продуктивність

- Логування є асинхронним відносно основних операцій
- При помилках логування основна робота системи не переривається
- Файли логів у форматі JSONL оптимізовані для потокової обробки

## Troubleshooting

### Audit module not available

Якщо ви бачите попередження `[WARNING] Audit module not available`, перевірте:

1. Чи файл `core/audit.py` існує
2. Чи `core/` директорія в `sys.path`
3. Чи немає синтаксичних помилок в audit.py

### Логи не створюються

Перевірте права доступу до директорії `~/cit/storage/audit_logs/`:

```bash
ls -la ~/cit/storage/audit_logs/
chmod -R u+w ~/cit/storage/audit_logs/
```

### Великі файли логів

Використовуйте ротацію логів або періодичне очищення:

```bash
# Архівувати старі логи
cd ~/cit/storage/audit_logs
gzip audit_*.jsonl.old

# Або truncate великі файли
> audit_api_requests.jsonl
```

## Майбутні покращення

- [ ] Інтеграція з ElasticSearch / Grafana для візуалізації
- [ ] Автоматична ротація логів
- [ ] Email / Telegram алерти при критичних подіях
- [ ] Dashboard для перегляду статистики
- [ ] Export в різні формати (CSV, PDF)

## Посилання

- [AGENTS.md](../AGENTS.md) - Інструкції для Copilot
- [docs/wiki/registry/matrix.json](../docs/wiki/registry/matrix.json) - GEC конфігурація
- [core/audit.py](../core/audit.py) - Вихідний код модуля
