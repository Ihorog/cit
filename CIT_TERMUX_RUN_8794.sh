#!/usr/bin/env bash
set -euo pipefail

BASE="$(git rev-parse --show-toplevel)"
cd "$BASE"

mkdir -p logs

# Local .env (keep existing OPENAI_API_KEY if present)
KEY_LINE=""
if [ -f .env ]; then
  KEY_LINE="$(grep -E '^OPENAI_API_KEY=' .env || true)"
fi

cat > .env <<EOF
CIT_PORT=8794
CIT_OPENAI_MODEL=gpt-4.1-mini
${KEY_LINE:-OPENAI_API_KEY=}
EOF
chmod 600 .env

# Stop any process listening on 8794/8790
for p in 8794 8790; do
  PID="$(lsof -ti tcp:$p 2>/dev/null || true)"
  if [ -n "$PID" ]; then
    kill -9 $PID || true
  fi
done

# Start CIT
export $(grep -v '^#' .env | xargs) || true
nohup env CIT_PORT=8794 python server/cit_server.py > logs/cit_8794.log 2>&1 &

sleep 1

echo "[HEALTH]"
curl -sS "http://127.0.0.1:8794/health" || true
echo
echo "OK: CIT running on :8794 (log: $BASE/logs/cit_8794.log)"
