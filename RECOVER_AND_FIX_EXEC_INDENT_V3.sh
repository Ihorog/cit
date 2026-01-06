#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT="/data/data/com.termux/files/home/cimeika/cit"
S="$ROOT/server/cit_server.py"
LOG="$ROOT/logs"

cd "$ROOT" || exit 1
mkdir -p "$LOG"

echo "=== [1/6] STOP API ==="
pkill -f "server/cit_server.py" 2>/dev/null || true
sleep 0.2

echo "=== [2/6] RESTORE known-good backup (latest) ==="
BKP="$(ls -1 "$S".bak.* 2>/dev/null | sort | tail -n 1 || true)"
if [ -z "${BKP}" ]; then
  echo "NO BACKUP FOUND: $S.bak.*"
  exit 1
fi
cp -f "$BKP" "$S"
echo "RESTORED: $BKP"

echo "=== [3/6] PATCH /api/exec block (indent-safe, uses _read_json if present) ==="
cp -f "$S" "$S.bak.$(date +%Y%m%d_%H%M%S)"

python - <<'PY'
import pathlib, re

S = pathlib.Path("/data/data/com.termux/files/home/cimeika/cit/server/cit_server.py")
txt = S.read_text(encoding="utf-8", errors="replace")

# Find the exec block marker inserted by v2 patch inside do_POST
marker = "# --- v2: POST /api/exec (SAFE)"
idx = txt.find(marker)
if idx < 0:
    raise SystemExit("MARKER_NOT_FOUND: expected v2 exec marker not present. Re-run RECOVER_AND_PATCH_EXEC_V2.sh first.")

# Determine indent of the marker line (inside do_POST)
line_start = txt.rfind("\n", 0, idx) + 1
line = txt[line_start: txt.find("\n", idx)]
m = re.match(r"^(\s*)#", line)
if not m:
    raise SystemExit("CANNOT_DETECT_INDENT")
indent = m.group(1)

# Replace from marker line to the following "return" at same indent level
after = txt[idx:]
pat = r'^\s*# --- v2: POST /api/exec \(SAFE\)\n(?:.*?\n)*?\s*return\s*$'
mm = re.search(pat, after, flags=re.M)
if not mm:
    raise SystemExit("EXEC_BLOCK_NOT_FOUND")

new_block = f"""{indent}# --- v2: POST /api/exec (SAFE)
{indent}if self.path.startswith("/api/exec"):
{indent}    try:
{indent}        # Prefer the same JSON reader used by existing routes (e.g. /api/chat)
{indent}        if "_read_json" in globals():
{indent}            data = _read_json(self)
{indent}        else:
{indent}            length = int(self.headers.get("Content-Length", "0") or "0")
{indent}            raw = self.rfile.read(length) if length > 0 else b"{{}}"
{indent}            try:
{indent}                data = json.loads(raw.decode("utf-8", errors="replace"))
{indent}            except Exception:
{indent}                data = {{}}
{indent}        if not isinstance(data, dict):
{indent}            data = {{}}
{indent}        out = _cit_exec_action(data)
{indent}        _cit_send_json_safe(self, 200 if (isinstance(out, dict) and out.get("ok")) else 400, out)
{indent}    except Exception as e:
{indent}        _cit_send_json_safe(self, 500, _cit_error_payload("exec_handler_crash", e))
{indent}    return
"""

txt = txt[:idx] + new_block + txt[idx + mm.end():]
S.write_text(txt, encoding="utf-8")
print("PATCH_INDENT_OK")
PY

echo "=== [4/6] COMPILE ==="
python -m py_compile "$S"

echo "=== [5/6] START API (:8790) ==="
nohup python "$S" > "$LOG/cit_api_8790.log" 2>&1 &
sleep 0.9

echo "=== [6/6] VERIFY ==="
echo "== health =="; curl -sS --max-time 2 http://127.0.0.1:8790/health || echo "NO"
echo
echo "== exec registry.get =="; curl -sS --max-time 3 -X POST http://127.0.0.1:8790/api/exec -H "Content-Type: application/json" -d '{"action":"actions.registry.get","input":{}}' || echo "NO"
echo
echo "== exec node_packages.get =="; curl -sS --max-time 3 -X POST http://127.0.0.1:8790/api/exec -H "Content-Type: application/json" -d '{"action":"actions.node_packages.get","input":{}}' || echo "NO"
echo
echo "== GET /registry =="; curl -sS --max-time 3 http://127.0.0.1:8790/registry || echo "NO"
echo

echo "=== READY LINKS ==="
echo "UI              : http://127.0.0.1:8010/"
echo "API exec        : http://127.0.0.1:8790/api/exec"
echo "Registry (GET)  : http://127.0.0.1:8790/registry"
echo "Node-packages   : http://127.0.0.1:8790/node-packages"
