#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

./citctl.sh stop || true

python - <<'PY'
from pathlib import Path
import re

p = Path("server/cit_server.py")
s = p.read_text(encoding="utf-8", errors="ignore")

marker = "CIT_BILLING_ERROR_REPLY_V1"
if marker in s:
    print("OK: patch already present")
else:
    # Patch: when building response JSON, ensure reply is populated on known billing error
    # We look for place where response dict is created with keys reply/api/raw.
    # If not found, we patch after 'raw' error is available (generic safe insertion).
    if 'billing_not_active' in s:
        print("INFO: file already contains billing_not_active text somewhere")
    # Insert a small helper near top (after imports)
    helper = f'''
# --- {marker} ---
def _friendly_error(raw):
    try:
        if isinstance(raw, dict):
            err = raw.get("error") or {{}}
            code = err.get("code") or ""
            msg  = err.get("message") or ""
            if code == "billing_not_active":
                return "OpenAI API billing не активний для цього акаунта. Активуй білінг у platform.openai.com/account/billing і повтори."
            if "billing" in msg.lower() and "active" in msg.lower():
                return "OpenAI API billing не активний. Перевір billing details у platform.openai.com/account/billing."
        return ""
    except Exception:
        return ""
# --- /{marker} ---
'''
    m = re.search(r'(?:^import[^\n]*\n|^from[^\n]*\n)+', s, re.M)
    ins = m.end() if m else 0
    s = s[:ins] + helper + s[ins:]

    # Patch inside POST handler right before sending JSON (search for '"reply":' dict literal)
    # If dict is created as out = {"reply": ..., "api": ..., "raw": ...}
    # We'll inject: if not out["reply"]: try friendly message from out["raw"]["body"] json if present.
    # We'll do a conservative insertion: after 'out =' line that includes '"raw"' or after first occurrence of '"raw":'
    pat = re.compile(r'out\s*=\s*\{[^\}]*"raw"\s*:\s*[^\}]*\}', re.S)
    m2 = pat.search(s)
    if not m2:
        # Fallback: find 'return self._json(' or similar is unknown; just append nothing.
        print("WARN: could not find 'out = {.. raw ..}' block; patch applied helper only.")
    else:
        block_end = m2.end()
        insert_at = block_end
        # Determine indent from 'out =' line
        line_start = s.rfind("\n", 0, m2.start()) + 1
        indent = re.match(r'^(\s*)', s[line_start:s.find("\n", line_start)]).group(1)
        inject = f'''
{indent}# --- {marker}_INJECT ---
{indent}try:
{indent}    if isinstance(out, dict) and not (out.get("reply") or "").strip():
{indent}        raw = out.get("raw") or {{}}
{indent}        # raw may contain {"error": "..."} or {"error": "...", "body": "...json..."}
{indent}        if isinstance(raw, dict) and "body" in raw and isinstance(raw["body"], str):
{indent}            import json as _json
{indent}            try:
{indent}                j = _json.loads(raw["body"])
{indent}                fr = _friendly_error(j)
{indent}                if fr:
{indent}                    out["reply"] = fr
{indent}                    out["ok"] = False
{indent}            except Exception:
{indent}                pass
{indent}        # direct dict error
{indent}        fr2 = _friendly_error(raw if isinstance(raw, dict) else {{}})
{indent}        if fr2 and not (out.get("reply") or "").strip():
{indent}            out["reply"] = fr2
{indent}            out["ok"] = False
{indent}except Exception:
{indent}    pass
{indent}# --- /{marker}_INJECT ---
'''
        s = s[:insert_at] + inject + s[insert_at:]
        print("OK: injected friendly billing error reply")

p.write_text(s, encoding="utf-8")
PY

git add server/cit_server.py || true
git commit -m "fix: show friendly reply on billing_not_active (UI)" || true

./citctl.sh start

echo "[CHECK] /api/chat (message)"
curl -sS --max-time 25 -X POST http://127.0.0.1:8794/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"тест"}' && echo
