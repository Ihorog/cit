#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT="/data/data/com.termux/files/home/cimeika/cit"
S="$ROOT/server/cit_server.py"
LOG="$ROOT/logs"
cd "$ROOT" || exit 1
mkdir -p "$LOG"

echo "=== [0/5] Snapshot: process + last log ==="
ps -A -o pid,args | grep -E 'server/cit_server\.py' | grep -v grep || echo "API NOT RUNNING"
echo "--- tail cit_api_8790.log (last 120) ---"
tail -n 120 "$LOG/cit_api_8790.log" 2>/dev/null || echo "NO LOG"
echo

echo "=== [1/5] Patch: add SAFE JSON wrappers (no crash → always respond) ==="
cp -f "$S" "$S.bak.$(date +%Y%m%d_%H%M%S)"

python - <<'PY'
import pathlib, re
S = pathlib.Path("/data/data/com.termux/files/home/cimeika/cit/server/cit_server.py")
txt = S.read_text(encoding="utf-8", errors="replace")

# Ensure imports
if re.search(r'^\s*import\s+traceback\b', txt, flags=re.M) is None:
    # place after import json if exists else after first import block
    m = re.search(r'^(?:\s*import[^\n]*\n)+', txt, flags=re.M)
    if m:
        txt = txt[:m.end()] + "import traceback\n" + txt[m.end():]
    else:
        txt = "import traceback\n" + txt

# Add safe wrappers once
if "_cit_send_json_safe" not in txt:
    wrappers = r'''
def _cit_send_json_safe(handler, code, payload):
    """
    Never let handler crash the connection.
    Wrap non-dict payloads into dict.
    """
    try:
        if not isinstance(payload, dict):
            payload = {"ok": True, "result": payload}
        _send_json(handler, code, payload)
    except Exception as e:
        try:
            # last resort plain text
            handler.send_response(500)
            handler.send_header("Content-Type", "text/plain; charset=utf-8")
            handler.end_headers()
            handler.wfile.write(f"CIT_FATAL_SEND: {e}".encode("utf-8"))
        except Exception:
            pass

def _cit_error_payload(code, e):
    return {
        "ok": False,
        "error": {
            "code": code,
            "message": str(e),
            "trace": traceback.format_exc()[-3000:]
        }
    }
'''
    txt = txt.rstrip() + "\n\n# === Ci/CIT SAFE WRAPPERS (v1c) ===\n" + wrappers + "\n"

# Replace our injected blocks to use safe wrappers + try/except
def replace_block(pattern, replacement):
    nonlocal_txt = None
    return re.sub(pattern, replacement, txt, flags=re.DOTALL)

# Patch do_POST /api/exec block (if exists)
post_pat = r'(# --- REAL: POST /api/exec.*?return\s*\n)'
m = re.search(post_pat, txt, flags=re.DOTALL)
if m:
    new_post = r'''# --- REAL: POST /api/exec (SAFE)
if self.path.startswith("/api/exec"):
    try:
        length = int(self.headers.get("Content-Length", "0") or "0")
        raw = self.rfile.read(length) if length > 0 else b"{}"
        try:
            data = json.loads(raw.decode("utf-8", errors="replace"))
        except Exception:
            data = {}
        out = _cit_exec_action(data)
        _cit_send_json_safe(self, 200 if (isinstance(out, dict) and out.get("ok")) else 400, out)
    except Exception as e:
        _cit_send_json_safe(self, 500, _cit_error_payload("exec_handler_crash", e))
    return
'''
    txt = re.sub(post_pat, new_post, txt, flags=re.DOTALL)

# Patch do_GET /registry + /node-packages block (if exists)
get_pat = r'(# --- REAL: GET /registry \+ /node-packages.*?return\s*\n)'
m = re.search(get_pat, txt, flags=re.DOTALL)
if m:
    new_get = r'''# --- REAL: GET /registry + /node-packages (SAFE)
if self.path == "/registry":
    try:
        j = _cit_load_json_file("/data/data/com.termux/files/home/cimeika/cit/registry/ci_registry.json")
        out = j.get("registry", j) if isinstance(j, dict) else j
        _cit_send_json_safe(self, 200, out)
    except Exception as e:
        _cit_send_json_safe(self, 500, _cit_error_payload("registry_get_crash", e))
    return
if self.path == "/node-packages":
    try:
        j = _cit_load_json_file("/data/data/com.termux/files/home/cimeika/cit/registry/node_packages.json")
        out = j.get("node_packages", j) if isinstance(j, dict) else j
        _cit_send_json_safe(self, 200, out)
    except Exception as e:
        _cit_send_json_safe(self, 500, _cit_error_payload("node_packages_get_crash", e))
    return
'''
    txt = re.sub(get_pat, new_get, txt, flags=re.DOTALL)

S.write_text(txt, encoding="utf-8")
print("PATCH_SAFE_OK")
PY

echo "=== [2/5] Compile-check ==="
python -m py_compile "$S"

echo "=== [3/5] Restart CIT API (:8790) ==="
pkill -f "server/cit_server.py" 2>/dev/null || true
nohup python "$S" > "$LOG/cit_api_8790.log" 2>&1 &
sleep 0.9

echo "=== [4/5] Verify endpoints ==="
echo "== health =="; curl -sS --max-time 2 http://127.0.0.1:8790/health || echo "NO"
echo
echo "== exec registry.get =="; curl -sS --max-time 3 -X POST http://127.0.0.1:8790/api/exec -H "Content-Type: application/json" -d '{"action":"actions.registry.get","input":{}}' || echo "NO"
echo
echo "== exec node_packages.get =="; curl -sS --max-time 3 -X POST http://127.0.0.1:8790/api/exec -H "Content-Type: application/json" -d '{"action":"actions.node_packages.get","input":{}}' || echo "NO"
echo
echo "== GET /registry =="; curl -sS --max-time 3 http://127.0.0.1:8790/registry || echo "NO"
echo
echo "== GET /node-packages =="; curl -sS --max-time 3 http://127.0.0.1:8790/node-packages || echo "NO"
echo

echo "=== [5/5] If still failing, show crash detail (last 200 log lines) ==="
tail -n 200 "$LOG/cit_api_8790.log" 2>/dev/null || true
echo

echo "=== READY LINKS ==="
echo "UI              : http://127.0.0.1:8010/"
echo "API health      : http://127.0.0.1:8790/health"
echo "API chat bridge : http://127.0.0.1:8790/api/chat"
echo "API exec        : http://127.0.0.1:8790/api/exec"
echo "Registry (GET)  : http://127.0.0.1:8790/registry"
echo "Node-packages   : http://127.0.0.1:8790/node-packages"
