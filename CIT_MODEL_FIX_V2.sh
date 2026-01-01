#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

# stop clean
./citctl.sh stop || true

echo "[1/4] Patch citctl default model -> gpt-4.1-mini"
python - <<'PY'
from pathlib import Path
import re

p = Path("citctl.sh")
s = p.read_text(encoding="utf-8")

# Replace default model fallback in citctl
s2 = re.sub(r'\$\{CIT_OPENAI_MODEL:-gpt-4o-mini\}', '${CIT_OPENAI_MODEL:-gpt-4.1-mini}', s)
s2 = re.sub(r'CIT_OPENAI_MODEL:-gpt-4o-mini', 'CIT_OPENAI_MODEL:-gpt-4.1-mini', s2)

p.write_text(s2, encoding="utf-8")
print("OK: patched", p)
PY
chmod +x citctl.sh

echo "[2/4] Patch /health response in server/cit_server.py to reflect CIT_OPENAI_MODEL"
python - <<'PY'
from pathlib import Path
import re

p = Path("server/cit_server.py")
s = p.read_text(encoding="utf-8")

# Ensure os imported
if not re.search(r'^\s*import\s+os\b', s, re.M):
    s = "import os\n" + s

# Force /health JSON to use env (best-effort generic patch):
# Replace any occurrence of '"model": "<something>"' in python dict-like construction
# and also JSON string fragments.
s = re.sub(r'("model"\s*:\s*)["\']gpt-[^"\']+["\']', r'\1os.getenv("CIT_OPENAI_MODEL","gpt-4.1-mini")', s)

# If health response is created as a dict without quotes (e.g., {"model": OPENAI_MODEL}),
# ensure it points to env var if OPENAI_MODEL isn't used.
# (No-op if not found)
s = re.sub(r'("model"\s*:\s*)(OPENAI_MODEL|MODEL|DEFAULT_MODEL)\b', r'\1os.getenv("CIT_OPENAI_MODEL","gpt-4.1-mini")', s)

p.write_text(s, encoding="utf-8")
print("OK: patched", p)
PY

echo "[3/4] Commit (local only)"
git add citctl.sh server/cit_server.py || true
git commit -m "fix: citctl default model + health reflects CIT_OPENAI_MODEL" || true

echo "[4/4] Restart with explicit env + verify"
export CIT_OPENAI_MODEL="gpt-4.1-mini"
./citctl.sh start
./citctl.sh health
