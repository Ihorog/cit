#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

./citctl.sh stop || true

python - <<'PY'
from pathlib import Path
import re

p = Path("server/cit_server.py")
s = p.read_text(encoding="utf-8", errors="ignore")

# 1) Ensure we have alias checks inside do_POST before the not_found handling.
# We locate the do_POST function and inject alias mapping near its top.
m = re.search(r'\n(?P<indent>[ \t]*)def do_POST\(\s*self\s*\)\s*:\s*\n', s)
if not m:
    raise SystemExit("do_POST not found in cit_server.py")

indent = m.group("indent")
start = m.end()

alias_block = f"""{indent}    # --- CHAT ALIASES (CIT_CHAT_ALIASES_V1) ---
{indent}    # accept common client endpoints and route them to /chat handler
{indent}    if self.path in ("/api/chat", "/v1/chat", "/api/message", "/message"):
{indent}        self.path = "/chat"
{indent}    # --- /CHAT ALIASES ---
"""

# Insert only if not already present
if "CIT_CHAT_ALIASES_V1" not in s:
    s = s[:start] + alias_block + s[start:]

# 2) Make message extraction flexible.
# Replace a strict '"message"' extraction pattern with a multi-key fallback.
# We patch conservatively: if we find 'missing_message' error block, we ensure it checks other keys too.

# Look for common pattern that triggers missing_message
# We'll inject a normalization snippet right after JSON payload is parsed into `data` (or similar).
# Heuristic: find first occurrence of "json.loads(" inside do_POST and add normalization after it.
do_post_region = s[start:start+12000]
j = re.search(r'json\.loads\([^\)]*\)', do_post_region)
if j:
    # find end of the line containing json.loads(...)
    line_end = do_post_region.find("\n", j.end())
    if line_end == -1:
        line_end = j.end()
    inject_at = start + line_end + 1

    norm = f"""{indent}    # --- PAYLOAD NORMALIZATION (CIT_CHAT_PAYLOAD_V1) ---
{indent}    # Accept multiple field names from different clients
{indent}    try:
{indent}        _m = None
{indent}        if isinstance(data, dict):
{indent}            _m = data.get("message") or data.get("text") or data.get("prompt") or data.get("input")
{indent}            if _m is not None and "message" not in data:
{indent}                data["message"] = _m
{indent}    except Exception:
{indent}        pass
{indent}    # --- /PAYLOAD NORMALIZATION ---
"""
    if "CIT_CHAT_PAYLOAD_V1" not in s:
        s = s[:inject_at] + norm + s[inject_at:]

# 3) Ensure /chat returns a consistent shape: ok + reply when possible.
# If it already returns {"error":"missing_message"} we keep that, but also allow "ping".
# If request contains {"ping":true} return ok:true quickly.
if "CIT_CHAT_PING_V1" not in s:
    # Inject ping handling near top of do_POST after aliasing
    ping_block = f"""{indent}    # --- PING (CIT_CHAT_PING_V1) ---
{indent}    try:
{indent}        if isinstance(data, dict) and data.get("ping") is True:
{indent}            body = b'{{"ok": true, "pong": true}}'
{indent}            self.send_response(200)
{indent}            self.send_header("Content-Type", "application/json; charset=utf-8")
{indent}            self.send_header("Content-Length", str(len(body)))
{indent}            self.end_headers()
{indent}            self.wfile.write(body)
{indent}            return
{indent}    except Exception:
{indent}        pass
{indent}    # --- /PING ---
"""
    # put after alias block we inserted (or after do_POST start)
    insert_pos = start
    # if alias block exists, insert after it
    k = s.find("CIT_CHAT_ALIASES_V1", start-500, start+2000)
    if k != -1:
        # insert after alias block end marker
        endm = s.find("# --- /CHAT ALIASES ---", k)
        if endm != -1:
            endline = s.find("\n", endm)
            insert_pos = endline + 1 if endline != -1 else endm
    s = s[:insert_pos] + ping_block + s[insert_pos:]

p.write_text(s, encoding="utf-8")
print("OK: patched chat aliases + payload normalization")
PY

git add server/cit_server.py || true
git commit -m "fix: chat aliases (/api/chat,/v1/chat) + flexible payload keys" || true

./citctl.sh start

echo "[CHECK] /health"
curl -sS --max-time 2 http://127.0.0.1:8794/health && echo

echo "[CHECK] /api/chat ping"
curl -sS --max-time 2 -X POST http://127.0.0.1:8794/api/chat \
  -H "Content-Type: application/json" -d '{"ping":true}' && echo

echo "[CHECK] /api/chat message"
curl -sS --max-time 4 -X POST http://127.0.0.1:8794/api/chat \
  -H "Content-Type: application/json" -d '{"text":"тест"}' && echo
