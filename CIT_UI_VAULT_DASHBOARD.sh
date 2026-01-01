#!/usr/bin/env bash
set -euo pipefail

cd ~/cimeika/cit
mkdir -p ui_dashboard logs

cat > ui_dashboard/index.html <<'HTML'
<!doctype html>
<html lang="uk">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>CIT • Vault Dashboard</title>
  <style>
    body{font-family:system-ui,Segoe UI,Roboto,Arial;margin:16px;line-height:1.35}
    .row{display:flex;gap:12px;flex-wrap:wrap}
    .card{border:1px solid #ddd;border-radius:12px;padding:12px;min-width:280px;flex:1}
    button{padding:10px 12px;border-radius:10px;border:1px solid #bbb;background:#fff}
    pre{white-space:pre-wrap;word-break:break-word;background:#f7f7f7;border-radius:10px;padding:10px}
    .muted{opacity:.7}
  </style>
</head>
<body>
  <h2>CIT • Vault Dashboard</h2>
  <div class="muted">CIT: <code id="citUrl">http://127.0.0.1:8794</code> • UI: <code>http://127.0.0.1:8795</code></div>

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
      <h3>Logs (last 80)</h3>
      <button onclick="loadLogs()">Оновити</button>
      <pre id="logs">—</pre>
    </div>
  </div>

<script>
async function loadHealth(){
  const r = await fetch('http://127.0.0.1:8794/health').catch(()=>null);
  document.getElementById('health').textContent = r ? await r.text() : 'CIT недоступний';
}
async function loadVault(){
  const r = await fetch('/api/vault').catch(()=>null);
  document.getElementById('vault').textContent = r ? await r.text() : 'UI API error';
}
async function loadLogs(){
  const r = await fetch('/api/logs').catch(()=>null);
  document.getElementById('logs').textContent = r ? await r.text() : 'UI API error';
}
loadHealth(); loadVault(); loadLogs();
</script>
</body>
</html>
HTML

cat > ui_dashboard/ui_server.py <<'PY'
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import os, subprocess

BASE = Path(__file__).resolve().parent.parent
DASH = BASE / "ui_dashboard"
VAULT = BASE / "vault" / "local"
LOG = BASE / "logs" / "cit_8794.log"

class H(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # serve dashboard directory as web root
        return str((DASH / path.lstrip("/")).resolve())

    def do_GET(self):
        if self.path == "/api/vault":
            VAULT.mkdir(parents=True, exist_ok=True)
            lines = []
            for p in sorted(VAULT.rglob("*")):
                if p.is_dir(): 
                    continue
                rel = p.relative_to(VAULT)
                try:
                    sz = p.stat().st_size
                except:
                    sz = -1
                lines.append(f"{rel}  ({sz} bytes)")
            out = "\n".join(lines[:500]) or "(empty)"
            self.send_response(200); self.end_headers()
            self.wfile.write(out.encode("utf-8"))
            return

        if self.path == "/api/logs":
            if LOG.exists():
                try:
                    out = subprocess.check_output(["tail","-n","80",str(LOG)], text=True)
                except Exception as e:
                    out = f"tail error: {e}"
            else:
                out = f"NO LOG: {LOG}"
            self.send_response(200); self.end_headers()
            self.wfile.write(out.encode("utf-8"))
            return

        return super().do_GET()

def main():
    port = int(os.getenv("CIT_UI_PORT","8795"))
    os.chdir(str(DASH))
    httpd = HTTPServer(("127.0.0.1", port), H)
    print(f"UI listening on http://127.0.0.1:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    main()
PY

# start UI server
PID="$(ps -A -o pid,args | grep -E 'python .*ui_dashboard/ui_server\.py' | grep -v grep | awk '{print $1}' | head -n1 || true)"
if [ -n "${PID:-}" ]; then kill -9 "$PID" || true; fi

nohup python ui_dashboard/ui_server.py > logs/ui_8795.log 2>&1 &

echo "OK: UI started"
echo "Open: http://127.0.0.1:8795"
