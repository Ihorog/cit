#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

./citctl.sh stop || true

python - <<'PY'
from pathlib import Path
import re, json

p = Path("server/cit_server.py")
s = p.read_text(encoding="utf-8", errors="ignore")

marker = "CIT_BILLING_REPLY_V2"
if marker in s:
    print("OK: patch already present")
else:
    # Helper (insert once after imports)
    helper = r'''
# --- CIT_BILLING_REPLY_V2 ---
def _inject_friendly_billing_reply(out):
    """
    If OpenAI returns billing_not_active, ensure UI gets a human reply (not empty).
    """
    try:
        if not isinstance(out, dict):
            return out
        if (out.get("reply") or "").strip():
            return out
        raw = out.get("raw") or {}
        # raw may be {"error": "HTTPError 429", "body": "...json..."}
        body = raw.get("body") if isinstance(raw, dict) else None
        if isinstance(body, str) and body.strip().startswith("{"):
            try:
                j = json.loads(body)
                err = (j.get("error") or {}) if isinstance(j, dict) else {}
                if err.get("code") == "billing_not_active":
                    out["ok"] = False
                    out["reply"] = "OpenAI API billing не активний для цього акаунта. Активуй білінг у platform.openai.com/account/billing і повтори."
            except Exception:
                pass
        return out
    except Exception:
        return out
# --- /CIT_BILLING_REPLY_V2 ---
'''
    imp = re.search(r'(?:^import[^\n]*\n|^from[^\n]*\n)+', s, re.M)
    ins = imp.end() if imp else 0
    s = s[:ins] + helper + s[ins:]

    # Patch immediately after out = call_openai(...)
    # Replace single line with 2 lines
    pattern = re.compile(r'(?m)^(?P<indent>\s*)out\s*=\s*call_openai\((?P<arg>[^)]*)\)\s*$')
    m = pattern.search(s)
    if not m:
        raise SystemExit("FAIL: cannot find line: out = call_openai(...)")

    indent = m.group("indent")
    arg = m.group("arg").strip()
    repl = f'{indent}out = call_openai({arg})\n{indent}out = _inject_friendly_billing_reply(out)  # {marker}'
    s = s[:m.start()] + repl + s[m.end():]

    p.write_text(s, encoding="utf-8")
    print("OK: injected billing-friendly reply right after call_openai(...)")

PY

git add server/cit_server.py || true
git commit -m "fix: inject friendly reply on billing_not_active (post-call_openai)" || true

./citctl.sh start

echo "[CHECK] /api/chat (message)"
curl -sS --max-time 25 -X POST http://127.0.0.1:8794/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"тест"}' && echo
