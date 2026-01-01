#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

./citctl.sh stop || true

python - <<'PY'
from pathlib import Path
import re

p = Path("server/cit_server.py")
s = p.read_text(encoding="utf-8", errors="ignore")

# Ensure imports we need
if not re.search(r'^\s*from\s+pathlib\s+import\s+Path\b', s, re.M):
    m = re.search(r'(?:^import[^\n]*\n|^from[^\n]*\n)+', s, re.M)
    ins = m.end() if m else 0
    s = s[:ins] + "from pathlib import Path\n" + s[ins:]

# Replace ANY existing _get_openai_key() function with a safe version (no recursion)
pattern = re.compile(r'^\s*def\s+_get_openai_key\s*\(\s*\)\s*:\s*\n(?:^[ \t]+.*\n)+', re.M)

safe_impl = (
'def _get_openai_key():\n'
'    """Return OpenAI API key from CIT_OPENAI_API_KEY or OPENAI_API_KEY or .env. No recursion."""\n'
'    k = (os.getenv("CIT_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") or "").strip()\n'
'    if k:\n'
'        return k\n'
'    # fallback: read from repo .env\n'
'    try:\n'
'        base = Path(__file__).resolve().parents[1]\n'
'        envp = base / ".env"\n'
'        if envp.exists():\n'
'            for line in envp.read_text(encoding="utf-8", errors="ignore").splitlines():\n'
'                line = line.strip()\n'
'                if not line or line.startswith("#") or "=" not in line:\n'
'                    continue\n'
'                kk, vv = line.split("=", 1)\n'
'                kk = kk.strip()\n'
'                vv = vv.strip().strip(\'"\').strip(\"'\")\n'
'                if kk in ("OPENAI_API_KEY", "CIT_OPENAI_API_KEY") and vv:\n'
'                    return vv\n'
'    except Exception:\n'
'        pass\n'
'    return ""\n'
)

if not pattern.search(s):
    raise SystemExit("Could not find def _get_openai_key() to replace")

s = pattern.sub(safe_impl + "\n", s, count=1)

p.write_text(s, encoding="utf-8")
print("OK: replaced _get_openai_key() with safe non-recursive implementation")
PY

git add server/cit_server.py || true
git commit -m "fix: _get_openai_key recursion (safe resolver)" || true

./citctl.sh start

echo "[CHECK] /api/chat (message)"
curl -sS --max-time 25 -X POST http://127.0.0.1:8794/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"тест"}' && echo
