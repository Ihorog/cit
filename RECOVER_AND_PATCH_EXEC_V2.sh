#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT="/data/data/com.termux/files/home/cimeika/cit"
S="$ROOT/server/cit_server.py"
LOG="$ROOT/logs"
REG="$ROOT/registry"

cd "$ROOT" || exit 1
mkdir -p "$LOG" "$REG"

echo "=== [1/7] STOP API ==="
pkill -f "server/cit_server.py" 2>/dev/null || true
sleep 0.3

echo "=== [2/7] RESTORE latest backup ==="
BKP="$(ls -1 "$S".bak.* 2>/dev/null | sort | tail -n 1 || true)"
if [ -z "${BKP}" ]; then
  echo "NO BACKUP FOUND: $S.bak.*"
  exit 1
fi
cp -f "$BKP" "$S"
echo "RESTORED: $BKP"

echo "=== [3/7] Ensure registry files exist ==="
test -f "$REG/ci_registry.json" || cat > "$REG/ci_registry.json" <<'JSON'
{"registry":{"name":"CiRegistry","version":"1.0","system":{"system_id":"cimeika-ci","timezone":"Europe/Kyiv","root_operator":"Ci","resource":"CIT","contract":{"name":"CiCIT_Contract","version":"1.0"}},"api":{"base":"http://127.0.0.1:8790","endpoints":{"health":"/health","exec":"/api/exec","chat_bridge":"/api/chat"}}}}
JSON
test -f "$REG/node_packages.json" || cat > "$REG/node_packages.json" <<'JSON'
{"node_packages":{"version":"1.0","nodes":[{"node_id":"ci","title":"Ci","capabilities":["actions.registry.get","actions.node_packages.get"]}]}}
JSON

echo "=== [4/7] PATCH v2 (safe, minimal, no block replace) ==="
cp -f "$S" "$S.prepatch.$(date +%Y%m%d_%H%M%S)"

python - <<'PY'
import pathlib, re

S = pathlib.Path("/data/data/com.termux/files/home/cimeika/cit/server/cit_server.py")
txt = S.read_text(encoding="utf-8", errors="replace")

# Ensure imports
need = ["json", "traceback"]
imports_block = re.search(r'^(?:\s*import[^\n]*\n)+', txt, flags=re.M)
if not imports_block:
    txt = "import json\nimport traceback\n" + txt
else:
    block = imports_block.group(0)
    add = ""
    for name in need:
        if re.search(rf'^\s*import\s+{name}\b', block, flags=re.M) is None:
            add += f"import {name}\n"
    txt = txt[:imports_block.end()] + add + txt[imports_block.end():]

# Insert helpers BEFORE first class definition (so handlers always see them)
helpers_tag = "# === Ci/CIT EXEC HELPERS (v2) ==="
if helpers_tag not in txt:
    helpers = f'''
{helpers_tag}
def _cit_load_json_file(path):
    try:
        import json, pathlib
        return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    except Exception as e:
        return {{"ok": False, "error": {{"code":"registry_read_failed","message": str(e)}}}}

def _cit_exec_action(data):
    action = (data or {{}}).get("action") or ""
    if action == "actions.registry.get":
        j = _cit_load_json_file("/data/data/com.termux/files/home/cimeika/cit/registry/ci_registry.json")
        return {{"ok": True, "action": action, "result": (j.get("registry", j) if isinstance(j, dict) else j)}}
    if action == "actions.node_packages.get":
        j = _cit_load_json_file("/data/data/com.termux/files/home/cimeika/cit/registry/node_packages.json")
        return {{"ok": True, "action": action, "result": (j.get("node_packages", j) if isinstance(j, dict) else j)}}
    return {{"ok": False, "action": action, "error": {{"code":"not_implemented","message":"action not implemented"}}}}

def _cit_send_json_safe(handler, code, payload):
    try:
        if not isinstance(payload, dict):
            payload = {{"ok": True, "result": payload}}
        _send_json(handler, code, payload)
    except Exception as e:
        try:
            handler.send_response(500)
            handler.send_header("Content-Type", "text/plain; charset=utf-8")
            handler.end_headers()
            handler.wfile.write(f"CIT_FATAL_SEND: {{e}}".encode("utf-8"))
        except Exception:
            pass

def _cit_error_payload(code, e):
    return {{"ok": False, "error": {{"code": code, "message": str(e), "trace": traceback.format_exc()[-3000:]}}}}
'''
    # place before first "class "
    m = re.search(r'^\s*class\s+\w+', txt, flags=re.M)
    if m:
        txt = txt[:m.start()] + helpers + "\n" + txt[m.start():]
    else:
        txt = helpers + "\n" + txt

# Inject routes into do_GET / do_POST as EARLY RETURNS (safe)
def inject_after_def(source: str, method: str, snippet: str) -> str:
    m = re.search(rf'^(\s*)def\s+{re.escape(method)}\s*\(self[^\)]*\)\s*:\s*$', source, flags=re.M)
    if not m:
        return source
    if snippet.strip() in source:
        return source
    base_indent = m.group(1)              # indent of def line
    body_indent = base_indent + "    "    # indent inside method
    insert_pos = m.end()
    return source[:insert_pos] + "\n" + body_indent + snippet.replace("\n", "\n"+body_indent) + "\n" + source[insert_pos:]

post_snip = r'''
# --- v2: POST /api/exec (SAFE)
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
get_snip = r'''
# --- v2: GET /registry + /node-packages (SAFE)
if self.path == "/registry":
    try:
        j = _cit_load_json_file("/data/data/com.termux/files/home/cimeika/cit/registry/ci_registry.json")
        out = (j.get("registry", j) if isinstance(j, dict) else j)
        _cit_send_json_safe(self, 200, out)
    except Exception as e:
        _cit_send_json_safe(self, 500, _cit_error_payload("registry_get_crash", e))
    return

if self.path == "/node-packages":
    try:
        j = _cit_load_json_file("/data/data/com.termux/files/home/cimeika/cit/registry/node_packages.json")
        out = (j.get("node_packages", j) if isinstance(j, dict) else j)
        _cit_send_json_safe(self, 200, out)
    except Exception as e:
        _cit_send_json_safe(self, 500, _cit_error_payload("node_packages_get_crash", e))
    return
'''

txt = inject_after_def(txt, "do_POST", post_snip)
txt = inject_after_def(txt, "do_GET", get_snip)

S.write_text(txt, encoding="utf-8")
print("PATCH_V2_OK")
PY

echo "=== [5/7] COMPILE ==="
python -m py_compile "$S"

echo "=== [6/7] START API (:8790) ==="
nohup python "$S" > "$LOG/cit_api_8790.log" 2>&1 &
sleep 0.9

echo "=== [7/7] VERIFY ==="
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

echo "=== READY LINKS ==="
echo "UI              : http://127.0.0.1:8010/"
echo "API health      : http://127.0.0.1:8790/health"
echo "API chat bridge : http://127.0.0.1:8790/api/chat"
echo "API exec        : http://127.0.0.1:8790/api/exec"
echo "Registry (GET)  : http://127.0.0.1:8790/registry"
echo "Node-packages   : http://127.0.0.1:8790/node-packages"
