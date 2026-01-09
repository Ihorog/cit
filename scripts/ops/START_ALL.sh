#!/data/data/com.termux/files/usr/bin/bash
source "/data/data/com.termux/files/home/cimeika/cit/bin/ui_restart.sh"
set -e

ROOT="/data/data/com.termux/files/home/cimeika/cit"
UI="$ROOT/ui"
LOG="$ROOT/logs"

cd "$ROOT" || exit 1
mkdir -p "$LOG"

echo "[STOP] old UI/API (best-effort)"
pkill -f "server/cit_server.py" 2>/dev/null || true

echo "[START] API (expected :8790)"
nohup python "$ROOT/server/cit_server.py" > "$LOG/cit_api_8790.log" 2>&1 &
sleep 0.8

echo "[START] UI (static :8010)"
cd "$UI" || exit 1
ui_restart
sleep 0.4

echo "[CHECK] UI"
curl -sS --max-time 2 -I http://127.0.0.1:8010/ | head -n 1 || echo "UI DOWN"

echo "[CHECK] API"
curl -sS --max-time 2 http://127.0.0.1:8790/health || echo "API DOWN"
echo

echo "[DONE]"
echo "UI  : http://127.0.0.1:8010/"
echo "API : http://127.0.0.1:8790/health"


# === CANON UI RESTART (Termux) ===
UI_PORT=8010
UI_HOST=127.0.0.1
ROOT="/data/data/com.termux/files/home/cimeika/cit/ui"
LOGDIR="/data/data/com.termux/files/home/cimeika/cit/logs"
LOGFILE="$LOGDIR/ui_${UI_PORT}.log"

mkdir -p "$LOGDIR" || exit 1

# stop
pids="$(ps -A -o pid,args | grep -E "python -m http\.server $UI_PORT" | grep -v grep | awk '{print $1}' || true)"
for pid in $pids; do kill -9 "$pid" 2>/dev/null || true; done
sleep 0.2

# start
cd "$ROOT" || exit 1
nohup python -m http.server "$UI_PORT" --bind "$UI_HOST" > "$LOGFILE" 2>&1 &
sleep 0.4

# verify
curl -sS --max-time 2 -I "http://$UI_HOST:$UI_PORT/" | head -n 1
# === /CANON UI RESTART ===
