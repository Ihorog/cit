import os
from pathlib import Path
from core.router import Router
from utils.multipart import parse_multipart_form
import json

def register_io_routes(router: Router):
    @router.route("/upload")
    def handle_upload(h):
        fields = parse_multipart_form(h.rfile, h.headers)
        if "file" not in fields:
            h.send_response(400)
            h.end_headers()
            h.wfile.write(b'{"error": "no file"}')
            return
        
        file_data = fields["file"]
        vault = Path("storage/vault")
        vault.mkdir(exist_ok=True)
        
        with open(vault / file_data.filename, "wb") as f:
            f.write(file_data.data)
            
        h.send_response(200)
        h.send_header("Content-Type", "application/json")
        h.end_headers()
        h.wfile.write(json.dumps({"ok": True, "file": file_data.filename}).encode())

    @router.route("/files")
    def handle_files(h):
        vault = Path("storage/vault")
        files = [f.name for f in vault.glob("*")] if vault.exists() else []
        h.send_response(200)
        h.send_header("Content-Type", "application/json")
        h.end_headers()
        h.wfile.write(json.dumps({"files": files}).encode())
