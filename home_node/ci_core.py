#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import json, os, sqlite3, urllib.parse
from datetime import datetime, timezone
from pathlib import Path

HOME = Path(os.environ.get("CI_HOME", str(Path.home())))
BASE = Path(os.environ.get("CI_BASE", str(HOME / "cimeika")))
DB   = Path(os.environ.get("CI_DB",   str(BASE / "db" / "cimeika.db")))
DATA = Path(os.environ.get("CI_DATA", str(BASE / "data")))
LOGS = Path(os.environ.get("CI_LOGS", str(BASE / "logs")))
TEXTS   = DATA / "texts"
GALLERY = DATA / "gallery"
VOICE   = DATA / "voice"

for p in [BASE, DB.parent, DATA, LOGS, TEXTS, GALLERY, VOICE]:
    p.mkdir(parents=True, exist_ok=True)

def now_utc():
    return datetime.now(timezone.utc).isoformat()

def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS kv (
        k TEXT PRIMARY KEY,
        v TEXT NOT NULL,
        ts TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

class CiHandler(BaseHTTPRequestHandler):
    server_version = "CiCore/0.1"

    def _send(self, code=200, obj=None, content_type="application/json; charset=utf-8"):
        raw = b""
        if obj is not None:
            raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        if raw:
            self.wfile.write(raw)

    def log_message(self, fmt, *args):
        try:
            LOGS.mkdir(parents=True, exist_ok=True)
            with (LOGS / "ci_core.log").open("a", encoding="utf-8") as f:
                f.write("%s %s\n" % (now_utc(), (fmt % args)))
        except Exception:
            pass

    def do_GET(self):
        p = urllib.parse.urlparse(self.path)
        if p.path == "/status":
            self._send(200, {
                "ok": True,
                "ci": {"mode": "home", "ts": now_utc()},
                "paths": {
                    "base": str(BASE),
                    "db": str(DB),
                    "data": str(DATA),
                    "texts": str(TEXTS),
                    "gallery": str(GALLERY),
                    "voice": str(VOICE),
                    "logs": str(LOGS),
                }
            })
            return

        if p.path == "/health":
            self._send(200, {"ok": True})
            return

        self._send(404, {"ok": False, "error": "not_found"})

    def do_POST(self):
        p = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(p.query)

        if p.path == "/store":
            typ = (qs.get("type", ["texts"])[0] or "texts").strip()
            name = (qs.get("name", ["item.txt"])[0] or "item.txt").strip()
            if "/" in name or ".." in name:
                self._send(400, {"ok": False, "error": "bad_name"})
                return

            dst_dir = {"texts": TEXTS, "gallery": GALLERY, "voice": VOICE}.get(typ, TEXTS)
            dst_dir.mkdir(parents=True, exist_ok=True)

            ln = int(self.headers.get("Content-Length", "0") or "0")
            body = self.rfile.read(ln) if ln > 0 else b""
            out = dst_dir / name
            out.write_bytes(body)

            self._send(200, {"ok": True, "saved": f"{typ}/{name}", "bytes": len(body)})
            return

        self._send(404, {"ok": False, "error": "not_found"})

def main():
    init_db()
    host = os.environ.get("CI_HOST", "127.0.0.1")
    port = int(os.environ.get("CI_PORT", "8787"))
    HTTPServer((host, port), CiHandler).serve_forever()

if __name__ == "__main__":
    main()
