# Cimeika · Samsung Home Node · Паспорт (фактичний стан)

## Початкове завдання чату (факт)
Побудувати "ґрунт" Ci-явища: локальний вузол на Samsung (Termux), який:
1) тримає локальний каркас даних (db/texts/gallery/voice/logs),
2) має локальний HTTP статус/API,
3) синхронізується у сховище Keenetic (WebDAV) як резерв/контроль,
4) доступний у LAN.

## Реалізовано (перевірено командами)
### 1) Локальний Ci Core
- Процес: `python .../ci_core.py`
- Статус: `http://127.0.0.1:8787/status`
- LAN: `http://<Samsung_IP>:8787/status` (у тебе підтверджено `OK_LAN`)
- Дані/шляхи (Termux):
  - BASE: `/data/data/com.termux/files/home/cimeika`
  - DB:   `/data/data/com.termux/files/home/cimeika/db/cimeika.db`
  - DATA: `/data/data/com.termux/files/home/cimeika/data`
  - TEXTS: `/data/data/com.termux/files/home/cimeika/data/texts`
  - GALLERY: `/data/data/com.termux/files/home/cimeika/data/gallery`
  - VOICE: `/data/data/com.termux/files/home/cimeika/data/voice`
  - LOGS: `/data/data/com.termux/files/home/cimeika/logs`

### 2) Keenetic Vault (WebDAV, факт)
- URL: `https://cimeiniy.keenetic.link/webdav/`
- Remote (rclone): `keenetik:`
- Папка кореня вузла: `keenetik:ci/`
- Структура (створено/існує):
  - `ci/backups`
  - `ci/credentials`
  - `ci/db`
  - `ci/gallery`
  - `ci/logs`
  - `ci/texts`
  - `ci/voice`
  - `ci/test`

### 3) Синхронізація (факт)
- Loop: `ci_sync_loop.sh` (кожні 120s)
- Логи:
  - `~/cimeika/logs/sync.log`
  - `~/cimeika/logs/ci_sync_loop.log`
- На Keenetic з’являються файли:
  - `ci/db/cimeika.db`
  - `ci/logs/ci_core.log`, `ci/logs/ci_sync_loop.log`, `ci/logs/sync.log`

## Невідомі/проблемні (факт)
### Voice/STT
- Команди termux-api працюють, але мікрофон дає файли ~40B (порожні).
- `pm list packages | grep termux.api` показував відсутність app `com.termux.api` (потрібно встановити Termux:API як Android-додаток, не лише пакет).
- Статус: VOICE_CAPTURE = НЕ ГОТОВО (потрібна корекція дозволів/провайдера запису).

## Авторизація / секрети (правило)
- Паролі WebDAV/SMB/VPN НЕ зберігаються у Git.
- Використовуємо `.env` локально (`~/.ci_home.env`) або ручний експорт змінних у Termux.

