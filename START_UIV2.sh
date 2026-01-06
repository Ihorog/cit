#!/data/data/com.termux/files/usr/bin/bash
set -e

ROOT="/data/data/com.termux/files/home/cimeika/cit"
UI="$ROOT/ui"
LOG="$ROOT/logs"
API_BASE="http://127.0.0.1:8790"

cd "$ROOT" || exit 1
mkdir -p "$LOG" "$UI"

# --- ensure Ci logo asset (best-effort) ---
mkdir -p "$UI/assets"
if [ ! -f "$UI/assets/ci.png" ]; then
  # try common places if exists
  for c in "$ROOT/assets/ci.png" "$ROOT/media/Ci.png" "$ROOT/ui/ci.png" "$ROOT/ui/assets/Ci.png"; do
    if [ -f "$c" ]; then cp -f "$c" "$UI/assets/ci.png"; break; fi
  done
fi

# --- write UIv2 files ---
cd "$UI" || exit 1

cat > index.html <<'HTML'
<!DOCTYPE html>
<html lang="uk">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>CIT — UIv2</title>
  <link rel="icon" href="assets/ci.png" />
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
  <div class="bg"></div>
  <header class="topbar">
    <button id="ciBtn" class="ciBtn" aria-label="Ci">
      <img class="ciLogo" src="assets/ci.png" alt="Ci" />
    </button>

    <div class="topTitle">
      <div class="h1">CIT</div>
      <div class="h2">Cimeika • Operator UIv2</div>
    </div>

    <div class="topRight">
      <div class="pill" id="apiPill">API: …</div>
    </div>
  </header>

  <main class="wrap">
    <section class="grid">
      <article class="card hero">
        <div class="heroTitle">Ci</div>
        <div class="heroSub">Центр. Є/Нема. Контроль. Оркестрація.</div>
        <div class="heroActions">
          <button class="btn" data-action="actions.registry.get">Registry</button>
          <button class="btn" data-action="actions.node_packages.get">Node-packages</button>
          <button class="btn ghost" id="openChat">Чат</button>
        </div>
        <div class="heroMeta">
          <div class="kv"><span>UI</span><span id="uiUrl">локально</span></div>
          <div class="kv"><span>API</span><span id="apiUrl">локально</span></div>
          <div class="kv"><span>Стан</span><span id="statusLine">…</span></div>
        </div>
      </article>

      <article class="card">
        <div class="cardHead">
          <div class="cardTitle">Казкар</div>
          <div class="badge">минуле</div>
        </div>
        <div class="cardBody">
          <div class="mini">✨ Легенда Ci</div>
          <div class="cardActions">
            <button class="btn" data-preset="kazkar.legend">Вузол</button>
            <button class="btn ghost" data-open="chat">Чат</button>
          </div>
        </div>
      </article>

      <article class="card">
        <div class="cardHead">
          <div class="cardTitle">ПоДія</div>
          <div class="badge">майбутнє</div>
        </div>
        <div class="cardBody">
          <div class="mini">Ініціації • Запуски • Тренди</div>
          <div class="cardActions">
            <button class="btn" data-preset="podija.emit">Emit</button>
            <button class="btn ghost" data-open="chat">Чат</button>
          </div>
        </div>
      </article>

      <article class="card">
        <div class="cardHead">
          <div class="cardTitle">Настрій</div>
          <div class="badge">стан</div>
        </div>
        <div class="cardBody">
          <div class="mini">Вода • Реакції • Підґрунтя</div>
          <div class="cardActions">
            <button class="btn" data-preset="nastrij.state">State</button>
            <button class="btn ghost" data-open="chat">Чат</button>
          </div>
        </div>
      </article>

      <article class="card">
        <div class="cardHead">
          <div class="cardTitle">Маля</div>
          <div class="badge">теперішнє</div>
        </div>
        <div class="cardBody">
          <div class="mini">Ідеї • Альтернативи • Повітря</div>
          <div class="cardActions">
            <button class="btn" data-preset="malya.idea">Idea</button>
            <button class="btn ghost" data-open="chat">Чат</button>
          </div>
        </div>
      </article>

      <article class="card">
        <div class="cardHead">
          <div class="cardTitle">Календар</div>
          <div class="badge">ритми</div>
        </div>
        <div class="cardBody">
          <div class="mini">Вузлові точки часу</div>
          <div class="cardActions">
            <button class="btn" data-preset="calendar.get">Get</button>
            <button class="btn ghost" data-open="chat">Чат</button>
          </div>
        </div>
      </article>

      <article class="card">
        <div class="cardHead">
          <div class="cardTitle">Галерея</div>
          <div class="badge">памʼять</div>
        </div>
        <div class="cardBody">
          <div class="mini">Слайди • Історії • Макети</div>
          <div class="cardActions">
            <button class="btn" data-preset="gallery.list">List</button>
            <button class="btn ghost" data-open="chat">Чат</button>
          </div>
        </div>
      </article>

      <article class="card wide">
        <div class="cardHead">
          <div class="cardTitle">Вивід</div>
          <div class="badge">факт</div>
        </div>
        <div class="cardBody">
          <pre id="out" class="out">…</pre>
        </div>
      </article>
    </section>
  </main>

  <!-- Drawer -->
  <aside id="drawer" class="drawer" aria-hidden="true">
    <div class="drawerGlass"></div>
    <div class="drawerPanel">
      <div class="drawerTop">
        <div class="drawerTitle">Ci • Чат</div>
        <div class="drawerBtns">
          <button class="miniBtn" id="btnRegistry">Registry</button>
          <button class="miniBtn" id="btnPackages">Node-packages</button>
          <button class="miniBtn danger" id="drawerClose">Закрити</button>
        </div>
      </div>

      <div id="chat" class="chat">
        <div class="b bot">Ci online. Пиши.</div>
      </div>

      <div class="bar">
        <input id="msg" placeholder="Напиши..." autocomplete="off" />
        <button id="send">➤</button>
      </div>
      <div class="hint">
        POST /api/chat • POST /api/exec • GET /registry • GET /node-packages
      </div>
    </div>
  </aside>

  <script src="app.js"></script>
</body>
</html>
HTML

cat > styles.css <<'CSS'
:root{
  --navy:#0B2340;
  --azure:#1FA4FF;
  --sky:#87D3FF;
  --gold:#FFC34D;
  --amber:#FFA72B;
  --cream:#FFE6B3;

  --bg0:#070A10;
  --bg1:#0B0F14;
  --stroke:rgba(255,255,255,.10);
  --stroke2:rgba(255,255,255,.14);
  --text:rgba(232,238,246,.92);
  --muted:rgba(232,238,246,.62);

  --glass:rgba(16,22,32,.58);
  --glass2:rgba(12,16,24,.62);

  --grad:linear-gradient(35deg, var(--azure) 0%, var(--sky) 38%, var(--gold) 100%);
  --glow:0 0 0 1px rgba(255,255,255,.10), 0 18px 50px rgba(0,0,0,.50);
}

*{ box-sizing:border-box; }
html,body{ height:100%; }
body{
  margin:0;
  color:var(--text);
  font-family:system-ui,-apple-system,"Segoe UI",Roboto,Arial;
  background:radial-gradient(900px 600px at 30% 20%, rgba(31,164,255,.20), transparent 60%),
             radial-gradient(900px 600px at 70% 80%, rgba(255,195,77,.18), transparent 60%),
             linear-gradient(180deg, #070A10 0%, #090E16 100%);
  overflow-x:hidden;
}

.bg{
  position:fixed; inset:0;
  background:
    radial-gradient(900px 500px at 55% -10%, rgba(135,211,255,.18), transparent 60%),
    radial-gradient(900px 500px at 30% 110%, rgba(255,167,43,.12), transparent 60%);
  pointer-events:none;
  filter:saturate(1.08);
}

.topbar{
  position:sticky; top:0; z-index:20;
  display:flex; align-items:center; gap:12px;
  padding:10px 12px;
  border-bottom:1px solid var(--stroke);
  background:linear-gradient(180deg, rgba(7,10,16,.76), rgba(7,10,16,.46));
  backdrop-filter: blur(10px);
}

.ciBtn{
  width:44px; height:44px;
  border-radius:14px;
  border:1px solid var(--stroke2);
  background:linear-gradient(180deg, rgba(255,255,255,.06), rgba(255,255,255,.02));
  box-shadow: var(--glow);
  display:grid; place-items:center;
  cursor:pointer;
  transition: transform .18s ease, border-color .18s ease;
}
.ciBtn:active{ transform: scale(.98); }
.ciBtn:hover{ border-color: rgba(255,255,255,.22); }

.ciLogo{
  width:26px; height:26px;
  object-fit:contain;
  filter: drop-shadow(0 8px 18px rgba(0,0,0,.45));
}

.topTitle{ flex:1; min-width:0; }
.h1{ font-weight:900; letter-spacing:.2px; }
.h2{ color:var(--muted); font-size:12px; margin-top:2px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }

.topRight{ display:flex; gap:8px; align-items:center; }
.pill{
  padding:8px 10px;
  border-radius:999px;
  border:1px solid var(--stroke);
  background:rgba(0,0,0,.20);
  color:var(--muted);
  font-size:12px;
}

.wrap{ padding:14px 12px 28px; }
.grid{
  display:grid;
  grid-template-columns: 1fr;
  gap:12px;
  max-width:1100px;
  margin:0 auto;
}

.card{
  border:1px solid var(--stroke);
  border-radius:18px;
  background:linear-gradient(180deg, rgba(255,255,255,.05), rgba(255,255,255,.02));
  box-shadow:0 16px 44px rgba(0,0,0,.45);
  overflow:hidden;
}

.cardHead{
  display:flex; align-items:center; justify-content:space-between;
  padding:12px 12px 0;
}
.cardTitle{ font-weight:800; }
.badge{
  font-size:12px;
  padding:6px 10px;
  border-radius:999px;
  border:1px solid var(--stroke);
  color:rgba(232,238,246,.70);
  background:rgba(0,0,0,.18);
}

.cardBody{ padding:12px; }
.mini{ color:var(--muted); font-size:13px; }
.cardActions{ display:flex; gap:10px; margin-top:10px; }

.btn{
  padding:10px 12px;
  border-radius:14px;
  border:1px solid rgba(255,255,255,.16);
  background:rgba(15,22,32,.56);
  color:var(--text);
  font-weight:750;
  cursor:pointer;
  transition: transform .18s ease, border-color .18s ease, background .18s ease;
}
.btn:hover{ border-color: rgba(255,255,255,.24); background:rgba(15,22,32,.72); }
.btn:active{ transform: scale(.99); }

.btn.ghost{
  background:transparent;
  border:1px solid rgba(255,255,255,.14);
  color:rgba(232,238,246,.82);
}

.hero{
  border-radius:22px;
  background:
    radial-gradient(700px 220px at 35% 0%, rgba(31,164,255,.20), transparent 70%),
    radial-gradient(700px 220px at 90% 80%, rgba(255,195,77,.18), transparent 70%),
    linear-gradient(180deg, rgba(255,255,255,.06), rgba(255,255,255,.02));
}
.heroTitle{
  font-weight:950;
  font-size:28px;
  letter-spacing:.2px;
}
.heroSub{ color:var(--muted); margin-top:4px; }
.heroActions{ display:flex; gap:10px; margin-top:12px; flex-wrap:wrap; }
.heroMeta{ margin-top:12px; display:grid; gap:6px; }
.kv{ display:flex; justify-content:space-between; color:rgba(232,238,246,.78); font-size:12px; }
.kv span:first-child{ color:rgba(232,238,246,.52); }

.wide{ grid-column:1 / -1; }
.out{
  margin:0;
  padding:12px;
  border-radius:16px;
  border:1px solid rgba(255,255,255,.12);
  background:rgba(0,0,0,.22);
  color:rgba(232,238,246,.86);
  font-size:12px;
  line-height:1.35;
  max-height:42vh;
  overflow:auto;
}

.drawer{
  position:fixed; inset:0;
  z-index:60;
  display:none;
}
.drawer.on{ display:block; }

.drawerGlass{
  position:absolute; inset:0;
  background:rgba(0,0,0,.46);
  backdrop-filter: blur(8px);
}

.drawerPanel{
  position:absolute;
  inset:10px;
  border-radius:22px;
  border:1px solid rgba(255,255,255,.14);
  background:rgba(10,14,22,.62);
  box-shadow:0 18px 70px rgba(0,0,0,.65);
  display:flex;
  flex-direction:column;
  overflow:hidden;
}

.drawerTop{
  display:flex; align-items:center; justify-content:space-between;
  padding:10px 12px;
  border-bottom:1px solid rgba(255,255,255,.10);
  background:linear-gradient(180deg, rgba(255,255,255,.05), rgba(255,255,255,.01));
}
.drawerTitle{ font-weight:900; }
.drawerBtns{ display:flex; gap:8px; }

.miniBtn{
  padding:8px 10px;
  border-radius:12px;
  border:1px solid rgba(255,255,255,.14);
  background:rgba(0,0,0,.18);
  color:rgba(232,238,246,.82);
  font-weight:800;
  cursor:pointer;
}
.miniBtn.danger{ border-color: rgba(255,120,120,.26); }

.chat{
  flex:1;
  overflow:auto;
  padding:12px;
  display:flex;
  flex-direction:column;
  gap:10px;
}
.b{
  padding:10px 12px;
  border:1px solid rgba(255,255,255,.12);
  border-radius:16px;
  max-width:92%;
  white-space:pre-wrap;
  word-break:break-word;
}
.me{
  align-self:flex-end;
  background:rgba(31,164,255,.10);
}
.bot{
  align-self:flex-start;
  background:rgba(255,195,77,.08);
}

.bar{
  display:flex;
  gap:10px;
  padding:10px;
  border-top:1px solid rgba(255,255,255,.10);
  background:rgba(0,0,0,.14);
}
#msg{
  flex:1;
  padding:12px;
  border-radius:14px;
  border:1px solid rgba(255,255,255,.12);
  background:rgba(0,0,0,.18);
  color:var(--text);
  outline:none;
}
#send{
  padding:0 14px;
  border-radius:14px;
  border:1px solid rgba(255,255,255,.18);
  background:linear-gradient(90deg, rgba(31,164,255,.22), rgba(255,195,77,.18));
  color:var(--text);
  font-weight:950;
  cursor:pointer;
}
.hint{
  padding:8px 12px 12px;
  font-size:11px;
  color:rgba(232,238,246,.52);
}

/* responsive */
@media (min-width: 880px){
  .grid{ grid-template-columns: 1.15fr 1fr; }
  .wide{ grid-column: 1 / -1; }
  .drawerPanel{ inset:14px; max-width:1100px; margin:0 auto; }
}
CSS

cat > app.js <<'JS'
(() => {
  const API_BASE = (new URLSearchParams(location.search).get('api')) || 'http://127.0.0.1:8790';

  const el = (id) => document.getElementById(id);
  const out = el('out');
  const apiPill = el('apiPill');
  const statusLine = el('statusLine');
  const apiUrl = el('apiUrl');
  const uiUrl = el('uiUrl');

  const drawer = el('drawer');
  const ciBtn = el('ciBtn');
  const openChat = el('openChat');
  const drawerClose = el('drawerClose');

  const chat = el('chat');
  const input = el('msg');
  const sendBtn = el('send');

  const btnRegistry = el('btnRegistry');
  const btnPackages = el('btnPackages');

  apiPill.textContent = `API: ${API_BASE}`;
  apiUrl.textContent = API_BASE;
  uiUrl.textContent = location.origin;

  function drawerOn(on) {
    if (on) {
      drawer.classList.add('on');
      drawer.setAttribute('aria-hidden', 'false');
      setTimeout(() => input?.focus(), 50);
    } else {
      drawer.classList.remove('on');
      drawer.setAttribute('aria-hidden', 'true');
    }
  }

  function addMsg(text, cls) {
    const d = document.createElement('div');
    d.className = `b ${cls}`;
    d.textContent = text;
    chat.appendChild(d);
    chat.scrollTop = chat.scrollHeight;
  }

  async function httpJSON(url, opts = {}) {
    const r = await fetch(url, opts);
    const t = await r.text();
    let j = null;
    try { j = JSON.parse(t); } catch (_) {}
    return { ok: r.ok, status: r.status, text: t, json: j };
  }

  function pretty(x) {
    try { return JSON.stringify(x, null, 2); } catch (_) { return String(x); }
  }

  async function checkHealth() {
    const h = await httpJSON(`${API_BASE}/health`);
    if (h.ok && h.json?.ok) {
      statusLine.textContent = `+ Є • model=${h.json.model || 'n/a'}`;
      out.textContent = pretty(h.json);
    } else {
      statusLine.textContent = `- Нема • ${h.status}`;
      out.textContent = h.text || '[no response]';
    }
  }

  async function execAction(action, payload = {}) {
    const body = { action, ...payload };
    const r = await httpJSON(`${API_BASE}/api/exec`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    out.textContent = r.json ? pretty(r.json) : (r.text || '[empty]');
    if (!r.ok) addMsg(`exec HTTP ${r.status}: ${(r.text || '').slice(0,120)}`, 'bot');
    return r;
  }

  async function getPath(path) {
    const r = await httpJSON(`${API_BASE}${path}`);
    out.textContent = r.json ? pretty(r.json) : (r.text || '[empty]');
    if (!r.ok) addMsg(`GET ${path} HTTP ${r.status}: ${(r.text || '').slice(0,120)}`, 'bot');
    return r;
  }

  async function sendChat() {
    const text = input.value.trim();
    if (!text) return;
    input.value = '';
    addMsg(text, 'me');

    const r = await httpJSON(`${API_BASE}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text })
    });

    if (!r.ok) {
      addMsg(`chat HTTP ${r.status}: ${(r.text || '').slice(0,160)}`, 'bot');
      return;
    }
    const reply = r.json?.reply ?? r.json?.text ?? r.text ?? '[empty]';
    addMsg(String(reply), 'bot');
  }

  // presets for node cards
  const PRESETS = {
    "kazkar.legend": () => execAction("actions.registry.get", { node: "kazkar", subnode: "legend_ci" }),
    "podija.emit": () => execAction("actions.event.emit", { node: "podija", event: { name: "podija.emit", ts: new Date().toISOString() } }),
    "nastrij.state": () => execAction("actions.state.get", { node: "nastrij" }),
    "malya.idea": () => execAction("actions.module.call", { node: "malya", module: "idea", input: { prompt: "А якщо?" } }),
    "calendar.get": () => execAction("actions.schedule.get", { node: "calendar" }),
    "gallery.list": () => execAction("actions.asset.get", { node: "gallery", query: { list: true } }),
  };

  document.addEventListener('click', async (e) => {
    const t = e.target;

    if (t?.id === 'ciBtn') drawerOn(true);
    if (t?.id === 'openChat') drawerOn(true);
    if (t?.id === 'drawerClose') drawerOn(false);

    if (t?.dataset?.open === 'chat') drawerOn(true);

    if (t?.dataset?.action) {
      await execAction(t.dataset.action);
    }

    if (t?.dataset?.preset) {
      const fn = PRESETS[t.dataset.preset];
      if (fn) await fn();
      else out.textContent = `Preset not found: ${t.dataset.preset}`;
    }
  });

  drawer.addEventListener('click', (e) => {
    if (e.target === drawer) drawerOn(false);
  });

  sendBtn.onclick = sendChat;
  input.addEventListener('keydown', (e) => { if (e.key === 'Enter') sendChat(); });

  btnRegistry.onclick = () => getPath('/registry');
  btnPackages.onclick = () => getPath('/node-packages');

  // init
  checkHealth();
})();
JS

# --- restart UI server on :8010 ---
cd "$ROOT" || exit 1
pkill -f "python -m http.server 8010" 2>/dev/null || true
nohup python -m http.server 8010 --directory "$UI" --bind 127.0.0.1 > "$LOG/ui_8010.log" 2>&1 &

sleep 0.4

echo "=== [VERIFY] UI ==="
curl -sS --max-time 2 -I http://127.0.0.1:8010/ | head -n 1 || echo "UI DOWN"
echo

echo "=== [VERIFY] API ==="
curl -sS --max-time 2 "$API_BASE/health" || echo "API DOWN"
echo
echo "=== READY LINKS ==="
echo "UI            : http://127.0.0.1:8010/"
echo "UI (alt API)  : http://127.0.0.1:8010/?api=http://127.0.0.1:8790"
echo "API health    : http://127.0.0.1:8790/health"
echo "API chat      : http://127.0.0.1:8790/api/chat"
echo "API exec      : http://127.0.0.1:8790/api/exec"
echo "Registry (GET): http://127.0.0.1:8790/registry"
echo "Node-packages : http://127.0.0.1:8790/node-packages"
