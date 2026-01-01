#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

FILE="server/cit_server.py"

# Stop service to avoid partial writes while running
./citctl.sh stop || true

# Patch: prefer CIT_OPENAI_MODEL env, fallback only if missing
python - <<'PY'
import re
from pathlib import Path

p = Path("server/cit_server.py")
s = p.read_text(encoding="utf-8")

# Ensure we import os at top (if missing)
if not re.search(r'^\s*import\s+os\b', s, re.M):
    s = re.sub(r'^(from __future__ import .*\n)?', lambda m: (m.group(0) or "") + "import os\n", s, count=1)

# Replace common model default patterns to env-based
patterns = [
    r'OPENAI_MODEL\s*=\s*["\'][^"\']+["\']',
    r'MODEL\s*=\s*["\'][^"\']+["\']',
    r'DEFAULT_MODEL\s*=\s*["\'][^"\']+["\']',
]
replaced_any = False
for pat in patterns:
    if re.search(pat, s):
        s = re.sub(pat, 'OPENAI_MODEL = os.getenv("CIT_OPENAI_MODEL", "gpt-4.1-mini")', s, count=1)
        replaced_any = True
        break

# If no obvious constant found, inject a safe global near top
if not replaced_any and 'CIT_OPENAI_MODEL' not in s:
    # Insert after imports block
    m = re.search(r'(?:^import[^\n]*\n|^from[^\n]*\n)+', s, re.M)
    insert_at = m.end() if m else 0
    inject = '\n# === Model selection (env-first) ===\nOPENAI_MODEL = os.getenv("CIT_OPENAI_MODEL", "gpt-4.1-mini")\n'
    s = s[:insert_at] + inject + s[insert_at:]

# Ensure /health uses OPENAI_MODEL variable if it returns "model"
# Replace '"model": "something"' with '"model": OPENAI_MODEL' if JSON built as dict.
s = re.sub(
    r'("model"\s*:\s*)["\'][^"\']+["\']',
    r'\1OPENAI_MODEL',
    s
)

p.write_text(s, encoding="utf-8")
print("OK: patched", p)
PY

# Commit patch locally (optional) but do not push automatically
git add "$FILE" || true
git commit -m "fix: model from CIT_OPENAI_MODEL env" || true

# Restart with explicit model
export CIT_OPENAI_MODEL="gpt-4.1-mini"
./citctl.sh start
./citctl.sh health
