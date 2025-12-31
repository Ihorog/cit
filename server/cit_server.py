"""
CIT (Ci Interface Terminal) — minimal HTTP server with:
- GET  /health  -> {"ok": true, "model": os.getenv("CIT_OPENAI_MODEL","gpt-4.1-mini")}
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
from pathlib import Path
import subprocess
import traceback
# --- CIT_SINGLE_KEY_RESOLVER_V1 ---
def _read_dotenv_key():
    try:
        base = Path(__file__).resolve().parents[1]
        envp = base / ".env"
        if not envp.exists():
            return ""
        for line in envp.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            kk, vv = line.split("=", 1)
            kk = kk.strip()
            vv = vv.strip().strip('"').strip("'")
            if kk in ("OPENAI_API_KEY", "CIT_OPENAI_API_KEY") and vv:
                return vv
        return ""
    except Exception:
        return ""

def _get_openai_key():
    """Single source of truth. No recursion."""
    return (os.getenv("CIT_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") or _read_dotenv_key() or "").strip()
# --- /CIT_SINGLE_KEY_RESOLVER_V1 ---


# --- CIT_KEY_RESOLVER_V1 ---
def _read_dotenv_key():
    try:
        base = Path(__file__).resolve().parents[1]
        envp = base / ".env"
        if not envp.exists():
            return ""
        for line in envp.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k in ("OPENAI_API_KEY", "CIT_OPENAI_API_KEY") and v:
                return v
        return ""
    except Exception:
        return ""
def _get_openai_key():
    """Return OpenAI API key from CIT_OPENAI_API_KEY or OPENAI_API_KEY or repo .env (no recursion)."""
    k = (os.getenv("CIT_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") or "").strip()
    if k:
        return k
    try:
        base = Path(__file__).resolve().parents[1]
        envp = base / ".env"
        if envp.exists():
            for line in envp.read_text(encoding="utf-8", errors="ignore").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                kk, vv = line.split("=", 1)
                kk = kk.strip()
                vv = vv.strip().strip('"').strip("'")
                if kk in ("OPENAI_API_KEY", "CIT_OPENAI_API_KEY") and vv:
                    return vv
    except Exception:
        pass
    return ""

# --- /CIT_KEY_RESOLVER_V1 ---

# --- CIT_OPENAI_KEY_READ_V1 ---
def _get_openai_key():
    return (os.getenv("CIT_OPENAI_API_KEY") or _get_openai_key() or "").strip()
# --- /CIT_OPENAI_KEY_READ_V1 ---

# === CIT_UI_INTEGRATED_V1 ===
UI_ROOT = "/ui"
BASE_DIR = Path(__file__).resolve().parent.parent
VAULT_DIR = BASE_DIR / "vault" / "local"
LOG_FILE = BASE_DIR / "logs" / "cit_8794.log"

UI_HTML = """<!doctype html>
<html lang="uk">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>CIT • Vault UI</title>
  <style>
    body{font-family:system-ui,Segoe UI,Roboto,Arial;margin:16px;line-height:1.35}
    .row{display:flex;gap:12px;flex-wrap:wrap}
    .card{border:1px solid #ddd;border-radius:12px;padding:12px;min-width:280px;flex:1}
    button{padding:10px 12px;border-radius:10px;border:1px solid #bbb;background:#fff}
    pre{white-space:pre-wrap;word-break:break-word;background:#f7f7f7;border-radius:10px;padding:10px}
    .muted{opacity:.7}
    code{background:#f2f2f2;padding:2px 6px;border-radius:8px}
  </style>
</head>
<body>
  <h2>CIT • Vault UI</h2>
  <div class="muted">
    Same port UI: <code>/ui</code> • API: <code>/ui/api/vault</code>, <code>/ui/api/logs</code> • Health: <code>/health</code>
  </div>

  <div class="row" style="margin-top:12px">
    <div class="card">
      <h3>Health</h3>
      <button onclick="loadHealth()">Оновити</button>
      <pre id="health">—</pre>
    </div>

    <div class="card">
      <h3>Vault (local)</h3>
      <button onclick="loadVault()">Оновити</button>
      <pre id="vault">—</pre>
    </div>

    <div class="card">
      <h3>Logs (last 120)</h3>
      <button onclick="loadLogs()">Оновити</button>
      <pre id="logs">—</pre>
    </div>
  </div>

<script>
async function loadHealth(){
  const r = await fetch('/health').catch(()=>null);
  document.getElementById('health').textContent = r ? await r.text() : 'CIT недоступний';
}
async function loadVault(){
  const r = await fetch('/ui/api/vault').catch(()=>null);
  document.getElementById('vault').textContent = r ? await r.text() : 'UI API error';
}
async function loadLogs(){
  const r = await fetch('/ui/api/logs').catch(()=>null);
  document.getElementById('logs').textContent = r ? await r.text() : 'UI API error';
}
loadHealth(); loadVault(); loadLogs();
</script>
</body>
</html>
"""

def _ui_list_vault(max_items: int = 600) -> str:
    VAULT_DIR.mkdir(parents=True, exist_ok=True)
    lines = []
    for fp in sorted(VAULT_DIR.rglob("*")):
        if fp.is_dir():
            continue
        rel = fp.relative_to(VAULT_DIR)
        try:
            sz = fp.stat().st_size
        except Exception:
            sz = -1
        lines.append(f"{rel}  ({sz} bytes)")
        if len(lines) >= max_items:
            break
    return "\n".join(lines) if lines else "(empty)"

def _ui_tail_log(n: int = 120) -> str:
    if not LOG_FILE.exists():
        return f"NO LOG: {LOG_FILE}"
    try:
        out = subprocess.check_output(["tail", "-n", str(n), str(LOG_FILE)], text=True)
        return out
    except Exception as e:
        try:
            # fallback: manual tail
            txt = LOG_FILE.read_text(encoding="utf-8", errors="ignore")
            return "\n".join(txt.splitlines()[-n:])
        except Exception:
            return f"tail error: {e}"
# === /CIT_UI_INTEGRATED_V1 ===

# === Model selection (env-first) ===
OPENAI_MODEL = os.getenv("CIT_OPENAI_MODEL", "gpt-4.1-mini")

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
    * { box-sizing: border-box; }
    body { margin:0; font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial; background:#0b0f14; color:#e8eef6; }
    .wrap { max-width: 900px; margin: 0 auto; padding: 14px; }
    .top { display:flex; gap:12px; align-items:center; justify-content:space-between; margin-bottom: 12px; }
    .badge { font-size:12px; opacity:.8; transition: opacity 0.3s ease; }
    .chat { border:1px solid rgba(255,255,255,.08); border-radius:16px; overflow:hidden; background:rgba(255,255,255,.03); box-shadow: 0 4px 16px rgba(0,0,0,.2); }
    .log { height: 62vh; overflow:auto; padding: 16px; scroll-behavior: smooth; }
    .m { margin: 12px 0; line-height: 1.45; white-space: pre-wrap; padding: 8px 12px; border-radius: 8px; }
    .me { color:#cfe6ff; background:rgba(79,137,255,.08); }
    .ai { color:#e8eef6; background:rgba(255,255,255,.03); }
    .bar { display:flex; gap:10px; padding: 14px; border-top:1px solid rgba(255,255,255,.08); background:rgba(0,0,0,.2); }
    textarea { flex:1; resize:none; height: 48px; border-radius: 12px; border:1px solid rgba(255,255,255,.12);
      background:rgba(0,0,0,.3); color:#e8eef6; padding:12px; outline:none; font-size: 14px; line-height: 1.5;
      transition: border-color 0.2s ease, background-color 0.2s ease; }
    textarea:focus { border-color: rgba(79,137,255,.4); background:rgba(0,0,0,.4); }
    button { border-radius: 12px; border:1px solid rgba(255,255,255,.16); background:rgba(255,255,255,.08);
      color:#e8eef6; padding: 11px 14px; cursor:pointer; font-size: 14px; font-weight: 500;
      transition: all 0.2s ease; }
    button:hover:not(:disabled) { background:rgba(255,255,255,.14); border-color: rgba(255,255,255,.24); transform: translateY(-1px); }
    button:active:not(:disabled) { transform: translateY(0); }
    button:disabled { opacity:.4; cursor:not-allowed; }
    .row { display:flex; gap:10px; }
    .hint { font-size: 12px; opacity: .65; margin-top: 10px; line-height: 1.4; }
    .small { font-size: 12px; opacity: .75; margin-top: 2px; }
    @media (max-width: 600px) {
      .wrap { padding: 10px; }
      .top { flex-wrap: wrap; }
      .bar { flex-direction: column; }
      textarea { height: 56px; }
      button { width: 100%; justify-content: center; }
    }
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
        # --- CIT_KEY_GUARD_AT_332_V1 ---
        k = _get_openai_key()
        if not k:
            return {"error": "OPENAI_API_KEY is not set"}
        os.environ["OPENAI_API_KEY"] = k
        os.environ["CIT_OPENAI_API_KEY"] = k
        # --- /CIT_KEY_GUARD_AT_332_V1 ---

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
            "model": os.getenv("CIT_OPENAI_MODEL","gpt-4.1-mini"),
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
            "model": os.getenv("CIT_OPENAI_MODEL","gpt-4.1-mini"),
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

        # --- UI integrated routes ---

        if self.path == "/ui" or self.path == "/ui/":

            body = UI_HTML.encode("utf-8")

            self.send_response(200)

            self.send_header("Content-Type", "text/html; charset=utf-8")

            self.send_header("Content-Length", str(len(body)))

            self.end_headers()

            self.wfile.write(body)

            return

        if self.path == "/ui/api/vault":

            body = _ui_list_vault().encode("utf-8")

            self.send_response(200)

            self.send_header("Content-Type", "text/plain; charset=utf-8")

            self.send_header("Content-Length", str(len(body)))

            self.end_headers()

            self.wfile.write(body)

            return

        if self.path == "/ui/api/logs":

            body = _ui_tail_log().encode("utf-8")

            self.send_response(200)

            self.send_header("Content-Type", "text/plain; charset=utf-8")

            self.send_header("Content-Length", str(len(body)))

            self.end_headers()

            self.wfile.write(body)

            return

        # --- /UI integrated routes ---
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
            _send_json(self, 200, {"ok": True, "model": os.getenv("CIT_OPENAI_MODEL","gpt-4.1-mini"), "ts": now_utc_iso()})
            return

        _send_json(self, 404, {"ok": False, "error": "not_found"})

    # --- CIT_SAFE_POST_WRAPPER_V1 ---

    def do_POST(self):

        try:

            return self._do_POST_impl()

        except Exception as e:

            # Never drop connection without a JSON response

            try:

                tb = traceback.format_exc(limit=12)

            except Exception:

                tb = "traceback_unavailable"

            try:

                self.send_response(500)

                self.send_header("Content-Type", "application/json; charset=utf-8")

                self.end_headers()

                import json

                payload = {"ok": False, "error": str(e), "type": e.__class__.__name__, "trace": tb}

                self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))

            except Exception:

                pass

    # --- /CIT_SAFE_POST_WRAPPER_V1 ---


    def _do_POST_impl(self):
        # --- CHAT ALIASES (CIT_CHAT_ALIASES_V1) ---
        # accept common client endpoints and route them to /chat handler
        if self.path in ("/api/chat", "/v1/chat", "/api/message", "/message"):
            self.path = "/chat"
        # --- /CHAT ALIASES ---
        # --- PING (CIT_CHAT_PING_V1) ---
        try:
            if isinstance(data, dict) and data.get("ping") is True:
                body = b'{"ok": true, "pong": true}'
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
        except Exception:
            pass
        # --- /PING ---
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
