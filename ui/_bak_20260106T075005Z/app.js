(() => {
  const chat = document.getElementById('chat');
  const input = document.getElementById('msg');
  const sendBtn = document.getElementById('send');

  const API_URL = 'http://127.0.0.1:8790/api/chat';

  function addMsg(text, cls) {
    const d = document.createElement('div');
    d.className = `b ${cls}`;
    d.textContent = text;
    chat.appendChild(d);
    chat.scrollTop = chat.scrollHeight;
  }

  async function send() {
    const text = input.value.trim();
    if (!text) return;

    input.value = '';
    addMsg(text, 'me');

    try {
      const r = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });

      const raw = await r.text();
      let j = null;
      try { j = JSON.parse(raw); } catch (_) {}

      if (!r.ok) {
        addMsg(`HTTP ${r.status}: ${(j && (j.error || j.message)) || raw.slice(0, 160)}`, 'bot');
        return;
      }

      const reply = (j && (j.reply || j.text || j.message)) || raw.slice(0, 240) || '[empty]';
      addMsg(reply, 'bot');
    } catch (e) {
      addMsg(`API error: ${String(e).slice(0, 160)}`, 'bot');
    }
  }

  sendBtn.onclick = send;
  input.addEventListener('keydown', (e) => { if (e.key === 'Enter') send(); });
})();
