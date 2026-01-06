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
