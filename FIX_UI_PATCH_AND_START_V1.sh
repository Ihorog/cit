#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

CIT_DIR="/data/data/com.termux/files/home/cimeika/cit"
STATE_FILE="$CIT_DIR/.ports.active"

say(){ printf "\n=== %s ===\n" "$1"; }
die(){ echo "FAIL: $*" >&2; exit 1; }

port_free(){
  local port="$1"
  python3 - <<PY >/dev/null 2>&1
import socket
s=socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
  s.bind(("127.0.0.1", int("$port")))
  s.close()
  raise SystemExit(0)
except OSError:
  raise SystemExit(1)
PY
}

pick_port(){
  local start="$1"
  local end="$2"
  for p in $(seq "$start" "$end"); do
    if port_free "$p"; then echo "$p"; return 0; fi
  done
  return 1
}

probe(){
  local url="$1"
  local code
  code="$(curl -m 3 -sS -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || true)"
  printf "%-10s -> %s\n" "${code:-ERR}" "$url"
}

say "0) PRECHECK"
[ -d "$CIT_DIR" ] || die "missing: $CIT_DIR"
[ -d "$CIT_DIR/ui" ] || die "missing: $CIT_DIR/ui"
[ -f "$CIT_DIR/ui/index.html" ] || die "missing: $CIT_DIR/ui/index.html"
[ -f "$CIT_DIR/server/cit_server.py" ] || die "missing: $CIT_DIR/server/cit_server.py"

say "1) PATCH ui/app.js (NO f-strings; raw JS)"
python3 - <<'PY'
from pathlib import Path
import datetime

CIT_DIR = Path("/data/data/com.termux/files/home/cimeika/cit")
APP = CIT_DIR/"ui"/"app.js"
CSS = CIT_DIR/"ui"/"styles.css"
IDX = CIT_DIR/"ui"/"index.html"

ts = datetime.datetime.now().strftime("%Y%m%dT%H%M%SZ")
for f in (APP, CSS, IDX):
    if f.exists():
        (f.parent/(f.name+f".bak.{ts}")).write_text(f.read_text(encoding="utf-8"), encoding="utf-8")

# Ensure index has #app + links
idx = IDX.read_text(encoding="utf-8")
if 'id="app"' not in idx:
    idx = idx.replace("</body>", '<div id="app"></div>\n</body>')
if "styles.css" not in idx:
    idx = idx.replace("</head>", '  <link rel="stylesheet" href="styles.css"/>\n</head>')
if "app.js" not in idx:
    idx = idx.replace("</body>", '  <script src="app.js"></script>\n</body>')
IDX.write_text(idx, encoding="utf-8")

css = CSS.read_text(encoding="utf-8") if CSS.exists() else ""
if "/* CANON_NAV_V1 */" not in css:
    css += """

/* CANON_NAV_V1 */
:root{
  --ci-bg:#0B2340;
  --ci-card:rgba(255,255,255,0.06);
  --ci-line:rgba(255,255,255,0.10);
  --ci-text:rgba(255,255,255,0.92);
  --ci-muted:rgba(255,255,255,0.68);
}
body{ margin:0; font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; background:var(--ci-bg); }

.ci-nav a{
  display:flex; align-items:center; gap:10px;
  padding:10px 12px; border-radius:14px;
  text-decoration:none; color:var(--ci-muted);
  transition:transform .18s ease, background .18s ease, color .18s ease, box-shadow .18s ease;
}
.ci-nav a:hover{ background:var(--ci-card); color:var(--ci-text); transform:translateX(2px); box-shadow:0 10px 30px rgba(0,0,0,.12); }
.ci-nav a.active{ background:rgba(255,255,255,0.10); color:var(--ci-text); box-shadow:0 12px 34px rgba(0,0,0,.16); }

.ci-view{ position:relative; overflow:hidden; min-height: calc(100vh - 32px); }
.ci-page{ position:absolute; inset:0; opacity:0; transform:translateY(6px); pointer-events:none; transition:opacity .18s ease, transform .18s ease; }
.ci-page.active{ opacity:1; transform:translateY(0); pointer-events:auto; }

.ci-card{ border-radius:22px; background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); box-shadow:0 30px 70px rgba(0,0,0,.25); }
.ci-chip{ display:inline-flex; align-items:center; gap:8px; padding:8px 12px; border-radius:999px; background:rgba(255,255,255,0.07); border:1px solid rgba(255,255,255,0.10); color:var(--ci-text); }
.ci-btn{ padding:8px 10px; border-radius:12px; border:1px solid rgba(255,255,255,0.10); background:rgba(255,255,255,0.06); color:var(--ci-text); cursor:pointer; }
pre{ margin:0; }
"""
    CSS.write_text(css, encoding="utf-8")

APP.write_text(r"""
/* CANON_ROUTER_V1 */
(function(){
  const LABELS = [
    {id:"kazkar",  title:"Казкар",   subtitle:"✨ Легенда сі", icon:"✨"},
    {id:"podija",  title:"ПоДія",    subtitle:"Події та ініціації", icon:"🔥"},
    {id:"nastrij", title:"Настрій",  subtitle:"Емоційний стан", icon:"💧"},
    {id:"malya",   title:"Маля",     subtitle:"Ідеї та варіанти", icon:"🌬️"},
    {id:"calendar",title:"Календар", subtitle:"Час і вузли", icon:"🗓️"},
    {id:"gallery", title:"Галерея",  subtitle:"Архів і історії", icon:"🖼️"}
  ];

  const q = (sel, root=document) => root.querySelector(sel);
  const qa = (sel, root=document) => Array.from(root.querySelectorAll(sel));

  function getApiBase(){
    try{
      const u = new URL(window.location.href);
      const api = u.searchParams.get("api");
      return (api ? api : "http://127.0.0.1:8790").replace(/\/$/, "");
    }catch(e){
      return "http://127.0.0.1:8790";
    }
  }

  function getHashId(){
    const h = (window.location.hash || "").replace("#","");
    return h || "kazkar";
  }

  function render(){
    const root = q("#app");
    if(!root) return;

    root.innerHTML = `
      <div style="min-height:100vh; display:grid; grid-template-columns:290px 1fr; gap:16px; padding:16px;">
        <aside class="ci-card" style="padding:14px;">
          <div style="display:flex; align-items:center; justify-content:space-between; padding:10px 8px 14px;">
            <div class="ci-chip"><b>Cimeika</b><span style="opacity:.7;">/ CiT</span></div>
            <a href="#kazkar" class="ci-chip" style="text-decoration:none;">Ci</a>
          </div>

          <nav class="ci-nav" style="display:flex; flex-direction:column; gap:6px; padding:6px;">
            ${LABELS.map(x => `
              <a href="#${x.id}" data-route="${x.id}">
                <span style="width:26px; text-align:center;">${x.icon}</span>
                <span style="display:flex; flex-direction:column; line-height:1.1;">
                  <span style="font-weight:650; color: var(--ci-text);">${x.title}</span>
                  <span style="font-size:12px; color: var(--ci-muted);">${x.subtitle}</span>
                </span>
              </a>
            `).join("")}
          </nav>

          <div style="margin-top:14px; padding:10px 8px; color: var(--ci-muted); font-size:12px;">
            <div>API: <span id="ci-api-base"></span></div>
            <div style="margin-top:6px;">
              <button id="ci-health" class="ci-btn">Health</button>
              <button id="ci-reg" class="ci-btn" style="margin-left:8px;">Registry</button>
            </div>
            <pre id="ci-out" style="white-space:pre-wrap; margin-top:10px; padding:10px; border-radius:14px; background: rgba(0,0,0,0.20); border:1px solid rgba(255,255,255,0.06); color: rgba(255,255,255,0.86); min-height:64px;"></pre>
          </div>
        </aside>

        <main class="ci-card ci-view" style="padding:16px;">
          ${LABELS.map(x => `
            <section class="ci-page" id="page-${x.id}">
              <div class="ci-chip" style="margin-bottom:12px;">
                <span>${x.icon}</span>
                <span style="font-weight:750;">${x.title}</span>
                <span style="opacity:.75;">—</span>
                <span style="opacity:.85;">${x.subtitle}</span>
              </div>

              <div style="padding:14px; border-radius:18px; background: rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); color: var(--ci-text);">
                <div style="font-size:14px; color: var(--ci-muted);">
                  Перехід активний. Анімація активна. Роут: <b>#${x.id}</b>
                </div>
                <div style="margin-top:10px; display:flex; gap:10px; flex-wrap:wrap;">
                  <button class="ci-btn" data-action="ping">Ping API</button>
                  <button class="ci-btn" data-action="open" data-route="${x.id}">Open ${x.title}</button>
                </div>
              </div>
            </section>
          `).join("")}
        </main>
      </div>
    `;

    const apiBase = getApiBase();
    q("#ci-api-base").textContent = apiBase;

    async function fetchJson(path){
      const r = await fetch(apiBase + path, {headers:{"accept":"application/json"}});
      const t = await r.text();
      try { return JSON.stringify(JSON.parse(t), null, 2); } catch(e){ return t; }
    }

    q("#ci-health").addEventListener("click", async () => { q("#ci-out").textContent = await fetchJson("/health"); });
    q("#ci-reg").addEventListener("click", async () => { q("#ci-out").textContent = await fetchJson("/registry"); });

    qa("[data-action='ping']").forEach(btn => btn.addEventListener("click", async () => {
      q("#ci-out").textContent = await fetchJson("/health");
    }));

    function applyRoute(){
      const id = getHashId();
      qa(".ci-nav a").forEach(a => a.classList.toggle("active", a.getAttribute("data-route") === id));
      qa(".ci-page").forEach(p => p.classList.toggle("active", p.id === "page-" + id));
    }

    window.addEventListener("hashchange", applyRoute);
    applyRoute();
  }

  if(document.readyState === "loading") document.addEventListener("DOMContentLoaded", render);
  else render();
})();
""".lstrip(), encoding="utf-8")

print("OK: patched", APP)
PY

say "2) START ON FREE PORTS (do not fight hidden listeners)"
NEW_API_PORT="$(pick_port 8790 8899)"
NEW_UI_PORT="$(pick_port 8010 8199)"
API_LOG="$CIT_DIR/.api.$NEW_API_PORT.log"
UI_LOG="$CIT_DIR/.ui.$NEW_UI_PORT.log"
: > "$API_LOG"
: > "$UI_LOG"

export CIT_HOST="127.0.0.1"
export CIT_PORT="$NEW_API_PORT"
nohup python3 "$CIT_DIR/server/cit_server.py" >"$API_LOG" 2>&1 &
API_PID="$!"
nohup python3 -m http.server "$NEW_UI_PORT" --bind "127.0.0.1" --directory "$CIT_DIR/ui" >"$UI_LOG" 2>&1 &
UI_PID="$!"

sleep 1

say "3) VERIFY"
probe "http://127.0.0.1:$NEW_API_PORT/health"
probe "http://127.0.0.1:$NEW_API_PORT/registry"
probe "http://127.0.0.1:$NEW_UI_PORT/"
probe "http://127.0.0.1:$NEW_UI_PORT/?api=http://127.0.0.1:$NEW_API_PORT"

say "4) SAVE .ports.active (proper heredoc)"
cat > "$STATE_FILE" <<EOF
CIT_DIR=$CIT_DIR
API_HOST=127.0.0.1
API_PORT=$NEW_API_PORT
API_PID=$API_PID
UI_HOST=127.0.0.1
UI_PORT=$NEW_UI_PORT
UI_PID=$UI_PID
UI_URL=http://127.0.0.1:$NEW_UI_PORT/
UI_URL_WITH_API=http://127.0.0.1:$NEW_UI_PORT/?api=http://127.0.0.1:$NEW_API_PORT
EOF
echo "OK: $STATE_FILE"

say "5) SMOKE LABELS (7/7)"
python3 - <<PY
import urllib.request
ui="http://127.0.0.1:$NEW_UI_PORT/?api=http://127.0.0.1:$NEW_API_PORT"
html=urllib.request.urlopen(ui, timeout=4).read().decode("utf-8","ignore")
labels=["Казкар","Легенда","ПоДія","Настрій","Маля","Календар","Галерея"]
hits=0
for s in labels:
    ok = s in html
    print(("HIT " if ok else "MISS"), ":", s)
    hits += 1 if ok else 0
print("labels_found:", f"{hits}/7")
PY

say "6) READY"
echo "UI           : http://127.0.0.1:$NEW_UI_PORT/"
echo "UI (with API): http://127.0.0.1:$NEW_UI_PORT/?api=http://127.0.0.1:$NEW_API_PORT"
echo "API health   : http://127.0.0.1:$NEW_API_PORT/health"
echo "API registry : http://127.0.0.1:$NEW_API_PORT/registry"
echo "Logs         : $API_LOG , $UI_LOG"
