import os
import json
from core.config import get_config

config = get_config()

def register_sys_routes(router):
    @router.route("/health")
    def handle_health(h):
        h.send_response(200)
        h.send_header("Content-Type", "application/json")
        h.end_headers()
        h.wfile.write(json.dumps({
            "ok": True, 
            "version": "2.2.0",
            "port": 8791
        }).encode())

    @router.route("/config")
    def handle_config(h):
        h.send_response(200)
        h.send_header("Content-Type", "application/json")
        h.end_headers()
        h.wfile.write(json.dumps({
            "storage_mode": config.get("storage.mode", "local"),
            "vault": "storage/vault"
        }).encode())
