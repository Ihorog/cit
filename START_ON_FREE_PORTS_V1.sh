#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

CIT_DIR="/data/data/com.termux/files/home/cimeika/cit"
API_HOST="127.0.0.1"
UI_HOST="127.0.0.1"

API_PORT_START="8790"
UI_PORT_START="8010"

API_LOG="$CIT_DIR/.api.auto.log"
UI_LOG="$CIT_DIR/.ui.auto.log"
STATE_FILE="$CIT_DIR/.ports.active"

say(){ printf "\n=== %s ===\n" "$1"; }

probe(){
  local url="$1"
  local code
  code="$(curl -m 2 -sS -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || true)"
  printf "%-10s -> %s\n" "${code:-ERR}" "$url"
}

port_free(){
  local port="$1"
  # якщо bind вже зайнятий — python поверне non-zero
  python3 - <<PY >/dev/null 2>&1
import socket
s=socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
  s.bind(("127.0.0.1", int("$port")))
  s.close()
  raise SystemExit(0)
except OSError:
  raise SystemExit(1)
PY
}

pick_port(){
  local start="$1"
  local end="$2"
  for p in $(seq "$start" "$end"); do
    if port_free "$p"; then
      echo "$p"
      return 0
    fi
  done
  return 1
}

say "0) PRECHECK"
cd "$CIT_DIR"
test -f "$CIT_DIR/server/cit_server.py"
test -d "$CIT_DIR/ui"

say "1) PICK FREE PORTS"
API_PORT="$(pick_port "$API_PORT_START" 8899 || true)"
UI_PORT="$(pick_port "$UI_PORT_START" 8199 || true)"

if [ -z "${API_PORT:-}" ] || [ -z "${UI_PORT:-}" ]; then
  echo "FAIL: cannot find free ports in ranges API ${API_PORT_START}-8899 or UI ${UI_PORT_START}-8199"
  exit 1
fi

echo "API_PORT=$API_PORT"
echo "UI_PORT=$UI_PORT"

say "2) START API (auto port)"
: > "$API_LOG"
export CIT_HOST="$API_HOST"
export CIT_PORT="$API_PORT"
nohup python3 "$CIT_DIR/server/cit_server.py" >"$API_LOG" 2>&1 &
API_PID="$!"
echo "api_pid: $API_PID"

say "3) START UI (auto port)"
: > "$UI_LOG"
nohup python3 -m http.server "$UI_PORT" --bind "$UI_HOST" --directory "$CIT_DIR/ui" >"$UI_LOG" 2>&1 &
UI_PID="$!"
echo "ui_pid: $UI_PID"

sleep 1

say "4) VERIFY (HTTP)"
probe "http://$API_HOST:$API_PORT/health"
probe "http://$API_HOST:$API_PORT/registry"
probe "http://$UI_HOST:$UI_PORT/"
probe "http://$UI_HOST:$UI_PORT/?api=http://$API_HOST:$API_PORT"

say "5) LOG TAIL"
echo "--- API LOG ---"
tail -n 30 "$API_LOG" 2>/dev/null || true
echo
echo "--- UI LOG ---"
tail -n 20 "$UI_LOG" 2>/dev/null || true

say "6) SAVE ACTIVE PORTS"
cat > "$STATE_FILE" <<EOF
CIT_DIR=$CIT_DIR
API_HOST=$API_HOST
API_PORT=$API_PORT
API_PID=$API_PID
UI_HOST=$UI_HOST
UI_PORT=$UI_PORT
UI_PID=$UI_PID
UI_URL=http://$UI_HOST:$UI_PORT/
UI_URL_WITH_API=http://$UI_HOST:$UI_PORT/?api=http://$API_HOST:$API_PORT
EOF
echo "OK: $STATE_FILE"

say "7) READY"
echo "UI            : http://$UI_HOST:$UI_PORT/"
echo "UI (with API)  : http://$UI_HOST:$UI_PORT/?api=http://$API_HOST:$API_PORT"
echo "API health     : http://$API_HOST:$API_PORT/health"
echo "Logs           : $API_LOG , $UI_LOG"
