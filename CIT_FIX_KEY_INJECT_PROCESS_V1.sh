#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

echo "== DOTENV CHECK =="
if [ -f .env ]; then
  echo "ENV: exists: $(pwd)/.env"
  if grep -qE '^(OPENAI_API_KEY|CIT_OPENAI_API_KEY)=' .env; then
    echo "ENV: has key line: YES"
  else
    echo "ENV: has key line: NO"
  fi
else
  echo "ENV: missing: $(pwd)/.env"
fi

echo
echo "== RUNTIME ENV CHECK (shell) =="
python - <<'PY'
import os
k1 = os.getenv("CIT_OPENAI_API_KEY","")
k2 = os.getenv("OPENAI_API_KEY","")
print("CIT_OPENAI_API_KEY:", "SET" if k1 else "NOT_SET", "len=", len(k1))
print("OPENAI_API_KEY:", "SET" if k2 else "NOT_SET", "len=", len(k2))
PY

get_dotenv_key() {
  [ -f .env ] || return 0
  # prefer CIT_ then OPENAI_
  awk -F= '
    $1=="CIT_OPENAI_API_KEY" && $2!="" {print $2; exit}
    $1=="OPENAI_API_KEY" && $2!="" {print $2; exit}
  ' .env | sed 's/^ *//; s/ *$//; s/^"//; s/"$//; s/^'\''//; s/'\''$//'
}

KEY="${CIT_OPENAI_API_KEY:-${OPENAI_API_KEY:-}}"
if [ -z "${KEY:-}" ]; then
  KEY="$(get_dotenv_key || true)"
fi

if [ -z "${KEY:-}" ]; then
  echo
  echo "FAIL: key NOT FOUND (neither shell env nor .env)."
  echo "ACTION: add ONE line to: $(pwd)/.env"
  echo "OPENAI_API_KEY=sk-..."
  exit 2
fi

export OPENAI_API_KEY="$KEY"
export CIT_OPENAI_API_KEY="$KEY"

echo
echo "== RESTART =="
./citctl.sh stop || true
./citctl.sh start

echo
echo "[CHECK] /api/chat (message)"
curl -sS --max-time 25 -X POST http://127.0.0.1:8794/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"тест"}' && echo

echo
echo "== LAST LOGS (tail 40) =="
tail -n 40 logs/cit_8794.log || true
