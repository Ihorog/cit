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
