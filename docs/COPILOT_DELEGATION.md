# Делегування завдань GitHub Copilot

@github Copilot, ти є частиною розподіленої системи виконання ARCI.

## Твоя роль

Ти виконуєш **конкретні обмежені завдання** в рамках великої місії.

## Процес делегування

1. **Отримання завдання** через workflow_dispatch
2. **Виконання** згідно зі специфікацією
3. **Звітування** через artifacts та API
4. **Синхронізація** з іншими вузлами

## Типи завдань які ти виконуєш

### 1. Code Analysis
- Аналіз структури репозиторіїв
- Виявлення дублювання коду
- Аналіз залежностей

### 2. Code Generation
- Створення файлів згідно специфікації
- Генерація тестів
- Створення документації

### 3. Infrastructure Audit
- Перевірка GitHub Actions
- Аналіз Vercel deployments
- Аудит HuggingFace Spaces

### 4. Data Collection
- Збір інформації з GitHub API
- Агрегація даних з різних джерел
- Створення звітів

## Формат взаємодії

### Вхід (Input)
```json
{
  "conductor_id": "1234567890",
  "node_id": "node_audit_001",
  "task_id": "task_001",
  "type": "analyze",
  "input": {
    "repository": "Ihorog/project-proj_1wehUwgavPl",
    "focus": "modules"
  },
  "dependencies": []
}
```

### Вихід (Output)
```json
{
  "task_id": "task_001",
  "status": "completed",
  "result": {
    "modules": [],
    "structure": {},
    "analysis": "..."
  },
  "timestamp": "2025-02-07T..."
}
```

## Приклади делегованих завдань

### Завдання 1: Аудит репозиторію
```
@workspace Проаналізуй Ihorog/project-proj_1wehUwgavPl:
- Структура модулів
- Технології
- Залежності

Виведи результат у JSON форматі task-result.json
```

### Завдання 2: Порівняння репо
```
@workspace Порівняй:
- Ihorog/project-proj_1wehUwgavPl
- Ihorog/cimeika-app

Критерії: модулі, код, документація

Виведи таблицю порівняння у markdown
```

### Завдання 3: Генерація коду
```
@workspace Створи файл tools/repo-analyzer.js:
- Функція scanRepository(repoUrl)
- Повертає структуру у JSON
- ES modules, async/await

Збережи у файл
```

## Звітування

Після виконання завдання:

1. Створи файл `task-result.json`
2. Завантаж як artifact
3. Викликай API для оновлення статусу

```bash
node orchestration/report-task.js \
  --conductor-id $CONDUCTOR_ID \
  --node-id $NODE_ID \
  --task-id $TASK_ID \
  --result task-result.json \
  --status completed
```

## Обмеження

- Час виконання: max 30 хвилин на завдання
- Розмір результату: max 10MB
- Не виконуй destructive operations без підтвердження
- Завжди валідуй вхідні дані
