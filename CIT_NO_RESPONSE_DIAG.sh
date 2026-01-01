#!/usr/bin/env bash
set -euo pipefail
cd ~/cimeika/cit

echo "== STATUS =="
./citctl.sh status || true
echo

echo "== HEALTH =="
curl -sS --max-time 2 http://127.0.0.1:8794/health && echo
echo

echo "== ROUTES QUICK =="
python - <<'PY'
from pathlib import Path
import re
s = Path("server/cit_server.py").read_text(encoding="utf-8", errors="ignore")
get = sorted(set(re.findall(r'self\.path\s*==\s*["\']([^"\']+)["\']', s)))
print("paths:", ", ".join(get[:60]))
print("has /chat:", "/chat" in s)
print("has /api/chat:", "/api/chat" in s)
print("has UI:", "/ui" in s)
print("markers:", "CIT_CHAT_ALIASES_V1" in s, "CIT_CHAT_PAYLOAD_V1" in s, "CIT_UI_INTEGRATED_V1" in s)
PY
echo

echo "== POST /chat (message) =="
curl -sS --max-time 6 -X POST http://127.0.0.1:8794/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"тест"}' && echo
echo

echo "== POST /api/chat (message) =="
curl -sS --max-time 6 -X POST http://127.0.0.1:8794/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"тест"}' && echo
echo

echo "== KEY PRESENCE (no secrets) =="
# show only set/unset + length, without printing the value
python - <<'PY'
import os
k = os.getenv("CIT_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") or ""
print("CIT_OPENAI_API_KEY/OPENAI_API_KEY:", "SET" if k else "NOT_SET", "len=", len(k))
m = os.getenv("CIT_OPENAI_MODEL","")
print("CIT_OPENAI_MODEL:", m if m else "(unset)")
PY
echo

echo "== LAST LOGS =="
tail -n 200 logs/cit_8794.log || true
