#!/data/data/com.termux/files/usr/bin/bash
set -e
ROOT="/data/data/com.termux/files/home/cimeika/cit"
UI="$ROOT/ui"
PAGES="$UI/pages"
ICONS="$UI/icons"
LOG="$ROOT/logs"

cd "$ROOT" || exit 1
mkdir -p "$LOG" "$UI" "$PAGES" "$ICONS"

# -----------------------------
# ICON: Ci (simple, no bg)
# -----------------------------
cat > "$ICONS/ci.svg" <<'SVG'
<svg xmlns="http://www.w3.org/2000/svg" width="96" height="96" viewBox="0 0 96 96">
  <defs>
    <linearGradient id="ciG" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#1FA4FF"/>
      <stop offset="0.45" stop-color="#87D3FF"/>
      <stop offset="1" stop-color="#FFC34D"/>
    </linearGradient>
    <filter id="glow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="2.2" result="b"/>
      <feMerge>
        <feMergeNode in="b"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  <circle cx="48" cy="48" r="36" fill="none" stroke="url(#ciG)" stroke-width="6" filter="url(#glow)"/>
  <path d="M56 31c-3-2-6-3-10-3-11 0-20 9-20 20s9 20 20 20c4 0 7-1 10-3"
        fill="none" stroke="url(#ciG)" stroke-width="6" stroke-linecap="round"/>
  <path d="M60 34v28" fill="none" stroke="url(#ciG)" stroke-width="6" stroke-linecap="round"/>
</svg>
SVG

# -----------------------------
# STYLES: CI palette + glass + dashboard + drawer chat
# -----------------------------
cat > "$UI/styles.css" <<'CSS'
:root{
  --bg0:#07111b;
  --bg1:#0b1624;
  --line:rgba(255,255,255,.10);
  --glass:rgba(255,255,255,.06);
  --txt:#e8eef6;
  --mut:#b5c2d6;

  --ciNavy:#0B2340;
  --ciAzure:#1FA4FF;
  --ciSky:#87D3FF;
  --ciGold:#FFC34D;
  --ciAmber:#FFA72B;
  --ciCream:#FFE6B3;

  --grad: linear-gradient(35deg, var(--ciAzure) 0%, var(--ciSky) 45%, var(--ciGold) 100%);
  --rad: 18px;
  --shadow: 0 10px 30px rgba(0,0,0,.35);
}

*{box-sizing:border-box;font-family:system-ui,-apple-system,"Segoe UI",Roboto,Arial}
html,body{height:100%}
body{
  margin:0;
  color:var(--txt);
  background:
    radial-gradient(1200px 800px at 20% 10%, rgba(31,164,255,.18), transparent 55%),
    radial-gradient(900px 700px at 80% 30%, rgba(255,195,77,.16), transparent 60%),
    linear-gradient(180deg, #07111b 0%, #061321 55%, #07111b 100%);
  overflow:hidden;
}

a{color:inherit;text-decoration:none}

.topbar{
  position:sticky; top:0; z-index:5;
  display:flex; align-items:center; justify-content:space-between;
  padding:14px 14px 12px;
  border-bottom:1px solid var(--line);
  background:linear-gradient(180deg, rgba(7,17,27,.92), rgba(7,17,27,.55));
  backdrop-filter: blur(10px);
}

.brand{
  display:flex; align-items:center; gap:10px;
}
.brand .logo{
  width:34px;height:34px;
  display:grid;place-items:center;
}
.brand .logo img{width:34px;height:34px;display:block}
.brand .title{
  display:flex; flex-direction:column; line-height:1.1;
}
.brand .title b{font-size:16px;letter-spacing:.3px}
.brand .title span{font-size:12px;color:var(--mut)}

.actions{
  display:flex; gap:8px; align-items:center;
}
.pill{
  padding:9px 12px;
  border:1px solid var(--line);
  border-radius:999px;
  background:rgba(255,255,255,.04);
  color:var(--txt);
}
.pill strong{font-weight:800}
.pill.ci{
  border:1px solid rgba(31,164,255,.35);
  background:linear-gradient(180deg, rgba(31,164,255,.10), rgba(255,195,77,.06));
}

.shell{
  height:calc(100% - 58px);
  display:grid;
  grid-template-columns: 1fr;
  overflow:hidden;
}

.main{
  height:100%;
  overflow:auto;
  padding:14px;
}

.grid{
  display:grid;
  grid-template-columns: 1fr;
  gap:12px;
}

.card{
  border:1px solid var(--line);
  background:rgba(255,255,255,.04);
  border-radius:var(--rad);
  padding:14px;
  box-shadow: var(--shadow);
}

.card .hdr{
  display:flex; align-items:center; justify-content:space-between;
  gap:10px;
}
.badge{
  font-size:12px;
  padding:6px 10px;
  border-radius:999px;
  border:1px solid rgba(255,255,255,.12);
  color:var(--mut);
  background:rgba(0,0,0,.18);
}
.badge.ci{
  border-color: rgba(31,164,255,.32);
  color:#dbefff;
  background:rgba(31,164,255,.08);
}

.h1{
  font-size:18px;
  margin:0;
}
.sub{
  margin-top:8px;
  color:var(--mut);
  font-size:13px;
  line-height:1.35;
}

.nav{
  display:grid;
  grid-template-columns: 1fr;
  gap:10px;
  margin-top:12px;
}
.nav a{
  border:1px solid var(--line);
  border-radius:16px;
  padding:12px;
  background:rgba(255,255,255,.035);
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:10px;
}
.nav a:hover{border-color:rgba(255,255,255,.22)}
.nav a .left{
  display:flex; flex-direction:column; gap:2px;
}
.nav a .left b{font-size:14px}
.nav a .left span{font-size:12px;color:var(--mut)}
.nav a .go{
  width:34px;height:34px;
  border-radius:14px;
  border:1px solid rgba(255,255,255,.12);
  display:grid;place-items:center;
  background:rgba(0,0,0,.15);
}
.nav a.ciItem{
  border-color: rgba(31,164,255,.28);
  background: linear-gradient(180deg, rgba(31,164,255,.08), rgba(255,195,77,.04));
}

/* Floating Ci logo button (global) */
.ci-fab{
  position:fixed;
  right:16px;
  bottom:22px;
  width:60px;height:60px;
  border-radius:22px;
  border:1px solid rgba(255,255,255,.14);
  background:rgba(255,255,255,.04);
  box-shadow: 0 14px 40px rgba(0,0,0,.45);
  display:grid;place-items:center;
  z-index:20;
  backdrop-filter: blur(10px);
}
.ci-fab img{width:40px;height:40px}
.ci-fab:active{transform:scale(.98)}

/* Drawer / Overlay */
.overlay{
  position:fixed; inset:0;
  background: rgba(0,0,0,.55);
  display:none;
  z-index:30;
}
.overlay.on{display:block}
.drawer{
  position:absolute;
  left:0; right:0; bottom:0;
  height:78vh;
  border-top-left-radius:24px;
  border-top-right-radius:24px;
  border:1px solid rgba(255,255,255,.10);
  background:
    radial-gradient(900px 700px at 20% 0%, rgba(31,164,255,.14), transparent 60%),
    radial-gradient(900px 700px at 80% 10%, rgba(255,195,77,.12), transparent 60%),
    rgba(7,17,27,.92);
  backdrop-filter: blur(12px);
  box-shadow: 0 -18px 50px rgba(0,0,0,.55);
  overflow:hidden;
  display:flex;
  flex-direction:column;
}
.drawerTop{
  display:flex; align-items:center; justify-content:space-between;
  padding:12px 14px;
  border-bottom:1px solid rgba(255,255,255,.10);
}
.drawerTop .t{
  display:flex; align-items:center; gap:10px;
}
.drawerTop .t b{font-size:14px}
.drawerTop .t span{font-size:12px;color:var(--mut)}
.drawerTop .x{
  width:42px;height:42px;
  border-radius:16px;
  border:1px solid rgba(255,255,255,.12);
  background:rgba(255,255,255,.04);
  color:var(--txt);
  font-weight:900;
}

.quick{
  display:flex; gap:8px; padding:10px 12px;
  overflow:auto;
  border-bottom:1px solid rgba(255,255,255,.08);
}
.q{
  white-space:nowrap;
  padding:8px 10px;
  border-radius:999px;
  border:1px solid rgba(255,255,255,.12);
  background:rgba(0,0,0,.18);
  color:var(--txt);
  font-size:12px;
}
.q.ci{border-color:rgba(31,164,255,.32); background:rgba(31,164,255,.08)}
.q.w{border-color:rgba(135,211,255,.30); background:rgba(135,211,255,.07)}
.q.g{border-color:rgba(255,195,77,.28); background:rgba(255,195,77,.06)}

.chat{
  flex:1;
  padding:12px;
  overflow:auto;
  display:flex;
  flex-direction:column;
  gap:10px;
}
.b{
  max-width:92%;
  padding:10px 12px;
  border-radius:16px;
  border:1px solid rgba(255,255,255,.10);
  background:rgba(255,255,255,.04);
}
.me{align-self:flex-end; border-color:rgba(31,164,255,.25); background:rgba(31,164,255,.08)}
.bot{align-self:flex-start}
.meta{
  font-size:11px;color:var(--mut); margin-top:6px;
}

.bar{
  display:flex; gap:8px;
  padding:10px 12px;
  border-top:1px solid rgba(255,255,255,.10);
  background:rgba(0,0,0,.18);
}
#msg{
  flex:1;
  padding:12px;
  border-radius:16px;
  border:1px solid rgba(255,255,255,.12);
  background:rgba(255,255,255,.04);
  color:var(--txt);
  outline:none;
}
#send{
  width:54px;
  border-radius:16px;
  border:1px solid rgba(31,164,255,.35);
  background:rgba(31,164,255,.14);
  color:var(--txt);
  font-weight:900;
}

.footerNote{
  margin-top:10px;
  font-size:12px;
  color:var(--mut);
}

@media (min-width: 900px){
  .grid{grid-template-columns: 1fr 1fr}
  .drawer{left:auto; right:16px; bottom:16px; width:440px; height:78vh; border-radius:24px}
  .overlay{background: rgba(0,0,0,.45)}
}
CSS

# -----------------------------
# INDEX (Dashboard)
# -----------------------------
cat > "$UI/index.html" <<'HTML'
<!doctype html>
<html lang="uk">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>CIT • Cimeika</title>
  <link rel="stylesheet" href="styles.css"/>
</head>
<body>
  <div class="topbar">
    <div class="brand">
      <div class="logo"><img src="icons/ci.svg" alt="Ci"></div>
      <div class="title">
        <b>CIT</b>
        <span>Cimeika • локальний вузол</span>
      </div>
    </div>
    <div class="actions">
      <a class="pill" href="/registry"><strong>Registry</strong></a>
      <a class="pill ci" href="/node-packages"><strong>Nodes</strong></a>
    </div>
  </div>

  <div class="shell">
    <div class="main">
      <div class="grid">

        <div class="card">
          <div class="hdr">
            <h1 class="h1">Простір Ci</h1>
            <span class="badge ci">є</span>
          </div>
          <div class="sub">
            Дашборд + глобальна кнопка Ci. Чат відкривається поверх будь-якого екрану.
            Вся палітра, підсвітка, текстура — прояв Ci.
          </div>

          <div class="nav">
            <a class="ciItem" href="pages/ci.html">
              <div class="left">
                <b>сі'</b>
                <span>центр / оператор / контакт</span>
              </div>
              <div class="go">➜</div>
            </a>

            <a href="pages/kazkar.html">
              <div class="left">
                <b>Казкар'</b>
                <span>пам’ять / оповідач / основа</span>
              </div>
              <div class="go">➜</div>
            </a>

            <a href="pages/legend_ci.html">
              <div class="left">
                <b>✨Легенда сі'</b>
                <span>бібліотека сенсів / було-є-буде</span>
              </div>
              <div class="go">➜</div>
            </a>
          </div>
        </div>

        <div class="card">
          <div class="hdr">
            <h1 class="h1">Вузли Cimeika</h1>
            <span class="badge">активні</span>
          </div>
          <div class="sub">
            Єдиний принцип взаємодії і активностей. Кожен вузол має свою сторінку домену (у нас зараз локальні routes).
          </div>

          <div class="nav">
            <a href="pages/podija.html">
              <div class="left">
                <b>ПоДія'</b>
                <span>майбутнє / ініціації / запуск</span>
              </div>
              <div class="go">➜</div>
            </a>
            <a href="pages/nastrij.html">
              <div class="left">
                <b>Настрій'</b>
                <span>стан / вода / зараз</span>
              </div>
              <div class="go">➜</div>
            </a>
            <a href="pages/malya.html">
              <div class="left">
                <b>Маля'</b>
                <span>ідеї / повітря / теперішнє</span>
              </div>
              <div class="go">➜</div>
            </a>
            <a href="pages/calendar.html">
              <div class="left">
                <b>Календар'</b>
                <span>ритми / точки часу / план</span>
              </div>
              <div class="go">➜</div>
            </a>
            <a href="pages/gallery.html">
              <div class="left">
                <b>Галерея'</b>
                <span>історії / слайди / медіа</span>
              </div>
              <div class="go">➜</div>
            </a>
          </div>

          <div class="footerNote">
            API: /health • /api/chat • /api/exec • /registry • /node-packages
          </div>
        </div>

      </div>
    </div>
  </div>

  <!-- Global Ci button -->
  <button class="ci-fab" id="ciFab" aria-label="Ci">
    <img src="icons/ci.svg" alt="Ci">
  </button>

  <!-- Overlay drawer -->
  <div class="overlay" id="overlay" aria-hidden="true">
    <div class="drawer" role="dialog" aria-label="Ci Chat">
      <div class="drawerTop">
        <div class="t">
          <img src="icons/ci.svg" alt="Ci" style="width:28px;height:28px">
          <div>
            <b>Ci • чат</b><br/>
            <span>локально через CIT API</span>
          </div>
        </div>
        <button class="x" id="closeDrawer" aria-label="Закрити">✕</button>
      </div>

      <div class="quick">
        <button class="q ci" data-q="actions.registry.get">registry.get</button>
        <button class="q w" data-q="actions.node_packages.get">node_packages.get</button>
        <button class="q g" data-q="ping">ping</button>
      </div>

      <div id="chat" class="chat">
        <div class="b bot">CIT піднявся. Відкрий Ci і пиши. 👌</div>
      </div>

      <div class="bar">
        <input id="msg" placeholder="Напиши...">
        <button id="send">➤</button>
      </div>
    </div>
  </div>

  <script src="app.js"></script>
</body>
</html>
HTML

# -----------------------------
# PAGES (simple shells; Ci button still works)
# -----------------------------
mkpage () {
  local file="$1" title="$2" lead="$3"
  cat > "$PAGES/$file" <<HTML
<!doctype html>
<html lang="uk">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>${title} • CIT</title>
  <link rel="stylesheet" href="../styles.css"/>
</head>
<body>
  <div class="topbar">
    <div class="brand">
      <div class="logo"><img src="../icons/ci.svg" alt="Ci"></div>
      <div class="title">
        <b>${title}</b>
        <span>${lead}</span>
      </div>
    </div>
    <div class="actions">
      <a class="pill" href="../index.html"><strong>Dashboard</strong></a>
      <a class="pill ci" href="/health"><strong>API</strong></a>
    </div>
  </div>

  <div class="shell">
    <div class="main">
      <div class="card">
        <div class="hdr">
          <h1 class="h1">${title}</h1>
          <span class="badge">є</span>
        </div>
        <div class="sub">${lead}</div>

        <div class="nav" style="margin-top:14px">
          <a href="../index.html">
            <div class="left">
              <b>Повернутись</b>
              <span>до дашборду</span>
            </div>
            <div class="go">↩</div>
          </a>
        </div>
      </div>
    </div>
  </div>

  <button class="ci-fab" id="ciFab" aria-label="Ci">
    <img src="../icons/ci.svg" alt="Ci">
  </button>

  <div class="overlay" id="overlay" aria-hidden="true">
    <div class="drawer" role="dialog" aria-label="Ci Chat">
      <div class="drawerTop">
        <div class="t">
          <img src="../icons/ci.svg" alt="Ci" style="width:28px;height:28px">
          <div>
            <b>Ci • чат</b><br/>
            <span>локально через CIT API</span>
          </div>
        </div>
        <button class="x" id="closeDrawer" aria-label="Закрити">✕</button>
      </div>

      <div class="quick">
        <button class="q ci" data-q="actions.registry.get">registry.get</button>
        <button class="q w" data-q="actions.node_packages.get">node_packages.get</button>
        <button class="q g" data-q="ping">ping</button>
      </div>

      <div id="chat" class="chat">
        <div class="b bot">Вузол: ${title}. Ci-чат доступний поверх сторінки.</div>
      </div>

      <div class="bar">
        <input id="msg" placeholder="Напиши...">
        <button id="send">➤</button>
      </div>
    </div>
  </div>

  <script src="../app.js"></script>
</body>
</html>
HTML
}

mkpage "ci.html"        "сі'"            "центр / контроль / контакт"
mkpage "kazkar.html"    "Казкар'"        "пам’ять / оповідач / основа"
mkpage "legend_ci.html" "✨Легенда сі'"   "бібліотека сенсів / було-є-буде"
mkpage "podija.html"    "ПоДія'"         "майбутнє / ініціації / запуск"
mkpage "nastrij.html"   "Настрій'"       "стан / вода / зараз"
mkpage "malya.html"     "Маля'"          "ідеї / повітря / теперішнє"
mkpage "calendar.html"  "Календар'"      "ритми / точки часу / план"
mkpage "gallery.html"   "Галерея'"       "історії / медіа / слайди"

# -----------------------------
# APP.JS (drawer + chat + exec shortcuts)
# -----------------------------
cat > "$UI/app.js" <<'JS'
(() => {
  const API_CHAT = 'http://127.0.0.1:8790/api/chat';
  const API_EXEC = 'http://127.0.0.1:8790/api/exec';

  const qs = (s) => document.querySelector(s);

  const overlay = qs('#overlay');
  const fab = qs('#ciFab');
  const closeBtn = qs('#closeDrawer');

  const chat = qs('#chat');
  const input = qs('#msg');
  const sendBtn = qs('#send');

  const addMsg = (text, cls, meta=null) => {
    if (!chat) return;
    const d = document.createElement('div');
    d.className = `b ${cls}`;
    d.textContent = text;
    if (meta) {
      const m = document.createElement('div');
      m.className = 'meta';
      m.textContent = meta;
      d.appendChild(m);
    }
    chat.appendChild(d);
    chat.scrollTop = chat.scrollHeight;
  };

  const openDrawer = () => {
    if (!overlay) return;
    overlay.classList.add('on');
    overlay.setAttribute('aria-hidden','false');
    setTimeout(() => input && input.focus(), 50);
  };

  const closeDrawer = () => {
    if (!overlay) return;
    overlay.classList.remove('on');
    overlay.setAttribute('aria-hidden','true');
  };

  if (fab) fab.addEventListener('click', openDrawer);
  if (closeBtn) closeBtn.addEventListener('click', closeDrawer);
  if (overlay) overlay.addEventListener('click', (e) => {
    if (e.target === overlay) closeDrawer();
  });

  // Quick actions
  document.addEventListener('click', async (e) => {
    const btn = e.target?.closest?.('button[data-q]');
    if (!btn) return;

    openDrawer();

    const q = btn.getAttribute('data-q');
    if (q === 'ping') {
      input.value = 'ping';
      send();
      return;
    }

    // exec action
    addMsg(`exec: ${q}`, 'me');
    try {
      const r = await fetch(API_EXEC, {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ action: q, payload: {} })
      });
      const raw = await r.text();
      let j=null; try{ j=JSON.parse(raw);}catch(_){}
      if (!r.ok) {
        addMsg(`HTTP ${r.status}: ${raw.slice(0,200)}`, 'bot');
        return;
      }
      addMsg(JSON.stringify(j?.result ?? j, null, 2).slice(0, 1200), 'bot', 'api: /api/exec');
    } catch (err) {
      addMsg(`API error: ${String(err).slice(0,120)}`, 'bot');
    }
  });

  async function send(){
    const text = (input?.value || '').trim();
    if (!text) return;
    input.value = '';
    addMsg(text, 'me');

    try {
      const r = await fetch(API_CHAT, {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ message: text })
      });

      const raw = await r.text();
      let j=null; try{ j=JSON.parse(raw);}catch(_){}

      if (!r.ok) {
        addMsg(`HTTP ${r.status}: ${raw.slice(0,200)}`, 'bot');
        return;
      }

      const reply = j?.reply ?? j?.text ?? j?.message ?? raw;
      addMsg(String(reply).slice(0, 2000), 'bot', 'api: /api/chat');
    } catch (err) {
      addMsg(`API error: ${String(err).slice(0,120)}`, 'bot');
    }
  }

  if (sendBtn) sendBtn.addEventListener('click', send);
  if (input) input.addEventListener('keydown', (e) => { if (e.key === 'Enter') send(); });

  // If user opens /pages/* directly, keep drawer closed by default.
})();
JS

# -----------------------------
# RESTART static UI server (:8010)
# -----------------------------
pkill -f "python -m http.server 8010" 2>/dev/null || true
cd "$UI" || exit 1
nohup python -m http.server 8010 --bind 127.0.0.1 > "$LOG/ui_8010.log" 2>&1 &

sleep 0.4

echo "=== UIv2 READY ==="
echo "Dashboard    : http://127.0.0.1:8010/"
echo "Ci'          : http://127.0.0.1:8010/pages/ci.html"
echo "Kazkar'      : http://127.0.0.1:8010/pages/kazkar.html"
echo "Legend Ci'   : http://127.0.0.1:8010/pages/legend_ci.html"
echo "PoDija'      : http://127.0.0.1:8010/pages/podija.html"
echo "Nastrij'     : http://127.0.0.1:8010/pages/nastrij.html"
echo "Malya'       : http://127.0.0.1:8010/pages/malya.html"
echo "Calendar'    : http://127.0.0.1:8010/pages/calendar.html"
echo "Gallery'     : http://127.0.0.1:8010/pages/gallery.html"
echo
echo "=== VERIFY ==="
curl -sS --max-time 2 -I http://127.0.0.1:8010/ | head -n 1 || echo "UI DOWN"
echo -n "API health: "
curl -sS --max-time 2 http://127.0.0.1:8790/health | head -c 120; echo
