#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

./citctl.sh stop || true

python - <<'PY'
from pathlib import Path
import re

p = Path("server/cit_server.py")
s = p.read_text(encoding="utf-8", errors="ignore")

# 1) Ensure robust key getter exists (CIT + OPENAI + .env)
if "CIT_KEY_RESOLVER_V1" not in s:
    helper = r'''
# --- CIT_KEY_RESOLVER_V1 ---
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
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k in ("OPENAI_API_KEY", "CIT_OPENAI_API_KEY") and v:
                return v
        return ""
    except Exception:
        return ""

def _get_openai_key():
    return (os.getenv("CIT_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") or _read_dotenv_key() or "").strip()
# --- /CIT_KEY_RESOLVER_V1 ---
'''
    # insert after imports block
    m = re.search(r'(?:^import[^\n]*\n|^from[^\n]*\n)+', s, re.M)
    ins = m.end() if m else 0
    s = s[:ins] + helper + s[ins:]

# 2) Patch the exact error-return line to use resolver + force env
# Replace: return {"error": "OPENAI_API_KEY is not set"}
# With a small guard that resolves key, sets env, or returns error.
marker = "CIT_KEY_GUARD_AT_332_V1"
if marker not in s:
    # Find the line containing the exact return
    target = 'return {"error": "OPENAI_API_KEY is not set"}'
    idx = s.find(target)
    if idx == -1:
        raise SystemExit("Target error return not found (file changed?)")

    # Determine indent of that return line
    line_start = s.rfind("\n", 0, idx) + 1
    line = s[line_start: s.find("\n", idx)]
    indent = re.match(r'^(\s*)', line).group(1)

    repl = f'''{indent}# --- {marker} ---
{indent}k = _get_openai_key()
{indent}if not k:
{indent}    return {{"error": "OPENAI_API_KEY is not set"}}
{indent}os.environ["OPENAI_API_KEY"] = k
{indent}os.environ["CIT_OPENAI_API_KEY"] = k
{indent}# --- /{marker} ---'''

    s = s[:line_start] + repl + s[s.find("\n", idx):]

p.write_text(s, encoding="utf-8")
print("OK: patched key check at error line to use _get_openai_key() + force env")
PY

git add server/cit_server.py || true
git commit -m "fix: key resolver + patch OPENAI_API_KEY check (line 332)" || true

./citctl.sh start

echo "[CHECK] /health"
curl -sS --max-time 2 http://127.0.0.1:8794/health && echo

echo "[CHECK] /api/chat (message)"
curl -sS --max-time 25 -X POST http://127.0.0.1:8794/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"тест"}' && echo
