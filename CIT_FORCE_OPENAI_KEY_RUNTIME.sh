#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

./citctl.sh stop || true

python - <<'PY'
from pathlib import Path
import re

p = Path("server/cit_server.py")
s = p.read_text(encoding="utf-8", errors="ignore")

# Ensure os is imported (it should be, but safe)
if not re.search(r'^\s*import\s+os\b', s, re.M):
    # insert near top
    s = "import os\n" + s

# 1) Add robust key getter that also reads .env (without printing)
marker = "CIT_KEY_FORCE_V2"
if marker not in s:
    helper = r'''
# --- CIT_KEY_FORCE_V2 ---
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
            k,v = line.split("=",1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k in ("OPENAI_API_KEY","CIT_OPENAI_API_KEY") and v:
                return v
        return ""
    except Exception:
        return ""

def _get_openai_key():
    return (os.getenv("CIT_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") or _read_dotenv_key() or "").strip()

def _force_openai_key_runtime():
    k = _get_openai_key()
    if not k:
        return ""
    # env
    os.environ["OPENAI_API_KEY"] = k
    os.environ["CIT_OPENAI_API_KEY"] = k
    # old SDK
    try:
        import openai  # type: ignore
        openai.api_key = k
    except Exception:
        pass
    return k
# --- /CIT_KEY_FORCE_V2 ---
'''
    # insert after imports block
    m = re.search(r'(?:^import[^\n]*\n|^from[^\n]*\n)+', s, re.M)
    ins = m.end() if m else 0
    s = s[:ins] + helper + s[ins:]

# 2) Force runtime key inside /chat handler branch
m = re.search(r'if\s+self\.path\s*==\s*["\']/chat["\']\s*:\s*\n', s)
if not m:
    raise SystemExit('"/chat" handler not found')

line_end = s.find("\n", m.end())
insert_at = line_end + 1
next_line = s[insert_at: s.find("\n", insert_at)]
indent = re.match(r'^(\s*)', next_line).group(1)

if "CIT_FORCE_OPENAI_KEY_IN_CHAT_V2" not in s:
    block = f"""{indent}# --- CIT_FORCE_OPENAI_KEY_IN_CHAT_V2 ---
{indent}_force_openai_key_runtime()
{indent}# --- /CIT_FORCE_OPENAI_KEY_IN_CHAT_V2 ---
"""
    s = s[:insert_at] + block + s[insert_at:]

# 3) If code uses new SDK client "OpenAI()" without api_key, inject it
# Replace ONLY exact empty constructor OpenAI() -> OpenAI(api_key=_get_openai_key())
s2 = re.sub(r'\bOpenAI\(\s*\)', 'OpenAI(api_key=_get_openai_key())', s)
s = s2

p.write_text(s, encoding="utf-8")
print("OK: forced key runtime + OpenAI() api_key injection (where applicable)")
PY

git add server/cit_server.py || true
git commit -m "fix: force OpenAI key at runtime + inject api_key into client" || true

./citctl.sh start

echo "[CHECK] /health"
curl -sS --max-time 2 http://127.0.0.1:8794/health && echo

echo "[CHECK] /api/chat (message)"
curl -sS --max-time 25 -X POST http://127.0.0.1:8794/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"тест"}' && echo
