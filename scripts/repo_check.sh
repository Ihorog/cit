#!/usr/bin/env bash
# Quick repo verification: Python syntax + ephemeral health check
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${CIT_PORT:-8979}"
LOG_FILE="$(mktemp "${TMPDIR:-/tmp}/cit_server.XXXXXX.log")"

cd "$ROOT_DIR"

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

for _ in {1..20}; do
  if curl -s "http://127.0.0.1:${PORT}/health" >/dev/null; then
    break
  fi
  sleep 0.2
done

if ! curl -s "http://127.0.0.1:${PORT}/health" >/dev/null; then
  echo "❌ Server did not become healthy. Logs:"
  cat "$LOG_FILE"
  exit 1
fi

echo "✅ /health response:"
curl -s "http://127.0.0.1:${PORT}/health" || true

if [[ -n "${OPENAI_API_KEY:-}" ]]; then
  printf "\n💬 /chat smoke test:\n"
  curl -s -X POST "http://127.0.0.1:${PORT}/chat" \
    -H 'Content-Type: application/json' \
    -d '{"message":"ping"}' || true
else
  printf "\nℹ️ OPENAI_API_KEY not set — skipping /chat check.\n"
fi
