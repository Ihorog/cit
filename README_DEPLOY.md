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
│   └── next.config.cjs    # Конфігурація Next.js
├── server/                # Python API сервер
│   └── cit_server.py      # HTTP сервер для OpenAI
├── ui/                    # Альтернативний HTML/JS UI
├── vercel.json            # Конфігурація Vercel
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
- Node.js ≥ 22.x
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
export OPENAI_API_KEY=sk-your-key-here

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

### vercel.json

```json
{
  "builds": [
    {
      "src": "web/package.json",
      "use": "@vercel/next"
    }
  ],
  "routes": [
    {
      "src": "/(_next|static)(.*)",
      "dest": "web/$0"
    },
    {
      "src": "/(favicon.ico|manifest.json|icons/.*)",
      "dest": "web/$0"
    },
    {
      "src": "/(.*)",
      "dest": "web/$1"
    }
  ]
}
```

### next.config.cjs

```javascript
const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
}

module.exports = nextConfig
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
2. Переконайтеся, що `vercel.json` правильно налаштований
3. Перевірте, що всі залежності у `package.json`

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

Workflow файл `.github/workflows/vercel-deploy.yml`:

```yaml
name: Vercel Deployment
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '22'
      - run: cd web && npm install
      - run: cd web && npm run build
      - uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
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
