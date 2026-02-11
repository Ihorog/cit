<p align="center">
  <img src="https://raw.githubusercontent.com/Ihorog/cit/main/ui/icons/icon-512.png" alt="CIT Logo" width="180" />
</p>

# CIT (Ci Interface Terminal)

[![Vercel Deployment](https://github.com/Ihorog/cit/actions/workflows/vercel-deploy.yml/badge.svg)](https://github.com/Ihorog/cit/actions/workflows/vercel-deploy.yml)
[![Unified CIT](https://github.com/Ihorog/cit/actions/workflows/cit-unified.yml/badge.svg)](https://github.com/Ihorog/cit/actions/workflows/cit-unified.yml)

**Version:** 2.1.0 (Final Release) 🏁

CIT (Ci Interface Terminal) is a lightweight API gateway that sits between your Cimeika devices and the OpenAI API.  
It exposes a minimal HTTP interface and forwards chat requests to OpenAI using Python's standard library.  
The service is designed to run locally on Android through Termux and can be connected to other systems over a LAN.

> **🧬 Unified Architecture:** CIT now serves as the core of a modular ecosystem that unifies 5 repositories (`cit`, `ciwiki`, `cimeika-unified`, `media`, `cit_versel`) following the **111 density principle** (1 core, 1 registry, 1 entry point). See [Unification Documentation](docs/UNIFICATION.md) for details.

> **🆕 v2.1 Features:** Autonomous OpenAI client, enhanced Job Manager, memory optimization (~80MB vs ~150MB), and complete API documentation. See [Release Notes](docs/RELEASE_v2.1.md) for details.

> **Note:** For conceptual understanding of Ci and its underlying framework, see the [Legend Ci documentation](LEGEND_CI.md) (canonical source: [ciwiki/Legend ci](https://github.com/Ihorog/ciwiki/tree/main/Legend%20ci)). This README focuses on technical implementation.

## Features

### Core (v2.1)
* **Autonomous OpenAI Client** – Standalone `OpenAIClient` class for programmatic API access with intelligent routing
* **Job Management System** – Create and track long-running tasks via `/v1/jobs/*` endpoints
* **Memory Optimized** – ~80MB memory usage (47% reduction from v2.0) through streaming multipart parsing
* **Audit System** – Comprehensive logging and monitoring of resources, API requests, and security (see [Audit Documentation](docs/AUDIT.md))

### API Endpoints
* **Health check** – `GET /health` returns a simple JSON object to verify the service is running.  
* **Web UI** – `GET /ui` (or `/`) provides a browser-based chat interface with Speech-to-Text (STT) and Text-to-Speech (TTS) support.
* **Chat proxy** – `POST /chat` forwards your chat messages to OpenAI and returns the response.  
* **Intelligent API routing** – uses OpenAI's Responses API with automatic fallback to Chat Completions API.
* **File operations** – Upload, download, and manage files via `/files`, `/file`, `/upload` endpoints
* **Configuration** – Runtime configuration via `/config` endpoint
* **Audit** – `GET /audit` and `GET /audit/resources` provide comprehensive system auditing (see [Audit Documentation](docs/AUDIT.md))

### Technical
* **No external dependencies** – implemented with Python's built‑in modules, so it works out of the box in Termux.  
* **Simple deployment** – start the server with a single script or integrate it into Termux Boot for auto‑start.

## Quick start in Termux

Follow these three steps to install and run CIT on your Android device using Termux:

1. **Install Termux packages**
   ```bash
   pkg update -y && pkg upgrade -y
   pkg install -y git python termux-services
   ```

2. **Clone the repository**
   ```bash
   git clone https://github.com/Ihorog/cit.git ~/cit
   cd ~/cit
   ```

3. **Run the server**
   ```bash
   # Export your OpenAI API key (required)
   export OPENAI_API_KEY="your-api-key-here"
   # Optional: Export your HuggingFace token for ML model access
   export HUGGINGFACE_API_TOKEN="your-token-here"
   # Start the server on port 8790
   python server/cit_server.py
   ```

The service will listen on all interfaces (port `8790` by default).  
You can add the start command to `scripts/termux_boot/cit_start.sh` and enable Termux Boot to run CIT automatically after a reboot.

Access the Web UI at `http://127.0.0.1:8790/ui` in your browser to use the chat interface with voice capabilities.

## Modular Engine

CIT now includes a modular engine that unifies multiple repositories into a single system. Use the engine CLI for advanced operations:

### Build & Validate
```bash
# Validate all modules and their dependencies
python core/engine.py build
```

### Run Server
```bash
# Start the HTTP server (alternative to python ci.py)
python core/engine.py run
```

### Module Management
```bash
# Run a specific module
python core/engine.py module <module-id>

# Show system status
python core/engine.py status
```

For detailed information about the modular architecture, see [Unification Documentation](docs/UNIFICATION.md).

## Example requests

### Web UI

Open your browser and navigate to:
```
http://127.0.0.1:8790/ui
```

The Web UI provides:
- Text input with "Send" button
- 🎙️ STT button for voice input (Ukrainian language)
- 🔊 TTS button to hear the assistant's response
- Real-time health status indicator
- Dark theme optimized for mobile

### API Endpoints

Check that CIT is running:

```bash
curl http://127.0.0.1:8790/health
# → {"ok": true, "model": "gpt-4o-mini", "ts": "2026-01-01T22:04:59.584648+00:00"}
```

Send a chat message to OpenAI via CIT:

```bash
curl -X POST http://127.0.0.1:8790/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello, world!"}'

# Example response:
# {
#   "reply": "Hello! How can I assist you today?",
#   "api": "chat.completions",
#   "raw": {
#     "id": "chatcmpl-abc123",
#     "object": "chat.completion",
#     "created": 1735756800,
#     "model": "gpt-4.1-mini",
#     "choices": [
#       {
#         "index": 0,
#         "message": {
#           "role": "assistant",
#           "content": "Hello! How can I assist you today?"
#         },
#         "finish_reason": "stop"
#       }
#     ]
#   }
# }
```

Or open the Web UI in your browser:

```bash
# Open http://127.0.0.1:8790/ui in your browser
# Features:
# - Interactive chat interface
# - 🎙️ Speech-to-Text (STT) for voice input
# - 🔊 Text-to-Speech (TTS) to hear responses
# - Dark theme optimized for mobile
```

## Repository check

Run a lightweight repo verification (syntax + /health probe) without external dependencies:

```bash
./scripts/repo_check.sh
```

The script starts a temporary server on port `8979` by default. Set `OPENAI_API_KEY` if you want to include the `/chat` smoke test.

## Repository layout

```
cit/
├── README.md             # this file
├── .gitignore            # common ignores (.env, Python cache)
├── docs/
│   └── ARCHITECTURE.md   # high‑level architecture description
├── server/
│   └── cit_server.py     # main HTTP server implementation
└── scripts/
    ├── termux_bootstrap.sh    # optional helper to set up Termux environment
    └── termux_boot/cit_start.sh # script run by Termux Boot
```

> **Note:** Operational scripts have been organized into `scripts/ops/` and vault/sync scripts into `scripts/vault/`. See README files in those directories for details.

## Web Interface (Cimeika)

In addition to the embedded UI served by the CIT server, there's a modern **Next.js PWA** interface called **Cimeika** in the `/web` directory.

**Features:**
- 🎨 Beautiful dark theme optimized for mobile
- 💬 Full-featured chat interface with AI
- 🎙️ Speech-to-Text (Ukrainian)
- 🔊 Text-to-Speech (Ukrainian)  
- 📱 PWA support (install as app)
- 🎯 Menu system with multiple sections
- 📊 Real-time health monitoring

**Quick start:**
```bash
# Start CIT server (required)
export OPENAI_API_KEY="your-api-key-here"
python server/cit_server.py

# In another terminal, start web app
cd web
npm install
npm run dev
# Open http://localhost:3000
```

See [`web/README_WEB.md`](web/README_WEB.md) for detailed documentation, deployment guides, and PWA setup.

## 🚀 Автоматичне розгортання

Веб-інтерфейс автоматично розгортається на Vercel при кожному push до `main` гілки.

### Швидкий старт

1. **Налаштуйте Vercel токени** — див. [docs/VERCEL_SETUP.md](docs/VERCEL_SETUP.md)
2. **Push код** — деплой відбудеться автоматично
3. **Створіть PR** — отримаєте preview URL для тестування

### Локальне тестування

```bash
# Перевірити що збірка працює
./scripts/test-vercel-deploy.sh

# Деплой вручну (потрібен Vercel CLI)
npm install -g vercel
vercel --prod
```

Детальна документація: [docs/VERCEL_SETUP.md](docs/VERCEL_SETUP.md)

## Copilot

GitHub Copilot development follows the canonical instructions defined in the [ciwiki repository](https://github.com/Ihorog/ciwiki/blob/main/.github/copilot-instructions.md).

Key principles:
- Anti-repeat: eliminate repeated actions
- Single execution path through PR → verification → approval
- Documentation first

See [.github/copilot-instructions.md](.github/copilot-instructions.md) for the full instructions synchronized from ciwiki.

## Development Process

### Implementation Proposals

For significant features or architectural changes, CIT uses a structured proposal process:

1. **Create Proposal** - Use the [implementation proposal template](docs/IMPLEMENTATION_PROPOSAL_TEMPLATE.md)
2. **Review** - Submit PR for team review and feedback
3. **Implement** - Build according to the approved proposal
4. **Verify** - Test against acceptance criteria
5. **Document** - Update CHANGELOG and documentation

**Quick start:**
```bash
# Create a new proposal
cp docs/IMPLEMENTATION_PROPOSAL_TEMPLATE.md docs/proposals/IMPL-$(date +%Y-%m-%d)-my-feature.md

# Edit the proposal and submit for review
git checkout -b proposal/my-feature
git add docs/proposals/IMPL-*-my-feature.md
git commit -m "Proposal: Add my feature"
git push origin proposal/my-feature
```

**Resources:**
- [Implementation Proposal Template](docs/IMPLEMENTATION_PROPOSAL_TEMPLATE.md) - Template for new proposals
- [Proposal Guide](docs/PROPOSAL_GUIDE.md) - Step-by-step guide with examples
- [Active Proposals](docs/proposals/) - Current proposals under review

See [docs/PROPOSAL_GUIDE.md](docs/PROPOSAL_GUIDE.md) for detailed instructions.

## License

This project is released under the MIT License.  See `LICENSE` for details.

---

## 📖 Казкар — Форма Оповіді (v0.1.0)

**Казкар** — перша з 7 формацій цілісності організму Cimeika. Це здатність зберігати сенс, бачити зв'язок між подіями, не загубитися в хаосі фактів.

### Філософія

```
Казкар — це здатність зберігати сенс.
Бачити зв'язок між подіями.
Не загубитися в хаосі фактів.

Відчувається як:
- "я розумію, що зі мною відбувається"
- внутрішня зв'язаність
- відсутність абсурду

Утримує цілісну картину без нав'язування істини.
```

### ✨ Легенда Сі

Всередині Казкара знаходиться **Легенда Сі** — інтерактивне поле знання, де користувач не читає текст, а досліджує сенси через семантичний граф.

**10 базових вузлів:**
- **Присутність** (центр, глибина 0)
- **Тиша**, **Достатність**, **Момент** (глибина 1)
- **Спокій**, **Прийняття**, **Час** (глибина 2)
- **Баланс**, **Мудрість**, **Цикл** (глибина 3)

**7 архетипів:**
- 🚪 Поріг — початок, перехід
- ✨ Творення — народження нового
- 🪞 Рефлексія — осмислення
- 🔄 Цикл — повторення з трансформацією
- 🔗 Зв'язок — об'єднання
- 🧭 Мандрівка — шлях, пошук
- 🦋 Перетворення — метаморфоза

### Запуск Казкара

```bash
# Встановити залежності
pip install -e .

# Запустити FastAPI сервер
uvicorn api.main:app --reload

# Або з параметрами
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Після запуску відкрийте браузер:
- Головна: http://localhost:8000/
- Казкар: http://localhost:8000/ui/kazkar/index.html
- Легенда Сі: http://localhost:8000/ui/kazkar/legenda.html
- API Docs: http://localhost:8000/docs

### API Endpoints

**Казкар:**
- `GET /api/kazkar/aktyvuvaty` — активувати формацію
- `GET /api/kazkar/proyav` — отримати стан для UI
- `POST /api/kazkar/plesty-zv-yaznist` — створити оповідь з подій
- `GET /api/kazkar/arkhetypy` — отримати всі архетипи
- `GET /api/kazkar/opovidi/ostanni` — останні оповіді

**Легенда Сі:**
- `GET /api/kazkar/legenda/aktyvuvaty` — увійти в легенду
- `GET /api/kazkar/legenda/navihuvaty/{vuzol_id}` — навігувати до вузла
- `POST /api/kazkar/legenda/poshuk` — семантичний пошук
- `GET /api/kazkar/legenda/eksport` — експортувати повний граф
- `POST /api/kazkar/legenda/vuzol` — **створити новий вузол** 🆕
- `POST /api/kazkar/legenda/zv-yazok` — **додати зв'язок між вузлами** 🆕
- `PUT /api/kazkar/legenda/vuzol/{vuzol_id}` — **оновити вузол** 🆕
- `DELETE /api/kazkar/legenda/vuzol/{vuzol_id}` — **видалити вузол** 🆕

**Пропозиції моменту (Ci-moment):** 🆕
- `GET /api/kazkar/porady/moment?potochnyy_vuzol={vuzol_id}` — **отримати пропозицію для моменту**
- `POST /api/kazkar/porady/opovid` — **пропозиція на основі оповіді**
- `GET /api/kazkar/porady/istoriya?kilkist={N}` — **історія пропозицій**
- `GET /api/kazkar/porady/statystyka` — **статистика пропозицій**

### Редагування Легенди Сі 🆕

Легенда Сі тепер підтримує **динамічне створення та редагування вузлів** прямо через веб-інтерфейс:

#### Створення нового вузла

Через UI (http://localhost:8000/ui/kazkar/legenda.html):
1. Прокрутіть до розділу "Редагування Графа"
2. Заповніть форму "Створити новий вузол":
   - **ID вузла**: унікальний ідентифікатор (наприклад: `spokiy_dushi`)
   - **Назва**: читабельна назва (наприклад: `Спокій Душі`)
   - **Опис**: детальний опис сенсу вузла
   - **Глибина**: рівень віддаленості від центру (0, 1, 2, 3, ...)
   - **Зв'язані вузли**: список ID існуючих вузлів через кому
   - **Резонансні сенси**: ключові слова через кому
   - **Архетип**: один з 7 архетипів (Поріг, Творення, Рефлексія, Цикл, Зв'язок, Мандрівка, Перетворення)
3. Натисніть "Створити вузол"
4. Система автоматично оновить граф і перейде до нового вузла

Через API:
```bash
curl -X POST http://localhost:8000/api/kazkar/legenda/vuzol \
  -H 'Content-Type: application/json' \
  -d '{
    "vuzol_id": "spokiy_dushi",
    "nazva": "Спокій Душі",
    "opys": "Глибокий внутрішній спокій, що приходить через прийняття",
    "hlybyna": 2,
    "zv_yazani_vuzly": ["prysutnist", "spokiy"],
    "rezonansni_sensy": ["спокій", "мир", "гармонія"],
    "arkhetyp": "Рефлексія"
  }'
```

#### Додавання зв'язків між вузлами

Через UI:
1. У розділі "Додати зв'язок між вузлами" введіть ID двох вузлів
2. Натисніть "Створити зв'язок"
3. Граф автоматично оновиться, показавши новий зв'язок

Через API:
```bash
curl -X POST http://localhost:8000/api/kazkar/legenda/zv-yazok \
  -H 'Content-Type: application/json' \
  -d '{
    "vuzol_id_1": "prysutnist",
    "vuzol_id_2": "spokiy_dushi"
  }'
```

#### Особливості динамічного редагування

- **Навігація без перезавантаження**: після створення вузла система автоматично переходить до нього
- **Реальний час**: зміни в графі відображаються миттєво
- **Збереження зв'язності**: система автоматично створює двосторонні зв'язки
- **Валідація**: перевірка існування вузлів та унікальності ID
- **Цілісність графа**: видалення вузла автоматично видаляє всі зв'язки з ним

### Пропозиції моменту (Ci-moment) 🆕

**Система пропозицій для моменту присутності** — механізм контекстуальних підказок, що допомагає користувачу глибше дослідити Легенду Сі.

#### Філософія

Пропозиції — це не команди, а м'які орієнтири. Як подих: природно виникають, не нав'язуються.

#### Типи пропозицій

1. **Пропозиції на основі поточного вузла**
   - Коли користувач у вузлі "Момент" → пропонується дослідити "Час" або повернутись до "Присутності"
   - Коли у центрі "Присутність" → пропонуються три первинні шляхи

2. **Пропозиції на основі оповіді**
   - Після створення оповіді через `plesty-zv-yaznist` система аналізує архетип
   - Якщо архетип "Цикл" (архетип Моменту) → пропонує дослідити вузол "Момент"

3. **Історія та статистика**
   - Система зберігає останні 50 пропозицій
   - Можна відстежити які дії пропонувалися найчастіше

#### Приклади використання

**Отримати пропозицію для моменту:**
```bash
# Без контексту (загальна пропозиція)
curl http://localhost:8000/api/kazkar/porady/moment

# З контекстом поточного вузла
curl http://localhost:8000/api/kazkar/porady/moment?potochnyy_vuzol=moment
```

**Отримати пропозицію на основі оповіді:**
```bash
curl -X POST http://localhost:8000/api/kazkar/porady/opovid \
  -H 'Content-Type: application/json' \
  -d '{
    "arkhetyp": {
      "nazva": "Цикл"
    },
    "opovid": "Повторення з трансформацією"
  }'
```

**Переглянути історію пропозицій:**
```bash
# Останні 10 пропозицій
curl http://localhost:8000/api/kazkar/porady/istoriya?kilkist=10
```

**Отримати статистику:**
```bash
curl http://localhost:8000/api/kazkar/porady/statystyka
```

#### Інтеграція з Сі (Si)

Пропозиції можуть бути інтегровані з центром присутності через hook:

```python
from core.si import Si
from zdibnosti.kazkar.porady import MomentPorady

si = Si()
porady = MomentPorady()

# Встановити hook
si.vstanovyty_moment_propozitsiya_hook(
    lambda moment: porady.daty_moment_propozitsiu(moment)
)

# Тепер при фіксації моменту автоматично генерується пропозиція
result = si.zafiksuvaty_teper()
print(result["propozitsiya"])  # Контекстуальна пропозиція
```

### Архітектура

```
cit/                      ← repo root = Python пакет
├── __init__.py
├── core/
│   ├── si.py            # Сі — центр присутності
│   ├── dzerkalo.py      # Дзеркало UI ↔ Dev
│   └── formatsiyi.py    # Базовий клас формацій
│
├── zdibnosti/
│   └── kazkar/
│       ├── forma_opovidi.py       # Основний модуль Казкара
│       ├── prostir_legendy.py     # ✨ Легенда Сі
│       ├── semantychnyi_graf.py   # Семантичний граф
│       ├── dvyhun_arkhetypiv.py   # Двигун архетипів
│       ├── opovidach.py           # Генератор оповідей
│       └── porady.py              # 🆕 Пропозиції моменту
│
├── api/
│   ├── main.py          # FastAPI app
│   └── kazkar_routes.py # API маршрути
│
├── ui/kazkar/           # Інтерфейс користувача
├── dani/kazkar/         # Дані (архетипи, легенди)
└── manifest.json        # Стан організму
```

### Компоненти

**Сі (Si)** — центр присутності:
- Фіксує момент "тепер"
- Приймає сигнали від формацій
- Підтримує дихальний цикл

**Дзеркало (Dzerkalo)** — синхронізація:
- Читає/записує manifest.json
- Синхронізує UI ↔ Dev
- Забезпечує узгодженість стану

**Казкар (Formatsiya)** — форма оповіді:
- Плете зв'язність між подіями
- Утримує семантичний граф
- Генерує оповіді через архетипи

### Приклади використання

**Python:**
```python
from zdibnosti.kazkar import Kazkar

# Ініціалізація
kazkar = Kazkar()

# Активація
result = kazkar.aktyvuvaty()
print(f"Цілісність: {result['tsilisnist']}")

# Вхід у Легенду Сі
kazkar.uviyty_v_legendu()

# Навігація
nav = kazkar.navihuvaty_po_legendi('tysha')
print(f"Поточний вузол: {nav['potochnyy_vuzol']['nazva']}")

# Плетіння зв'язності
podiyi = ["Ранок почався", "Виникла ідея", "Написав код"]
opovid = kazkar.plesty_zv_yaznist(podiyi)
print(f"Архетип: {opovid['opovid']['arkhetyp']['nazva']}")
```

**JavaScript (UI):**
```javascript
// Активація
const response = await fetch('/api/kazkar/aktyvuvaty');
const data = await response.json();

// Навігація по легенді
await fetch('/api/kazkar/legenda/aktyvuvaty');
const nav = await fetch('/api/kazkar/legenda/navihuvaty/tysha');
```

### Дані

**dani/kazkar/arkhetypy.yaml** — 7 архетипів з тригерами  
**dani/kazkar/semantychni_vuzly.json** — 10 вузлів графа  
**dani/kazkar/legendy/001_probudzhennya.md** — перша легенда

### Майбутнє

Казкар — перша з 7 формацій цілісності. Наступні формації будуть додані в майбутніх версіях, кожна з унікальними здібностями та інтеграцією з організмом Cimeika.
