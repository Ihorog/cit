#!/data/data/com.termux/files/usr/bin/bash
set -e
cd /data/data/com.termux/files/home/cimeika/cit || exit 1

python - <<'PY'
import pathlib, re

p = pathlib.Path("server/cit_server.py")
s = p.read_text(encoding="utf-8")

# Ensure we can read UI file
if "server/ui/index.html" not in s and "ui/index.html" not in s:
    pass

# Add helper to serve file if not exists
if "_serve_ui_html" not in s:
    insert_at = s.find("\nclass ")
    if insert_at == -1:
        raise SystemExit("Cannot find class definition to patch safely.")
    helper = """
def _serve_ui_html(handler, code=200):
    try:
        html = (pathlib.Path(__file__).resolve().parent / "ui" / "index.html").read_text(encoding="utf-8")
    except Exception as e:
        handler.send_response(500)
        handler.send_header("Content-Type", "text/plain; charset=utf-8")
        handler.end_headers()
        handler.wfile.write(f"UI load error: {e}".encode("utf-8"))
        return
    handler.send_response(code)
    handler.send_header("Content-Type", "text/html; charset=utf-8")
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(html.encode("utf-8"))
"""
    # add pathlib import if missing
    if re.search(r"^\s*import\s+pathlib\s*$", s, flags=re.M) is None:
        s = re.sub(r"(^import\s+.*\n)", r"\1import pathlib\n", s, count=1, flags=re.M)
    s = s[:insert_at] + helper + s[insert_at:]

# Patch do_GET to serve UI for / and /ui (only if do_GET exists)
if re.search(r"def\s+do_GET\s*\(", s) is None:
    # create do_GET before do_POST
    s = re.sub(
        r"(\n\s*def\s+do_POST\s*\()",
        "\n    def do_GET(self):\n"
        "        p = (self.path or '/').split('?',1)[0]\n"
        "        if p in ('/', '/ui'):\n"
        "            return _serve_ui_html(self, 200)\n"
        "        if p == '/health':\n"
        "            return _send_json(self, 200, {\"ok\": True, \"model\": MODEL_NAME, \"ts\": now()})\n"
        "        return _send_json(self, 404, {\"ok\": False, \"error\": \"not_found\"})\n"
        "\n\\1",
        s,
        count=1
    )
else:
    # if do_GET exists, minimally ensure '/' and '/ui' are handled
    if "p in ('/', '/ui')" not in s:
        s = re.sub(
            r"(def\s+do_GET\s*\(self\):\n)",
            r"\1        p = (self.path or '/').split('?',1)[0]\n        if p in ('/', '/ui'):\n            return _serve_ui_html(self, 200)\n",
            s,
            count=1
        )

p.write_text(s, encoding="utf-8")
print("OK: patched UI routes into server/cit_server.py")
PY
