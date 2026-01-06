#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT="/data/data/com.termux/files/home/cimeika/cit"
LOG="$ROOT/logs"
UI_PORT="8010"
API_PORT="8790"

cd "$ROOT" || exit 1
mkdir -p "$LOG"

echo "=== [STOP] old processes ==="
pkill -f "python -m http.server ${UI_PORT}" 2>/dev/null || true
pkill -f "server/cit_server.py" 2>/dev/null || true
sleep 0.2

echo "=== [CHECK] python ==="
python -V

echo "=== [CHECK] cit_server.py syntax ==="
python -m py_compile "$ROOT/server/cit_server.py"

echo "=== [START] CIT API :${API_PORT} ==="
nohup python "$ROOT/server/cit_server.py" > "$LOG/cit_api_${API_PORT}.log" 2>&1 &
sleep 0.6

echo "=== [START] UI (static) :${UI_PORT} ==="
cd "$ROOT/ui" || exit 1
nohup python -m http.server "${UI_PORT}" --bind 127.0.0.1 > "$LOG/ui_${UI_PORT}.log" 2>&1 &
sleep 0.4

echo
echo "=== [VERIFY] API health ==="
API_HEALTH="$(curl -sS --max-time 2 "http://127.0.0.1:${API_PORT}/health" || true)"
if [ -z "$API_HEALTH" ]; then
  echo "API DOWN"
  echo "=== [TAIL] $LOG/cit_api_${API_PORT}.log ==="
  tail -n 120 "$LOG/cit_api_${API_PORT}.log" || true
  exit 1
fi
echo "$API_HEALTH"

echo
echo "=== [VERIFY] exec registry.get ==="
curl -sS --max-time 2 -X POST "http://127.0.0.1:${API_PORT}/api/exec" \
  -H "Content-Type: application/json" \
  -d '{"action":"actions.registry.get"}' || true
echo

echo "=== [VERIFY] UI HEAD ==="
curl -sS --max-time 2 -I "http://127.0.0.1:${UI_PORT}/" | head -n 1 || true
echo

echo "=== READY LINKS ==="
echo "UI Dashboard : http://127.0.0.1:${UI_PORT}/"
echo "Ci'         : http://127.0.0.1:${UI_PORT}/pages/ci.html"
echo "Kazkar'     : http://127.0.0.1:${UI_PORT}/pages/kazkar.html"
echo "Legend Ci'  : http://127.0.0.1:${UI_PORT}/pages/legend_ci.html"
echo "PoDija'     : http://127.0.0.1:${UI_PORT}/pages/podija.html"
echo "Nastrij'    : http://127.0.0.1:${UI_PORT}/pages/nastrij.html"
echo "Malya'      : http://127.0.0.1:${UI_PORT}/pages/malya.html"
echo "Calendar'   : http://127.0.0.1:${UI_PORT}/pages/calendar.html"
echo "Gallery'    : http://127.0.0.1:${UI_PORT}/pages/gallery.html"
echo
echo "API health  : http://127.0.0.1:${API_PORT}/health"
echo "API chat    : http://127.0.0.1:${API_PORT}/api/chat"
echo "API exec    : http://127.0.0.1:${API_PORT}/api/exec"
echo "Registry    : http://127.0.0.1:${API_PORT}/registry"
echo "Node-pack   : http://127.0.0.1:${API_PORT}/node-packages"
