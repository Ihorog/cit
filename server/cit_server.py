"""
Ci Interface Terminal (CIT) server implementation.

This module implements a minimal HTTP server exposing two endpoints:

  * `GET /health` returns `{ "ok": true }` to indicate the service is up.
  * `POST /chat` forwards chat messages to the OpenAI Chat Completions API and
    returns the upstream response.

The implementation uses only Python's standard library so that it can run
unchanged on Termux (Android) without installing external packages.  To start
the server manually:

```
export OPENAI_API_KEY=sk-...
python server/cit_server.py
```

By default the server listens on port 8790 on all interfaces.  You can set
`PORT` in the environment to override the port.
"""

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, List
import urllib.request
import urllib.error


class CITHandler(BaseHTTPRequestHandler):
    """Request handler for CIT.

    Handles only `GET /health` and `POST /chat`.  All other endpoints return
    HTTP 404.  Responses are always JSON.
    """

    server_version = "CIT/0"

    def _write_json(self, obj: Dict[str, Any], status: int = 200) -> None:
        """Send a JSON response with the given HTTP status."""
        body = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        """Handle GET requests."""
        if self.path.rstrip("/") == "/health":
            self._write_json({"ok": True})
        else:
            self._write_json({"error": "Not found"}, status=404)

    def do_POST(self) -> None:
        """Handle POST requests."""
        if self.path.rstrip("/") != "/chat":
            self._write_json({"error": "Not found"}, status=404)
            return
        # Read the request body
        content_length = int(self.headers.get("Content-Length", 0))
        try:
            raw_body = self.rfile.read(content_length)
            data = json.loads(raw_body.decode("utf-8"))
        except Exception as exc:
            self._write_json({"error": f"Invalid JSON: {exc}"}, status=400)
            return

        # Extract messages and optional model
        messages: List[Dict[str, str]] = data.get("messages")  # type: ignore[assignment]
        model: str = data.get("model", "gpt-3.5-turbo")
        if not messages:
            self._write_json({"error": "The request body must include a 'messages' array."}, status=400)
            return

        # Retrieve the OpenAI API key
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            self._write_json({"error": "OPENAI_API_KEY environment variable is not set."}, status=500)
            return

        # Build the OpenAI request payload
        payload = json.dumps({"model": model, "messages": messages}).encode("utf-8")
        req = urllib.request.Request(
            url="https://api.openai.com/v1/chat/completions",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                resp_body = resp.read()
            # Return the upstream response directly
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(resp_body)))
            self.end_headers()
            self.wfile.write(resp_body)
        except urllib.error.HTTPError as http_err:
            # Forward upstream error messages
            try:
                err_json = json.loads(http_err.read().decode("utf-8"))
            except Exception:
                err_json = {"error": http_err.reason}
            self._write_json(err_json, status=http_err.code)
        except Exception as exc:
            self._write_json({"error": f"Upstream error: {exc}"}, status=502)


def run_server() -> None:
    """Run the HTTP server until interrupted."""
    port = int(os.environ.get("PORT", 8790))
    server = HTTPServer(("0.0.0.0", port), CITHandler)
    print(f"[CIT] Listening on port {port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        print("[CIT] Server stopped.")


if __name__ == "__main__":
    run_server()
