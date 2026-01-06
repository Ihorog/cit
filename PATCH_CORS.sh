#!/data/data/com.termux/files/usr/bin/bash
set -e
cd /data/data/com.termux/files/home/cimeika/cit || exit 1

python - <<'PY'
import re, pathlib

p = pathlib.Path("server/cit_server.py")
s = p.read_text(encoding="utf-8")

# 1) Patch _send_json: add CORS headers after Content-Type if not present
if "Access-Control-Allow-Origin" not in s:
    s = re.sub(
        r'(send_header\(\s*[\'"]Content-Type[\'"]\s*,\s*[\'"]application/json[\'"]\s*\)\s*\n)',
        r"\1    handler.send_header('Access-Control-Allow-Origin', '*')\n"
        r"    handler.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')\n"
        r"    handler.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')\n",
        s,
        count=1
    )

# 2) Add do_OPTIONS method before do_POST in handler class if missing
if re.search(r"def\s+do_OPTIONS\s*\(", s) is None:
    s = re.sub(
        r"(\n\s*def\s+do_POST\s*\()",
        "\n    def do_OPTIONS(self):\n"
        "        self.send_response(204)\n"
        "        self.send_header('Access-Control-Allow-Origin', '*')\n"
        "        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')\n"
        "        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')\n"
        "        self.end_headers()\n"
        "\n\\1",
        s,
        count=1
    )

p.write_text(s, encoding="utf-8")
print("OK: patched CORS in server/cit_server.py")
PY
