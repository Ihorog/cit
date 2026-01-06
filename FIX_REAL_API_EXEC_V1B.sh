#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT="/data/data/com.termux/files/home/cimeika/cit"
S="$ROOT/server/cit_server.py"
LOG="$ROOT/logs"
REG="$ROOT/registry"

cd "$ROOT" || exit 1
mkdir -p "$LOG" "$REG"

echo "=== [1/6] Ensure registry payloads exist ==="
test -f "$REG/ci_registry.json" || cat > "$REG/ci_registry.json" <<'JSON'
{"registry":{"name":"CiRegistry","version":"1.0","system":{"system_id":"cimeika-ci","timezone":"Europe/Kyiv","root_operator":"Ci","resource":"CIT","contract":{"name":"CiCIT_Contract","version":"1.0"}},"api":{"base":"http://127.0.0.1:8790","endpoints":{"health":"/health","exec":"/api/exec","chat_bridge":"/api/chat"}},"nodes":[{"id":"ci","title":"Ci","kind":"operator","capabilities":["actions.registry.get","actions.node_packages.get"]}]}}
JSON
test -f "$REG/node_packages.json" || cat > "$REG/node_packages.json" <<'JSON'
{"node_packages":{"version":"1.0","nodes":[{"node_id":"ci","title":"Ci","capabilities":["actions.registry.get","actions.node_packages.get"]}]}}
JSON

echo "=== [2/6] Backup cit_server.py ==="
cp -f "$S" "$S.bak.$(date +%Y%m%d_%H%M%S)"

echo "=== [3/6] Patch cit_server.py (no nonlocal) ==="
python - <<'PY'
import pathlib, re

S = pathlib.Path("/data/data/com.termux/files/home/cimeika/cit/server/cit_server.py")
txt = S.read_text(encoding="utf-8", errors="replace")

# Ensure json import exists
if re.search(r'^\s*import\s+json\b', txt, flags=re.M) is None:
    m = re.search(r'^(?:\s*import[^\n]*\n)+', txt, flags=re.M)
    if m:
        txt = txt[:m.end()] + "import json\n" + txt[m.end():]
    else:
        txt = "import json\n" + txt

# Inject helpers once
if "_cit_load_json_file" not in txt:
    helper = r'''
def _cit_load_json_file(path):
    try:
        import json, pathlib
        return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    except Exception as e:
        return {"ok": False, "error": {"code":"registry_read_failed","message": str(e)}}

def _cit_exec_action(data):
    action = (data or {}).get("action") or ""
    if action == "actions.registry.get":
        j = _cit_load_json_file("/data/data/com.termux/files/home/cimeika/cit/registry/ci_registry.json")
        if isinstance(j, dict) and "registry" in j: return {"ok": True, "action": action, "result": j["registry"]}
        return {"ok": True, "action": action, "result": j}
    if action == "actions.node_packages.get":
        j = _cit_load_json_file("/data/data/com.termux/files/home/cimeika/cit/registry/node_packages.json")
        if isinstance(j, dict) and "node_packages" in j: return {"ok": True, "action": action, "result": j["node_packages"]}
        return {"ok": True, "action": action, "result": j}
    return {"ok": False, "action": action, "error": {"code":"not_implemented","message":"action not implemented","details":{"action":action}}}
'''
    txt = txt.rstrip() + "\n\n# === Ci/CIT REAL EXEC (v1) ===\n" + helper + "\n"

def inject_into_method(source: str, method_name: str, snippet: str) -> str:
    m = re.search(rf'\n(\s*)def\s+{re.escape(method_name)}\s*\(self[^\)]*\)\s*:\s*\n', source)
    if not m:
        return source
    if snippet.strip() in source:
        return source
    indent = m.group(1) + "    "
    pos = m.end()
    return source[:pos] + indent + snippet.replace("\n", "\n"+indent) + "\n" + source[pos:]

post_snip = r'''
# --- REAL: POST /api/exec
if self.path.startswith("/api/exec"):
    length = int(self.headers.get("Content-Length", "0") or "0")
    raw = self.rfile.read(length) if length > 0 else b"{}"
    try:
        data = json.loads(raw.decode("utf-8", errors="replace"))
    except Exception:
        data = {}
    out = _cit_exec_action(data)
    _send_json(self, 200 if out.get("ok") else 400, out)
    return
'''
get_snip = r'''
# --- REAL: GET /registry + /node-packages
if self.path == "/registry":
    j = _cit_load_json_file("/data/data/com.termux/files/home/cimeika/cit/registry/ci_registry.json")
    _send_json(self, 200, j.get("registry", j) if isinstance(j, dict) else j)
    return
if self.path == "/node-packages":
    j = _cit_load_json_file("/data/data/com.termux/files/home/cimeika/cit/registry/node_packages.json")
    _send_json(self, 200, j.get("node_packages", j) if isinstance(j, dict) else j)
    return
'''

txt = inject_into_method(txt, "do_POST", post_snip)
txt = inject_into_method(txt, "do_GET", get_snip)

S.write_text(txt, encoding="utf-8")
print("PATCH_OK")
PY

echo "=== [4/6] Compile-check ==="
python -m py_compile "$S"

echo "=== [5/6] Restart CIT API (:8790) ==="
pkill -f "server/cit_server.py" 2>/dev/null || true
nohup python "$S" > "$LOG/cit_api_8790.log" 2>&1 &
sleep 0.8

echo "=== [6/6] Verify ==="
echo "== health =="; curl -sS --max-time 2 http://127.0.0.1:8790/health || echo "NO"
echo
echo "== exec registry.get =="; curl -sS --max-time 2 -X POST http://127.0.0.1:8790/api/exec -H "Content-Type: application/json" -d '{"action":"actions.registry.get","input":{}}' || echo "NO"
echo
echo "== exec node_packages.get =="; curl -sS --max-time 2 -X POST http://127.0.0.1:8790/api/exec -H "Content-Type: application/json" -d '{"action":"actions.node_packages.get","input":{}}' || echo "NO"
echo
echo "== GET /registry =="; curl -sS --max-time 2 http://127.0.0.1:8790/registry || echo "NO"
echo
echo "== GET /node-packages =="; curl -sS --max-time 2 http://127.0.0.1:8790/node-packages || echo "NO"
echo

echo "=== READY LINKS ==="
echo "UI              : http://127.0.0.1:8010/"
echo "API health      : http://127.0.0.1:8790/health"
echo "API chat bridge : http://127.0.0.1:8790/api/chat"
echo "API exec        : http://127.0.0.1:8790/api/exec"
echo "Registry (GET)  : http://127.0.0.1:8790/registry"
echo "Node-packages   : http://127.0.0.1:8790/node-packages"
