# Cimeika Web Interface

**Cimeika** — це сучасний PWA (Progressive Web App) інтерфейс для CIT (Ci Interface Terminal), побудований на Next.js 15 та React 19.

## Особливості

- 🎨 **Темна тема** — елегантний темний інтерфейс (#0b0b0b)
- 📱 **PWA підтримка** — встановлюється як додаток на Android/iOS
- 🇺🇦 **Українська мова** — повністю локалізований інтерфейс
- 💬 **Інтелектуальний чат** — секція "Казкар" з повною інтеграцією CIT API:
  - 🎤 **STT** (Speech-to-Text) для української мови
  - 🔊 **TTS** (Text-to-Speech) автоозвучення відповідей
  - 📝 Зручний інтерфейс чату з історією
  - ⚡ Реал-тайм комунікація з AI
- 🎯 **Меню "Сімейка"** — швидкий доступ до секцій:
  - Казкар (AI чат)
  - ✨ Легенда Ci (ядро сенсів)
  - ПоДія (події)
  - Настрій (mood tracker)
  - Маля (творчість)
  - Календар (планування)
  - Галерея (медіа)
- 📐 **Responsive дизайн** — адаптується під будь-який розмір екрану
- ⚡ **Швидкий запуск** — оптимізовано для продуктивності

## Швидкий старт

### Локальна розробка

```bash
# Перейти в директорію web
cd web

# Встановити залежності
npm install

# Створити файл .env.local з налаштуваннями
cp .env.local.example .env.local

# Відредагувати .env.local та вказати URL CIT API
# NEXT_PUBLIC_CIT_API_URL=http://127.0.0.1:8790/chat

# Запустити dev сервер (порт 3000)
npm run dev
```

Відкрийте [http://localhost:3000](http://localhost:3000) у браузері.

### Налаштування CIT API

Для роботи чату потрібен запущений CIT сервер:

```bash
# У кореневій директорії проекту
export OPENAI_API_KEY=sk-...
python server/cit_server.py
```

Сервер запуститься на `http://127.0.0.1:8790`.

### Збірка для продакшену

```bash
# Створити production build
npm run build

# Запустити production сервер
npm start
```

## Deployment на Vercel

Репозиторій налаштований для **автоматичного deployment** на Vercel. Деплой відбувається без ручного налаштування Root Directory.

### Крок 1: Підготовка

1. Створіть акаунт на [vercel.com](https://vercel.com)
2. Встановіть Vercel CLI (опціонально):
   ```bash
   npm install -g vercel
   ```

### Крок 2: Автоматичний Deployment

### Крок 2.5: Налаштування змінних середовища

**ВАЖЛИВО**: Для роботи чату потрібно налаштувати змінні середовища:

1. У Vercel Dashboard → Ваш проект → Settings → Environment Variables
2. Додайте змінну:
   - **Name**: `NEXT_PUBLIC_CIT_API_URL`
   - **Value**: URL вашого CIT сервера (наприклад, `http://100.x.x.x:8790/chat` для Tailscale)
   - **Environment**: Production, Preview, Development

**Примітка**: Якщо ваш CIT сервер працює локально або в приватній мережі (Tailscale), веб-інтерфейс на Vercel не зможе до нього підключитися. У такому випадку розгляньте один з варіантів:
- Запускайте веб-інтерфейс локально (`npm run dev`)
- Розгорніть CIT сервер на публічному хості
- Використовуйте Tailscale Funnel для безпечного публічного доступу

### Крок 3: Deployment

#### Через Vercel Dashboard (рекомендовано)

1. Перейдіть на [vercel.com/new](https://vercel.com/new)
2. Імпортуйте ваш GitHub репозиторій `Ihorog/cit`
3. ✅ **НЕ ПОТРІБНО** налаштовувати Root Directory — все працює автоматично!
4. Натисніть **Deploy**

Vercel автоматично:
- Виявить Next.js застосунок у `web/` директорії
- Запустить build через `vercel.json` конфігурацію
- Налаштує правильні routes

#### Через CLI

```bash
# З кореневої директорії проєкту
vercel --prod
```

### Як це працює?

Репозиторій містить:
- `package.json` у корені з командою `vercel-build`
- `vercel.json` з правильною конфігурацією для Next.js у subdirectory
- Автоматичний routing на `web/` директорію

### Налаштування домену

Після успішного деплою ви можете:
1. Використовувати автоматичний домен Vercel: `your-project.vercel.app`
2. Налаштувати власний домен у Settings → Domains

## Заміна іконок PWA

### Вимоги до іконок

Для повноцінної PWA підтримки потрібні дві іконки:
- **192x192 пікселів** — для Android та загального використання
- **512x512 пікселів** — для splash screen та iOS

### Інструкція

1. **Підготуйте ваші іконки**:
   - Формат: PNG з прозорим фоном або квадратним кольоровим
   - Розміри: 192x192 та 512x512 пікселів
   - Рекомендація: використовуйте логотип Ci або Cimeika

2. **Замініть файли**:
   ```bash
   # Замініть існуючі placeholder іконки
   cp your-icon-192.png web/public/icons/icon-192.png
   cp your-icon-512.png web/public/icons/icon-512.png
   ```

3. **Перевірте результат**:
   ```bash
   npm run dev
   ```
   
   Відкрийте DevTools → Application → Manifest і перевірте іконки.

### Генерація іконок

Якщо у вас є тільки одна велика іконка (наприклад, 1024x1024), використайте:

**Онлайн інструменти**:
- [favicon.io](https://favicon.io/) — генерує всі розміри
- [realfavicongenerator.net](https://realfavicongenerator.net/) — детальна настройка

**CLI інструмент**:
```bash
# Використайте ImageMagick
convert your-icon.png -resize 192x192 web/public/icons/icon-192.png
convert your-icon.png -resize 512x512 web/public/icons/icon-512.png
```

## Структура проєкту

```
web/
├── package.json              # Налаштування npm
├── next.config.js            # Конфігурація Next.js
├── README_WEB.md             # Ця документація
├── public/
│   ├── manifest.json         # PWA manifest
│   └── icons/
│       ├── icon-192.png      # Іконка 192x192
│       └── icon-512.png      # Іконка 512x512
└── src/
    ├── app/
    │   ├── layout.tsx        # Root layout з metadata
    │   └── page.tsx          # Головна сторінка
    ├── components/
    │   ├── AppShell.tsx          # Головний компонент UI з меню
    │   ├── AppShell.module.css   # Стилі AppShell
    │   ├── ChatInterface.tsx     # Компонент чату з STT/TTS
    │   └── ChatInterface.module.css  # Стилі чату
    └── styles/
        └── globals.css       # Глобальні стилі
```

## Технології

- **Next.js 15.1.4** — React framework з App Router
- **React 19.0.0** — UI бібліотека
- **TypeScript** — типізований JavaScript
- **CSS Modules** — локальні стилі компонентів
- **PWA** — Progressive Web App можливості

## Розробка

### Функціональність чату

Компонент `ChatInterface` надає повноцінний чат-інтерфейс:

- **Підключення до CIT сервера**: автоматично підключається до `http://127.0.0.1:8790`
- **Моніторинг здоров'я**: відображає статус підключення кожні 4 секунди
- **Відправка повідомлень**: POST запити до `/chat` з автоматичним відображенням відповідей
- **STT (Speech-to-Text)**: голосове введення українською мовою через Web Speech API
- **TTS (Text-to-Speech)**: озвучування відповідей асистента
- **Історія чату**: зберігається локально в компоненті (очищається при перезавантаженні)

### Конфігурація API endpoint

За замовчуванням чат підключається до `http://127.0.0.1:8790`. Для зміни адреси:

```typescript
// В AppShell.tsx
<ChatInterface apiEndpoint="http://your-server:8790" />
```

### Додавання нової секції до меню

Відкрийте `src/components/AppShell.tsx` та додайте елемент до масиву `menuItems`:

```typescript
const menuItems = useMemo<MenuItem[]>(() => [
  // ... існуючі пункти
  { id: 'new-section', label: 'Нова Секція' },
], [])
```

Потім додайте відповідний випадок у render секції:

```typescript
{activeSection === 'Нова Секція' && <ChatInterface />}
// або
{activeSection === 'Нова Секція' && (
  <div className={styles.placeholder}>
    <h2>Нова Секція</h2>
    <p>Опис секції</p>
  </div>
)}
```

### Зміна теми

Основний колір теми (`#0b0b0b`) визначено в:
- `src/styles/globals.css` — body background
- `src/components/AppShell.module.css` — компонент стилі
- `src/app/layout.tsx` — viewport themeColor
- `public/manifest.json` — PWA theme

Для зміни кольору оновіть усі ці файли.

### Hot Module Replacement (HMR)

Next.js автоматично перезавантажує сторінку при змінах у коді:
- Зміни в `.tsx` файлах — миттєве оновлення
- Зміни в `.css` файлах — миттєве оновлення
- Зміни в `layout.tsx` — потрібне перезавантаження сторінки

## Troubleshooting

### Vercel Deployment не працює

**Проблема:** Білий екран або помилка "404: NOT_FOUND"

**Рішення:**
1. ✅ З новою конфігурацією (`vercel.json` + root `package.json`) деплой має працювати автоматично
2. Якщо проблема залишається:
   - Перевірте Vercel build logs у Dashboard → Deployments → [ваш deployment] → Building
   - Переконайтесь що білд завершився успішно
3. Якщо білд падає:
   - Перейдіть у Deployments
   - Натисніть "Redeploy" на останньому деплої

**Проблема:** Build fails або "Command not found"

**Рішення:**
1. Перевірте що у корені репозиторію є:
   - `package.json` з командою `vercel-build`
   - `vercel.json` з правильною конфігурацією
2. Спробуйте локально: `npm run vercel-build` (з кореневої директорії)
3. Якщо локально працює, а на Vercel ні — Redeploy

### Порт 3000 зайнятий

```bash
# Використайте інший порт
npm run dev -- -p 3001
```

### Помилки TypeScript

```bash
# Очистіть кеш та перебудуйте
rm -rf .next node_modules
npm install
npm run dev
```

### PWA не встановлюється

1. Перевірте, що сайт працює через HTTPS (Vercel автоматично надає SSL)
2. Відкрийте DevTools → Application → Manifest
3. Перевірте консоль на помилки

## Ліцензія

Цей проєкт є частиною CIT (Ci Interface Terminal) та використовує MIT ліцензію.

## Підтримка

Для питань та звіту про баги відкрийте issue в [GitHub репозиторії](https://github.com/Ihorog/cit).
