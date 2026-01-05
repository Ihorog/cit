# 🚀 Автоматичне розгортання на Vercel

Цей гайд допоможе налаштувати повністю автоматичний deployment веб-інтерфейсу CIT на Vercel через GitHub Actions.

## 📋 Передумови

- Акаунт на [Vercel](https://vercel.com)
- Репозиторій підключений до GitHub
- Права адміністратора репозиторію

## 🔧 Крок 1: Отримання Vercel токену

1. Перейдіть на [Vercel Dashboard](https://vercel.com/account/tokens)
2. Натисніть **"Create Token"**
3. Введіть назву: `GitHub Actions CI`
4. Виберіть Scope: **Full Account**
5. Скопіюйте згенерований токен (показується тільки один раз!)

## 🔑 Крок 2: Додавання секретів в GitHub

1. Перейдіть у налаштування репозиторію: `Settings` → `Secrets and variables` → `Actions`
2. Натисніть **"New repository secret"**
3. Додайте наступні секрети:

### VERCEL_TOKEN
- **Name:** `VERCEL_TOKEN`
- **Value:** токен з Кроку 1

### VERCEL_ORG_ID (опціонально для команд)
- **Name:** `VERCEL_ORG_ID`
- **Value:** ID вашої організації Vercel

### VERCEL_PROJECT_ID
- **Name:** `VERCEL_PROJECT_ID`
- **Value:** ID проекту Vercel

#### Як знайти Project ID:
```bash
# Встановіть Vercel CLI
npm i -g vercel

# Авторизуйтесь
vercel login

# З кореневої директорії репозиторію
vercel link

# ID будуть збережені в .vercel/project.json
cat .vercel/project.json
```

## 🎯 Крок 3: Налаштування змінних оточення в Vercel

1. Перейдіть на [Vercel Dashboard](https://vercel.com/dashboard)
2. Виберіть ваш проект
3. `Settings` → `Environment Variables`
4. Додайте змінну:
   - **Name:** `NEXT_PUBLIC_CIT_API_URL`
   - **Value:** URL вашого CIT API (наприклад: `https://your-api.example.com/chat`)
   - **Environment:** Production, Preview, Development

## ✅ Крок 4: Перевірка автоматизації

### Автоматичний деплой на Production:
```bash
git add .
git commit -m "feat: update UI"
git push origin main
```

Перейдіть у вкладку **Actions** GitHub репозиторію та спостерігайте за процесом деплою.

### Автоматичний деплой Preview для PR:
```bash
git checkout -b feature/new-ui
# Внесіть зміни
git commit -m "feat: add new feature"
git push origin feature/new-ui
```

Створіть Pull Request — бот автоматично додасть коментар з посиланням на preview deployment.

## 🔄 Як це працює

1. **Push до main** → Production deployment на Vercel
2. **Pull Request** → Preview deployment з унікальним URL
3. **Manual trigger** → Можна запустити деплой вручну через вкладку Actions

## 🛠️ Troubleshooting

### Помилка: "VERCEL_TOKEN not found"
- Перевірте що секрет `VERCEL_TOKEN` додано в налаштуваннях репозиторію
- Секрет має бути у розділі **Actions**, а не **Dependabot**

### Помилка: "Project not found"
- Переконайтесь що проект існує на Vercel
- Перевірте `VERCEL_PROJECT_ID` (якщо використовується)

### Deployment не запускається
- Перевірте що зміни внесені у директорію `web/` або файли `vercel.json`/`package.json`
- Workflow запускається тільки при змінах цих файлів

## 📚 Додаткові ресурси

- [Vercel CLI документація](https://vercel.com/docs/cli)
- [GitHub Actions Vercel Integration](https://vercel.com/guides/how-can-i-use-github-actions-with-vercel)
- [Next.js Deployment на Vercel](https://nextjs.org/docs/deployment)
