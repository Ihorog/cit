#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

FILE="server/cit_server.py"

# Stop controlled instance (if running)
./citctl.sh stop || true

python - <<'PY'
from pathlib import Path
import re

p = Path("server/cit_server.py")
s = p.read_text(encoding="utf-8")

# Ensure imports we need
need_imports = ["import os", "from pathlib import Path", "import subprocess"]
for imp in need_imports:
    if imp not in s:
        # insert after first import block if possible
        m = re.search(r'(?:^import[^\n]*\n|^from[^\n]*\n)+', s, re.M)
        if m:
            s = s[:m.end()] + imp + "\n" + s[m.end():]
        else:
            s = imp + "\n" + s

# UI block to inject (idempotent marker)
if "CIT_UI_INTEGRATED_V1" not in s:
    ui_block = r'''
# === CIT_UI_INTEGRATED_V1 ===
UI_ROOT = "/ui"
BASE_DIR = Path(__file__).resolve().parent.parent
VAULT_DIR = BASE_DIR / "vault" / "local"
LOG_FILE = BASE_DIR / "logs" / "cit_8794.log"

UI_HTML = """<!doctype html>
<html lang="uk">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>CIT • Vault UI</title>
  <style>
    body{font-family:system-ui,Segoe UI,Roboto,Arial;margin:16px;line-height:1.35}
    .row{display:flex;gap:12px;flex-wrap:wrap}
    .card{border:1px solid #ddd;border-radius:12px;padding:12px;min-width:280px;flex:1}
    button{padding:10px 12px;border-radius:10px;border:1px solid #bbb;background:#fff}
    pre{white-space:pre-wrap;word-break:break-word;background:#f7f7f7;border-radius:10px;padding:10px}
    .muted{opacity:.7}
    code{background:#f2f2f2;padding:2px 6px;border-radius:8px}
  </style>
</head>
<body>
  <h2>CIT • Vault UI</h2>
  <div class="muted">
    Same port UI: <code>/ui</code> • API: <code>/ui/api/vault</code>, <code>/ui/api/logs</code> • Health: <code>/health</code>
  </div>

  <div class="row" style="margin-top:12px">
    <div class="card">
      <h3>Health</h3>
      <button onclick="loadHealth()">Оновити</button>
      <pre id="health">—</pre>
    </div>

    <div class="card">
      <h3>Vault (local)</h3>
      <button onclick="loadVault()">Оновити</button>
      <pre id="vault">—</pre>
    </div>

    <div class="card">
      <h3>Logs (last 120)</h3>
      <button onclick="loadLogs()">Оновити</button>
      <pre id="logs">—</pre>
    </div>
  </div>

<script>
async function loadHealth(){
  const r = await fetch('/health').catch(()=>null);
  document.getElementById('health').textContent = r ? await r.text() : 'CIT недоступний';
}
async function loadVault(){
  const r = await fetch('/ui/api/vault').catch(()=>null);
  document.getElementById('vault').textContent = r ? await r.text() : 'UI API error';
}
async function loadLogs(){
  const r = await fetch('/ui/api/logs').catch(()=>null);
  document.getElementById('logs').textContent = r ? await r.text() : 'UI API error';
}
loadHealth(); loadVault(); loadLogs();
</script>
</body>
</html>
"""

def _ui_list_vault(max_items: int = 600) -> str:
    VAULT_DIR.mkdir(parents=True, exist_ok=True)
    lines = []
    for fp in sorted(VAULT_DIR.rglob("*")):
        if fp.is_dir():
            continue
        rel = fp.relative_to(VAULT_DIR)
        try:
            sz = fp.stat().st_size
        except Exception:
            sz = -1
        lines.append(f"{rel}  ({sz} bytes)")
        if len(lines) >= max_items:
            break
    return "\n".join(lines) if lines else "(empty)"

def _ui_tail_log(n: int = 120) -> str:
    if not LOG_FILE.exists():
        return f"NO LOG: {LOG_FILE}"
    try:
        out = subprocess.check_output(["tail", "-n", str(n), str(LOG_FILE)], text=True)
        return out
    except Exception as e:
        try:
            # fallback: manual tail
            txt = LOG_FILE.read_text(encoding="utf-8", errors="ignore")
            return "\n".join(txt.splitlines()[-n:])
        except Exception:
            return f"tail error: {e}"
# === /CIT_UI_INTEGRATED_V1 ===
'''
    # insert UI block after imports block
    m = re.search(r'(?:^import[^\n]*\n|^from[^\n]*\n)+', s, re.M)
    insert_at = m.end() if m else 0
    s = s[:insert_at] + ui_block + s[insert_at:]

# Try direct injection into Handler.do_GET if exists
# We look for a BaseHTTPRequestHandler subclass with def do_GET(self):
handler_do_get = re.search(r'\n(\s*)def do_GET\s*\(\s*self\s*\)\s*:\s*\n', s)
inserted = False

if handler_do_get:
    indent = handler_do_get.group(1)
    # Insert at beginning of do_GET body
    # Find position right after the do_GET def line
    start = handler_do_get.end()
    ui_routes = f"""{indent}    # --- UI integrated routes ---
{indent}    if self.path == "/ui" or self.path == "/ui/":
{indent}        body = UI_HTML.encode("utf-8")
{indent}        self.send_response(200)
{indent}        self.send_header("Content-Type", "text/html; charset=utf-8")
{indent}        self.send_header("Content-Length", str(len(body)))
{indent}        self.end_headers()
{indent}        self.wfile.write(body)
{indent}        return
{indent}    if self.path == "/ui/api/vault":
{indent}        body = _ui_list_vault().encode("utf-8")
{indent}        self.send_response(200)
{indent}        self.send_header("Content-Type", "text/plain; charset=utf-8")
{indent}        self.send_header("Content-Length", str(len(body)))
{indent}        self.end_headers()
{indent}        self.wfile.write(body)
{indent}        return
{indent}    if self.path == "/ui/api/logs":
{indent}        body = _ui_tail_log().encode("utf-8")
{indent}        self.send_response(200)
{indent}        self.send_header("Content-Type", "text/plain; charset=utf-8")
{indent}        self.send_header("Content-Length", str(len(body)))
{indent}        self.end_headers()
{indent}        self.wfile.write(body)
{indent}        return
{indent}    # --- /UI integrated routes ---
"""
    # Avoid double insert
    if "UI integrated routes" not in s[start:start+2000]:
        s = s[:start] + ui_routes + s[start:]
        inserted = True

# Fallback: create IntegratedHandler and swap in main()
if not inserted and "class IntegratedHandler" not in s:
    # Find existing Handler class name by locating "Handler" used in HTTPServer(..., Handler)
    m = re.search(r'HTTPServer\(\([^)]*\)\s*,\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)', s)
    handler_name = m.group(1) if m else "Handler"

    inject = f'''
# === UI Handler wrapper (fallback) ===
class IntegratedHandler({handler_name}):
    def do_GET(self):
        if self.path == "/ui" or self.path == "/ui/":
            body = UI_HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path == "/ui/api/vault":
            body = _ui_list_vault().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path == "/ui/api/logs":
            body = _ui_tail_log().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        return super().do_GET()
# === /UI Handler wrapper (fallback) ===
'''
    # Insert near bottom before main() if possible
    mm = re.search(r'\n\s*def main\s*\(\s*\)\s*:\s*\n', s)
    insert_at = mm.start() if mm else len(s)
    s = s[:insert_at] + inject + s[insert_at:]

    # Replace HTTPServer(..., Handler) with IntegratedHandler
    s = re.sub(r'(HTTPServer\(\([^)]*\)\s*,\s*)' + re.escape(handler_name) + r'(\s*\))',
               r'\1IntegratedHandler\2', s, count=1)

p.write_text(s, encoding="utf-8")
print("OK: UI integrated into", p)
PY

# Local commit (no auto-push)
git add "$FILE" || true
git commit -m "feat: integrate /ui dashboard into cit_server (same port)" || true

# Restart (model already fixed via env)
export CIT_OPENAI_MODEL="${CIT_OPENAI_MODEL:-gpt-4.1-mini}"
./citctl.sh start

# Verify endpoints
echo "[CHECK] /health"
curl -sS "http://127.0.0.1:8794/health" && echo
echo "[CHECK] /ui (first 3 lines)"
curl -sS "http://127.0.0.1:8794/ui" | head -n 3
echo "[CHECK] /ui/api/vault (first 10 lines)"
curl -sS "http://127.0.0.1:8794/ui/api/vault" | head -n 10 || true
