#!/data/data/com.termux/files/usr/bin/bash
set -e

ROOT="/data/data/com.termux/files/home/cimeika/cit"
UI="$ROOT/ui"
LOG="$ROOT/logs"

cd "$ROOT" || exit 1
mkdir -p "$LOG"

echo "=== [1/6] STOP any UI on :8010 (best-effort) ==="
pkill -f "python -m http.server 8010" 2>/dev/null || true
pkill -f "http.server 8010" 2>/dev/null || true

echo "=== [2/6] VERIFY UI files ==="
test -f "$UI/index.html" || { echo "MISSING: $UI/index.html"; exit 2; }
test -f "$UI/app.js"     || { echo "MISSING: $UI/app.js"; exit 2; }

echo "=== [3/6] START UIv2 :8010 (serve /ui folder) ==="
nohup python -m http.server 8010 --bind 127.0.0.1 --directory "$UI" > "$LOG/ui_8010.log" 2>&1 &
sleep 0.4

echo "=== [4/6] VERIFY (single pass) ==="
echo -n "UI:  "
curl -sS --max-time 2 -I http://127.0.0.1:8010/ | head -n 1 || { echo "UI DOWN"; tail -n 80 "$LOG/ui_8010.log" || true; exit 3; }

echo -n "API: "
curl -sS --max-time 2 http://127.0.0.1:8790/health | head -c 140; echo

echo "=== [5/6] READY LINKS ==="
echo "UI            : http://127.0.0.1:8010/"
echo "UI (other API): http://127.0.0.1:8010/?api=http://127.0.0.1:8790"
echo "API health    : http://127.0.0.1:8790/health"
echo "API chat      : http://127.0.0.1:8790/api/chat"
echo "API exec      : http://127.0.0.1:8790/api/exec"

echo "=== [6/6] LOG ==="
echo "$LOG/ui_8010.log"
