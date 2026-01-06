#!/data/data/com.termux/files/usr/bin/bash
set -e

ROOT="/data/data/com.termux/files/home/cimeika/cit"
UI="$ROOT/ui"
ASSETS="$UI/assets"
LOG="$ROOT/logs"

cd "$ROOT" || exit 1
mkdir -p "$LOG" "$ASSETS"

echo "=== [0] STOP old UI server (best-effort) ==="
pkill -f "python -m http.server 8010" 2>/dev/null || true

echo "=== [1] ENSURE CI LOGO (assets/ci.png) ==="
# 1) Try canonical raw (case sensitive)
CANON_URL="https://raw.githubusercontent.com/Ihorog/media/main/Ci.png"
TMP="$ASSETS/ci.png.tmp"

if command -v curl >/dev/null 2>&1; then
  if curl -fsSL --max-time 8 "$CANON_URL" -o "$TMP" 2>/dev/null; then
    mv -f "$TMP" "$ASSETS/ci.png"
    echo "OK: downloaded canonical -> $ASSETS/ci.png"
  else
    rm -f "$TMP" 2>/dev/null || true
    echo "WARN: canonical download failed, trying local copies..."
  fi
fi

if [ ! -s "$ASSETS/ci.png" ]; then
  for src in \
    "$UI/brand/ci.png" \
    "$UI/icons/ci.png" \
    "$ROOT/brand/ci.png" \
    "$ROOT/assets/ci.png"
  do
    if [ -s "$src" ]; then
      cp -f "$src" "$ASSETS/ci.png"
      echo "OK: copied from $src -> $ASSETS/ci.png"
      break
    fi
  done
fi

if [ ! -s "$ASSETS/ci.png" ]; then
  echo "FAIL: ci.png not found/downloaded. Put it at: $ASSETS/ci.png"
  exit 1
fi

echo "=== [2] WRITE UIv2 (dashboard + chat in logo drawer) ==="
cat > "$UI/index.html" <<'HTML'
<!doctype html>
<html lang="uk">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>CIT — UIv2</title>
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
  <div class="app">

    <header class="topbar">
      <button id="ciBtn" class="ci-btn" aria-label="Ci">
        <img class="ci-logo" src="assets/ci.png" alt="Ci" />
      </button>

      <div class="top-title">
        <div class="t1">Ci</div>
        <div class="t2">Cimeika / CIT</div>
      </div>

      <div class="top-actions">
        <button id="refreshBtn" class="btn ghost">⟲</button>
        <button id="themeBtn" class="btn ghost">◐</button>
      </div>
    </header>

    <main class="main">
      <section class="hero">
        <div class="hero-bg"></div>
        <div class="hero-card">
          <div class="hero-title">Дашборд</div>
          <div class="hero-sub">Єдиний принцип взаємодії та активностей. Все — прояв Ci.</div>

          <div class="stats">
            <div class="stat">
              <div class="k">API</div>
              <div class="v" id="apiState">…</div>
              <div class="s" id="apiModel">…</div>
            </div>
            <div class="stat">
              <div class="k">UI</div>
              <div class="v">ONLINE</div>
              <div class="s">:8010</div>
            </div>
            <div class="stat">
              <div class="k">Node</div>
              <div class="v">CIT</div>
              <div class="s">Termux</div>
            </div>
          </div>

          <div class="quick">
            <button class="btn" data-act="chat:ping">Ping</button>
            <button class="btn" data-act="exec:registry">Registry</button>
            <button class="btn" data-act="exec:nodepkgs">Node-packages</button>
          </div>
        </div>
      </section>

      <section class="grid">
        <div class="card">
          <div class="card-h">Сімейний оператор</div>
          <div class="card-b mono">
сі'
Cimeika
Казкар'
✨Легенда сі'
…
ПоДія'
Настрій'
Маля'
Календар'
Галерея'
          </div>
        </div>

        <div class="card">
          <div class="card-h">Вузли</div>
          <div class="card-b">
            <div class="chips">
              <span class="chip">Ci</span>
              <span class="chip">Казкар</span>
              <span class="chip">✨Легенда Ci</span>
              <span class="chip">ПоДія</span>
              <span class="chip">Настрій</span>
              <span class="chip">Маля</span>
              <span class="chip">Календар</span>
              <span class="chip">Галерея</span>
            </div>
            <div class="hint">Чат завжди доступний через лого Ci на будь-якому екрані.</div>
          </div>
        </div>

        <div class="card">
          <div class="card-h">Лінки</div>
          <div class="card-b">
            <div class="links">
              <a id="lnkUI" target="_blank" rel="noreferrer">UI</a>
              <a id="lnkHealth" target="_blank" rel="noreferrer">API /health</a>
              <a id="lnkChat" target="_blank" rel="noreferrer">API /api/chat</a>
              <a id="lnkExec" target="_blank" rel="noreferrer">API /api/exec</a>
              <a id="lnkReg" target="_blank" rel="noreferrer">/registry</a>
              <a id="lnkNP" target="_blank" rel="noreferrer">/node-packages</a>
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- Ci Drawer -->
    <div id="overlay" class="overlay hidden"></div>

    <aside id="drawer" class="drawer hidden" aria-hidden="true">
      <div class="drawer-top">
        <div class="drawer-brand">
          <img class="ci-logo sm" src="assets/ci.png" alt="Ci"/>
          <div>
            <div class="t1">Ci</div>
            <div class="t2">чат / exec</div>
          </div>
        </div>
        <button id="closeDrawer" class="btn ghost">✕</button>
      </div>

      <div class="tabs">
        <button class="tab active" data-tab="chat">Чат</button>
        <button class="tab" data-tab="exec">Exec</button>
        <button class="tab" data-tab="menu">Меню</button>
      </div>

      <div class="pane" data-pane="chat">
        <div id="chat" class="chat">
          <div class="b bot">CIT піднявся. Пиши.</div>
        </div>
        <div class="bar">
          <input id="msg" placeholder="Напиши..." autocomplete="off" />
          <button id="send" class="btn primary">➤</button>
        </div>
      </div>

      <div class="pane hidden" data-pane="exec">
        <div class="exec">
          <div class="exec-row">
            <div class="lbl">Action</div>
            <input id="execAction" class="in" placeholder="actions.registry.get" value="actions.registry.get" />
          </div>
          <div class="exec-row">
            <div class="lbl">Payload (JSON)</div>
            <textarea id="execPayload" class="ta" placeholder='{"ping":true}'>{}</textarea>
          </div>
          <div class="exec-row">
            <button id="execRun" class="btn primary">Виконати</button>
            <button id="execReg" class="btn">Registry</button>
            <button id="execNP" class="btn">Node-packages</button>
          </div>
          <pre id="execOut" class="out">{}</pre>
        </div>
      </div>

      <div class="pane hidden" data-pane="menu">
        <div class="menu">
          <button class="menu-item" data-open="page:ci">сі'</button>
          <button class="menu-item" data-open="page:cimeika">Cimeika</button>
          <button class="menu-item" data-open="page:kazkar">Казкар'</button>
          <button class="menu-item" data-open="page:legend">✨Легенда сі'</button>
          <div class="sep"></div>
          <button class="menu-item" data-open="page:podija">ПоДія'</button>
          <button class="menu-item" data-open="page:nastrij">Настрій'</button>
          <button class="menu-item" data-open="page:malya">Маля'</button>
          <div class="sep"></div>
          <button class="menu-item" data-open="page:calendar">Календар'</button>
          <button class="menu-item" data-open="page:gallery">Галерея'</button>
          <div class="hint">Поки це UI-шаблон: сторінки будуть доменними роутами в Cimeika.</div>
        </div>
      </div>
    </aside>

  </div>

  <script src="app.js"></script>
</body>
</html>
HTML

cat > "$UI/styles.css" <<'CSS'
:root{
  --bg0:#070B12;
  --bg1:#0B1422;
  --ink:#E8EEF6;
  --mut:#9FB0C3;
  --br:#1F2A36;
  --glass: rgba(12,18,28,.55);
  --glow: rgba(31,164,255,.24);
  --glow2: rgba(255,195,77,.18);
  --blue:#1FA4FF;
  --sky:#87D3FF;
  --gold:#FFC34D;
}

*{box-sizing:border-box; font-family:system-ui,-apple-system,"Segoe UI",Roboto,Arial}
body{margin:0;background:radial-gradient(1100px 700px at 15% 10%, var(--glow), transparent 60%),
                 radial-gradient(900px 600px at 90% 25%, var(--glow2), transparent 62%),
                 linear-gradient(180deg, var(--bg0), var(--bg1));
     color:var(--ink); min-height:100vh;}

a{color:var(--sky); text-decoration:none}
a:hover{opacity:.9}

.app{min-height:100vh; display:flex; flex-direction:column}

.topbar{
  position:sticky; top:0; z-index:10;
  display:flex; align-items:center; gap:10px;
  padding:10px 12px;
  border-bottom:1px solid var(--br);
  background:linear-gradient(180deg, rgba(10,16,26,.78), rgba(10,16,26,.52));
  backdrop-filter: blur(10px);
}

.ci-btn{
  width:42px; height:42px; border-radius:14px;
  border:1px solid rgba(255,255,255,.10);
  background:rgba(255,255,255,.04);
  display:flex; align-items:center; justify-content:center;
  box-shadow: 0 0 0 1px rgba(31,164,255,.10), 0 10px 30px rgba(0,0,0,.35);
}
.ci-btn:active{transform:scale(.98)}
.ci-logo{width:26px;height:26px;object-fit:contain}
.ci-logo.sm{width:22px;height:22px}

.top-title{flex:1}
.t1{font-weight:900; letter-spacing:.2px}
.t2{font-size:12px; color:var(--mut); margin-top:2px}

.btn{
  border:1px solid rgba(255,255,255,.12);
  background:rgba(255,255,255,.05);
  color:var(--ink);
  border-radius:14px;
  padding:10px 12px;
  font-weight:800;
}
.btn:active{transform:scale(.99)}
.btn.ghost{padding:10px 12px}
.btn.primary{
  border:1px solid rgba(31,164,255,.35);
  background: linear-gradient(35deg, rgba(31,164,255,.22), rgba(135,211,255,.12), rgba(255,195,77,.10));
}

.main{padding:12px}

.hero{position:relative; border-radius:22px; overflow:hidden; border:1px solid rgba(255,255,255,.10); background:rgba(255,255,255,.03)}
.hero-bg{
  position:absolute; inset:0;
  background:
    radial-gradient(900px 520px at 20% 20%, rgba(31,164,255,.20), transparent 65%),
    radial-gradient(700px 520px at 80% 35%, rgba(255,195,77,.16), transparent 65%),
    linear-gradient(180deg, rgba(255,255,255,.02), rgba(0,0,0,.10));
  filter:saturate(1.08);
}
.hero-card{position:relative; padding:14px}
.hero-title{font-size:18px; font-weight:900}
.hero-sub{margin-top:6px; color:var(--mut); font-size:13px}

.stats{display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin-top:12px}
.stat{border:1px solid rgba(255,255,255,.10); background:rgba(0,0,0,.16); border-radius:18px; padding:10px}
.stat .k{font-size:12px; color:var(--mut); font-weight:800}
.stat .v{margin-top:6px; font-size:14px; font-weight:900}
.stat .s{margin-top:2px; font-size:12px; color:var(--mut)}

.quick{display:flex; gap:10px; margin-top:12px; flex-wrap:wrap}

.grid{display:grid; grid-template-columns:1fr; gap:12px; margin-top:12px}
@media(min-width:920px){ .grid{grid-template-columns:repeat(3,1fr)} }

.card{border:1px solid rgba(255,255,255,.10); background:rgba(255,255,255,.03); border-radius:22px; overflow:hidden}
.card-h{padding:12px 12px 10px; font-weight:900; border-bottom:1px solid rgba(255,255,255,.07)}
.card-b{padding:12px; color:var(--ink)}
.mono{white-space:pre-wrap; font-family:ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; color:rgba(232,238,246,.92)}

.chips{display:flex; flex-wrap:wrap; gap:8px}
.chip{padding:8px 10px; border-radius:999px; border:1px solid rgba(255,255,255,.10); background:rgba(0,0,0,.14); font-weight:900; font-size:12px}
.hint{margin-top:10px; color:var(--mut); font-size:12px}

.links{display:flex; flex-direction:column; gap:8px}
.links a{padding:10px 12px; border-radius:16px; border:1px solid rgba(255,255,255,.10); background:rgba(0,0,0,.14)}

.overlay{
  position:fixed; inset:0; z-index:50;
  background:rgba(0,0,0,.55);
  backdrop-filter: blur(2px);
}
.hidden{display:none !important}

.drawer{
  position:fixed; top:0; right:0; z-index:60;
  width:min(420px, 92vw); height:100vh;
  border-left:1px solid rgba(255,255,255,.10);
  background:linear-gradient(180deg, rgba(10,16,26,.92), rgba(10,16,26,.78));
  backdrop-filter: blur(12px);
  display:flex; flex-direction:column;
}
.drawer-top{display:flex; align-items:center; justify-content:space-between; padding:12px; border-bottom:1px solid rgba(255,255,255,.08)}
.drawer-brand{display:flex; gap:10px; align-items:center}
.tabs{display:flex; gap:8px; padding:10px 12px; border-bottom:1px solid rgba(255,255,255,.07)}
.tab{
  flex:1; padding:10px 10px; border-radius:14px;
  border:1px solid rgba(255,255,255,.10);
  background:rgba(255,255,255,.04);
  color:var(--ink); font-weight:900;
}
.tab.active{border-color: rgba(31,164,255,.35); background: rgba(31,164,255,.10)}

.pane{display:flex; flex-direction:column; height:100%}
.chat{flex:1; overflow:auto; padding:12px; display:flex; flex-direction:column; gap:10px}
.b{padding:10px 12px; border:1px solid rgba(255,255,255,.10); border-radius:16px; max-width:92%}
.me{align-self:flex-end; background:rgba(31,164,255,.10)}
.bot{align-self:flex-start; background:rgba(0,0,0,.18)}
.bar{display:flex; gap:8px; padding:10px 12px; border-top:1px solid rgba(255,255,255,.08)}
#msg{flex:1; padding:12px; border-radius:14px; border:1px solid rgba(255,255,255,.10); background:rgba(0,0,0,.18); color:var(--ink)}

.exec{padding:12px; display:flex; flex-direction:column; gap:10px}
.exec-row{display:flex; flex-direction:column; gap:6px}
.lbl{font-size:12px; color:var(--mut); font-weight:900}
.in,.ta{
  padding:12px; border-radius:14px; border:1px solid rgba(255,255,255,.10);
  background:rgba(0,0,0,.18); color:var(--ink)
}
.ta{min-height:120px; resize:vertical}
.out{
  border:1px solid rgba(255,255,255,.10);
  background:rgba(0,0,0,.18);
  border-radius:18px;
  padding:12px;
  overflow:auto;
  max-height:36vh;
}

.menu{padding:12px; display:flex; flex-direction:column; gap:10px}
.menu-item{
  text-align:left; padding:12px 12px; border-radius:18px;
  border:1px solid rgba(255,255,255,.10);
  background:rgba(0,0,0,.16);
  color:var(--ink); font-weight:900;
}
.sep{height:1px; background:rgba(255,255,255,.08); margin:6px 0}
CSS

cat > "$UI/app.js" <<'JS'
(() => {
  const $ = (s, r=document) => r.querySelector(s);
  const $$ = (s, r=document) => Array.from(r.querySelectorAll(s));

  // API base: default -> 127.0.0.1:8790
  const qp = new URLSearchParams(location.search);
  const API_BASE = qp.get('api') || localStorage.getItem('CIT_API_BASE') || 'http://127.0.0.1:8790';
  localStorage.setItem('CIT_API_BASE', API_BASE);

  // Links
  $('#lnkUI').href = location.origin + '/';
  $('#lnkHealth').href = API_BASE + '/health';
  $('#lnkChat').href = API_BASE + '/api/chat';
  $('#lnkExec').href = API_BASE + '/api/exec';
  $('#lnkReg').href = API_BASE + '/registry';
  $('#lnkNP').href = API_BASE + '/node-packages';

  // Drawer
  const overlay = $('#overlay');
  const drawer = $('#drawer');
  const openDrawer = () => {
    overlay.classList.remove('hidden');
    drawer.classList.remove('hidden');
    drawer.setAttribute('aria-hidden', 'false');
  };
  const closeDrawer = () => {
    overlay.classList.add('hidden');
    drawer.classList.add('hidden');
    drawer.setAttribute('aria-hidden', 'true');
  };

  $('#ciBtn').onclick = openDrawer;
  $('#closeDrawer').onclick = closeDrawer;
  overlay.onclick = closeDrawer;

  // Tabs
  const tabs = $$('.tab');
  const panes = $$('.pane');
  tabs.forEach(t => t.onclick = () => {
    tabs.forEach(x => x.classList.remove('active'));
    t.classList.add('active');
    const name = t.dataset.tab;
    panes.forEach(p => p.classList.toggle('hidden', p.dataset.pane !== name));
  });

  // Chat
  const chat = $('#chat');
  const input = $('#msg');
  const sendBtn = $('#send');
  const addMsg = (text, cls) => {
    const d = document.createElement('div');
    d.className = `b ${cls}`;
    d.textContent = text;
    chat.appendChild(d);
    chat.scrollTop = chat.scrollHeight;
  };

  async function chatSend(text){
    const r = await fetch(API_BASE + '/api/chat', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({message:text})
    });
    const raw = await r.text();
    let j=null; try{ j=JSON.parse(raw); }catch(_){}
    if(!r.ok) throw new Error(`HTTP ${r.status}: ${raw.slice(0,160)}`);
    return j?.reply ?? j?.text ?? j?.message ?? raw;
  }

  async function send(){
    const text = input.value.trim();
    if(!text) return;
    input.value='';
    addMsg(text,'me');
    try{
      const reply = await chatSend(text);
      addMsg(reply || '[empty]','bot');
    }catch(e){
      addMsg(String(e).slice(0,180),'bot');
    }
  }

  sendBtn.onclick = send;
  input.addEventListener('keydown', (e)=>{ if(e.key==='Enter') send(); });

  // Exec
  const execAction = $('#execAction');
  const execPayload = $('#execPayload');
  const execOut = $('#execOut');

  function pretty(x){
    try{ return JSON.stringify(x, null, 2); }catch(_){ return String(x); }
  }

  async function execCall(action, payloadObj){
    const r = await fetch(API_BASE + '/api/exec', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ action, payload: payloadObj || {} })
    });
    const raw = await r.text();
    let j=null; try{ j=JSON.parse(raw); }catch(_){}
    if(!r.ok) throw new Error(`HTTP ${r.status}: ${raw.slice(0,200)}`);
    return j || raw;
  }

  $('#execRun').onclick = async () => {
    try{
      const action = execAction.value.trim();
      let payloadObj = {};
      const t = execPayload.value.trim();
      if(t) payloadObj = JSON.parse(t);
      const out = await execCall(action, payloadObj);
      execOut.textContent = pretty(out);
    }catch(e){
      execOut.textContent = String(e);
    }
  };

  $('#execReg').onclick = async () => {
    execAction.value = 'actions.registry.get';
    execPayload.value = '{}';
    $('#execRun').click();
  };

  $('#execNP').onclick = async () => {
    execAction.value = 'actions.node_packages.get';
    execPayload.value = '{}';
    $('#execRun').click();
  };

  // Dashboard quick actions
  $$('.btn[data-act]').forEach(b => b.onclick = async () => {
    const v = b.dataset.act;
    try{
      if(v === 'chat:ping'){
        openDrawer();
        tabs.find(t=>t.dataset.tab==='chat')?.click();
        addMsg('ping','me');
        const reply = await chatSend('ping');
        addMsg(reply,'bot');
        return;
      }
      if(v === 'exec:registry'){
        openDrawer();
        tabs.find(t=>t.dataset.tab==='exec')?.click();
        $('#execReg').click();
        return;
      }
      if(v === 'exec:nodepkgs'){
        openDrawer();
        tabs.find(t=>t.dataset.tab==='exec')?.click();
        $('#execNP').click();
        return;
      }
    }catch(e){
      openDrawer();
      tabs.find(t=>t.dataset.tab==='chat')?.click();
      addMsg(String(e).slice(0,180),'bot');
    }
  });

  // Health tick
  async function health(){
    try{
      const r = await fetch(API_BASE + '/health', {method:'GET'});
      const j = await r.json();
      $('#apiState').textContent = j.ok ? 'OK' : 'DOWN';
      $('#apiModel').textContent = j.model || '—';
    }catch(_){
      $('#apiState').textContent = 'DOWN';
      $('#apiModel').textContent = '—';
    }
  }
  health();
  $('#refreshBtn').onclick = health;

  // Theme button (simple toggle)
  $('#themeBtn').onclick = () => {
    document.body.classList.toggle('alt');
  };

  // Menu clicks (stub)
  $$('.menu-item').forEach(mi => mi.onclick = () => {
    const key = mi.dataset.open || '';
    addMsg(`UI: ${mi.textContent.trim()} (${key})`, 'bot');
    tabs.find(t=>t.dataset.tab==='chat')?.click();
  });
})();
JS

echo "=== [3] START UI :8010 ==="
cd "$UI" || exit 1
nohup python -m http.server 8010 --bind 127.0.0.1 > "$LOG/ui_8010.log" 2>&1 &
sleep 0.4

echo "=== [4] VERIFY (single pass) ==="
echo -n "UI: "; curl -sS --max-time 2 -I http://127.0.0.1:8010/ | head -n 1 || echo "DOWN"
echo -n "ASSET(ci.png): "; curl -sS --max-time 2 -I http://127.0.0.1:8010/assets/ci.png | head -n 1 || echo "DOWN"
echo

echo "=== READY ==="
echo "UI  : http://127.0.0.1:8010/"
echo "API : http://127.0.0.1:8790/health"
echo "TIP : відкриття UI з іншим API -> http://127.0.0.1:8010/?api=http://127.0.0.1:8790"
