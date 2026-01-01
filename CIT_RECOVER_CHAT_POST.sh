#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

# 0) Ensure CIT is running even if patch fails later
safe_start() { ./citctl.sh start || true; }

./citctl.sh stop || true

python - <<'PY'
from pathlib import Path
import re

p = Path("server/cit_server.py")
s = p.read_text(encoding="utf-8")

# Patch strategy:
# - Find any def do_POST(self): block that contains /ui/api/pull or /ui/api/push
# - Ensure it ends with: return super().do_POST()
# - Remove any "send_response(404)" default that would swallow other POST routes.

def patch_one(block: str, indent: str) -> str:
    # Remove 404 default at end (best-effort)
    block2 = re.sub(rf'\n{indent}\s*self\.send_response\(404\)[\s\S]*?{indent}\s*self\.end_headers\(\)\s*', '\n', block, flags=re.S)
    # Ensure delegation exists
    if re.search(r'return\s+super\(\)\.do_POST\(\)', block2) is None:
        block2 = block2.rstrip() + f"\n\n{indent}    return super().do_POST()\n"
    return block2

changed = False

# Find do_POST blocks inside classes by indentation.
# This is robust enough for typical BaseHTTPRequestHandler subclasses.
pattern = re.compile(r'\n(?P<indent>[ \t]*)def do_POST\(\s*self\s*\)\s*:\s*\n(?P<body>[\s\S]*?)(?=\n(?P=indent)def |\nclass |\n\s*def main|\Z)', re.M)
out = []
pos = 0

for m in pattern.finditer(s):
    indent = m.group("indent")
    body = m.group("body")
    full = s[m.start():m.end()]

    needs = ("/ui/api/pull" in full) or ("/ui/api/push" in full)
    if needs:
        new_body = patch_one(body, indent)
        if new_body != body:
            full_new = full.replace(body, new_body)
            out.append(s[pos:m.start()] + full_new)
            pos = m.end()
            changed = True

if changed:
    out.append(s[pos:])
    s2 = "".join(out)
    p.write_text(s2, encoding="utf-8")
    print("OK: patched UI do_POST to delegate to super().do_POST() (chat-safe)")
else:
    print("OK: no UI do_POST block found to patch (nothing changed)")

PY

# Commit if anything changed
git add server/cit_server.py || true
git diff --cached --quiet || git commit -m "fix: UI do_POST delegates to base handler (restore chat)" || true

# 1) Start CIT
safe_start

# 2) Hard health check
curl -sS --max-time 2 "http://127.0.0.1:8794/health" && echo
