[#!/bin/bash
set -euo pipefail
exec 2>&1
cd "$HOME/cit" || (mkdir -p "$HOME/cit" && cd "$HOME/cit")
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'
echo -e "${CYAN}╔════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  CIT AUTO-BOOTSTRAP & ORCHESTRATION    ║${NC}"
echo -e "${CYAN}║  Запуск: $(date '+%Y-%m-%d %H:%M:%S')                    ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════╝${NC}"
echo ""
CIT_ROOT="$HOME/cit"
CIMEIKA_BASE="$HOME/cimeika"
VENV_PATH="$CIT_ROOT/venv"
ENV_FILE="$HOME/.ci_home.env"
LOG_DIR="$CIMEIKA_BASE/logs"
BIN_DIR="$CIMEIKA_BASE/bin"
DB_DIR="$CIMEIKA_BASE/db"
DATA_DIR="$CIMEIKA_BASE/data"
PID_FILE_SERVER="$BIN_DIR/.server.pid"
PID_FILE_SYNC="$BIN_DIR/.sync.pid"
CIT_PORT="8790"
REMOTE_NAME="keenetik"
REMOTE_ROOT="ci"
log_ok() { echo -e "${GREEN}✓${NC} $1"; }
log_err() { echo -e "${RED}✗${NC} $1"; }
log_warn() { echo -e "${YELLOW}⚠${NC} $1"; }
log_header() { echo ""; echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"; echo -e "${CYAN}  $1${NC}"; echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"; echo ""; }
die() { log_err "$1"; exit 1; }
step_1_check() {
	log_header "ШАГ 1: ПЕРЕВІРКА СИСТЕМИ"
	if ! command -v python3 &> /dev/null; then die "python3 не встановлений"; fi
	if ! command -v git &> /dev/null; then die "git не встановлений"; fi
	if [ ! -d "$CIT_ROOT" ]; then die "CIT репо не знайдений в $CIT_ROOT"; fi
	log_ok "python3: $(python3 --version 2>&1 | awk '{print $2}')"
	log_ok "git: $(git --version 2>&1 | awk '{print $3}')"
	log_ok "CIT репозиторій знайдений"
}
step_2_env() {
	log_header "ШАГ 2: НАЛАШТУВАННЯ КОНФІГУ"
	if [ ! -f "$ENV_FILE" ]; then
		cat > "$ENV_FILE" << 'EOF'
export OPENAI_API_KEY="${OPENAI_API_KEY:-}"
export CIT_MODEL="gpt-4o-mini"
export CIT_PORT="8790"
export LOCAL_BASE="$HOME/cimeika"
export REMOTE_NAME="keenetik"
export REMOTE_ROOT="ci"
EOF
		log_ok "Конфіг створений: $ENV_FILE"
	else
		log_ok "Конфіг вже існує"
	fi
	set -a
	source "$ENV_FILE" 2>/dev/null || true
	set +a
}
step_3_dirs() {
	log_header "ШАГ 3: СТВОРЕННЯ ДИРЕКТОРІЙ"
	mkdir -p "$LOG_DIR" "$BIN_DIR" "$DB_DIR" "${DATA_DIR}/texts" "${DATA_DIR}/gallery" "${DATA_DIR}/voice"
	log_ok "Директорії: $CIMEIKA_BASE"
}
step_4_python() {
	log_header "ШАГ 4: НАЛАШТУВАННЯ PYTHON"
	if [ ! -d "$VENV_PATH" ]; then
		python3 -m venv "$VENV_PATH" || die "Не можу створити venv"
		log_ok "venv створений"
	else
		log_ok "venv вже існує"
	fi
	source "$VENV_PATH/bin/activate"
	pip install -q --upgrade pip 2>/dev/null || true
	pip install -q flask requests aiohttp python-dotenv 2>/dev/null || die "Не можу встановити залежності"
	log_ok "Залежності встановлені"
}
step_5_db() {
	log_header "ШАГ 5: ІНІЦІАЛІЗАЦІЯ БД"
	if [ ! -f "$DB_DIR/cimeika.db" ]; then
		python3 << 'PYEOF'
import sqlite3
from pathlib import Path
db_path = Path("$HOME/cimeika/db/cimeika.db")
db_path.parent.mkdir(parents=True, exist_ok=True)
conn = sqlite3.connect(str(db_path))
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS kv (k TEXT PRIMARY KEY, v TEXT NOT NULL, ts TEXT NOT NULL)''')
conn.commit()
conn.close()
PYEOF
		log_ok "База даних ініціалізована"
	else
		log_ok "База даних вже існує"
	fi
}
step_6_stop_old() {
	log_header "ШАГ 6: ОЧИСТКА СТАРИХ ПРОЦЕСІВ"
	pkill -f "cit_server.py" 2>/dev/null || true
	pkill -f "ci_sync_loop" 2>/dev/null || true
	sleep 1
	rm -f "$PID_FILE_SERVER" "$PID_FILE_SYNC"
	log_ok "Старі процеси зупинені"
}
step_7_server() {
	log_header "ШАГ 7: ЗАПУСК CIT СЕРВЕРА"
	source "$VENV_PATH/bin/activate"
	nohup python3 "$CIT_ROOT/server/cit_server.py" > "$LOG_DIR/cit_server.log" 2>&1 &
	SERVER_PID=$!
	echo "$SERVER_PID" > "$PID_FILE_SERVER"
	sleep 2
	if ps -p "$SERVER_PID" > /dev/null 2>&1; then
		log_ok "CIT сервер запущений (PID: $SERVER_PID, порт: $CIT_PORT)"
	else
		die "Не можу запустити CIT сервер"
	fi
}
step_8_sync() {
	log_header "ШАГ 8: ЗАПУСК СИНХРОНІЗАЦІЇ"
	cat > "$BIN_DIR/ci_sync_loop.sh" << 'SYNCEOF'
#!/bin/bash
set -euo pipefail
while true; do
	REMOTE_NAME="keenetik" REMOTE_ROOT="ci" LOCAL_BASE="$HOME/cimeika" bash "$HOME/cit/home_node/ci_sync_loop.sh" >> "$HOME/cimeika/logs/ci_sync_loop.log" 2>&1 || true
	sleep 120
done
SYNCEOF
	chmod +x "$BIN_DIR/ci_sync_loop.sh"
	nohup bash "$BIN_DIR/ci_sync_loop.sh" > /dev/null 2>&1 &
	SYNC_PID=$!
	echo "$SYNC_PID" > "$PID_FILE_SYNC"
	sleep 1
	if ps -p "$SYNC_PID" > /dev/null 2>&1; then
		log_ok "Синхронізація запущена (PID: $SYNC_PID, інтервал: 120s)"
	else
		log_warn "Синхронізація не запущена (можливо rclone не налаштований)"
	fi
}
step_9_verify() {
	log_header "ШАГ 9: ПЕРЕВІРКА СТАТУСУ"
	sleep 1
	if [ -f "$PID_FILE_SERVER" ]; then
		SERVER_PID=$(cat "$PID_FILE_SERVER")
		if ps -p "$SERVER_PID" > /dev/null 2>&1; then
			log_ok "✓ CIT сервер: ЗАПУЩЕНИЙ"
		else
			log_err "✗ CIT сервер: ЗУПИНЕНИЙ"
		fi
	fi
	if [ -f "$PID_FILE_SYNC" ]; then
		SYNC_PID=$(cat "$PID_FILE_SYNC")
		if ps -p "$SYNC_PID" > /dev/null 2>&1; then
			log_ok "✓ Синхронізація: ЗАПУЩЕНА"
		else
			log_warn "⚠ Синхронізація: ЗУПИНЕНА"
		fi
	fi
	if [ -f "$LOG_DIR/cit_server.log" ]; then
		echo ""
		echo -e "${CYAN}Останні eventos (server):${NC}"
		tail -3 "$LOG_DIR/cit_server.log" | sed 's/^/  /'
	fi
}
step_10_done() {
	log_header "ЗАВЕРШЕННЯ"
	echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
	echo -e "${GREEN}║  ✓ CIT СИСТЕМА ГОТОВА                   ║${NC}"
	echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
	echo ""
	echo "API:          http://localhost:$CIT_PORT"
	echo "API Health:   curl http://localhost:$CIT_PORT/health"
	echo "API Chat:     curl -X POST http://localhost:$CIT_PORT/chat -H 'Content-Type: application/json' -d '{\"message\":\"Привіт\"}'"
	echo ""
	echo "Логи:"
	echo "  Server:  tail -f $LOG_DIR/cit_server.log"
	echo "  Sync:    tail -f $LOG_DIR/ci_sync_loop.log"
	echo ""
	echo "Зупинити:"
	echo "  pkill -f 'cit_server.py'"
	echo "  pkill -f 'ci_sync_loop'"
	echo ""
	echo "Статус:"
	echo "  ps aux | grep -E '(cit_server|ci_sync)'"
	echo ""
}
run() {
	step_1_check
	step_2_env
	step_3_dirs
	step_4_python
	step_5_db
	step_6_stop_old
	step_7_server
	step_8_sync
	step_9_verify
	step_10_done
}
run
]
