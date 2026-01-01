#!/usr/bin/env bash
set -euo pipefail
cd ~/cimeika/cit

echo "== RUNNING =="
./citctl.sh status || true
echo

echo "== ROUTES (cit_server.py) =="
python - <<'PY'
import re
from pathlib import Path

p = Path("server/cit_server.py")
s = p.read_text(encoding="utf-8", errors="ignore")

def routes(method):
    # crude but effective: looks for self.path == "/something"
    out = set(re.findall(rf'\b{method}\b[\s\S]*?self\.path\s*==\s*["\']([^"\']+)["\']', s))
    # also catch: if self.path.startswith("/x")
    out |= set(re.findall(rf'\b{method}\b[\s\S]*?self\.path\.startswith\(\s*["\']([^"\']+)["\']\s*\)', s))
    return sorted(out)

get = routes("do_GET")
post = routes("do_POST")

print("[GET]")
for r in get[:200]:
    print(" ", r)
print("\n[POST]")
for r in post[:200]:
    print(" ", r)

# Heuristic: likely chat endpoints
cand = sorted({r for r in (get+post) if "chat" in r or "message" in r or "api" in r})
print("\n[CANDIDATES]")
for r in cand[:200]:
    print(" ", r)
PY
echo

echo "== QUICK PROBE (common endpoints) =="
for ep in /api/chat /chat /v1/chat /api/message /message; do
  echo "-- POST $ep"
  curl -sS -m 3 -X POST "http://127.0.0.1:8794$ep" \
    -H "Content-Type: application/json" \
    -d '{"ping":true}' || echo "ERR"
  echo
done

echo "== LAST LOGS =="
tail -n 80 logs/cit_8794.log || true
