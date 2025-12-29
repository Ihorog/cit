"""
CIT (Ci Interface Terminal) — minimal HTTP server with:
- GET  /health  -> {"ok": true, "model": "..."}
- GET  /ui      -> Web UI (chat + STT + TTS in browser)
- GET  /        -> same as /ui
- POST /chat    -> forwards to OpenAI Responses API (or Chat Completions fallback)

Env:
- OPENAI_API_KEY   (required)
- CIT_MODEL        (optional, default: "gpt-4o-mini")
- CIT_PORT         (optional, default: "8790")
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone

MODEL = os.getenv("CIT_MODEL", "gpt-4o-mini")
PORT = int(os.getenv("CIT_PORT", "8790"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

UI_HTML = """<!doctype html>
<html lang="uk">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>CIT</title>
  <style>
    :root { color-scheme: dark; }
    body { margin:0; font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial; background:#0b0f14; color:#e8eef6; }
    .wrap { max-width: 900px; margin: 0 auto; padding: 14px; }
    .top { display:flex; gap:10px; align-items:center; justify-content:space-between; margin-bottom: 10px; }
    .badge { font-size:12px; opacity:.8; }
    .chat { border:1px solid rgba(255,255,255,.08); border-radius:14px; overflow:hidden; background:rgba(255,255,255,.03); }
    .log { height: 62vh; overflow:auto; padding: 12px; }
    .m { margin: 10px 0; line-height: 1.35; white-space: pre-wrap; }
    .me { color:#cfe6ff; }
    .ai { color:#e8eef6; }
    .bar { display:flex; gap:10px; padding: 12px; border-top:1px solid rgba(255,255,255,.08); background:rgba(0,0,0,.15); }
    textarea { flex:1; resize:none; height: 44px; border-radius: 12px; border:1px solid rgba(255,255,255,.12);
      background:rgba(0,0,0,.25); color:#e8eef6; padding:10px; outline:none; }
    button { border-radius: 12px; border:1px solid rgba(255,255,255,.14); background:rgba(255,255,255,.06);
      color:#e8eef6; padding: 10px 12px; cursor:pointer; }
    button:disabled { opacity:.5; cursor:not-allowed; }
    .row { display:flex; gap:10px; }
    .hint { font-size: 12px; opacity: .7; margin-top: 8px; }
    .small { font-size: 12px; opacity: .8; }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="top">
      <div>
        <div style="font-weight:700;">CIT</div>
        <div class="badge" id="status">offline</div>
        <div class="small" id="model"></div>
      </div>
      <div class="row">
        <button id="btnMic">🎙️ STT</button>
        <button id="btnSpeak" disabled>🔊 TTS</button>
        <button id="btnClear">🧹</button>
      </div>
    </div>

    <div class="chat">
      <div class="log" id="log"></div>
      <div class="bar">
        <textarea id="inp" placeholder="Напиши або натисни 🎙️ і продиктуй..."></textarea>
        <button id="btnSend">Send</button>
      </div>
    </div>

    <div class="hint">
      Якщо STT недоступний у WebView/браузері — робимо Android wrapper (SpeechRecognizer → WebView, TTS → Android).
    </div>
  </div>

<script>
const logEl = document.getElementById('log');
const inp = document.getElementById('inp');
const btnSend = document.getElementById('btnSend');
const btnMic = document.getElementById('btnMic');
const btnSpeak = document.getElementById('btnSpeak');
const btnClear = document.getElementById('btnClear');
const statusEl = document.getElementById('status');
const modelEl = document.getElementById('model');

let lastAssistantText = "";

function addMsg(text, cls){
  const div = document.createElement('div');
  div.className = 'm ' + cls;
  div.textContent = text;
  logEl.appendChild(div);
  logEl.scrollTop = logEl.scrollHeight;
}

async function health(){
  try{
    const r = await fetch('/health');
    const j = await r.json();
    statusEl.textContent = j.ok ? 'online' : 'offline';
    modelEl.textContent = j.model ? ('model: ' + j.model) : '';
  }catch(e){
    statusEl.textContent = 'offline';
    modelEl.textContent = '';
  }
}

async function send(){
  const text = (inp.value || "").trim();
  if(!text) return;
  inp.value = "";
  addMsg("You: " + text, "me");
  btnSend.disabled = true;
  btnMic.disabled = true;
  btnSpeak.disabled = true;

  try{
    const r = await fetch('/chat', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ message: text })
    });
    const j = await r.json();
    const reply = (j.reply || "").trim();
    lastAssistantText = reply;
    addMsg("Ci: " + reply, "ai");
    btnSpeak.disabled = !reply;
  }catch(e){
    addMsg("Ci: (error)", "ai");
  }finally{
    btnSend.disabled = false;
    btnMic.disabled = false;
  }
}

btnSend.onclick = send;
inp.addEventListener('keydown', (e)=>{
  if(e.key === 'Enter' && !e.shiftKey){
    e.preventDefault();
    send();
  }
});
btnClear.onclick = ()=>{
  logEl.innerHTML = "";
  lastAssistantText = "";
  btnSpeak.disabled = true;
};

btnSpeak.onclick = ()=>{
  if(!lastAssistantText) return;
  if(!('speechSynthesis' in window)) return;
  window.speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(lastAssistantText);
  u.lang = 'uk-UA';
  window.speechSynthesis.speak(u);
};

btnMic.onclick = ()=>{
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if(!SR){
    addMsg("Ci: STT недоступний у цьому WebView. Робимо Android wrapper.", "ai");
    return;
  }
  const rec = new SR();
  rec.lang = 'uk-UA';
  rec.interimResults = false;
  rec.maxAlternatives = 1;

  btnMic.disabled = true;
  addMsg("Ci: (слухаю…)", "ai");

  rec.onresult = (ev)=>{
    const t = ev.results[0][0].transcript || "";
    inp.value = t;
  };
  rec.onerror = ()=>{
    addMsg("Ci: (STT error)", "ai");
  };
  rec.onend = ()=>{
    btnMic.disabled = false;
  };
  rec.start();
};

health();
setInterval(health, 4000);
</script>
</body>
</html>
"""

def now_utc_iso():
    return datetime.now(timezone.utc).isoformat()

def _json_bytes(obj) -> bytes:
    return json.dumps(obj, ensure_ascii=False).encode("utf-8")

def _read_json(handler: BaseHTTPRequestHandler):
    length = int(handler.headers.get("Content-Length", "0") or "0")
    raw = handler.rfile.read(length) if length > 0 else b"{}"
    try:
        return json.loads(raw.decode("utf-8"))
    except Exception:
        return {}

def _send_json(handler: BaseHTTPRequestHandler, code: int, obj):
    raw = _json_bytes(obj)
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(raw)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
    handler.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
    handler.end_headers()
    handler.wfile.write(raw)

def _openai_request(url: str, payload: dict) -> dict:
    if not OPENAI_API_KEY:
        return {"error": "OPENAI_API_KEY is not set"}

    req = urllib.request.Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8", errors="ignore")
        except Exception:
            body = ""
        return {"error": f"HTTPError {e.code}", "body": body}
    except Exception as e:
        return {"error": str(e)}

def call_openai(message: str) -> dict:
    """
    Primary: Responses API
    Fallback: Chat Completions API
    """
    # 1) Responses API
    resp = _openai_request(
        "https://api.openai.com/v1/responses",
        {
            "model": MODEL,
            "input": message,
        },
    )

    # extract output_text if present
    if isinstance(resp, dict) and "output_text" in resp and resp.get("output_text"):
        return {"reply": resp["output_text"], "raw": resp, "api": "responses"}

    # 2) Fallback: Chat Completions
    resp2 = _openai_request(
        "https://api.openai.com/v1/chat/completions",
        {
            "model": MODEL,
            "messages": [{"role": "user", "content": message}],
        },
    )
    try:
        reply = resp2["choices"][0]["message"]["content"]
        return {"reply": reply, "raw": resp2, "api": "chat.completions"}
    except Exception:
        return {"reply": "", "raw": resp2, "api": "chat.completions"}

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.end_headers()

    def do_GET(self):
        if self.path in ("/", "/ui"):
            raw = UI_HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(raw)
            return

        if self.path.startswith("/health"):
            _send_json(self, 200, {"ok": True, "model": MODEL, "ts": now_utc_iso()})
            return

        _send_json(self, 404, {"ok": False, "error": "not_found"})

    def do_POST(self):
        if self.path.startswith("/chat"):
            data = _read_json(self)
            msg = (data.get("message") or "").strip()
            if not msg:
                _send_json(self, 400, {"error": "missing_message"})
                return

            out = call_openai(msg)
            # normalize
            reply = (out.get("reply") or "").strip()
            _send_json(self, 200, {"reply": reply, "api": out.get("api"), "raw": out.get("raw")})
            return

        _send_json(self, 404, {"ok": False, "error": "not_found"})

def main():
    host = "0.0.0.0"
    httpd = HTTPServer((host, PORT), Handler)
    print(f"[CIT] listening on http://{host}:{PORT}")
    print(f"[CIT] UI: http://127.0.0.1:{PORT}/ui")
    httpd.serve_forever()

if __name__ == "__main__":
    main()
