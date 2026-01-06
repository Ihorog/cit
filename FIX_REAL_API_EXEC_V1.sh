#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT="/data/data/com.termux/files/home/cimeika/cit"
S="$ROOT/server/cit_server.py"
LOG="$ROOT/logs"
REG="$ROOT/registry"

cd "$ROOT" || exit 1
mkdir -p "$LOG" "$REG"

echo "=== [1/6] Write registry payloads (JSON) ==="
cat > "$REG/ci_registry.json" <<'JSON'
{
  "registry": {
    "name": "CiRegistry",
    "version": "1.0",
    "system": {
      "system_id": "cimeika-ci",
      "timezone": "Europe/Kyiv",
      "root_operator": "Ci",
      "resource": "CIT",
      "contract": { "name": "CiCIT_Contract", "version": "1.0" }
    },
    "api": {
      "base": "http://127.0.0.1:8790",
      "endpoints": { "health": "/health", "exec": "/api/exec", "chat_bridge": "/api/chat" }
    },
    "nodes": [
      {"id":"ci","title":"Ci","kind":"operator","capabilities":["actions.state.get","actions.state.set","actions.event.emit","actions.registry.get","actions.module.call"]},
      {"id":"kazkar","title":"Казкар","kind":"node","capabilities":["actions.state.get","actions.state.set","actions.module.call"],"subnodes":[{"id":"legend_ci","title":"✨Легенда Ci","kind":"subnode","capabilities":["actions.state.get","actions.state.set"]}]},
      {"id":"podija","title":"ПоДія","kind":"node","capabilities":["actions.event.emit","actions.state.set","actions.module.call"]},
      {"id":"nastrij","title":"Настрій","kind":"node","capabilities":["actions.state.get","actions.state.set","actions.module.call"]},
      {"id":"malya","title":"Маля","kind":"node","capabilities":["actions.module.call","actions.event.emit"]},
      {"id":"calendar","title":"Календар","kind":"node","capabilities":["actions.schedule.get","actions.schedule.set","actions.state.get","actions.state.set"]},
      {"id":"gallery","title":"Галерея","kind":"node","capabilities":["actions.asset.get","actions.asset.put","actions.state.get","actions.state.set"]}
    ],
    "channels": [
      {"id":"web_local_ui","title":"Web UI (local)","kind":"projection","access":{"url":"http://127.0.0.1:8010/"},"binds_to":{"api_base":"http://127.0.0.1:8790","primary":["POST /api/chat","POST /api/exec"]}},
      {"id":"telegram_bot","title":"Telegram Bot","kind":"projection","access":{"url":"telegram://"},"binds_to":{"api_base":"http://127.0.0.1:8790","primary":["POST /api/exec","POST /api/chat"]}},
      {"id":"cli","title":"CLI","kind":"projection","access":{"url":"local-shell"},"binds_to":{"api_base":"http://127.0.0.1:8790","primary":["POST /api/exec"]}}
    ]
  }
}
JSON

cat > "$REG/node_packages.json" <<'JSON'
{
  "node_packages": {
    "version": "1.0",
    "nodes": [
      {"node_id":"ci","title":"Ci","capabilities":["actions.state.get","actions.state.set","actions.event.emit","actions.registry.get"],"processes":[{"id":"cit_api","entry":"server/cit_server.py","port":8790}]},
      {"node_id":"kazkar","title":"Казкар","capabilities":["actions.state.get","actions.state.set","actions.module.call"],"subnodes":[{"node_id":"legend_ci","title":"✨Легенда Ci","capabilities":["actions.state.get","actions.state.set"]}]},
      {"node_id":"podija","title":"ПоДія","capabilities":["actions.event.emit","actions.state.set","actions.schedule.set"]},
      {"node_id":"nastrij","title":"Настрій","capabilities":["actions.state.get","actions.state.set"]},
      {"node_id":"malya","title":"Маля","capabilities":["actions.module.call","actions.event.emit"]},
      {"node_id":"calendar","title":"Календар","capabilities":["actions.schedule.get","actions.schedule.set","actions.state.get","actions.state.set"]},
      {"node_id":"gallery","title":"Галерея","capabilities":["actions.asset.get","actions.asset.put","actions.state.get","actions.state.set"]}
    ]
  }
}
JSON

echo "=== [2/6] Backup cit_server.py ==="
cp -f "$S" "$S.bak.$(date +%Y%m%d_%H%M%S)"

echo "=== [3/6] Patch cit_server.py: add /api/exec + /registry + /node-packages ==="
python - <<'PY'
import pathlib, re

S = pathlib.Path("/data/data/com.termux/files/home/cimeika/cit/server/cit_server.py")
txt = S.read_text(encoding="utf-8", errors="replace")

# Ensure json import exists somewhere
if re.search(r'^\s*import\s+json\b', txt, flags=re.M) is None:
    # place after first import block
    txt = re.sub(r'(^\s*import[^\n]*\n)+', lambda m: m.group(0) + "import json\n", txt, count=1, flags=re.M) or ("import json\n" + txt)

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

def inject_into_method(method_name, snippet):
    nonlocal txt
    m = re.search(rf'\n(\s*)def\s+{re.escape(method_name)}\s*\(self[^\)]*\)\s*:\s*\n', txt)
    if not m:
        return
    if snippet.strip() in txt:
        return
    indent = m.group(1) + "    "
    pos = m.end()
    txt = txt[:pos] + indent + snippet.replace("\n", "\n"+indent) + "\n" + txt[pos:]

# Route injections (early return)
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

inject_into_method("do_POST", post_snip)
inject_into_method("do_GET", get_snip)

S.write_text(txt, encoding="utf-8")
PY

echo "=== [4/6] Compile-check ==="
python -m py_compile "$S"

echo "=== [5/6] Restart CIT API (:8790) ==="
pkill -f "server/cit_server.py" 2>/dev/null || true
nohup python "$S" > "$LOG/cit_api_8790.log" 2>&1 &
sleep 0.8

echo "=== [6/6] Verify (health + exec + registry) ==="
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
