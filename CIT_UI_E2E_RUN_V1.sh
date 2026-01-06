#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

UI_PORT=8010
API_PORT=8790
CIT_DIR="$HOME/cimeika/cit"

say(){ printf "\n=== %s ===\n" "$1"; }
code(){ curl -m 2 -sS -o /dev/null -w "%{http_code}" "$1" 2>/dev/null || echo ERR; }

say "E2E CHECK (UI + API)"

cd "$CIT_DIR" || exit 1

say "STOP OLD"
pkill -f "http.server $UI_PORT" 2>/dev/null || true
pkill -f "cit_server.py" 2>/dev/null || true
sleep 0.5

say "START API"
nohup python3 server/cit_server.py > .api.e2e.log 2>&1 &
sleep 0.7

say "START UI"
nohup python3 -m http.server "$UI_PORT" --bind 127.0.0.1 -d ui > .ui.e2e.log 2>&1 &
sleep 0.7

say "VERIFY"
printf "UI        : %s\n" "$(code http://127.0.0.1:$UI_PORT/)"
printf "API       : %s\n" "$(code http://127.0.0.1:$API_PORT/health)"
printf "REGISTRY  : %s\n" "$(code http://127.0.0.1:$API_PORT/registry)"

say "DONE"
echo "UI  -> http://127.0.0.1:$UI_PORT/"
echo "API -> http://127.0.0.1:$API_PORT/health"
