#!/usr/bin/env bash
set -euo pipefail



# --- CIT_ENV_INJECT_V2 ---
# Load .env if present (simple KEY=VALUE lines). Does not print values.
if [ -f ".env" ]; then
  set -a
  # shellcheck disable=SC1091
  . ".env"
  set +a
fi

# Ensure OPENAI_API_KEY is present if CIT_OPENAI_API_KEY exists
if [ -n "${CIT_OPENAI_API_KEY:-}" ] && [ -z "${OPENAI_API_KEY:-}" ]; then
  export OPENAI_API_KEY="$CIT_OPENAI_API_KEY"
fi
# --- /CIT_ENV_INJECT_V2 ---
# --- CIT_OPENAI_KEY_ALIAS_V1 ---
# Provide OPENAI_API_KEY for code that expects the standard env var.
# Prefer CIT_OPENAI_API_KEY if present.
if [ -n "${CIT_OPENAI_API_KEY:-}" ] && [ -z "${OPENAI_API_KEY:-}" ]; then
  export OPENAI_API_KEY="$CIT_OPENAI_API_KEY"
fi
# --- /CIT_OPENAI_KEY_ALIAS_V1 ---
BASE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BASE"

PORT="${CIT_PORT:-8794}"
LOG="logs/cit_${PORT}.log"
PIDFILE="logs/cit_${PORT}.pid"

mkdir -p logs

pid_running() {
  if [ -f "$PIDFILE" ]; then
    PID="$(cat "$PIDFILE" 2>/dev/null || true)"
    if [ -n "${PID:-}" ] && kill -0 "$PID" 2>/dev/null; then
      echo "$PID"
      return 0
    fi
  fi
  return 1
}

cmd="${1:-status}"

case "$cmd" in
  start)
    # keep OPENAI_API_KEY if already set
    KEY_LINE=""
    if [ -f .env ]; then KEY_LINE="$(grep -E '^OPENAI_API_KEY=' .env || true)"; fi

    cat > .env <<EOF
CIT_PORT=$PORT
CIT_OPENAI_MODEL=${CIT_OPENAI_MODEL:-gpt-4.1-mini}
${KEY_LINE:-OPENAI_API_KEY=}
EOF
    chmod 600 .env
    export $(grep -v '^#' .env | xargs) || true

    if pid_running >/dev/null; then
      echo "ALREADY: PID=$(pid_running)"
      exit 0
    fi

    env OPENAI_API_KEY="${OPENAI_API_KEY:-}" CIT_OPENAI_API_KEY="${CIT_OPENAI_API_KEY:-}" CIT_OPENAI_MODEL="${CIT_OPENAI_MODEL:-}" nohup env CIT_PORT="$PORT" python server/cit_server.py > "$LOG" 2>&1 &
    PID="$!"
    echo "$PID" > "$PIDFILE"
    sleep 1

    echo "STARTED: PID=$PID PORT=$PORT LOG=$LOG"
    ;;

  stop)
    if pid_running >/dev/null; then
      PID="$(pid_running)"
      kill -9 "$PID" || true
      rm -f "$PIDFILE"
      echo "STOPPED: PID=$PID"
    else
      echo "STOPPED: not running"
    fi
    ;;

  status)
    if pid_running >/dev/null; then
      PID="$(pid_running)"
      echo "RUNNING: PID=$PID PORT=$PORT"
    else
      echo "NOT RUNNING: PORT=$PORT"
    fi
    ;;

  health)
    curl -sS --max-time 2 "http://127.0.0.1:$PORT/health" && echo
    ;;

  logs)
    tail -n 80 "$LOG" 2>/dev/null || echo "NO LOG: $LOG"
    ;;

  restart)
    "$0" stop || true
    "$0" start
    ;;

  *)
    echo "Usage: $0 {start|stop|restart|status|health|logs}"
    exit 2
    ;;
esac
