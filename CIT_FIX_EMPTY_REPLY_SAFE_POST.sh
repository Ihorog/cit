#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

./citctl.sh stop || true

python - <<'PY'
from pathlib import Path
import re

p = Path("server/cit_server.py")
s = p.read_text(encoding="utf-8", errors="ignore")

marker = "CIT_SAFE_POST_WRAPPER_V1"
if marker in s:
    print("OK: safe POST wrapper already installed")
    raise SystemExit(0)

# 1) Ensure traceback import exists
if not re.search(r'^\s*import\s+traceback\b', s, re.M):
    m = re.search(r'(?:^import[^\n]*\n|^from[^\n]*\n)+', s, re.M)
    ins = m.end() if m else 0
    s = s[:ins] + "import traceback\n" + s[ins:]

# 2) Find do_POST
m = re.search(r'^\s*def\s+do_POST\s*\(\s*self\s*\)\s*:\s*\n', s, re.M)
if not m:
    raise SystemExit("do_POST not found")

# Rename existing do_POST -> _do_POST_impl
s = s[:m.start()] + re.sub(r'def\s+do_POST', 'def _do_POST_impl', s[m.start():], count=1)

# Insert new safe do_POST that calls _do_POST_impl
# Determine indent from original def line
def_line_start = s.rfind("\n", 0, m.start()) + 1
# After rename, find the renamed def line to get indent
m2 = re.search(r'^(\s*)def\s+_do_POST_impl\s*\(\s*self\s*\)\s*:\s*\n', s, re.M)
indent = m2.group(1) if m2 else ""

wrapper = f"""{indent}# --- {marker} ---
{indent}def do_POST(self):
{indent}    try:
{indent}        return self._do_POST_impl()
{indent}    except Exception as e:
{indent}        # Never drop connection without a JSON response
{indent}        try:
{indent}            tb = traceback.format_exc(limit=12)
{indent}        except Exception:
{indent}            tb = "traceback_unavailable"
{indent}        try:
{indent}            self.send_response(500)
{indent}            self.send_header("Content-Type", "application/json; charset=utf-8")
{indent}            self.end_headers()
{indent}            import json
{indent}            payload = {{"ok": False, "error": str(e), "type": e.__class__.__name__, "trace": tb}}
{indent}            self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
{indent}        except Exception:
{indent}            pass
{indent}# --- /{marker} ---

"""

# Insert wrapper just before _do_POST_impl definition
if m2:
    s = s[:m2.start()] + wrapper + s[m2.start():]
else:
    # fallback: insert near the end if regex fails
    s = s + "\n" + wrapper

p.write_text(s, encoding="utf-8")
print("OK: installed safe do_POST wrapper (prevents Empty reply)")
PY

git add server/cit_server.py || true
git commit -m "fix: prevent empty reply by wrapping do_POST with safe JSON error" || true

./citctl.sh start

echo "[CHECK] /api/chat (message)"
curl -sS --max-time 25 -X POST http://127.0.0.1:8794/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"тест"}' && echo
