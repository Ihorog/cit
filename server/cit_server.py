from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone

API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL = os.getenv("CIT_MODEL", "gpt-4o-mini")
PORT = int(os.getenv("CIT_PORT", "8790"))

UI_HTML = """<!doctype html>
<html lang="uk">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>CIT - ChatGPT</title>
  <style>
    :root { color-scheme: dark; }
    * { box-sizing: border-box; }
    body { margin:0; font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial; background:#0b0f14; color:#e8eef6; }
    .wrap { max-width: 900px; margin: 0 auto; padding: 14px; }
    .header { margin-bottom: 20px; }
    .header h1 { margin: 0; font-size: 24px; color: #10a37f; }
    .header p { margin: 5px 0 0; font-size: 12px; opacity: 0.7; }
    .chat { border:1px solid rgba(255,255,255,.08); border-radius:16px; overflow:hidden; background:rgba(255,255,255,.03); box-shadow: 0 4px 16px rgba(0,0,0,.2); }
    .log { height: 60vh; overflow:auto; padding: 16px; scroll-behavior: smooth; }
    .m { margin: 12px 0; line-height: 1.5; white-space: pre-wrap; padding: 12px; border-radius: 8px; word-wrap: break-word; }
    .me { color:#cfe6ff; background:rgba(100,150,255,.12); border-left: 3px solid rgba(100,150,255,.6); }
    .ai { color:#e8eef6; background:rgba(16,163,127,.08); border-left: 3px solid rgba(16,163,127,.4); }
    .bar { display:flex; gap:10px; padding: 14px; border-top:1px solid rgba(255,255,255,.08); background:rgba(0,0,0,.2); }
    textarea { flex:1; resize:none; height: 50px; border-radius: 12px; border:1px solid rgba(255,255,255,.12); background:rgba(0,0,0,.3); color:#e8eef6; padding:12px; outline:none; font-size:14px; line-height:1.4; }
    textarea:focus { border-color: rgba(16,163,127,.6); background:rgba(0,0,0,.4); }
    button { border-radius: 12px; border:1px solid rgba(255,255,255,.16); background:rgba(16,163,127,.15); color:#10a37f; padding: 12px 20px; cursor:pointer; font-weight:500; }
    button:hover { background:rgba(16,163,127,.3); }
    .status { padding: 10px; font-size: 12px; opacity: 0.7; }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="header">
      <h1>🤖 CIT - ChatGPT Interface</h1>
      <p id="model-name">Model: Loading...</p>
    </div>
    <div class="chat">
      <div class="log" id="log"></div>
      <div class="bar">
        <textarea id="msg" placeholder="Напиши щось..." autocomplete="off"></textarea>
        <button onclick="send()">Відправити</button>
      </div>
    </div>
    <div class="status">
      API Status: <span id="status">✓ Connected</span>
    </div>
  </div>
  <script>
    let isLoading = false;

    fetch('/health')
      .then(r => r.json())
      .then(d => {
        document.getElementById('model-name').textContent = 'Model: ' + d.model;
      })
      .catch(e => console.log(e));

    async function send() {
      if (isLoading) return;
      const msg = document.getElementById('msg').value.trim();
      if (!msg) return;
      const log = document.getElementById('log');
      log.innerHTML += '<div class="m me">👤 ' + msg.replace(/</g, '&lt;') + '</div>';
      document.getElementById('msg').value = '';
      log.scrollTop = log.scrollHeight;
      isLoading = true;
      const btn = document.querySelector('button');
      btn.disabled = true;
      btn.textContent = 'Чекаю...';
      try {
        const resp = await fetch('/chat', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({message: msg})
        });
        const data = await resp.json();
        let reply = data.reply || (data.raw && data.raw.error ? 'Ошибка: ' + data.raw.error : 'Помилка');
        if (reply) {
          log.innerHTML += '<div class="m ai">🤖 ' + reply.replace(/</g, '&lt;') + '</div>';
        }
      } catch (e) {
        log.innerHTML += '<div class="m ai">🤖 Помилка: ' + e.message + '</div>';
      }
      log.scrollTop = log.scrollHeight;
      isLoading = false;
      btn.disabled = false;
      btn.textContent = 'Відправити';
    }
    
    document.getElementById('msg').onkeydown = (e) => {
      if (e.key === 'Enter' && !e.shiftKey && !isLoading) {
        e.preventDefault();
        send();
      }
    };
    document.getElementById('msg').focus();
  </script>
</body>
</html>"""

class CITHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ['/', '/ui']:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(UI_HTML.encode())
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "ok": True,
                "model": MODEL,
                "api": "openai",
                "ts": datetime.now(timezone.utc).isoformat()
            }).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/chat':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                req_data = json.loads(body)
                user_msg = req_data.get('message', '')
                api_req = urllib.request.Request(
                    'https://api.openai.com/v1/chat/completions',
                    headers={
                        'Authorization': f'Bearer {API_KEY}',
                        'Content-Type': 'application/json'
                    },
                    data=json.dumps({
                        'model': MODEL,
                        'messages': [
                            {'role': 'system', 'content': 'Ти помічник. Відповідай українською.'},
                            {'role': 'user', 'content': user_msg}
                        ],
                        'max_tokens': 1024,
                        'temperature': 0.7
                    }).encode()
                )
                reply = ""
                raw_response = None
                try:
                    with urllib.request.urlopen(api_req, timeout=30) as resp:
                        resp_data = json.loads(resp.read().decode())
                        if resp_data.get('choices') and len(resp_data['choices']) > 0:
                            reply = resp_data['choices'][0].get('message', {}).get('content', '')
                        raw_response = resp_data
                except urllib.error.HTTPError as e:
                    raw_response = {"error": f"HTTPError {e.code}", "body": e.read().decode()}
                except Exception as e:
                    raw_response = {"error": str(e)}
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                resp_json = {'reply': reply, 'api': 'openai', 'model': MODEL}
                if raw_response and not reply:
                    resp_json['raw'] = raw_response
                self.wfile.write(json.dumps(resp_json).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    print(f"╔════════════════════════════════════════╗")
    print(f"║  CIT запущений на http://127.0.0.1:{PORT}      ║")
    print(f"║  Model: {MODEL:<32} ║")
    print(f"╚════════════════════════════════════════╝")
    server = HTTPServer(('127.0.0.1', PORT), CITHandler)
    server.serve_forever()
