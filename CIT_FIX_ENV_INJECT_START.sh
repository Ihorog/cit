#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

./citctl.sh stop || true

python - <<'PY'
from pathlib import Path
import re

p = Path("citctl.sh")
s = p.read_text(encoding="utf-8", errors="ignore")

marker = "CIT_ENV_INJECT_V2"
if marker in s:
    print("OK: citctl already has env-inject v2")
    raise SystemExit(0)

# 1) Ensure .env is loaded (safe, no secrets printed)
load_env = r'''
# --- CIT_ENV_INJECT_V2 ---
# Load .env if present (simple KEY=VALUE lines). Does not print values.
if [ -f ".env" ]; then
  set -a
  # shellcheck disable=SC1091
  . ".env"
  set +a
fi

# Ensure OPENAI_API_KEY is present if CIT_OPENAI_API_KEY exists
if [ -n "${CIT_OPENAI_API_KEY:-}" ] && [ -z "${OPENAI_API_KEY:-}" ]; then
  export OPENAI_API_KEY="$CIT_OPENAI_API_KEY"
fi
# --- /CIT_ENV_INJECT_V2 ---
'''

# Insert after set -euo pipefail
m = re.search(r'^\s*set\s+-euo\s+pipefail\s*\n', s, re.M)
insert_at = m.end() if m else 0
s = s[:insert_at] + load_env + s[insert_at:]

# 2) Force env injection on python start
# Replace a line that starts python server/cit_server.py (or similar) with env-prefixed version.
# We patch conservatively: find the first occurrence of "python" that references "server/cit_server.py"
pat = re.compile(r'^(?P<indent>\s*)(?P<cmd>(?:nohup\s+)?python(?:3)?\s+.*server/cit_server\.py.*)$', re.M)
mm = pat.search(s)
if not mm:
    # fallback: look for "server/cit_server.py" and prefix the line
    lines = s.splitlines(True)
    for i, line in enumerate(lines):
        if "server/cit_server.py" in line and "python" in line:
            mm = True
            indent = re.match(r'^(\s*)', line).group(1)
            lines[i] = indent + 'env OPENAI_API_KEY="${OPENAI_API_KEY:-}" CIT_OPENAI_API_KEY="${CIT_OPENAI_API_KEY:-}" CIT_OPENAI_MODEL="${CIT_OPENAI_MODEL:-}" ' + line.lstrip()
            s = "".join(lines)
            break
    if mm is not True:
        print("WARN: could not locate python start line in citctl.sh; manual start may be used")
else:
    indent = mm.group("indent")
    cmd = mm.group("cmd")
    repl = indent + 'env OPENAI_API_KEY="${OPENAI_API_KEY:-}" CIT_OPENAI_API_KEY="${CIT_OPENAI_API_KEY:-}" CIT_OPENAI_MODEL="${CIT_OPENAI_MODEL:-}" ' + cmd
    s = s[:mm.start("cmd")] + repl + s[mm.end("cmd"):]

p.write_text(s, encoding="utf-8")
print("OK: patched citctl.sh to load .env and inject OPENAI_API_KEY into process")
PY

chmod +x citctl.sh
git add citctl.sh || true
git commit -m "fix: citctl loads .env and injects OPENAI_API_KEY into server process" || true

# Start (now with guaranteed env)
./citctl.sh start

echo "[CHECK] /health"
curl -sS --max-time 2 http://127.0.0.1:8794/health && echo

echo "[CHECK] /api/chat (message)"
curl -sS --max-time 12 -X POST http://127.0.0.1:8794/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"тест"}' && echo
