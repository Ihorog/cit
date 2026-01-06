# CIMEIKA DEPLOYMENT GUIDE

## Огляд системи

CIMEIKA — це інтегрований інтелектуальний помічник з розподіленою архітектурою, що включає:

- **Ci** — центральний координатор
- **PoDija** — планувальник подій
- **Nastrij** — емоційний аналітик
- **Malya** — освітньо-ігровий інтерфейс
- **Kazkar** — голосовий генератор історій
- **Gallery** — менеджер візуального контенту

## Швидке розгортання

### Передумови

- Docker & Docker Compose
- Git
- Python 3.10+
- Налаштовані секрети GitHub Actions

### Крок 1: Клонування репозиторію

```bash
git clone https://github.com/Ihorog/cimeika-ai-deploy.git
cd cimeika-ai-deploy
```

### Крок 2: Налаштування середовища

```bash
# Копіювати шаблон конфігурації
cp cimeika/configs/CIMEIKA_FULL_ACCESS.env .env

# Заповнити API ключі у .env файлі
nano .env
```

### Крок 3: Запуск системи

```bash
# Запуск всіх сервісів
docker-compose up -d

# Перевірка статусу
docker-compose ps
curl http://localhost:8790/health
```

### Крок 4: Доступ до інтерфейсів

- **Web UI**: http://localhost:8000
- **API**: http://localhost:8790
- **Health Check**: http://localhost:8790/health
- **Tasks API**: http://localhost:8790/tasks

## Архітектура розгортання

### Компоненти

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web UI        │    │    API Gateway   │    │  Orchestrator   │
│   (Nginx)       │◄──►│    (Flask)       │◄──►│  (Python)       │
│   Port: 8000    │    │   Port: 8790     │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                    ┌─────────────────────┐
                    │   Sensomatyka       │
                    │   Analyzer          │
                    └─────────────────────┘
```

### Сервіси Docker Compose

- **cimeika-api**: Основний API сервер (Flask)
- **cimeika-orchestrator**: Розподільник задач
- **cimeika-web**: Web інтерфейс (Nginx)
- **cimeika-watchdog**: Моніторинг та автоматичне відновлення

## Конфігурація

### Змінні середовища (.env)

```bash
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_ORGANIZATION=org-...

# HuggingFace
HF_TOKEN=hf_...
HF_SPACE_URL=https://ihorog-cimeika-api.hf.space

# Telegram Bots
TELEGRAM_BOT_TOKEN_CIMEIKA=123456:ABC-...
TELEGRAM_BOT_TOKEN_KAZKAR=123456:ABC-...
TELEGRAM_CHANNEL_ID=@ci_channel

# Database
MYSQL_HOST=um542319.mysql.tools
MYSQL_USER=um542319
MYSQL_PASSWORD=...
MYSQL_DATABASE=um542319_db

# System
LOG_LEVEL=INFO
AUTO_SYNC_INTERVAL=3600
```

### GitHub Secrets

Встановіть у Settings > Secrets and variables > Actions:

- `DOCKER_HUB_USERNAME`
- `DOCKER_HUB_TOKEN`
- `PRODUCTION_HOST`
- `PRODUCTION_USER`
- `PRODUCTION_SSH_KEY`
- `CIMEIKA_API_URL`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHANNEL_ID`

## CI/CD Pipeline

### Автоматичне розгортання

При push до `main` гілки:

1. **Тестування**: Синтаксичні перевірки Python
2. **Збірка**: Docker образів
3. **Розгортання**: На production сервер
4. **Моніторинг**: Health check та повідомлення в Telegram

### Ручне розгортання

```bash
# Локальна збірка
docker-compose build

# Push до Docker Hub
docker-compose push

# Розгортання на сервері
ssh user@server "cd /opt/cimeika && docker-compose pull && docker-compose up -d"
```

## Моніторинг та підтримка

### Health Checks

```bash
# API health
curl http://localhost:8790/health

# Orchestrator tasks
curl http://localhost:8790/tasks

# System logs
docker-compose logs -f
```

### Автоматичне відновлення

- **Watchdog**: Перевіряє стан системи кожні 12 годин
- **Auto-restart**: При збоях автоматично перезапускає сервіси
- **Telegram notifications**: Повідомлення про стан системи

### Логи

```
logs/
├── autosync.log      # Синхронізація з Git
├── watchdog.log      # Моніторинг системи
├── health_report.json # Звіт стану
└── api.log          # API запити
```

## API Endpoints

### Основні

- `GET /health` — Стан системи
- `POST /chat` — Чат з Ci
- `GET /tasks` — Список активних задач
- `POST /task/<id>/run` — Виконати задачу

### Приклади використання

```bash
# Health check
curl http://localhost:8790/health

# Chat request
curl -X POST http://localhost:8790/chat \
  -H "Content-Type: application/json" \
  -d '{"input": "Привіт, як справи?"}'

# Get tasks
curl http://localhost:8790/tasks
```

## Інтеграції

### HuggingFace Space

Автоматична синхронізація з `Ihorog/Cimeika.com.ua`

### OpenAI

- GPT-4 для текстових відповідей
- Whisper для голосового введення

### Telegram Bots

- `@cimeika_bot` — основний бот
- `@cimeika_kazkar_bot` — генератор історій
- `@ci_channel` — канал повідомлень

## Troubleshooting

### Поширені проблеми

1. **Container не стартує**
   ```bash
   docker-compose logs <service_name>
   docker-compose restart <service_name>
   ```

2. **API не відповідає**
   ```bash
   curl -v http://localhost:8790/health
   docker-compose ps
   ```

3. **Проблеми з ключами API**
   - Перевірити .env файл
   - Перезапустити контейнери: `docker-compose restart`

4. **База даних недоступна**
   - Перевірити з'єднання з MySQL
   - Провірити credentials у .env

### Логи діагностики

```bash
# Всі логи
docker-compose logs

# Логи конкретного сервісу
docker-compose logs cimeika-api

# Слідкувати за логами
docker-compose logs -f cimeika-orchestrator
```

## Безпека

- Всі секрети зберігаються у GitHub Secrets
- API ключі не комітяться у репозиторій
- SSH доступ тільки по ключам
- Автоматичні security updates

## Підтримка

При проблемах:

1. Перевірити логи: `docker-compose logs`
2. Health check: `curl http://localhost:8790/health`
3. GitHub Issues: https://github.com/Ihorog/cimeika-ai-deploy/issues

---

**Розроблено**: CIMEIKA SYSTEM / Ci-in-CIT
**Версія**: 1.0.0
**Дата**: січень 2026