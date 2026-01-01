#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

./citctl.sh stop || true

python - <<'PY'
from pathlib import Path
import re

p = Path("server/cit_server.py")
s = p.read_text(encoding="utf-8", errors="ignore")

before = s

# 1) Replace the exact recursive return (most common variants)
s = s.replace(
    'return (os.getenv("CIT_OPENAI_API_KEY") or _get_openai_key() or "").strip()',
    'return (os.getenv("CIT_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") or _read_dotenv_key() or "").strip()'
)

s = s.replace(
    "return (os.getenv('CIT_OPENAI_API_KEY') or _get_openai_key() or '').strip()",
    "return (os.getenv('CIT_OPENAI_API_KEY') or os.getenv('OPENAI_API_KEY') or _read_dotenv_key() or '').strip()"
)

# 2) If still present, do a regex replace (covers spacing)
s = re.sub(
    r'return\s*\(\s*os\.getenv\(\s*["\']CIT_OPENAI_API_KEY["\']\s*\)\s*or\s*_get_openai_key\(\s*\)\s*or\s*["\']{0,1}["\']{0,1}\s*\)\.strip\(\s*\)',
    'return (os.getenv("CIT_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") or _read_dotenv_key() or "").strip()',
    s
)

# 3) Sanity: ensure no remaining self-call inside _get_openai_key return
if "_get_openai_key() or" in s or "or _get_openai_key()" in s:
    # we only fail if it appears on a return line (strong signal)
    bad = [ln for ln in s.splitlines() if "_get_openai_key()" in ln and "return" in ln]
    if bad:
        raise SystemExit("STILL BAD return line(s):\n" + "\n".join(bad))

if s == before:
    print("WARN: no changes applied (pattern not found). Showing nearby lines for manual inspection:")
    # print function area around first occurrence of '_get_openai_key' text
    lines = s.splitlines()
    idx = next((i for i,l in enumerate(lines) if "_get_openai_key" in l), None)
    if idx is not None:
        for j in range(max(0, idx-5), min(len(lines), idx+25)):
            print(f"{j+1:04d}: {lines[j]}")
    else:
        print("No _get_openai_key text found in file.")
else:
    p.write_text(s, encoding="utf-8")
    print("OK: recursion return line patched")
PY

git add server/cit_server.py || true
git commit -m "fix: remove recursion from _get_openai_key return line" || true

./citctl.sh start

echo "[CHECK] /api/chat (message)"
curl -sS --max-time 25 -X POST http://127.0.0.1:8794/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"тест"}' && echo
