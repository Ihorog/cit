#!/usr/bin/env bash
# Quick repo verification: Python syntax + ephemeral health check
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# Validate PORT to prevent command injection and ensure valid range
PORT="${CIT_PORT:-8979}"
if ! [[ "$PORT" =~ ^[0-9]+$ ]] || [ "$PORT" -lt 1024 ] || [ "$PORT" -gt 65535 ]; then
  echo "❌ Invalid PORT: $PORT (must be 1024-65535)"
  exit 1
fi

# Safely create temp log file
LOG_FILE="$(mktemp "${TMPDIR:-/tmp}/cit_server.XXXXXX.log")"
if [[ ! -f "$LOG_FILE" ]]; then
  echo "❌ Failed to create temporary log file"
  exit 1
fi

cd "$ROOT_DIR"

# Common security options for curl
CURL_SECURITY_OPTS="--connect-timeout 3 --max-filesize 1048576"
CURL_TIMEOUT_SHORT="--max-time 5"
CURL_TIMEOUT_LONG="--max-time 10"  # /chat needs longer timeout for LLM response

cleanup() {
  if [[ -n "${PID:-}" ]]; then
    kill "$PID" 2>/dev/null || true
  fi
  rm -f "$LOG_FILE"
}
trap cleanup EXIT

echo "🔍 Python syntax check (compileall)..."
python -m compileall server

echo "🚀 Starting CIT server on port ${PORT} for health probe..."
export CIT_PORT="$PORT"
python server/cit_server.py > "$LOG_FILE" 2>&1 &
PID=$!

is_healthy=false
for _ in {1..20}; do
  # Add security options to prevent hanging and limit response size
  # shellcheck disable=SC2086  # Word splitting is intentional for curl options
  if curl -s $CURL_SECURITY_OPTS $CURL_TIMEOUT_SHORT "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; then
    is_healthy=true
    break
  fi
  sleep 0.2
done

if ! $is_healthy; then
  echo "❌ Server did not become healthy. Logs:"
  cat "$LOG_FILE"
  exit 1
fi

echo "✅ /health response:"
# shellcheck disable=SC2086  # Word splitting is intentional for curl options
curl -s $CURL_SECURITY_OPTS $CURL_TIMEOUT_SHORT "http://127.0.0.1:${PORT}/health"
echo

if [[ -n "${OPENAI_API_KEY:-}" ]]; then
  printf "\n💬 /chat smoke test:\n"
  # shellcheck disable=SC2086  # Word splitting is intentional for curl options
  curl -s $CURL_SECURITY_OPTS $CURL_TIMEOUT_LONG -X POST "http://127.0.0.1:${PORT}/chat" \
    -H 'Content-Type: application/json' \
    -d '{"message":"ping"}'
  echo
else
  printf "\nℹ️ OPENAI_API_KEY not set — skipping /chat check.\n"
fi
