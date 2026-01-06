#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

CIT_DIR="/data/data/com.termux/files/home/cimeika/cit"
API_PORT="8790"
UI_PORT="8010"
API_LOG="$CIT_DIR/.api.${API_PORT}.log"
UI_LOG="$CIT_DIR/.ui.${UI_PORT}.log"

say(){ printf "\n=== %s ===\n" "$1"; }
probe(){
  local url="$1"
  local code
  code="$(curl -m 3 -sS -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || true)"
  printf "%-10s -> %s\n" "$code" "$url"
}

say "0) PRECHECK"
cd "$CIT_DIR"
test -f "$CIT_DIR/server/cit_server.py"

say "1) STOP (ports ${API_PORT}/${UI_PORT})"
# kill listeners on ports (best-effort)
for p in "$API_PORT" "$UI_PORT"; do
  pid="$(ss -ltnp 2>/dev/null | awk -v P=":$p" '$4 ~ P {print $0}' | sed -n 's/.*pid=\([0-9]\+\).*/\1/p' | head -n1 || true)"
  if [ -n "${pid:-}" ]; then
    echo "KILL pid=$pid (port $p)"
    kill "$pid" 2>/dev/null || true
    sleep 0.5
  fi
done

say "2) START API (server/cit_server.py)"
# NOTE: якщо OPENAI_API_KEY вже SET — не чіпаємо
nohup python3 "$CIT_DIR/server/cit_server.py" >"$API_LOG" 2>&1 &
echo "api_pid: $!"

say "3) START UI (static server -> ui/)"
nohup python3 -m http.server "$UI_PORT" --bind 127.0.0.1 --directory "$CIT_DIR/ui" >"$UI_LOG" 2>&1 &
echo "ui_pid: $!"

sleep 1

say "4) VERIFY (HTTP probes)"
probe "http://127.0.0.1:${API_PORT}/health"
probe "http://127.0.0.1:${API_PORT}/registry"
probe "http://127.0.0.1:${UI_PORT}/"
probe "http://127.0.0.1:${UI_PORT}/?api=http://127.0.0.1:${API_PORT}"

say "5) LOG TAIL (last lines)"
echo "--- API LOG ---"
tail -n 30 "$API_LOG" 2>/dev/null || true
echo
echo "--- UI LOG ---"
tail -n 10 "$UI_LOG" 2>/dev/null || true

say "DONE"
