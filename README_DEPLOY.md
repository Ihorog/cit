# 🚀 Інструкція з розгортання Cimeika / Ci

## Огляд системи

**Cimeika (Ci)** — це інтелектуальна екосистема з веб-інтерфейсом та API для оркестрації модулів:
- **Казкар** — голосовий чат-асистент з AI
- **ПоДія** — планувальник подій
- **Настрій** — емоційний аналітик
- **Маля** — творчий модуль
- **Галерея** — медіа-менеджер

## 📦 Структура проєкту

```
/vercel/sandbox/
├── web/                    # Next.js PWA інтерфейс
│   ├── src/
│   │   ├── app/           # Next.js App Router
│   │   ├── components/    # React компоненти
│   │   └── styles/        # CSS стилі
│   ├── public/            # Статичні файли
│   ├── package.json       # Залежності
│   ├── vercel.json        # Конфігурація Vercel для Next.js
│   └── next.config.mjs    # Конфігурація Next.js
├── server/                # Python API сервер
│   └── cit_server.py      # HTTP сервер для OpenAI
├── ui/                    # Альтернативний HTML/JS UI
└── package.json           # Root package.json
```

## 🛠️ Технології

### Frontend (Web UI)
- **Next.js 14.1.0** — React фреймворк з SSG/SSR
- **React 18.2.0** — UI бібліотека
- **TypeScript** — типізація
- **CSS Modules** — стилізація компонентів
- **PWA** — Progressive Web App підтримка

### Backend (API)
- **Python 3.10+** — мова програмування
- **HTTP Server** — вбудований http.server
- **OpenAI API** — інтеграція з GPT-4

### Інтеграції
- **Hugging Face** — ML моделі
- **GitHub Actions** — CI/CD
- **Vercel** — хостинг frontend
- **Telegram Bots** — @cimeika_bot, @cimeika_kazkar_bot

## 📋 Вимоги

### Локальна розробка
- Node.js ≥ 20.x (рекомендовано 20.19.0 або новіше)
- npm або yarn
- Python ≥ 3.10
- Git

### Production
- Vercel акаунт (для frontend)
- OpenAI API ключ
- (Опціонально) Hugging Face токен

## 🚀 Швидкий старт

### 1. Клонування репозиторію

```bash
git clone https://github.com/Ihorog/cit.git
cd cit
```

### 2. Налаштування змінних середовища

Створіть `.env.local` у директорії `web/`:

```bash
cd web
cp .env.local.example .env.local
```

Відредагуйте `.env.local`:

```env
# CIT API Endpoint
# Для локальної розробки:
NEXT_PUBLIC_CIT_API_URL=http://127.0.0.1:8790/chat

# Для production (замініть на ваш домен):
# NEXT_PUBLIC_CIT_API_URL=https://your-api-server.com/chat
```

### 3. Встановлення залежностей

```bash
# У директорії web/
npm install
```

### 4. Запуск у режимі розробки

#### Варіант A: Тільки Frontend (без API)

```bash
cd web
npm run dev
```

Відкрийте http://localhost:3000

#### Варіант B: Frontend + Backend API

**Термінал 1 — API сервер:**
```bash
# Експортуйте OpenAI ключ
export OPENAI_API_KEY="your-api-key-here"

# Запустіть Python API
python server/cit_server.py
# API буде доступний на http://127.0.0.1:8790
```

**Термінал 2 — Web UI:**
```bash
cd web
npm run dev
# UI буде доступний на http://localhost:3000
```

### 5. Збірка для production

```bash
cd web
npm run build
npm start
```

## 🌐 Розгортання на Vercel

### Автоматичне розгортання (рекомендовано)

1. **Підключіть репозиторій до Vercel:**
   - Зайдіть на https://vercel.com
   - Натисніть "Import Project"
   - Виберіть GitHub репозиторій `Ihorog/cit`

2. **Налаштуйте змінні середовища:**
   - У Vercel Dashboard → Settings → Environment Variables
   - Додайте:
     ```
     NEXT_PUBLIC_CIT_API_URL=https://your-api-server.com/chat
     ```

3. **Розгорніть:**
   - Vercel автоматично розгорне при push до `main`
   - Preview URL створюється для кожного PR

### Ручне розгортання

```bash
# Встановіть Vercel CLI
npm install -g vercel

# Увійдіть
vercel login

# Розгорніть
vercel --prod
```

## 🔧 Конфігурація

### Структура Vercel

Проєкт використовує монорепо структуру з Next.js додатком у директорії `web/`.

**Важливо:** При налаштуванні проєкту на Vercel:
- Встановіть **Root Directory** на `web` у налаштуваннях проєкту
- Або використовуйте Vercel CLI з `web/` як робочою директорією (як у CI/CD workflow)

Конфігурація фреймворку знаходиться в `web/vercel.json`:

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "framework": "nextjs"
}
```

**Примітка:** Кореневий `vercel.json` був видалений, оскільки використовував застарілий синтаксис `builds`, що викликав попередження. Сучасний підхід Vercel - налаштовувати Root Directory безпосередньо в проєкті або через CLI.

### next.config.mjs

```javascript
const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
}

export default nextConfig
```

## 🧪 Тестування

### Перевірка збірки

```bash
cd web
npm run build
```

Очікуваний результат:
```
✓ Compiled successfully
✓ Generating static pages (4/4)
✓ Finalizing page optimization
```

### Тестування API

```bash
# Перевірка health endpoint
curl http://127.0.0.1:8790/health

# Тест chat endpoint
curl -X POST http://127.0.0.1:8790/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Привіт!"}'
```

## 📱 PWA Features

Веб-додаток підтримує Progressive Web App функції:

- ✅ Встановлення на домашній екран
- ✅ Офлайн підтримка (Service Worker)
- ✅ Адаптивний дизайн
- ✅ Темна тема
- ✅ Голосовий ввід (STT)
- ✅ Голосовий вивід (TTS)

### Manifest

Файл `public/manifest.json` містить метадані PWA:

```json
{
  "name": "Cimeika",
  "short_name": "Cimeika",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#0b0b0b",
  "theme_color": "#0b0b0b",
  "icons": [...]
}
```

## 🔐 Безпека

### Змінні середовища

**НІКОЛИ** не комітьте файли з секретами:
- `.env.local`
- `.env.production`
- Файли з API ключами

### CORS

API сервер повинен дозволяти запити з вашого frontend домену:

```python
# У cit_server.py
headers = {
    'Access-Control-Allow-Origin': 'https://your-frontend-domain.vercel.app',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
}
```

## 🐛 Troubleshooting

### Проблема: "Module not found"

```bash
cd web
rm -rf node_modules package-lock.json
npm install
```

### Проблема: "API connection failed"

1. Перевірте, чи запущений API сервер:
   ```bash
   curl http://127.0.0.1:8790/health
   ```

2. Перевірте CORS налаштування

3. Перевірте змінну `NEXT_PUBLIC_CIT_API_URL`

### Проблема: "Build failed on Vercel"

1. Перевірте логи у Vercel Dashboard
2. Переконайтеся, що Root Directory встановлено на `web` у налаштуваннях проєкту Vercel
3. Перевірте, що всі залежності у `web/package.json` коректні
4. Перевірте конфігурацію у `web/vercel.json`

### Проблема: "Speech recognition not working"

- STT працює тільки в HTTPS або localhost
- Перевірте дозволи браузера для мікрофону
- Підтримується тільки в Chrome/Edge

## 📊 Моніторинг

### Health Check

```bash
# API health
curl http://127.0.0.1:8790/health

# Очікувана відповідь:
{
  "ok": true,
  "model": "gpt-4o-mini",
  "ts": "2026-01-06T17:00:00.000000+00:00"
}
```

### Логи

```bash
# API логи
tail -f .api.auto.log

# UI логи
tail -f .ui.auto.log
```

## 🔄 CI/CD Pipeline

### GitHub Actions

Workflow файл `.github/workflows/vercel-deploy.yml` автоматично розгортає проєкт на Vercel при кожному push до `main` або створенні PR.

#### Необхідні GitHub Secrets

Додайте наступний секрет в Settings → Secrets and variables → Actions:

- **VERCEL_TOKEN** — токен доступу до Vercel (отримайте в https://vercel.com/account/tokens)

**Примітка:** Новіша версія Vercel CLI автоматично визначає проект через конфігурацію в `web/vercel.json` та проект на Vercel Dashboard, тому `VERCEL_ORG_ID` та `VERCEL_PROJECT_ID` більше не потрібні.

#### Як отримати Vercel токен:

1. Зайдіть на https://vercel.com/account/tokens
2. Створіть новий токен з назвою "GitHub Actions"
3. Скопіюйте токен і додайте його як `VERCEL_TOKEN` в GitHub Secrets

#### Workflow конфігурація:

```yaml
name: Vercel Deployment
on:
  push:
    branches: [main]
    paths: ['web/**']
  pull_request:
    branches: [main]
    paths: ['web/**']
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: 'web/package-lock.json'
      - run: npm install -g vercel@latest
      - working-directory: ./web
        run: vercel pull --yes --environment=preview --token=${{ secrets.VERCEL_TOKEN }}
      - working-directory: ./web
        run: vercel build --token=${{ secrets.VERCEL_TOKEN }}
      - working-directory: ./web
        run: vercel deploy --prebuilt --prod --token=${{ secrets.VERCEL_TOKEN }}
```

## 📚 Додаткові ресурси

- [Next.js Documentation](https://nextjs.org/docs)
- [Vercel Documentation](https://vercel.com/docs)
- [React Documentation](https://react.dev)
- [OpenAI API Reference](https://platform.openai.com/docs)

## 🤝 Підтримка

- **GitHub Issues:** https://github.com/Ihorog/cit/issues
- **Telegram:** @ci_chanal
- **Email:** support@cimeika.com.ua

## 📄 Ліцензія

MIT License — див. файл `LICENSE`

---

**Статус:** ✅ Готово до розгортання  
**Розробник:** CIMEIKA SYSTEM / Ci-in-CIT  
**Дата:** 6 січня 2026  
**Версія:** 1.0.0
