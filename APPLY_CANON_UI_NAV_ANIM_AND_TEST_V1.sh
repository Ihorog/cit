#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

CIT_DIR="/data/data/com.termux/files/home/cimeika/cit"
STATE_FILE="$CIT_DIR/.ports.active"

say(){ printf "\n=== %s ===\n" "$1"; }
die(){ echo "FAIL: $*" >&2; exit 1; }

# ---------- helpers ----------
probe(){
  local url="$1"
  local code
  code="$(curl -m 3 -sS -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || true)"
  printf "%-10s -> %s\n" "${code:-ERR}" "$url"
}

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
    if port_free "$p"; then
      echo "$p"; return 0
    fi
  done
  return 1
}

kill_port(){
  local port="$1"
  # ss може не показати в Termux; пробуємо fuser/lsof, потім pkill по патернах
  if command -v fuser >/dev/null 2>&1; then
    fuser -k "${port}/tcp" >/dev/null 2>&1 || true
  fi
  if command -v lsof >/dev/null 2>&1; then
    local pids
    pids="$(lsof -ti tcp:"$port" 2>/dev/null || true)"
    [ -n "$pids" ] && kill -9 $pids 2>/dev/null || true
  fi
}

say "0) PRECHECK"
[ -d "$CIT_DIR" ] || die "CIT_DIR not found: $CIT_DIR"
[ -d "$CIT_DIR/ui" ] || die "ui/ not found: $CIT_DIR/ui"
[ -f "$CIT_DIR/ui/index.html" ] || die "ui/index.html not found"
[ -f "$CIT_DIR/ui/app.js" ] || die "ui/app.js not found"
[ -f "$CIT_DIR/server/cit_server.py" ] || die "server/cit_server.py not found"
[ -f "$STATE_FILE" ] || die "state file not found: $STATE_FILE"

say "1) LOAD ACTIVE PORTS (from state)"
# shellcheck disable=SC1090
source "$STATE_FILE" || true
API_HOST="${API_HOST:-127.0.0.1}"
UI_HOST="${UI_HOST:-127.0.0.1}"
API_PORT="${API_PORT:-8791}"
UI_PORT="${UI_PORT:-8011}"

echo "API: $API_HOST:$API_PORT"
echo "UI : $UI_HOST:$UI_PORT"

say "2) PATCH UI (canonical nav + hash routes + animations)"
python3 - <<'PY'
from pathlib import Path
import re, datetime

CIT_DIR = Path("/data/data/com.termux/files/home/cimeika/cit")
APP = CIT_DIR/"ui"/"app.js"
IDX = CIT_DIR/"ui"/"index.html"
CSS = CIT_DIR/"ui"/"styles.css"

ts = datetime.datetime.now().strftime("%Y%m%dT%H%M%SZ")
for f in (APP, IDX, CSS):
    if f.exists():
        b = f.with_suffix(f.suffix + f".bak.{ts}")
        b.write_text(f.read_text(encoding="utf-8"), encoding="utf-8")

# --- Ensure index loads app.js + styles ---
idx = IDX.read_text(encoding="utf-8")
if "ui/app.js" in idx:
    idx = idx.replace("ui/app.js", "app.js")
if "ui/styles.css" in idx:
    idx = idx.replace("ui/styles.css", "styles.css")

# Guarantee basic shell elements used by app.js
if 'id="app"' not in idx:
    idx = re.sub(r"</body>", '<div id="app"></div>\n</body>', idx, flags=re.I)

IDX.write_text(idx, encoding="utf-8")

# --- styles: add minimal transitions/active states (non-destructive append) ---
css = CSS.read_text(encoding="utf-8") if CSS.exists() else ""
if "/* CANON_NAV_V1 */" not in css:
    css += """

/* CANON_NAV_V1 */
:root{
  --ci-bg: #0B2340;
  --ci-card: rgba(255,255,255,0.06);
  --ci-line: rgba(255,255,255,0.10);
  --ci-text: rgba(255,255,255,0.90);
  --ci-muted: rgba(255,255,255,0.68);
  --ci-accent: rgba(255,215,128,0.95);
}

.ci-nav a{
  display:flex; align-items:center; gap:10px;
  padding:10px 12px;
  border-radius:14px;
  text-decoration:none;
  color: var(--ci-muted);
  transition: transform .18s ease, background .18s ease, color .18s ease, box-shadow .18s ease;
  user-select:none;
}

.ci-nav a:hover{
  background: var(--ci-card);
  color: var(--ci-text);
  transform: translateX(2px);
  box-shadow: 0 10px 30px rgba(0,0,0,.12);
}

.ci-nav a.active{
  background: rgba(255,255,255,0.10);
  color: var(--ci-text);
  box-shadow: 0 12px 34px rgba(0,0,0,.16);
}

.ci-view{
  position:relative;
  overflow:hidden;
}

.ci-page{
  position:absolute;
  inset:0;
  opacity:0;
  transform: translateY(6px);
  pointer-events:none;
  transition: opacity .18s ease, transform .18s ease;
}

.ci-page.active{
  opacity:1;
  transform: translateY(0);
  pointer-events:auto;
}

.ci-chip{
  display:inline-flex; align-items:center; gap:8px;
  padding:8px 12px;
  border-radius:999px;
  background: rgba(255,255,255,0.07);
  border: 1px solid rgba(255,255,255,0.10);
  color: var(--ci-text);
}

"""
    CSS.write_text(css, encoding="utf-8")

# --- app.js: inject canonical router if not present ---
app = APP.read_text(encoding="utf-8")

marker = "/* CANON_ROUTER_V1 */"
if marker not in app:
    app = f"""{marker}
(function(){{
  const LABELS = [
    {{id:"kazkar",  title:"Казкар",      subtitle:"✨ Легенда сі", icon:"✨"}},
    {{id:"podija",  title:"ПоДія",       subtitle:"Події та ініціації", icon:"🔥"}},
    {{id:"nastrij", title:"Настрій",     subtitle:"Емоційний стан", icon:"💧"}},
    {{id:"malya",   title:"Маля",        subtitle:"Ідеї та варіанти", icon:"🌬️"}},
    {{id:"calendar",title:"Календар",    subtitle:"Час і вузли", icon:"🗓️"}},
    {{id:"gallery", title:"Галерея",     subtitle:"Архів і історії", icon:"🖼️"}}
  ];

  function q(sel, root=document){{ return root.querySelector(sel); }}
  function qa(sel, root=document){{ return Array.from(root.querySelectorAll(sel)); }}

  function getApiBase(){{
    try {{
      const u = new URL(window.location.href);
      const api = u.searchParams.get("api");
      return api ? api.replace(/\\/$/, "") : "http://127.0.0.1:8790";
    }} catch(e) {{
      return "http://127.0.0.1:8790";
    }}
  }}

  function setHash(id){{
    window.location.hash = "#" + id;
  }}

  function getHashId(){{
    const h = (window.location.hash || "").replace("#","");
    return h || "kazkar";
  }}

  function render(){{
    const root = q("#app");
    if(!root) return;

    root.innerHTML = `
      <div class="ci-shell" style="min-height:100vh; display:grid; grid-template-columns: 290px 1fr; gap:16px; padding:16px; background: var(--ci-bg);">
        <aside style="border-radius:22px; padding:14px; background: rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); box-shadow: 0 30px 70px rgba(0,0,0,.25);">
          <div style="display:flex; align-items:center; justify-content:space-between; padding:10px 8px 14px;">
            <div class="ci-chip">
              <span style="font-weight:700;">Cimeika</span>
              <span style="opacity:.7;">/ CiT</span>
            </div>
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
              <button id="ci-health" style="padding:8px 10px; border-radius:12px; border:1px solid rgba(255,255,255,0.10); background: rgba(255,255,255,0.06); color: var(--ci-text);">Health</button>
              <button id="ci-reg" style="padding:8px 10px; border-radius:12px; border:1px solid rgba(255,255,255,0.10); background: rgba(255,255,255,0.06); color: var(--ci-text); margin-left:8px;">Registry</button>
            </div>
            <pre id="ci-out" style="white-space:pre-wrap; margin-top:10px; padding:10px; border-radius:14px; background: rgba(0,0,0,0.20); border:1px solid rgba(255,255,255,0.06); color: rgba(255,255,255,0.86); min-height:64px;"></pre>
          </div>
        </aside>

        <main class="ci-view" style="border-radius:22px; padding:16px; background: rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); box-shadow: 0 30px 70px rgba(0,0,0,.25);">
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
                  <button class="ci-chip" data-action="ping">Ping API</button>
                  <button class="ci-chip" data-action="open" data-route="${x.id}">Open ${x.title}</button>
                </div>
              </div>
            </section>
          `).join("")}
        </main>
      </div>
    `;

    const apiBase = getApiBase();
    q("#ci-api-base").textContent = apiBase;

    async function fetchJson(path){{
      const r = await fetch(apiBase + path, {{headers:{{"accept":"application/json"}}}});
      const t = await r.text();
      try {{ return JSON.stringify(JSON.parse(t), null, 2); }} catch(e) {{ return t; }}
    }}

    q("#ci-health").addEventListener("click", async () => {{
      q("#ci-out").textContent = await fetchJson("/health");
    }});
    q("#ci-reg").addEventListener("click", async () => {{
      q("#ci-out").textContent = await fetchJson("/registry");
    }});

    qa("[data-action='ping']").forEach(btn => {{
      btn.addEventListener("click", async () => {{
        q("#ci-out").textContent = await fetchJson("/health");
      }});
    }});

    function applyRoute(){{
      const id = getHashId();
      qa(".ci-nav a").forEach(a => a.classList.toggle("active", a.getAttribute("data-route") === id));
      qa(".ci-page").forEach(p => p.classList.toggle("active", p.id === "page-" + id));
    }}

    window.addEventListener("hashchange", applyRoute);
    applyRoute();
  }}

  if(document.readyState === "loading") {{
    document.addEventListener("DOMContentLoaded", render);
  }} else {{
    render();
  }}
}})();
"""
    APP.write_text(app, encoding="utf-8")

print("OK: UI patched:", APP, IDX, CSS)
PY

say "3) RESTART CLEAN (use fresh ports, avoid invisible bind conflicts)"
# беремо нові порти, щоб не зачіпати старі невидимі демони
NEW_API_PORT="$(pick_port 8790 8899)"
NEW_UI_PORT="$(pick_port 8010 8199)"
echo "NEW_API_PORT=$NEW_API_PORT"
echo "NEW_UI_PORT=$NEW_UI_PORT"

# пробуємо звільнити стандартні й поточні, але це best-effort
kill_port "$API_PORT" || true
kill_port "$UI_PORT" || true
kill_port "$NEW_API_PORT" || true
kill_port "$NEW_UI_PORT" || true

API_LOG="$CIT_DIR/.api.$NEW_API_PORT.log"
UI_LOG="$CIT_DIR/.ui.$NEW_UI_PORT.log"
: > "$API_LOG"
: > "$UI_LOG"

say "3.1) START API"
export CIT_HOST="127.0.0.1"
export CIT_PORT="$NEW_API_PORT"
nohup python3 "$CIT_DIR/server/cit_server.py" >"$API_LOG" 2>&1 &
API_PID="$!"
echo "api_pid: $API_PID"

say "3.2) START UI"
nohup python3 -m http.server "$NEW_UI_PORT" --bind "127.0.0.1" --directory "$CIT_DIR/ui" >"$UI_LOG" 2>&1 &
UI_PID="$!"
echo "ui_pid: $UI_PID"

sleep 1

say "4) VERIFY"
probe "http://127.0.0.1:$NEW_API_PORT/health"
probe "http://127.0.0.1:$NEW_API_PORT/registry"
probe "http://127.0.0.1:$NEW_UI_PORT/"
probe "http://127.0.0.1:$NEW_UI_PORT/?api=http://127.0.0.1:$NEW_API_PORT"

say "5) SMOKE TEST (labels + routes)"
python3 - <<PY
import urllib.request, re
ui="http://127.0.0.1:$NEW_UI_PORT/?api=http://127.0.0.1:$NEW_API_PORT"
html=urllib.request.urlopen(ui, timeout=4).read().decode("utf-8","ignore")
# простий факт-тест: лейбли присутні в HTML/JS (7/7)
labels=["Казкар","Легенда","ПоДія","Настрій","Маля","Календар","Галерея"]
hits=0
for s in labels:
    if s in html:
        print("HIT :", s); hits+=1
    else:
        print("MISS:", s)
print("labels_found:", f"{hits}/7")
PY

say "6) SAVE ACTIVE PORTS"
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

say "7) READY"
echo "UI           : http://127.0.0.1:$NEW_UI_PORT/"
echo "UI (with API) : http://127.0.0.1:$NEW_UI_PORT/?api=http://127.0.0.1:$NEW_API_PORT"
echo "API health    : http://127.0.0.1:$NEW_API_PORT/health"
echo "API registry  : http://127.0.0.1:$NEW_API_PORT/registry"
echo "Logs          : $API_LOG , $UI_LOG"
