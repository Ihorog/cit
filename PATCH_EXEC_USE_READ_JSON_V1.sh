#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT="/data/data/com.termux/files/home/cimeika/cit"
S="$ROOT/server/cit_server.py"
LOG="$ROOT/logs"

cd "$ROOT" || exit 1
mkdir -p "$LOG"

echo "=== [1/5] STOP API ==="
pkill -f "server/cit_server.py" 2>/dev/null || true
sleep 0.2

echo "=== [2/5] PATCH do_POST /api/exec to use _read_json(self) ==="
cp -f "$S" "$S.bak.$(date +%Y%m%d_%H%M%S)"

python - <<'PY'
import pathlib, re
S = pathlib.Path("/data/data/com.termux/files/home/cimeika/cit/server/cit_server.py")
txt = S.read_text(encoding="utf-8", errors="replace")

marker = r"# --- v2: POST /api/exec \(SAFE\)"
m = re.search(marker, txt)
if not m:
    raise SystemExit("MARKER_NOT_FOUND: cannot locate exec block")

# Replace block from marker line down to the next "return" that belongs to it.
# We match from marker to the first "\n    return" (method-indented) after it.
pat = r"(# --- v2: POST /api/exec \(SAFE\)\n(?:.*?\n)\s*return\n)"
mm = re.search(pat, txt, flags=re.DOTALL)
if not mm:
    raise SystemExit("BLOCK_NOT_FOUND: cannot match exec block region")

new_block = """# --- v2: POST /api/exec (SAFE)
if self.path.startswith("/api/exec"):
    try:
        # Prefer the same JSON reader used by existing routes (e.g. /api/chat)
        if "_read_json" in globals():
            data = _read_json(self)
        else:
            length = int(self.headers.get("Content-Length", "0") or "0")
            raw = self.rfile.read(length) if length > 0 else b"{}"
            try:
                data = json.loads(raw.decode("utf-8", errors="replace"))
            except Exception:
                data = {}
        if not isinstance(data, dict):
            data = {}
        out = _cit_exec_action(data)
        _cit_send_json_safe(self, 200 if (isinstance(out, dict) and out.get("ok")) else 400, out)
    except Exception as e:
        _cit_send_json_safe(self, 500, _cit_error_payload("exec_handler_crash", e))
    return
"""
txt = txt[:mm.start()] + new_block + txt[mm.end():]
S.write_text(txt, encoding="utf-8")
print("PATCH_EXEC_OK")
PY

echo "=== [3/5] COMPILE ==="
python -m py_compile "$S"

echo "=== [4/5] START API (:8790) ==="
nohup python "$S" > "$LOG/cit_api_8790.log" 2>&1 &
sleep 0.9

echo "=== [5/5] VERIFY ==="
echo "== health =="; curl -sS --max-time 2 http://127.0.0.1:8790/health || echo "NO"
echo
echo "== exec registry.get =="; curl -sS --max-time 3 -X POST http://127.0.0.1:8790/api/exec -H "Content-Type: application/json" -d '{"action":"actions.registry.get","input":{}}' || echo "NO"
echo
echo "== exec node_packages.get =="; curl -sS --max-time 3 -X POST http://127.0.0.1:8790/api/exec -H "Content-Type: application/json" -d '{"action":"actions.node_packages.get","input":{}}' || echo "NO"
echo

echo "=== READY LINKS ==="
echo "UI              : http://127.0.0.1:8010/"
echo "API exec        : http://127.0.0.1:8790/api/exec"
echo "Registry (GET)  : http://127.0.0.1:8790/registry"
echo "Node-packages   : http://127.0.0.1:8790/node-packages"
