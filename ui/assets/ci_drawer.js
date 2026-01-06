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
