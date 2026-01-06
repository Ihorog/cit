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

pids_on_port(){
  local p=":$1"
  ss -ltnp 2>/dev/null \
  | awk -v P="$p" '$4 ~ P {print $0}' \
  | sed -n 's/.*pid=\([0-9]\+\).*/\1/p' \
  | sort -u
}

kill_port(){
  local port="$1"
  local pids=""
  pids="$(pids_on_port "$port" || true)"
  if [ -n "${pids:-}" ]; then
    echo "PORT $port -> PIDS: $pids"
    for pid in $pids; do
      kill "$pid" 2>/dev/null || true
    done
    sleep 0.5
    # hard kill остатків
    pids="$(pids_on_port "$port" || true)"
    if [ -n "${pids:-}" ]; then
      for pid in $pids; do
        kill -9 "$pid" 2>/dev/null || true
      done
    fi
  else
    echo "PORT $port -> no listeners"
  fi

  # wait until free
  for _ in $(seq 1 20); do
    if [ -z "$(pids_on_port "$port" || true)" ]; then
      echo "PORT $port -> FREE"
      return 0
    fi
    sleep 0.2
  done

  echo "PORT $port -> STILL BUSY"
  ss -ltnp 2>/dev/null | awk -v P=":$port" '$4 ~ P {print}'
  return 1
}

say "0) PRECHECK"
cd "$CIT_DIR"
test -f "$CIT_DIR/server/cit_server.py"
test -d "$CIT_DIR/ui"

say "1) HARD STOP (free ports ${API_PORT}/${UI_PORT})"
kill_port "$API_PORT"
kill_port "$UI_PORT"

say "2) START API (server/cit_server.py)"
# гарантуємо чисте логування
: > "$API_LOG"
# якщо сервер підтримує env-порти — добре; якщо ні — не завадить
export CIT_PORT="$API_PORT"
export CIT_HOST="127.0.0.1"
nohup python3 "$CIT_DIR/server/cit_server.py" >"$API_LOG" 2>&1 &
API_PID="$!"
echo "api_pid: $API_PID"

say "3) START UI (static http server -> ui/)"
: > "$UI_LOG"
nohup python3 -m http.server "$UI_PORT" --bind 127.0.0.1 --directory "$CIT_DIR/ui" >"$UI_LOG" 2>&1 &
UI_PID="$!"
echo "ui_pid: $UI_PID"

sleep 1

say "4) VERIFY (ports actually owned by NEW pids)"
echo "ss :${API_PORT} ->"
ss -ltnp 2>/dev/null | awk -v P=":$API_PORT" '$4 ~ P {print}' || true
echo "ss :${UI_PORT} ->"
ss -ltnp 2>/dev/null | awk -v P=":$UI_PORT" '$4 ~ P {print}' || true

say "5) VERIFY (HTTP probes)"
probe "http://127.0.0.1:${API_PORT}/health"
probe "http://127.0.0.1:${API_PORT}/registry"
probe "http://127.0.0.1:${UI_PORT}/"
probe "http://127.0.0.1:${UI_PORT}/?api=http://127.0.0.1:${API_PORT}"

say "6) LOG TAIL"
echo "--- API LOG ---"
tail -n 40 "$API_LOG" 2>/dev/null || true
echo
echo "--- UI LOG ---"
tail -n 20 "$UI_LOG" 2>/dev/null || true

say "DONE"
