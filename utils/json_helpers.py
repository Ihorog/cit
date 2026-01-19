import json
from http.server import BaseHTTPRequestHandler
from typing import Any, Dict

def read_json(handler: BaseHTTPRequestHandler) -> Dict[str, Any]:
    try:
        length = int(handler.headers.get('Content-Length', 0))
        if length == 0: return {}
        return json.loads(handler.rfile.read(length).decode('utf-8'))
    except: return {}

def send_json(handler: BaseHTTPRequestHandler, code: int, data: Any):
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.end_headers()
    handler.wfile.write(json.dumps(data).encode('utf-8'))
