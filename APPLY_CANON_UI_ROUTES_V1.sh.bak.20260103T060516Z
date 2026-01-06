#!/data/data/com.termux/files/usr/bin/bash
set -e

ROOT="/data/data/com.termux/files/home/cimeika/cit"
UI="$ROOT/ui"
LOG="$ROOT/logs"
API="http://127.0.0.1:8790"
UI_BASE="http://127.0.0.1:8010"

cd "$ROOT" || exit 1
mkdir -p "$LOG" "$UI/pages" "$UI/assets"

echo "=== [1/6] Write Ci Canon UI assets (drawer + styles) ==="

# --- CSS ---
cat > "$UI/assets/ci.css" <<'CSS'
:root{
  --bg:#0b0f14; --panel:#0f1620; --panel2:#101b28;
  --stroke:#1f2a36; --text:#e8eef6; --muted:#9fb0c4;
  --blue:#1FA4FF; --gold:#FFC34D;
  --shadow: 0 20px 60px rgba(0,0,0,.35);
  --r:18px;
}
*{box-sizing:border-box;font-family:system-ui,-apple-system,"Segoe UI",Roboto,Arial}
html,body{height:100%}
body{margin:0;background:radial-gradient(1200px 800px at 25% 20%, rgba(31,164,255,.16), transparent 55%),
                 radial-gradient(1200px 800px at 70% 70%, rgba(255,195,77,.12), transparent 55%),
                 var(--bg);
     color:var(--text)}
a{color:inherit;text-decoration:none}
.wrap{max-width:1200px;margin:0 auto;padding:18px}
.topbar{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:14px 18px;border-bottom:1px solid var(--stroke);position:sticky;top:0;background:rgba(11,15,20,.75);backdrop-filter: blur(10px);z-index:5}
.brand{display:flex;align-items:center;gap:10px}
.brand .title{font-weight:900;letter-spacing:.4px}
.pills{display:flex;gap:8px;flex-wrap:wrap}
.pill{border:1px solid var(--stroke);background:rgba(15,22,32,.72);padding:8px 10px;border-radius:999px;color:var(--muted);font-size:12px}
.btn{border:1px solid rgba(42,58,74,1);background:rgba(22,49,75,.85);color:var(--text);font-weight:800;border-radius:12px;padding:10px 12px;cursor:pointer}
.btn:active{transform:translateY(1px)}
.btn.ghost{background:rgba(15,22,32,.72);border-color:var(--stroke);font-weight:700;color:var(--text)}
.grid{display:grid;grid-template-columns:repeat(12,1fr);gap:14px;margin-top:16px}
.card{grid-column:span 4;border:1px solid var(--stroke);border-radius:var(--r);background:linear-gradient(180deg, rgba(15,22,32,.92), rgba(15,22,32,.75));box-shadow:var(--shadow);padding:14px}
.card h3{margin:0 0 6px 0;font-size:18px}
.card .sub{color:var(--muted);font-size:13px;margin-bottom:10px}
.tags{display:flex;gap:6px;flex-wrap:wrap}
.tag{border:1px solid var(--stroke);background:rgba(16,27,40,.9);padding:6px 10px;border-radius:999px;font-size:12px;color:var(--muted)}
@media (max-width: 980px){ .card{grid-column:span 6} }
@media (max-width: 640px){ .card{grid-column:span 12} .wrap{padding:12px} }

.section{margin-top:16px;border:1px solid var(--stroke);border-radius:var(--r);background:rgba(15,22,32,.75);box-shadow:var(--shadow)}
.section .head{padding:14px 14px 10px;border-bottom:1px solid var(--stroke);display:flex;align-items:center;justify-content:space-between;gap:10px}
.section .head h2{margin:0;font-size:16px}
.section .body{padding:14px}
.mono{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12px;color:#d6e1ef;white-space:pre-wrap;background:rgba(11,15,20,.6);border:1px solid var(--stroke);border-radius:14px;padding:12px;overflow:auto}
input,select,textarea{
  width:100%; padding:12px; border-radius:12px;
  border:1px solid var(--stroke);
  background:rgba(15,22,32,.9); color:var(--text);
}
textarea{min-height:140px;resize:vertical}

.fab{
  position:fixed; right:18px; bottom:18px; z-index:50;
  width:62px; height:62px; border-radius:999px;
  border:1px solid rgba(42,58,74,1);
  background:radial-gradient(circle at 35% 30%, rgba(31,164,255,.95), rgba(31,164,255,.25) 35%, rgba(255,195,77,.20) 65%, rgba(255,195,77,.85));
  box-shadow:0 18px 60px rgba(0,0,0,.55);
  display:flex; align-items:center; justify-content:center;
  cursor:pointer;
}
.fab img{width:34px;height:34px;display:block;filter:drop-shadow(0 8px 14px rgba(0,0,0,.45))}
.drawerOverlay{
  position:fixed; inset:0; background:rgba(0,0,0,.45);
  z-index:60; display:none;
}
.drawer{
  position:fixed; right:14px; bottom:92px;
  width:min(520px, calc(100vw - 28px));
  max-height:min(78vh, 680px);
  border:1px solid var(--stroke); border-radius:22px;
  background:linear-gradient(180deg, rgba(15,22,32,.98), rgba(11,15,20,.92));
  box-shadow:0 22px 80px rgba(0,0,0,.6);
  z-index:61; display:none; overflow:hidden;
}
.drawer .dTop{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:12px 12px;border-bottom:1px solid var(--stroke)}
.drawer .dTop .left{display:flex;align-items:center;gap:10px}
.drawer .dTop .left .name{font-weight:900}
.drawer .tabs{display:flex;gap:8px}
.drawer .tab{padding:8px 10px;border-radius:999px;border:1px solid var(--stroke);background:rgba(16,27,40,.75);color:var(--muted);cursor:pointer;font-weight:800;font-size:12px}
.drawer .tab.active{background:rgba(22,49,75,.85);color:var(--text);border-color:rgba(42,58,74,1)}
.drawer .dBody{padding:12px;display:grid;gap:12px}
.chatBox{border:1px solid var(--stroke);border-radius:16px;overflow:hidden}
.chatLog{height:210px;overflow:auto;padding:10px;display:flex;flex-direction:column;gap:10px;background:rgba(11,15,20,.35)}
.b{padding:10px 12px;border:1px solid var(--stroke);border-radius:14px;max-width:92%}
.me{align-self:flex-end;background:rgba(18,32,47,.9)}
.bot{align-self:flex-start;background:rgba(15,22,32,.9)}
.chatBar{display:flex;gap:8px;padding:10px;border-top:1px solid var(--stroke);background:rgba(15,22,32,.85)}
.chatBar input{flex:1}
.smallBtns{display:flex;gap:8px;flex-wrap:wrap}
CSS

# --- Drawer JS ---
cat > "$UI/assets/ci_drawer.js" <<'JS'
(() => {
  const API = window.CIT_API || 'http://127.0.0.1:8790';

  function el(tag, attrs={}, ...kids){
    const e = document.createElement(tag);
    Object.entries(attrs).forEach(([k,v]) => {
      if (k === 'class') e.className = v;
      else if (k === 'html') e.innerHTML = v;
      else e.setAttribute(k, v);
    });
    kids.forEach(k => { if (k) e.appendChild(k); });
    return e;
  }

  function safeJSON(str){
    try { return JSON.parse(str); } catch { return null; }
  }

  async function httpJSON(url, opt={}){
    const r = await fetch(url, opt);
    const t = await r.text();
    const j = safeJSON(t);
    return { ok: r.ok, status: r.status, text: t, json: j };
  }

  function mountDrawer(){
    const overlay = el('div', { class:'drawerOverlay', id:'ciOverlay' });
    const drawer  = el('div', { class:'drawer', id:'ciDrawer' });

    const close = () => {
      overlay.style.display = 'none';
      drawer.style.display  = 'none';
    };
    overlay.onclick = close;

    const tabChat = el('div', { class:'tab active', id:'ciTabChat' }, document.createTextNode('Чат'));
    const tabExec = el('div', { class:'tab', id:'ciTabExec' }, document.createTextNode('Exec'));

    const top = el('div', { class:'dTop' },
      el('div', { class:'left' },
        el('div', { class:'name' }, document.createTextNode('Ci')),
        el('div', { class:'pill', id:'ciHealthPill' }, document.createTextNode('health: ...'))
      ),
      el('div', { class:'tabs' }, tabChat, tabExec),
      el('button', { class:'btn ghost', id:'ciClose' }, document.createTextNode('Закрити'))
    );

    const body = el('div', { class:'dBody', id:'ciBody' });

    // CHAT VIEW
    const chatLog = el('div', { class:'chatLog', id:'ciChatLog' });
    const chatInput = el('input', { id:'ciChatInput', placeholder:'Напиши...' });
    const chatSend  = el('button', { class:'btn', id:'ciChatSend' }, document.createTextNode('➤'));
    const chatPing  = el('button', { class:'btn ghost', id:'ciChatPing' }, document.createTextNode('Пінг'));
    const chatClear = el('button', { class:'btn ghost', id:'ciChatClear' }, document.createTextNode('Очистити'));

    const chatBox = el('div', { class:'chatBox', id:'ciChatBox' },
      chatLog,
      el('div', { class:'chatBar' }, chatInput, chatSend),
      el('div', { style:'padding:10px;border-top:1px solid var(--stroke);display:flex;gap:8px;flex-wrap:wrap;background:rgba(15,22,32,.85)' },
        chatPing, chatClear
      )
    );

    function addMsg(text, cls){
      const d = el('div', { class:`b ${cls}` });
      d.textContent = text;
      chatLog.appendChild(d);
      chatLog.scrollTop = chatLog.scrollHeight;
    }

    async function sendChat(text){
      const msg = (text || '').trim();
      if (!msg) return;
      addMsg(msg, 'me');
      const res = await httpJSON(`${API}/api/chat`, {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ message: msg })
      });
      if (!res.ok){
        addMsg(`HTTP ${res.status}: ${res.json?.error || res.text.slice(0,160)}`, 'bot');
        return;
      }
      const reply = res.json?.reply ?? res.json?.text ?? res.text;
      addMsg(String(reply || '[empty]').slice(0, 4000), 'bot');
    }

    chatSend.onclick = () => { const v = chatInput.value; chatInput.value=''; sendChat(v); };
    chatInput.addEventListener('keydown', (e) => { if (e.key==='Enter') chatSend.onclick(); });
    chatPing.onclick  = () => sendChat('ping');
    chatClear.onclick = () => { chatLog.innerHTML=''; addMsg('Ci online. Пиши.', 'bot'); };

    // EXEC VIEW
    const execAction = el('select', { id:'ciExecAction' });
    const execTpl    = el('select', { id:'ciExecTpl' });
    const execIn     = el('textarea', { id:'ciExecInput' });
    const execOut    = el('div', { class:'mono', id:'ciExecOut' });

    const btnRun     = el('button', { class:'btn', id:'ciExecRun' }, document.createTextNode('Виконати'));
    const btnHealth  = el('button', { class:'btn ghost', id:'ciExecHealth' }, document.createTextNode('Перевірити health'));
    const btnReg     = el('button', { class:'btn ghost', id:'ciExecReg' }, document.createTextNode('GET /registry'));
    const btnNP      = el('button', { class:'btn ghost', id:'ciExecNP' }, document.createTextNode('GET /node-packages'));
    const btnCopy    = el('button', { class:'btn ghost', id:'ciExecCopy' }, document.createTextNode('Копіювати вихід'));
    const btnClrOut  = el('button', { class:'btn ghost', id:'ciExecClear' }, document.createTextNode('Очистити'));

    const execBox = el('div', { class:'section', style:'margin:0' },
      el('div', { class:'head' },
        el('h2', {}, document.createTextNode('Exec (POST /api/exec)')),
        el('div', { class:'smallBtns' }, btnRun, btnReg, btnNP, btnHealth, btnCopy, btnClrOut)
      ),
      el('div', { class:'body' },
        el('div', { style:'display:grid;grid-template-columns:1fr 1fr;gap:10px' },
          el('div', {}, el('div', { class:'sub', style:'color:var(--muted);margin-bottom:6px' }, document.createTextNode('Дія')), execAction),
          el('div', {}, el('div', { class:'sub', style:'color:var(--muted);margin-bottom:6px' }, document.createTextNode('Шаблон')), execTpl)
        ),
        el('div', { class:'sub', style:'color:var(--muted);margin:12px 0 6px' }, document.createTextNode('Корисне навантаження (JSON)')),
        execIn,
        el('div', { class:'sub', style:'color:var(--muted);margin:12px 0 6px' }, document.createTextNode('Вихід')),
        execOut
      )
    );

    function pretty(objOrText){
      if (typeof objOrText === 'string'){
        const j = safeJSON(objOrText);
        if (j) return JSON.stringify(j, null, 2);
        return objOrText;
      }
      return JSON.stringify(objOrText, null, 2);
    }

    async function refreshHealth(){
      const res = await httpJSON(`${API}/health`);
      const pill = document.getElementById('ciHealthPill');
      if (!pill) return;
      if (!res.ok) { pill.textContent = `health: DOWN`; return; }
      const m = res.json?.model || 'ok';
      const ts = res.json?.ts || '';
      pill.textContent = `health: ${m} ${ts}`;
    }

    async function loadRegistryAndActions(){
      // default actions (canon)
      const actions = [
        { label:'дії.реєстр.get', action:'actions.registry.get', input:{} },
        { label:'node-packages.get', action:'actions.node_packages.get', input:{} },
        { label:'стан.get', action:'actions.state.get', input:{ node_id:'ci', key:'*' } },
        { label:'стан.set', action:'actions.state.set', input:{ node_id:'ci', key:'demo', value:'1' } },
        { label:'подія.emit', action:'actions.event.emit', input:{ node_id:'podija', event:'demo', payload:{ v:1 } } }
      ];

      execAction.innerHTML = '';
      actions.forEach((a,i) => {
        const o = document.createElement('option');
        o.value = a.action;
        o.textContent = a.label;
        if (i===0) o.selected = true;
        execAction.appendChild(o);
      });

      const tpls = [
        { name:'вхід: {}', input:{} },
        { name:'вхід: state.get (ci)', input:{ node_id:'ci', key:'*' } },
        { name:'вхід: event.emit', input:{ node_id:'podija', event:'demo', payload:{ v:1 } } }
      ];
      execTpl.innerHTML = '';
      tpls.forEach((t,i)=>{
        const o=document.createElement('option');
        o.value = JSON.stringify(t.input);
        o.textContent = t.name;
        if(i===0) o.selected=true;
        execTpl.appendChild(o);
      });

      execIn.value = JSON.stringify({ action: actions[0].action, input: actions[0].input }, null, 2);
      execTpl.onchange = () => {
        const base = safeJSON(execTpl.value) || {};
        execIn.value = JSON.stringify({ action: execAction.value, input: base }, null, 2);
      };
      execAction.onchange = () => {
        const base = safeJSON(execTpl.value) || {};
        execIn.value = JSON.stringify({ action: execAction.value, input: base }, null, 2);
      };

      await refreshHealth();
    }

    async function runExec(payload){
      const res = await httpJSON(`${API}/api/exec`, {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify(payload)
      });
      execOut.textContent = res.ok ? pretty(res.json || res.text) : `HTTP ${res.status}\n` + pretty(res.json || res.text);
    }

    btnRun.onclick = () => {
      const j = safeJSON(execIn.value);
      if (!j) { execOut.textContent = 'ERROR: invalid JSON'; return; }
      runExec(j);
    };
    btnReg.onclick = async () => {
      const r = await httpJSON(`${API}/registry`);
      execOut.textContent = r.ok ? pretty(r.json || r.text) : `HTTP ${r.status}\n` + pretty(r.json || r.text);
    };
    btnNP.onclick = async () => {
      const r = await httpJSON(`${API}/node-packages`);
      execOut.textContent = r.ok ? pretty(r.json || r.text) : `HTTP ${r.status}\n` + pretty(r.json || r.text);
    };
    btnHealth.onclick = async () => {
      const r = await httpJSON(`${API}/health`);
      execOut.textContent = r.ok ? pretty(r.json || r.text) : `HTTP ${r.status}\n` + pretty(r.json || r.text);
      refreshHealth();
    };
    btnCopy.onclick = async () => {
      try { await navigator.clipboard.writeText(execOut.textContent || ''); } catch {}
    };
    btnClrOut.onclick = () => { execOut.textContent = ''; };

    const closeBtn = top.querySelector('#ciClose');
    closeBtn.onclick = close;

    // switch views
    const setTab = (which) => {
      tabChat.classList.toggle('active', which==='chat');
      tabExec.classList.toggle('active', which==='exec');
      body.innerHTML = '';
      if (which==='chat') body.appendChild(chatBox);
      else body.appendChild(execBox);
    };
    tabChat.onclick = () => setTab('chat');
    tabExec.onclick = () => setTab('exec');

    // defaults
    addMsg('Ci online. Пиши.', 'bot');
    setTab('chat');
    loadRegistryAndActions();

    drawer.appendChild(top);
    drawer.appendChild(body);

    document.body.appendChild(overlay);
    document.body.appendChild(drawer);

    const fab = document.getElementById('ciFab');
    fab.onclick = async () => {
      overlay.style.display = 'block';
      drawer.style.display = 'block';
      await refreshHealth();
    };
  }

  window.CI_MOUNT_DRAWER = mountDrawer;
})();
JS

# --- Common JS: registry-driven nav/cards ---
cat > "$UI/assets/app.js" <<'JS'
(() => {
  window.CIT_API = 'http://127.0.0.1:8790';

  const $ = (id) => document.getElementById(id);

  async function httpJSON(url, opt={}){
    const r = await fetch(url, opt);
    const t = await r.text();
    let j=null; try{ j=JSON.parse(t);}catch{}
    return { ok:r.ok, status:r.status, text:t, json:j };
  }

  function nodeCard(n){
    const a = document.createElement('a');
    a.className = 'card';
    a.href = n._page || '#';

    const h3 = document.createElement('h3');
    h3.textContent = n.title || n.id;

    const sub = document.createElement('div');
    sub.className = 'sub';
    sub.textContent = (n._sub || '').trim();

    const tags = document.createElement('div');
    tags.className = 'tags';
    (n._tags || []).forEach(t => {
      const s = document.createElement('span');
      s.className = 'tag';
      s.textContent = t;
      tags.appendChild(s);
    });

    a.appendChild(h3);
    if (sub.textContent) a.appendChild(sub);
    a.appendChild(tags);

    return a;
  }

  async function render(){
    const api = window.CIT_API;
    const health = await httpJSON(`${api}/health`);
    $('healthPill').textContent = health.ok
      ? `здоров'я: ${health.json?.model || 'ok'} ${health.json?.ts || ''}`
      : `здоров'я: DOWN`;

    const reg = await httpJSON(`${api}/registry`);
    if (!reg.ok || !reg.json){
      $('nodesGrid').innerHTML = '';
      const d = document.createElement('div');
      d.className='mono';
      d.textContent = `Registry load failed (HTTP ${reg.status})\n` + (reg.text || '').slice(0, 600);
      $('nodesGrid').appendChild(d);
      return;
    }

    const nodes = reg.json.nodes || [];
    const cards = [];

    const canonMap = {
      "ci":        { page:"/pages/ci.html",        sub:"Центр / оператор", tags:["центр","контакт"] },
      "kazkar":    { page:"/pages/kazkar.html",    sub:"Пам'ять / легенда", tags:["земля","було"] },
      "podija":    { page:"/pages/podija.html",    sub:"Події / ініціації", tags:["вогонь","буде"] },
      "nastrij":   { page:"/pages/nastrij.html",   sub:"Стан / емоції",     tags:["вода","зараз"] },
      "malya":     { page:"/pages/malya.html",     sub:"Ідеї / інновації",  tags:["повітря","є"] },
      "calendar":  { page:"/pages/calendar.html",  sub:"Ритми / вузли",     tags:["час","цикли"] },
      "gallery":   { page:"/pages/gallery.html",   sub:"Архів / образи",    tags:["медіа","історії"] },
    };

    nodes.forEach(n => {
      const m = canonMap[n.id] || { page:"#", sub:"", tags:[] };
      cards.push({
        id: n.id,
        title: n.title || n.id,
        _page: m.page,
        _sub: m.sub,
        _tags: m.tags
      });

      // legend_ci subnode (if exists)
      if (n.id === 'kazkar' && Array.isArray(n.subnodes)){
        const hasLegend = n.subnodes.find(s => s.id === 'legend_ci' || s.node_id === 'legend_ci');
        if (hasLegend){
          cards.push({
            id: 'legend_ci',
            title: '✨Легенда Ci',
            _page: '/pages/legend_ci.html',
            _sub: 'Ядро бібліотеки',
            _tags: ['земля','було','ядро']
          });
        }
      }
    });

    $('nodesGrid').innerHTML = '';
    cards.forEach(c => $('nodesGrid').appendChild(nodeCard(c)));
  }

  window.CI_RENDER_DASHBOARD = render;
})();
JS

echo "=== [2/6] Write UI pages (Ci Drawer on every page) ==="

# Common page template generator (bash)
mkpage() {
  local file="$1" title="$2" subtitle="$3" hint="$4"
  cat > "$UI/pages/$file" <<HTML
<!doctype html>
<html lang="uk">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>${title} — Cimeika</title>
  <link rel="stylesheet" href="../assets/ci.css"/>
</head>
<body>
  <div class="topbar">
    <div class="brand">
      <div class="title">${title}</div>
      <div class="pills">
        <span class="pill">${subtitle}</span>
        <span class="pill">API: <span id="apiLbl">127.0.0.1:8790</span></span>
        <span class="pill" id="healthPill">здоров'я: ...</span>
      </div>
    </div>
    <div style="display:flex;gap:8px;align-items:center">
      <a class="btn ghost" href="/">Дашборд</a>
      <button class="btn" id="btnRefresh">Оновити</button>
    </div>
  </div>

  <div class="wrap">
    <div class="section">
      <div class="head"><h2>${title}'</h2></div>
      <div class="body">
        <div class="mono" id="pageInfo">${hint}</div>
      </div>
    </div>
  </div>

  <!-- Ci FAB + Drawer -->
  <div class="fab" id="ciFab" title="Ci">
    <img src="../icons/icon-192.png" alt="Ci" onerror="this.style.display='none'; this.parentElement.textContent='Ci'; this.parentElement.style.fontWeight='900';"/>
  </div>

  <script>window.CIT_API='http://127.0.0.1:8790';</script>
  <script src="../assets/ci_drawer.js"></script>
  <script>
    const api = window.CIT_API;
    document.getElementById('apiLbl').textContent = api.replace('http://','');
    async function health(){
      try{
        const r = await fetch(api + '/health');
        const j = await r.json();
        document.getElementById('healthPill').textContent = "здоров'я: " + (j.model||'ok') + " " + (j.ts||'');
      }catch{
        document.getElementById('healthPill').textContent = "здоров'я: DOWN";
      }
    }
    document.getElementById('btnRefresh').onclick = health;
    window.CI_MOUNT_DRAWER();
    health();
  </script>
</body>
</html>
HTML
}

mkpage "ci.html"        "Ci"        "центр / оператор"   "Ci — глобальний контакт. Відкрий Ci-лого (праворуч-внизу) → Чат / Exec."
mkpage "kazkar.html"    "Казкар"    "пам'ять / легенда"  "Казкар — пам'ять, наратив, архів сенсів (було)."
mkpage "legend_ci.html" "✨Легенда Ci" "ядро бібліотеки"  "✨Легенда Ci — джерело сенсу в просторі Казкаря (було → сенс)."
mkpage "podija.html"    "ПоДія"     "події / ініціації"  "ПоДія — події, запуск, ініціації (буде)."
mkpage "nastrij.html"   "Настрій"   "стан / емоції"      "Настрій — емоційний стан (зараз)."
mkpage "malya.html"     "Маля"      "ідеї / інновації"   "Маля — ідеї, альтернативи (є)."
mkpage "calendar.html"  "Календар"  "ритми / вузли"      "Календар — вузли часу, ритми, цикли."
mkpage "gallery.html"   "Галерея"   "архів / образи"     "Галерея — медіа, історії, слайди."

echo "=== [3/6] Write Dashboard index (canon) ==="

cat > "$UI/index.html" <<'HTML'
<!doctype html>
<html lang="uk">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>CIT — Dashboard</title>
  <link rel="stylesheet" href="assets/ci.css"/>
</head>
<body>
  <div class="topbar">
    <div class="brand">
      <div class="title">CIT</div>
      <div class="pills">
        <span class="pill">UIv2.2 — Canon</span>
        <span class="pill">Інтерфейс: <span id="uiLbl">http://127.0.0.1:8010/</span></span>
        <span class="pill">API: <span id="apiLbl">http://127.0.0.1:8790</span></span>
        <span class="pill" id="healthPill">здоров'я: ...</span>
      </div>
    </div>
    <div style="display:flex;gap:8px;align-items:center">
      <button class="btn" id="btnRefresh">Оновити</button>
    </div>
  </div>

  <div class="wrap">
    <div class="section">
      <div class="head"><h2>Вузли Cimeika</h2></div>
      <div class="body">
        <div class="grid" id="nodesGrid"></div>
      </div>
    </div>

    <div class="section">
      <div class="head">
        <h2>Швидкі дії (через Ci Drawer → Exec)</h2>
        <a class="btn ghost" href="pages/ci.html">Відкрити Ci'</a>
      </div>
      <div class="body">
        <div class="mono">
Канон:
- На кожній сторінці є Ci-лого (праворуч-внизу) → Drawer: Чат / Exec
- /registry є джерелом істини для вузлів
- /api/exec виконує канонічні actions.*
        </div>
      </div>
    </div>
  </div>

  <!-- Ci FAB + Drawer -->
  <div class="fab" id="ciFab" title="Ci">
    <img src="icons/icon-192.png" alt="Ci" onerror="this.style.display='none'; this.parentElement.textContent='Ci'; this.parentElement.style.fontWeight='900';"/>
  </div>

  <script>window.CIT_API='http://127.0.0.1:8790';</script>
  <script src="assets/app.js"></script>
  <script src="assets/ci_drawer.js"></script>
  <script>
    document.getElementById('uiLbl').textContent = location.origin + '/';
    document.getElementById('apiLbl').textContent = window.CIT_API;
    document.getElementById('btnRefresh').onclick = () => window.CI_RENDER_DASHBOARD();
    window.CI_MOUNT_DRAWER();
    window.CI_RENDER_DASHBOARD();
  </script>
</body>
</html>
HTML

echo "=== [4/6] Patch registry JSON files (best-effort, no crash) ==="
python - <<'PY'
import os, json, pathlib

ROOT = pathlib.Path("/data/data/com.termux/files/home/cimeika/cit")

canon = {
  "ci": {"page":"/pages/ci.html","tags":{
    "_бренд":"Cimeika","_продукт":"Ci","_характер":"оператор/контакт",
    "_напрямок_полюс":{"element":"ефір","time":"є","sign":"+"},
    "_досвід":"active","_контроль":["👉 state +/-","👉 ci_marker_checkin"],"_памʼять":{"store":"data/state.json"}
  }},
  "kazkar": {"page":"/pages/kazkar.html","tags":{
    "_бренд":"Cimeika","_продукт":"Kazkar","_характер":"памʼять/оповідь",
    "_напрямок_полюс":{"element":"земля","time":"було","sign":"-"},
    "_досвід":"passive","_контроль":["👉 state +/-"],"_памʼять":{"store":"data/kazkar.json"}
  }},
  "podija": {"page":"/pages/podija.html","tags":{
    "_бренд":"Cimeika","_продукт":"PoDija","_характер":"події/ініціації",
    "_напрямок_полюс":{"element":"вогонь","time":"буде","sign":"+"},
    "_досвід":"active","_контроль":["👉 event.emit"],"_памʼять":{"store":"data/podija.json"}
  }},
  "nastrij": {"page":"/pages/nastrij.html","tags":{
    "_бренд":"Cimeika","_продукт":"Nastrij","_характер":"емоції/стан",
    "_напрямок_полюс":{"element":"вода","time":"зараз","sign":"-"},
    "_досвід":"active","_контроль":["👉 state +/-"],"_памʼять":{"store":"data/nastrij.json"}
  }},
  "malya": {"page":"/pages/malya.html","tags":{
    "_бренд":"Cimeika","_продукт":"Malya","_характер":"ідеї/альтернативи",
    "_напрямок_полюс":{"element":"повітря","time":"є","sign":"+"},
    "_досвід":"active","_контроль":["👉 event.emit"],"_памʼять":{"store":"data/malya.json"}
  }},
  "calendar": {"page":"/pages/calendar.html","tags":{
    "_бренд":"Cimeika","_продукт":"Calendar","_характер":"вузли/ритми",
    "_напрямок_полюс":{"element":"час","time":"перетин","sign":"+"},
    "_досвід":"active","_контроль":["👉 schedule +/-"],"_памʼять":{"store":"data/calendar.json"}
  }},
  "gallery": {"page":"/pages/gallery.html","tags":{
    "_бренд":"Cimeika","_продукт":"Gallery","_характер":"медіа/історії",
    "_напрямок_полюс":{"element":"архів","time":"перетин","sign":"-"},
    "_досвід":"passive","_контроль":["👉 asset.put/get"],"_памʼять":{"store":"data/gallery.json"}
  }},
  "legend_ci": {"page":"/pages/legend_ci.html","tags":{
    "_бренд":"Cimeika","_продукт":"LegendCi","_характер":"ядро/сенс",
    "_напрямок_полюс":{"element":"земля","time":"було","sign":"+"},
    "_досвід":"passive","_контроль":["👉 state +/-"],"_памʼять":{"store":"data/legend_ci.json"}
  }},
}

def try_patch_file(p: pathlib.Path):
  try:
    txt = p.read_text(encoding="utf-8", errors="ignore")
    if "CiRegistry" not in txt:
      return False
    data = json.loads(txt)
    nodes = data.get("nodes", [])
    for n in nodes:
      nid = n.get("id") or n.get("node_id")
      if not nid: 
        continue
      if nid in canon:
        n["page"] = canon[nid]["page"]
        n["tags"] = canon[nid]["tags"]
      # patch subnodes
      subs = n.get("subnodes") or []
      for s in subs:
        sid = s.get("id") or s.get("node_id")
        if sid and sid in canon:
          s["page"] = canon[sid]["page"]
          s["tags"] = canon[sid]["tags"]

    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return True
  except Exception:
    return False

patched = []
for p in ROOT.rglob("*.json"):
  if try_patch_file(p):
    patched.append(str(p))

# also try .webmanifest if it is JSON-like but ignore errors
print("PATCHED_FILES:", len(patched))
for x in patched[:20]:
  print(" -", x)
PY

echo "=== [5/6] Ensure UI static server is running (:8010) ==="
# stop old server best-effort
pkill -f "python -m http.server 8010" 2>/dev/null || true

cd "$UI" || exit 1
nohup python -m http.server 8010 --bind 127.0.0.1 > "$LOG/ui_8010.log" 2>&1 &
sleep 0.4

echo "=== [6/6] VERIFY (one pass) ==="
cd "$ROOT" || exit 1

echo "--- UI HEAD ---"
curl -sS --max-time 2 -I "$UI_BASE/" | head -n 1 || echo "UI DOWN"

echo "--- API health ---"
curl -sS --max-time 2 "$API/health" || echo "API DOWN"; echo

echo "--- API registry (GET) ---"
curl -sS --max-time 2 "$API/registry" | head -c 220; echo; echo

echo "--- Pages HEAD ---"
for f in ci kazkar legend_ci podija nastrij malya calendar gallery; do
  echo -n "$f: "
  curl -sS --max-time 2 -I "$UI_BASE/pages/$f.html" | head -n 1 || echo "DOWN"
done

echo
echo "=== READY LINKS ==="
echo "UI Dashboard : $UI_BASE/"
echo "Ci'         : $UI_BASE/pages/ci.html"
echo "Kazkar'     : $UI_BASE/pages/kazkar.html"
echo "Legend Ci'  : $UI_BASE/pages/legend_ci.html"
echo "PoDija'     : $UI_BASE/pages/podija.html"
echo "Nastrij'    : $UI_BASE/pages/nastrij.html"
echo "Malya'      : $UI_BASE/pages/malya.html"
echo "Calendar'   : $UI_BASE/pages/calendar.html"
echo "Gallery'    : $UI_BASE/pages/gallery.html"
echo "API health  : $API/health"
echo "API exec    : $API/api/exec"
echo "Registry    : $API/registry"
