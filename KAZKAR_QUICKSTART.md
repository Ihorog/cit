# Казкар — Quick Start Guide

## Швидкий старт

### 1. Встановлення залежностей

```bash
cd /path/to/cit
pip install -e .
```

Або вручну:
```bash
pip install fastapi uvicorn pyyaml python-multipart
```

### 2. Запуск сервера

```bash
uvicorn api.main:app --reload
```

Або з параметрами:
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Відкрийте браузер

- **Головна сторінка**: http://localhost:8000/
- **Казкар UI**: http://localhost:8000/ui/kazkar/index.html
- **Легенда Сі**: http://localhost:8000/ui/kazkar/legenda.html
- **API Документація**: http://localhost:8000/docs

## Перше використання

### Через UI

1. Відкрийте http://localhost:8000/ui/kazkar/index.html
2. Натисніть "Активувати Казкар"
3. Натисніть "Увійти в Легенду" для доступу до Легенди Сі
4. Або створіть оповідь через "Плетіння Зв'язності"

### Через API

```bash
# Активувати Казкар
curl http://localhost:8000/api/kazkar/aktyvuvaty

# Увійти в Легенду Сі
curl http://localhost:8000/api/kazkar/legenda/aktyvuvaty

# Навігувати до вузла "Тиша"
curl http://localhost:8000/api/kazkar/legenda/navihuvaty/tysha

# Отримати всі архетипи
curl http://localhost:8000/api/kazkar/arkhetypy
```

### Через Python

```python
from zdibnosti.kazkar import Kazkar

# Ініціалізація
kazkar = Kazkar()

# Активація
kazkar.aktyvuvaty()

# Вхід у Легенду Сі
kazkar.uviyty_v_legendu()

# Навігація
kazkar.navihuvaty_po_legendi('tysha')

# Плетіння зв'язності
podiyi = ["Подія 1", "Подія 2", "Подія 3"]
opovid = kazkar.plesty_zv_yaznist(podiyi)
print(opovid)
```

## Структура проекту

```
cit/
├── core/                  # Базові модулі
│   ├── si.py             # Сі — центр присутності
│   ├── dzerkalo.py       # Дзеркало синхронізації
│   └── formatsiyi.py     # Базовий клас формацій
│
├── zdibnosti/kazkar/     # Казкар формація
│   ├── forma_opovidi.py  # Головний модуль
│   ├── prostir_legendy.py # Легенда Сі (10 вузлів)
│   ├── semantychnyi_graf.py # Семантичний граф
│   ├── dvyhun_arkhetypiv.py # 7 архетипів
│   └── opovidach.py      # Генератор оповідей
│
├── api/                  # FastAPI backend
│   ├── main.py          # Головний додаток
│   └── kazkar_routes.py # API endpoints
│
├── ui/kazkar/           # Інтерфейс користувача
│   ├── index.html       # Головна сторінка
│   ├── legenda.html     # Легенда Сі
│   ├── styli/          # CSS
│   └── skripty/        # JavaScript
│
├── dani/kazkar/         # Дані
│   ├── arkhetypy.yaml  # 7 архетипів
│   ├── semantychni_vuzly.json # 10 вузлів
│   └── legendy/        # Легенди
│
└── manifest.json        # Стан організму
```

## API Endpoints

### Казкар
- `GET /api/kazkar/aktyvuvaty` — активувати формацію
- `GET /api/kazkar/proyav` — отримати стан
- `POST /api/kazkar/plesty-zv-yaznist` — створити оповідь
- `GET /api/kazkar/arkhetypy` — отримати архетипи
- `GET /api/kazkar/opovidi/ostanni` — останні оповіді

### Легенда Сі
- `GET /api/kazkar/legenda/aktyvuvaty` — увійти в легенду
- `GET /api/kazkar/legenda/navihuvaty/{vuzol_id}` — навігувати
- `POST /api/kazkar/legenda/poshuk` — семантичний пошук
- `GET /api/kazkar/legenda/eksport` — експортувати граф

## 10 Вузлів Легенди Сі

**Глибина 0 (Центр):**
- **prysutnist** — Присутність

**Глибина 1:**
- **tysha** — Тиша
- **dostatnist** — Достатність
- **moment** — Момент

**Глибина 2:**
- **spokiy** — Спокій
- **pryynyattya** — Прийняття
- **chas** — Час

**Глибина 3:**
- **balans** — Баланс
- **mudrist** — Мудрість
- **tsykl** — Цикл

## 7 Архетипів

- 🚪 **Поріг** (porih) — початок, перехід
- ✨ **Творення** (tvorennya) — народження нового
- 🪞 **Рефлексія** (refleksiya) — осмислення
- 🔄 **Цикл** (tsykl) — повторення з трансформацією
- 🔗 **Зв'язок** (zv_yazok) — об'єднання
- 🧭 **Мандрівка** (mandrivka) — шлях, пошук
- 🦋 **Перетворення** (peretvorennya) — метаморфоза

## Усунення проблем

### Сервер не запускається

```bash
# Перевірте залежності
pip list | grep -E 'fastapi|uvicorn|pyyaml'

# Переустановіть
pip install --upgrade fastapi uvicorn pyyaml
```

### Помилка імпорту модулів

```bash
# Встановіть пакет в editable mode
pip install -e .

# Або додайте до PYTHONPATH
export PYTHONPATH=/path/to/cit:$PYTHONPATH
```

### Порт зайнятий

```bash
# Використайте інший порт
uvicorn api.main:app --port 8001
```

## Наступні кроки

1. Експериментуйте з навігацією по Легенді Сі
2. Створюйте оповіді через API
3. Досліджуйте архетипи та їх тригери
4. Інтегруйте з іншими частинами Cimeika екосистеми

---

Для детальної інформації див. [README.md](../README.md)
