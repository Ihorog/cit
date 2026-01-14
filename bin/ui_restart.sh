#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ui_restart() {
  set +m  # disable job-control notifications (hide 'Killed')

  local UI_PORT="${UI_PORT:-8010}"
  local UI_HOST="${UI_HOST:-127.0.0.1}"
  local ROOT="${UI_ROOT:-/data/data/com.termux/files/home/cimeika/cit/ui}"
  local LOGDIR="${UI_LOGDIR:-/data/data/com.termux/files/home/cimeika/cit/logs}"
  local LOGFILE="$LOGDIR/ui_${UI_PORT}.log"

  mkdir -p "$LOGDIR" || return 1

  local pids
  pids="$(ps -A -o pid,args | grep -E "python -m http\.server ${UI_PORT}\b" | grep -v grep | awk '{print $1}' || true)"
  if [ -n "${pids:-}" ]; then
    for pid in $pids; do kill -9 "$pid" 2>/dev/null || true; done
  fi
  sleep 0.2

  cd "$ROOT" || return 2
  nohup python -m http.server "$UI_PORT" --bind "$UI_HOST" > "$LOGFILE" 2>&1 &
  sleep 0.4

  curl -sS --max-time 2 -I "http://$UI_HOST:$UI_PORT/" | head -n 1
}
