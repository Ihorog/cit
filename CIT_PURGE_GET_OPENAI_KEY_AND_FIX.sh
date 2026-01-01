#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

./citctl.sh stop || true

python - <<'PY'
from pathlib import Path
import re

p = Path("server/cit_server.py")
s = p.read_text(encoding="utf-8", errors="ignore")

# Remove ALL existing def _get_openai_key() blocks
pat = re.compile(r'^\s*def\s+_get_openai_key\s*\s*\s*:\s*\n(?:^[ \t]+.*\n)+', re.M)
matches = list(pat.finditer(s))
print("FOUND _get_openai_key defs:", len(matches))
s = pat.sub("", s)

# Ensure import
if not re.search(r'^\s*from\s+pathlib\s+import\s+Path\b', s, re.M):
    m = re.search(r'(?:^import[^\n]*\n|^from[^\n]*\n)+', s, re.M)
    ins = m.end() if m else 0
    s = s[:ins] + "from pathlib import Path\n" + s[ins:]

# Insert single safe resolver after imports
marker = "CIT_SINGLE_KEY_RESOLVER_V1"
if marker not in s:
    impl = f'''
# --- {marker} ---
def _read_dotenv_key():
    try:
        base = Path(__file__).resolve().parents[1]
        envp = base / ".env"
        if not envp.exists():
            return ""
        for line in envp.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            kk, vv = line.split("=", 1)
            kk = kk.strip()
            vv = vv.strip().strip('"').strip("'")
            if kk in ("OPENAI_API_KEY", "CIT_OPENAI_API_KEY") and vv:
                return vv
        return ""
    except Exception:
        return ""

def _get_openai_key():
    """Single source of truth. No recursion."""
    return (os.getenv("CIT_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") or _read_dotenv_key() or "").strip()
# --- /{marker} ---
'''.lstrip()

    m = re.search(r'(?:^import[^\n]*\n|^from[^\n]*\n)+', s, re.M)
    ins = m.end() if m else 0
    s = s[:ins] + impl + "\n" + s[ins:]

p.write_text(s, encoding="utf-8")
print("OK: purged duplicates and installed single safe _get_openai_key()")
PY

git add server/cit_server.py || true
git commit -m "fix: purge duplicate _get_openai_key and install single safe resolver" || true

./citctl.sh start

echo "[CHECK] /api/chat (message)"
curl -sS --max-time 25 -X POST http://127.0.0.1:8794/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"тест"}' && echo
