#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

./citctl.sh stop || true

# 1) Patch citctl.sh to always provide OPENAI_API_KEY to the server process
python - <<'PY'
from pathlib import Path
import re

p = Path("citctl.sh")
s = p.read_text(encoding="utf-8", errors="ignore")

marker = "CIT_OPENAI_KEY_ALIAS_V1"
if marker not in s:
    # Insert near the top after set -euo pipefail if present
    m = re.search(r'^\s*set\s+-euo\s+pipefail\s*\n', s, re.M)
    insert_at = m.end() if m else 0
    block = f'''
# --- {marker} ---
# Provide OPENAI_API_KEY for code that expects the standard env var.
# Prefer CIT_OPENAI_API_KEY if present.
if [ -n "${{CIT_OPENAI_API_KEY:-}}" ] && [ -z "${{OPENAI_API_KEY:-}}" ]; then
  export OPENAI_API_KEY="$CIT_OPENAI_API_KEY"
fi
# --- /{marker} ---
'''
    s = s[:insert_at] + block + s[insert_at:]

p.write_text(s, encoding="utf-8")
print("OK: patched citctl.sh (OPENAI_API_KEY alias)")
PY
chmod +x citctl.sh

# 2) Patch server to accept both env var names (belt + suspenders)
python - <<'PY'
from pathlib import Path
import re

p = Path("server/cit_server.py")
s = p.read_text(encoding="utf-8", errors="ignore")

marker = "CIT_OPENAI_KEY_READ_V1"
if marker not in s:
    # Replace strict OPENAI_API_KEY lookup with fallback if possible
    # We patch by inserting a helper function near imports.
    helper = r'''
# --- CIT_OPENAI_KEY_READ_V1 ---
def _get_openai_key():
    return (os.getenv("CIT_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") or "").strip()
# --- /CIT_OPENAI_KEY_READ_V1 ---
'''
    # Insert after imports block
    m = re.search(r'(?:^import[^\n]*\n|^from[^\n]*\n)+', s, re.M)
    insert_at = m.end() if m else 0
    s = s[:insert_at] + helper + s[insert_at:]

    # Now swap common patterns:
    #   os.getenv("OPENAI_API_KEY") -> _get_openai_key()
    s = s.replace('os.getenv("OPENAI_API_KEY")', '_get_openai_key()')

p.write_text(s, encoding="utf-8")
print("OK: patched server/cit_server.py (key fallback)")
PY

# 3) Commit locally (no auto-push)
git add citctl.sh server/cit_server.py || true
git commit -m "fix: alias CIT_OPENAI_API_KEY -> OPENAI_API_KEY for chat" || true

# 4) Start with explicit model (key will be injected if set in shell/.env)
export CIT_OPENAI_MODEL="${CIT_OPENAI_MODEL:-gpt-4.1-mini}"
./citctl.sh start

# 5) Verify
echo "[CHECK] /health"
curl -sS --max-time 2 http://127.0.0.1:8794/health && echo

echo "[CHECK] /api/chat (message)"
curl -sS --max-time 10 -X POST http://127.0.0.1:8794/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"тест"}' && echo
