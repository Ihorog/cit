# 🎨 CIMEIKA Brand Guidelines

## Загальні принципи

CIMEIKA — це екосистема, де кожна формація має офіційну українську назву.
Всі компоненти коду, бази даних, UI та API повинні відповідати цим стандартам.

---

## 📋 Офіційні назви формацій

| Формація | Код (folders/imports) | UI (display) | Database enum |
|----------|----------------------|--------------|---------------|
| ПоДія    | `podiya`             | `ПоДія`      | `podiya`      |
| Настрій  | `nastriy`            | `Настрій`    | `nastriy`     |
| Казкар   | `kazkar`             | `Казкар`     | `kazkar`      |
| Маля     | `malya`              | `Маля`       | `malya`       |
| Галерея  | `galereya`           | `Галерея`    | `galereya`    |
| Календар | `kalendar`           | `Календар`   | `kalendar`    |
| Сі       | `si`                 | `Сі`         | `si`          |

---

## ❌ Заборонені форми (deprecated)

| Неправильно | Правильно (код) | Правильно (UI) |
|-------------|-----------------|----------------|
| `podija`    | `podiya`        | `ПоДія`        |
| `nastrij`   | `nastriy`       | `Настрій`      |
| `gallery`   | `galereya`      | `Галерея`      |
| `calendar`  | `kalendar`      | `Календар`     |

---

## 📁 Структура директорій

```
modules/
├── podiya/       # ✅ (не podija/)
├── nastriy/      # ✅ (не nastrij/)
├── kazkar/       # ✅
├── malya/        # ✅
├── galereya/     # ✅ (не gallery/)
├── kalendar/     # ✅ (не calendar/)
└── si/           # ✅
```

---

## 🔗 API Routes

```
/api/podiya/      # ✅ (не /api/podija/)
/api/nastriy/     # ✅ (не /api/nastrij/)
/api/galereya/    # ✅ (не /api/gallery/)
/api/kalendar/    # ✅ (не /api/calendar/)
```

---

## 🗄️ Database Enums

```sql
CREATE TYPE persona_type AS ENUM (
    'podiya',     -- ✅ (не 'podija')
    'nastriy',    -- ✅ (не 'nastrij')
    'kazkar',
    'malya',
    'galereya',   -- ✅ (не 'gallery')
    'kalendar',   -- ✅ (не 'calendar')
    'si'
);
```

---

## 🖥️ UI Display Rules

- Завжди використовувати **українські назви** у відображенні для користувача
- Ніколи не показувати транслітеровані назви (podiya, nastriy) в UI
- Використовувати офіційний регістр: **ПоДія** (не Подія)

---

## 🔍 Автоматизована перевірка

Для перевірки відповідності запустіть:

```bash
python brand_compliance_scanner.py
```

Звіт буде збережено у `BRAND_COMPLIANCE_REPORT.md`.

---

## 📜 Міграція

Для автоматичної міграції застарілих назв:

```bash
# 1. Сканування
python brand_compliance_scanner.py

# 2. Перегляд звіту
cat BRAND_COMPLIANCE_REPORT.md

# 3. Міграція (перегляньте перед запуском!)
./migrate_brand_compliance.sh

# 4. Тести
python -m pytest tests/ -v
```
