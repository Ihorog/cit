(() => {
  const API_BASE = 'http://127.0.0.1:8790';
  const CHAT_URL = `${API_BASE}/api/chat`;
  const EXEC_URL = `${API_BASE}/api/exec`;
  const REG_URL  = `${API_BASE}/registry`;
  const NODES_URL= `${API_BASE}/node-packages`;
  const HEALTH_URL = `${API_BASE}/health`;

  const chat = document.getElementById('chat');
  const input = document.getElementById('msg');
  const sendBtn = document.getElementById('send');
  const pingChat = document.getElementById('pingChat');
  const clearChat = document.getElementById('clearChat');

  const actionSel = document.getElementById('action');
  const templateSel = document.getElementById('template');
  const payloadEl = document.getElementById('payload');

  const runExec = document.getElementById('runExec');
  const loadRegistry = document.getElementById('loadRegistry');
  const loadNodes = document.getElementById('loadNodes');
  const copyOut = document.getElementById('copyOut');
  const wipeOut = document.getElementById('wipeOut');

  const healthBtn = document.getElementById('health');
  const out = document.getElementById('out');
  const apiStatus = document.getElementById('apiStatus');

  function addMsg(text, cls) {
    const d = document.createElement('div');
    d.className = `b ${cls}`;
    d.textContent = text;
    chat.appendChild(d);
    chat.scrollTop = chat.scrollHeight;
  }

  function setOut(objOrText) {
    if (typeof objOrText === 'string') out.textContent = objOrText;
    else out.textContent = JSON.stringify(objOrText, null, 2);
  }

  async function fetchText(url, opts) {
    const r = await fetch(url, opts);
    const t = await r.text();
    let j = null;
    try { j = JSON.parse(t); } catch (_) {}
    return { r, t, j };
  }

  function setHealth(ok, text) {
    apiStatus.innerHTML = `<span class="dot ${ok ? "ok":"no"}"></span><span class="tiny">health: ${text}</span>`;
  }

  async function checkHealth() {
    try {
      const { r, t, j } = await fetchText(HEALTH_URL, { method: 'GET' });
      if (!r.ok) { setHealth(false, `HTTP ${r.status}`); return; }
      const model = j?.model || '';
      const ts = j?.ts || '';
      setHealth(true, `${model} ${ts}`.trim() || 'ok');
      setOut(j || t);
    } catch (e) {
      setHealth(false, String(e).slice(0, 60));
      setOut(`health error: ${String(e)}`);
    }
  }

  function applyTemplate() {
    const action = actionSel.value;
    const tpl = templateSel.value;
    let input = {};
    if (tpl === 'id_ci') input = { node_id: "ci" };
    payloadEl.value = JSON.stringify({ action, input }, null, 2);
  }

  async function sendChat(message) {
    addMsg(message, 'me');
    try {
      const { r, t, j } = await fetchText(CHAT_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
      });

      if (!r.ok) {
        addMsg(`HTTP ${r.status}: ${j?.error || t.slice(0, 160)}`, 'bot');
        return;
      }

      const reply = j?.reply ?? j?.text ?? j?.message ?? t;
      addMsg(reply || '[empty]', 'bot');
      setOut(j || t);
    } catch (e) {
      addMsg(`API error: ${String(e).slice(0, 160)}`, 'bot');
    }
  }

  async function runExecAction() {
    let payload;
    try {
      payload = JSON.parse(payloadEl.value);
    } catch (e) {
      setOut({ ok:false, error:{ code:"bad_json", message:String(e) } });
      return;
    }

    try {
      const { r, t, j } = await fetchText(EXEC_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!r.ok) {
        setOut(j || t);
        addMsg(`exec: HTTP ${r.status}`, 'bot');
        return;
      }

      setOut(j || t);
      const ok = j?.ok === true;
      addMsg(ok ? `exec ok: ${payload.action}` : `exec fail: ${payload.action}`, 'bot');
    } catch (e) {
      setOut(`exec error: ${String(e)}`);
    }
  }

  async function loadGet(url, label) {
    try {
      const { r, t, j } = await fetchText(url, { method:'GET' });
      if (!r.ok) { setOut(j || t); addMsg(`${label}: HTTP ${r.status}`, 'bot'); return; }
      setOut(j || t);
      addMsg(`${label}: loaded`, 'bot');
    } catch (e) {
      setOut(`${label} error: ${String(e)}`);
    }
  }

  // Wire
  sendBtn.onclick = () => sendChat(input.value.trim());
  input.addEventListener('keydown', (e) => { if (e.key === 'Enter') sendBtn.click(); });

  pingChat.onclick = () => sendChat("ping");
  clearChat.onclick = () => { chat.innerHTML = ''; addMsg("CIT UIv2 ready.", "bot"); };

  actionSel.onchange = applyTemplate;
  templateSel.onchange = applyTemplate;

  runExec.onclick = runExecAction;
  loadRegistry.onclick = () => loadGet(REG_URL, "registry");
  loadNodes.onclick = () => loadGet(NODES_URL, "node-packages");
  healthBtn.onclick = checkHealth;

  copyOut.onclick = async () => {
    try {
      await navigator.clipboard.writeText(out.textContent || '');
      addMsg("output copied", "bot");
    } catch (e) {
      addMsg("clipboard denied", "bot");
    }
  };

  wipeOut.onclick = () => setOut({});

  // Init
  addMsg("CIT UIv2 ready.", "bot");
  applyTemplate();
  checkHealth();
})();
