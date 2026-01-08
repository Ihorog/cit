from cit_ui_pwa import UI_HTML_PWA
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
import pathlib
import os
import urllib.request
import urllib.error
import base64
import cgi
import mimetypes
import shutil
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote

import traceback
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import traceback

# --- CIT_BILLING_REPLY_V2 ---
def _inject_friendly_billing_reply(out):
    """
    If OpenAI returns billing_not_active, ensure UI gets a human reply (not empty).
    """
    try:
        if not isinstance(out, dict):
            return out
        if (out.get("reply") or "").strip():
            return out
        raw = out.get("raw") or {}
        # raw may be {"error": "HTTPError 429", "body": "...json..."}
        body = raw.get("body") if isinstance(raw, dict) else None
        if isinstance(body, str) and body.strip().startswith("{"):
            try:
                j = json.loads(body)
                err = (j.get("error") or {}) if isinstance(j, dict) else {}
                if err.get("code") == "billing_not_active":
                    out["ok"] = False
                    out["reply"] = "OpenAI API billing не активний для цього акаунта. Активуй білінг у platform.openai.com/account/billing і повтори."
            except Exception:
                pass
        return out
    except Exception:
        return out
# --- /CIT_BILLING_REPLY_V2 ---

# --- CIT_BILLING_ERROR_REPLY_V1 ---
def _friendly_error(raw):
    try:
        if isinstance(raw, dict):
            err = raw.get("error") or {}
            code = err.get("code") or ""
            msg  = err.get("message") or ""
            if code == "billing_not_active":
                return "OpenAI API billing не активний для цього акаунта. Активуй білінг у platform.openai.com/account/billing і повтори."
            if "billing" in msg.lower() and "active" in msg.lower():
                return "OpenAI API billing не активний. Перевір billing details у platform.openai.com/account/billing."
        return ""
    except Exception:
        return ""
# --- /CIT_BILLING_ERROR_REPLY_V1 ---
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
    return (os.getenv("CIT_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") or _read_dotenv_key() or "").strip()
# --- /CIT_OPENAI_KEY_READ_V1 ---

# === CIT_UI_INTEGRATED_V1 ===
UI_ROOT = "/ui"
BASE_DIR = Path(__file__).resolve().parent.parent
VAULT_DIR = BASE_DIR / "vault" / "local"
LOG_FILE = BASE_DIR / "logs" / "cit_8794.log"

UI_HTML_PWA = """<!doctype html>
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


BIND = os.getenv("CIT_BIND", "127.0.0.1")
# --- CIT_FILES_API_V1 ---

# CIT_FILES_API_V1
HOME_DIR = os.getenv("HOME", "/data/data/com.termux/files/home")
CFG_DIR = Path(os.getenv("CIT_CFG_DIR", str(Path(HOME_DIR) / ".cit")))
CFG_DIR.mkdir(parents=True, exist_ok=True)
CFG_PATH = Path(os.getenv("CIT_CFG_PATH", str(CFG_DIR / "config.json")))

def _load_cfg():
  cfg = {}
  try:
    cfg = json.loads(CFG_PATH.read_text(encoding="utf-8"))
  except Exception:
    cfg = {}
  # env overrides (if present)
  if os.getenv("CIT_MODEL"):
    cfg["model"] = os.getenv("CIT_MODEL")
  if os.getenv("CIT_STORAGE_MODE"):
    cfg["storage_mode"] = os.getenv("CIT_STORAGE_MODE")
  if os.getenv("CIT_VAULT_DIR"):
    cfg["vault_dir"] = os.getenv("CIT_VAULT_DIR")
  if os.getenv("CIT_WEBDAV_URL"):
    cfg["webdav_url"] = os.getenv("CIT_WEBDAV_URL")
  if os.getenv("CIT_WEBDAV_USER"):
    cfg["webdav_user"] = os.getenv("CIT_WEBDAV_USER")
  # never env-pass into cfg unless set explicitly
  return cfg

def _save_cfg(update: dict):
  cfg = _load_cfg()
  # secrets
  if update.get("openai_api_key"):
    cfg["openai_api_key"] = update["openai_api_key"]
  if update.get("webdav_pass"):
    cfg["webdav_pass"] = update["webdav_pass"]
  # non-secrets
  for k in ("model","storage_mode","vault_dir","webdav_url","webdav_user"):
    v = update.get(k)
    if isinstance(v,str) and v.strip():
      cfg[k] = v.strip()
  CFG_PATH.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
  return cfg

def _mask(s: str):
  if not s: return ""
  if len(s) <= 8: return "*"*len(s)
  return s[:3] + "*"*(len(s)-7) + s[-4:]

def _vault_dir(cfg):
  return Path(cfg.get("vault_dir") or os.getenv("CIT_VAULT_DIR") or "/storage/emulated/0/CimeikaVault")

def _storage_mode(cfg):
  return (cfg.get("storage_mode") or os.getenv("CIT_STORAGE_MODE") or "local").strip().lower()

def _webdav(cfg):
  return {
    "url": (cfg.get("webdav_url") or os.getenv("CIT_WEBDAV_URL") or "").strip(),
    "user": (cfg.get("webdav_user") or os.getenv("CIT_WEBDAV_USER") or "").strip(),
    "pass": (cfg.get("webdav_pass") or os.getenv("CIT_WEBDAV_PASS") or "").strip(),
  }

def _safe_name(name: str):
  name = (name or "").replace("\\","/").split("/")[-1]
  name = re.sub(r"[^A-Za-z0-9._ -]+", "_", name).strip()
  if not name: name = "file"
  return name

def _json(handler, code, obj):
  data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
  handler.send_response(code)
  handler.send_header("Content-Type", "application/json; charset=utf-8")
  handler.send_header("Content-Length", str(len(data)))
  handler.end_headers()
  handler.wfile.write(data)

def _bin(handler, code, data: bytes, ctype="application/octet-stream", extra_headers=None):
  handler.send_response(code)
  handler.send_header("Content-Type", ctype)
  handler.send_header("Content-Length", str(len(data)))
  if extra_headers:
    for k,v in extra_headers.items():
      handler.send_header(k,v)
  handler.end_headers()
  handler.wfile.write(data)

def _webdav_put(cfg, rel_name: str, content: bytes):
  wd = _webdav(cfg)
  if not wd["url"]:
    raise ValueError("webdav_url not set")
  base = wd["url"].rstrip("/")
  url = base + "/" + rel_name
  req = urllib.request.Request(url, data=content, method="PUT")
  if wd["user"] or wd["pass"]:
    token = base64.b64encode((wd["user"] + ":" + wd["pass"]).encode("utf-8")).decode("ascii")
    req.add_header("Authorization", "Basic " + token)
  req.add_header("Content-Type", "application/octet-stream")
  with urllib.request.urlopen(req, timeout=15) as r:
    return r.status

def _webdav_delete(cfg, rel_name: str):
  wd = _webdav(cfg)
  if not wd["url"]:
    raise ValueError("webdav_url not set")
  base = wd["url"].rstrip("/")
  url = base + "/" + rel_name
  req = urllib.request.Request(url, method="DELETE")
  if wd["user"] or wd["pass"]:
    token = base64.b64encode((wd["user"] + ":" + wd["pass"]).encode("utf-8")).decode("ascii")
    req.add_header("Authorization", "Basic " + token)
  with urllib.request.urlopen(req, timeout=15) as r:
    return r.status

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

UI_HTML_PWA = """<!doctype html>
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
      <div style="display:flex;align-items:center;gap:10px;">
        <img src="/icons/icon-192.png" alt="CIT" width="40" height="40" style="border-radius:10px;">
        <div>
          <div style="font-weight:700;">CIT</div>
          <div class="badge" id="status">offline</div>
          <div class="small" id="model"></div>
        </div>
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

# === Ci/CIT EXEC HELPERS (v2) ===
def _cit_load_json_file(path):
    try:
        import json, pathlib
        return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    except Exception as e:
        return {"ok": False, "error": {"code":"registry_read_failed","message": str(e)}}

def _cit_exec_action(data):
    action = (data or {}).get("action") or ""
    if action == "actions.registry.get":
        j = _cit_load_json_file("/data/data/com.termux/files/home/cimeika/cit/registry/ci_registry.json")
        return {"ok": True, "action": action, "result": (j.get("registry", j) if isinstance(j, dict) else j)}
    if action == "actions.node_packages.get":
        j = _cit_load_json_file("/data/data/com.termux/files/home/cimeika/cit/registry/node_packages.json")
        return {"ok": True, "action": action, "result": (j.get("node_packages", j) if isinstance(j, dict) else j)}
    return {"ok": False, "action": action, "error": {"code":"not_implemented","message":"action not implemented"}}

def _cit_send_json_safe(handler, code, payload):
    try:
        if not isinstance(payload, dict):
            payload = {"ok": True, "result": payload}
        _send_json(handler, code, payload)
    except Exception as e:
        try:
            handler.send_response(500)
            handler.send_header("Content-Type", "text/plain; charset=utf-8")
            handler.end_headers()
            handler.wfile.write(f"CIT_FATAL_SEND: {e}".encode("utf-8"))
        except Exception:
            pass

def _cit_error_payload(code, e):
    return {"ok": False, "error": {"code": code, "message": str(e), "trace": traceback.format_exc()[-3000:]}}


class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.end_headers()

    def do_GET(self):


    # --- files/config endpoints ---
    parsed = urlparse(self.path)
    path = parsed.path or "/"
    qs = parse_qs(parsed.query or "")
    if path == "/config":
      cfg = _load_cfg()
      out = {
        "model": cfg.get("model") or MODEL,
        "storage_mode": _storage_mode(cfg),
        "vault_dir": str(_vault_dir(cfg)),
        "webdav_url": _webdav(cfg).get("url",""),
        "webdav_user": _webdav(cfg).get("user",""),
        "openai_api_key_masked": _mask(cfg.get("openai_api_key") or os.getenv("OPENAI_API_KEY","")),
      }
      return _json(self, 200, out)

    if path == "/files":
      cfg = _load_cfg()
      mode = _storage_mode(cfg)
      if mode != "local":
        # list for webdav: not implemented (server would need PROPFIND). keep minimal.
        return _json(self, 200, {"mode": mode, "items": [], "note": "webdav list not implemented"})
      vd = _vault_dir(cfg)
      vd.mkdir(parents=True, exist_ok=True)
      items = []
      for fp in sorted(vd.glob("*")):
        if fp.is_file():
          st = fp.stat()
          items.append({"name": fp.name, "size": st.st_size, "mtime": __import__("datetime").datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds")})
      return _json(self, 200, {"mode": mode, "vault": str(vd), "items": items})

    if path == "/file":
      name = unquote((qs.get("name") or [""])[0])
      cfg = _load_cfg()
      mode = _storage_mode(cfg)
      safe = _safe_name(name)
      if mode == "local":
        vd = _vault_dir(cfg); vd.mkdir(parents=True, exist_ok=True)
        fp = vd / safe
        if not fp.exists() or not fp.is_file():
          return _json(self, 404, {"ok": False, "err": "not found"})
        data = fp.read_bytes()
        ctype = mimetypes.guess_type(fp.name)[0] or "application/octet-stream"
        return _bin(self, 200, data, ctype=ctype, extra_headers={"Content-Disposition": f'inline; filename="{fp.name}"'})
      # webdav get: minimal via GET pass-through
      wd = _webdav(cfg)
      if not wd["url"]:
        return _json(self, 400, {"ok": False, "err": "webdav_url not set"})
      url = wd["url"].rstrip("/") + "/" + safe
      req = urllib.request.Request(url, method="GET")
      if wd["user"] or wd["pass"]:
        token = base64.b64encode((wd["user"] + ":" + wd["pass"]).encode("utf-8")).decode("ascii")
        req.add_header("Authorization", "Basic " + token)
      try:
        with urllib.request.urlopen(req, timeout=15) as r:
          data = r.read()
          ctype = r.headers.get("Content-Type") or "application/octet-stream"
          return _bin(self, 200, data, ctype=ctype, extra_headers={"Content-Disposition": f'inline; filename="{safe}"'})
      except Exception as e:
        return _json(self, 502, {"ok": False, "err": str(e)})

        


        

        # --- v2: GET /registry + /node-packages (SAFE)

        if self.path == "/registry":

            try:

                j = _cit_load_json_file("/data/data/com.termux/files/home/cimeika/cit/registry/ci_registry.json")

                out = (j.get("registry", j) if isinstance(j, dict) else j)

                _cit_send_json_safe(self, 200, out)

            except Exception as e:

                _cit_send_json_safe(self, 500, _cit_error_payload("registry_get_crash", e))

            return

        

        if self.path == "/node-packages":

            try:

                j = _cit_load_json_file("/data/data/com.termux/files/home/cimeika/cit/registry/node_packages.json")

                out = (j.get("node_packages", j) if isinstance(j, dict) else j)

                _cit_send_json_safe(self, 200, out)

            except Exception as e:

                _cit_send_json_safe(self, 500, _cit_error_payload("node_packages_get_crash", e))

            return

        

        # --- REAL: GET /registry + /node-packages

        if self.path == "/registry":

            j = _cit_load_json_file("/data/data/com.termux/files/home/cimeika/cit/registry/ci_registry.json")

            _send_json(self, 200, j.get("registry", j) if isinstance(j, dict) else j)

            return

        if self.path == "/node-packages":

            j = _cit_load_json_file("/data/data/com.termux/files/home/cimeika/cit/registry/node_packages.json")

            _send_json(self, 200, j.get("node_packages", j) if isinstance(j, dict) else j)

            return

        
        p = (self.path or '/').split('?',1)[0]
        if p in ('/', '/ui'):
            return _serve_ui_html(self, 200)
        import os

        # --- UI integrated routes ---

        # === PWA ROUTES ===
        if self.path == "/manifest.webmanifest":
            try:
                manifest_path = os.path.join(os.path.dirname(__file__), "..", "ui", "manifest.webmanifest")
                with open(manifest_path, "r", encoding="utf-8") as mf:
                    body = mf.read().encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/manifest+json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            except Exception as e:
                self.send_response(404)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(f"Manifest not found: {e}".encode())
                return

        if self.path.startswith("/icons/"):
            try:
                filename = self.path.split("/icons/")[1]
                icon_path = os.path.join(os.path.dirname(__file__), "..", "ui", "icons", filename)
                with open(icon_path, "rb") as icf:
                    body = icf.read()
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            except Exception as e:
                self.send_response(404)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(f"Icon not found: {e}".encode())
                return

        if self.path == "/ui" or self.path == "/ui/":

            body = UI_HTML_PWA.encode("utf-8")

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
            raw = UI_HTML_PWA.encode("utf-8")
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


    # --- config + upload endpoints ---
    parsed = urlparse(self.path)
    path = parsed.path or "/"
    if path == "/config":
      try:
        ln = int(self.headers.get("Content-Length","0") or "0")
        raw = self.rfile.read(ln) if ln>0 else b"{}"
        payload = json.loads(raw.decode("utf-8", errors="ignore") or "{}")
        cfg = _save_cfg(payload if isinstance(payload, dict) else {})
        return _json(self, 200, {"ok": True, "model": cfg.get("model") or MODEL})
      except Exception as e:
        return _json(self, 400, {"ok": False, "err": str(e)})

    if path == "/upload":
      try:
        cfg = _load_cfg()
        mode = _storage_mode(cfg)
        ctype = self.headers.get("Content-Type","")
        if "multipart/form-data" not in ctype:
          return _json(self, 400, {"ok": False, "err": "multipart/form-data required"})
        form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={
          "REQUEST_METHOD":"POST",
          "CONTENT_TYPE": ctype,
        })
        if "file" not in form:
          return _json(self, 400, {"ok": False, "err": "file field missing"})
        f = form["file"]
        kind = (form.getfirst("kind") or "file").strip()
        filename = _safe_name(getattr(f, "filename", "") or "file")
        data = f.file.read() if getattr(f, "file", None) else b""
        if mode == "local":
          vd = _vault_dir(cfg); vd.mkdir(parents=True, exist_ok=True)
          out = vd / filename
          out.write_bytes(data)
          return _json(self, 200, {"ok": True, "mode": mode, "kind": kind, "name": filename, "path": str(out), "size": len(data)})
        # webdav
        st = _webdav_put(cfg, filename, data)
        return _json(self, 200, {"ok": True, "mode": mode, "kind": kind, "name": filename, "path": ( (_webdav(cfg)["url"].rstrip("/") + "/" + filename) if _webdav(cfg)["url"] else filename ), "status": st, "size": len(data)})
      except Exception as e:
        return _json(self, 500, {"ok": False, "err": str(e)})



        


        

                # --- v2: POST /api/exec (SAFE)
        if self.path.startswith("/api/exec"):
            try:
                # Prefer the same JSON reader used by existing routes (e.g. /api/chat)
                if "_read_json" in globals():
                    data = _read_json(self)
                else:
                    length = int(self.headers.get("Content-Length", "0") or "0")
                    raw = self.rfile.read(length) if length > 0 else b"{}"
                    try:
                        data = json.loads(raw.decode("utf-8", errors="replace"))
                    except Exception:
                        data = {}
                if not isinstance(data, dict):
                    data = {}
                out = _cit_exec_action(data)
                _cit_send_json_safe(self, 200 if (isinstance(out, dict) and out.get("ok")) else 400, out)
            except Exception as e:
                _cit_send_json_safe(self, 500, _cit_error_payload("exec_handler_crash", e))
            return

        # --- REAL: POST /api/exec

        if self.path.startswith("/api/exec"):

            length = int(self.headers.get("Content-Length", "0") or "0")

            raw = self.rfile.read(length) if length > 0 else b"{}"

            try:

                data = json.loads(raw.decode("utf-8", errors="replace"))

            except Exception:

                data = {}

            out = _cit_exec_action(data)

            _send_json(self, 200 if out.get("ok") else 400, out)

            return

        
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

            out = _inject_friendly_billing_reply(out)  # CIT_BILLING_REPLY_V2
            # normalize
            reply = (out.get("reply") or "").strip()
            _send_json(self, 200, {"reply": reply, "api": out.get("api"), "raw": out.get("raw")})
            return

        _send_json(self, 404, {"ok": False, "error": "not_found"})

def main():
    host = "0.0.0.0"
    HTTPServer.allow_reuse_address = True
    httpd = HTTPServer((host, PORT), Handler)
    print(f"[CIT] listening on http://{host}:{PORT}")
    print(f"[CIT] UI: http://127.0.0.1:{PORT}/ui")
    httpd.serve_forever()

if __name__ == "__main__":
    main()
from server.cit_ui_pwa import UI_HTML_PWA

# === Ci/CIT REAL EXEC (v1) ===

def _cit_load_json_file(path):
    try:
        import json, pathlib
        return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    except Exception as e:
        return {"ok": False, "error": {"code":"registry_read_failed","message": str(e)}}

def _cit_exec_action(data):
    action = (data or {}).get("action") or ""
    if action == "actions.registry.get":
        j = _cit_load_json_file("/data/data/com.termux/files/home/cimeika/cit/registry/ci_registry.json")
        if isinstance(j, dict) and "registry" in j: return {"ok": True, "action": action, "result": j["registry"]}
        return {"ok": True, "action": action, "result": j}
    if action == "actions.node_packages.get":
        j = _cit_load_json_file("/data/data/com.termux/files/home/cimeika/cit/registry/node_packages.json")
        if isinstance(j, dict) and "node_packages" in j: return {"ok": True, "action": action, "result": j["node_packages"]}
        return {"ok": True, "action": action, "result": j}
    return {"ok": False, "action": action, "error": {"code":"not_implemented","message":"action not implemented","details":{"action":action}}}




  def do_DELETE(self):
    parsed = urlparse(self.path)
    path = parsed.path or "/"
    qs = parse_qs(parsed.query or "")
    if path == "/file":
      name = unquote((qs.get("name") or [""])[0])
      cfg = _load_cfg()
      mode = _storage_mode(cfg)
      safe = _safe_name(name)
      try:
        if mode == "local":
          vd = _vault_dir(cfg); vd.mkdir(parents=True, exist_ok=True)
          fp = vd / safe
          if fp.exists() and fp.is_file():
            fp.unlink()
            return _json(self, 200, {"ok": True, "mode": mode, "name": safe})
          return _json(self, 404, {"ok": False, "err": "not found"})
        st = _webdav_delete(cfg, safe)
        return _json(self, 200, {"ok": True, "mode": mode, "name": safe, "status": st})
      except Exception as e:
        return _json(self, 500, {"ok": False, "err": str(e)})
    return _json(self, 404, {"ok": False, "err": "unknown route"})

