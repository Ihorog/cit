#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

# 0) Stop CIT
./citctl.sh stop || true

# 1) Create PUSH script (mirror of PULL)
cat > cit_vault_push.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail
cd ~/cimeika/cit

# Push local vault -> WebDAV
rclone sync vault/local keenetic_webdav:/ \
  --create-empty-src-dirs \
  --cache-dir vault/cache \
  --log-file logs/rclone_webdav_push.log \
  --log-level INFO

echo "OK: PUSH local -> WebDAV"
SH
chmod +x cit_vault_push.sh

# 2) Patch server to enable UI buttons (POST handlers)
python - <<'PY'
from pathlib import Path
import re

p = Path("server/cit_server.py")
s = p.read_text(encoding="utf-8")

if "def do_POST" not in s:
    m = re.search(r'class\s+IntegratedHandler\([^)]+\):\s*\n', s)
    if not m:
        raise SystemExit("IntegratedHandler not found")

    insert_at = m.end()
    do_post = '''
    def do_POST(self):
        if self.path == "/ui/api/pull":
            try:
                out = subprocess.check_output(["bash", str((BASE_DIR / "cit_vault_pull.sh").resolve())],
                                              stderr=subprocess.STDOUT, text=True, timeout=600)
            except Exception as e:
                out = f"ERROR: {e}\\n"
            body = out.encode("utf-8")
            self.send_response(200); self.end_headers()
            self.wfile.write(body); return

        if self.path == "/ui/api/push":
            try:
                out = subprocess.check_output(["bash", str((BASE_DIR / "cit_vault_push.sh").resolve())],
                                              stderr=subprocess.STDOUT, text=True, timeout=600)
            except Exception as e:
                out = f"ERROR: {e}\\n"
            body = out.encode("utf-8")
            self.send_response(200); self.end_headers()
            self.wfile.write(body); return

        self.send_response(404); self.end_headers()
'''
    s = s[:insert_at] + do_post + s[insert_at:]

p.write_text(s, encoding="utf-8")
print("OK: UI Pull/Push API enabled")
PY

# 3) Commit locally
git add cit_vault_push.sh server/cit_server.py || true
git commit -m "feat: enable vault push + UI pull/push actions" || true

# 4) Restart
./citctl.sh start
./citctl.sh health
