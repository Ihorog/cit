#!/usr/bin/env bash
# Quick repo verification: Python syntax + ephemeral health check
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${CIT_PORT:-8979}"

cd "$ROOT_DIR"

echo "🔍 Python syntax check (compileall)..."
python -m compileall server

echo "🚀 Starting CIT server on port ${PORT} for health probe..."
export CIT_PORT="$PORT"
python server/cit_server.py > /tmp/cit_server.log 2>&1 &
PID=$!
trap 'kill "$PID" 2>/dev/null || true' EXIT
sleep 1

echo "✅ /health response:"
curl -s "http://127.0.0.1:${PORT}/health" || true

if [[ -n "${OPENAI_API_KEY:-}" ]]; then
  echo "\n💬 /chat smoke test:"
  curl -s -X POST "http://127.0.0.1:${PORT}/chat" \
    -H 'Content-Type: application/json' \
    -d '{"message":"ping"}' || true
else
  echo "\nℹ️ OPENAI_API_KEY not set — skipping /chat check."
fi

kill "$PID" 2>/dev/null || true
trap - EXIT
