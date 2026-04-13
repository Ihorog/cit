#!/usr/bin/env bash
# ════════════════════════════════════════════
#  CIT · Запуск локально (Termux / Linux)
#  Використання: bash run.sh [start|stop|restart|status|logs|health]
# ════════════════════════════════════════════
set -euo pipefail

BASE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BASE"

GREEN='\033[0;32m'; CYAN='\033[0;36m'; RED='\033[0;31m'; NC='\033[0m'
log()  { echo -e "${CYAN}▶${NC} $*"; }
ok()   { echo -e "${GREEN}✓${NC} $*"; }
err()  { echo -e "${RED}✗${NC} $*"; exit 1; }

CMD="${1:-start}"

# ─── git pull ────────────────────────────────
log "git pull..."
git pull --ff-only origin main 2>&1 | tail -3

# ─── venv ────────────────────────────────────
VENV="$BASE/venv"
if [ ! -d "$VENV" ]; then
  log "Створення venv..."
  python3 -m venv "$VENV"
fi
source "$VENV/bin/activate"

# ─── deps (тільки якщо змінились) ────────────
REQ_HASH_FILE="$BASE/.req_hash"
REQ_HASH=$(md5sum requirements.txt 2>/dev/null | cut -d' ' -f1 || echo "none")
SAVED_HASH=$(cat "$REQ_HASH_FILE" 2>/dev/null || echo "")

if [ "$REQ_HASH" != "$SAVED_HASH" ]; then
  log "Встановлення залежностей..."
  pip install -r requirements.txt -q --break-system-packages 2>/dev/null || \
  pip install -r requirements.txt -q
  echo "$REQ_HASH" > "$REQ_HASH_FILE"
  ok "Залежності встановлені"
else
  ok "Залежності актуальні"
fi

# ─── storage dirs ────────────────────────────
mkdir -p storage/registry storage/jobs storage/audit logs

# ─── .env ────────────────────────────────────
if [ ! -f ".env" ]; then
  cp .env.example .env
  log ".env створено з .env.example — перевір OPENAI_API_KEY"
fi

# ─── запуск через citctl.sh ───────────────────
log "citctl.sh $CMD..."
bash citctl.sh "$CMD"

# ─── health check ────────────────────────────
if [ "$CMD" = "start" ] || [ "$CMD" = "restart" ]; then
  sleep 2
  PORT="${CIT_PORT:-8794}"
  if curl -sf "http://127.0.0.1:$PORT/health" > /dev/null 2>&1; then
    ok "CIT сервер працює → http://127.0.0.1:$PORT"
    curl -s "http://127.0.0.1:$PORT/health" | python3 -m json.tool 2>/dev/null || true
  else
    echo ""
    log "Лог сервера:"
    bash citctl.sh logs
  fi
fi
