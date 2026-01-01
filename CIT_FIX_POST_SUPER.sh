#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

./citctl.sh stop || true

python - <<'PY'
from pathlib import Path
import re

p = Path("server/cit_server.py")
s = p.read_text(encoding="utf-8")

# Find IntegratedHandler.do_POST block
m = re.search(r'class\s+IntegratedHandler\([^)]+\):[\s\S]*?\n(\s*)def do_POST\(\s*self\s*\):([\s\S]*?)(\n\1def |\nclass |\n\s*def main|\Z)', s)
if not m:
    raise SystemExit("do_POST in IntegratedHandler not found. Nothing to patch.")

indent = m.group(1)
body = m.group(2)

# If it already calls super, exit
if re.search(r'return\s+super\(\)\.do_POST\(\)', body):
    print("OK: do_POST already delegates to super()")
else:
    # Remove terminal 404 default if present, and replace with super delegation
    body2 = re.sub(rf'\n{indent}\s*self\.send_response\(404\).*?{indent}\s*self\.end_headers\(\)\s*', '\n', body, flags=re.S)

    # Ensure we have a fallback delegation
    # Add at end of body with correct indent
    body2 = body2.rstrip() + f"\n\n{indent}    return super().do_POST()\n"

    # Rebuild whole match region
    start = m.start(2)
    end = m.end(2)
    s = s[:start] + body2 + s[end:]

p.write_text(s, encoding="utf-8")
print("OK: patched do_POST to delegate to super()")
PY

git add server/cit_server.py || true
git commit -m "fix: IntegratedHandler do_POST delegates to base handler (restore chat)" || true

./citctl.sh start
./citctl.sh health
