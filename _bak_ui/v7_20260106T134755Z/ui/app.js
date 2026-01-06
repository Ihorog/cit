(function(){
  const qs = new URLSearchParams(location.search);
  const API = qs.get("api") || (location.origin.replace(/:\d+$/, "") + ":8790");

  const ROUTES = [
    {id:"home",    label:"Ci", path:"#/",                 desc:"Центр керування сенсами", badge:"центр"},
    {id:"kazkar",  label:"Казкар", path:"#/kazkar",        desc:"Памʼять, історії, досвід", badge:"земля"},
    {id:"legend",  label:"✨ Легенда сі", path:"#/legend", desc:"Бібліотека символів і ядро", badge:"легенда"},
    {id:"podija",  label:"ПоДія", path:"#/podija",        desc:"Майбутнє, події, запуск", badge:"вогонь"},
    {id:"nastrij", label:"Настрій", path:"#/nastrij",      desc:"Стан, хвиля, реакції", badge:"вода"},
    {id:"malya",   label:"Маля", path:"#/malya",          desc:"Ідеї, варіанти, нове", badge:"повітря"},
    {id:"calendar",label:"Календар", path:"#/calendar",    desc:"Час, вузли, ритми", badge:"час"},
    {id:"gallery", label:"Галерея", path:"#/gallery",      desc:"Фото, історії, слайди", badge:"світло"},
  ];

  const el = (tag, cls, html) => {
    const n = document.createElement(tag);
    if(cls) n.className = cls;
    if(html != null) n.innerHTML = html;
    return n;
  };

  const root = document.getElementById("app");

  // Topbar
  const top = el("div","topbar");
  const brand = el("div","brand");
  const logo = el("div","logo");
  const img = el("img");
  img.src = "icons/ci.svg";
  img.alt = "Ci";
  img.width = 24; img.height = 24;
  logo.appendChild(img);

  const t = el("div","title");
  t.innerHTML = "<b>Cimeika</b><span>Ci Interface Terminal</span>";
  brand.appendChild(logo);
  brand.appendChild(t);

  const actions = el("div","actions");
  const apiPill = el("button","iconbtn pill");
  apiPill.title = "API endpoint";
  apiPill.innerHTML = `<span style="opacity:.8;font-size:12px">API</span><span style="font-weight:700">${API.replace("http://","")}</span>`;
  const ciBtn = el("button","iconbtn");
  ciBtn.id = "ciBtnTop";
  ciBtn.title = "Ci (чат)";
  ciBtn.innerHTML = `<span style="font-weight:800">Ci</span>`;

  actions.appendChild(apiPill);
  actions.appendChild(ciBtn);

  top.appendChild(brand);
  top.appendChild(actions);

  // Shell
  const shell = el("div","shell");

  // Left nav
  const left = el("div","panel left");
  const nav = el("div","nav");
  ROUTES.filter(r=>r.id!=="home").forEach(r=>{
    const a = el("a");
    a.href = r.path;
    a.dataset.route = r.id;
    a.innerHTML = `<div><div style="font-weight:750">${r.label}</div><small>${r.desc}</small></div><span class="badge">${r.badge}</span>`;
    nav.appendChild(a);
  });
  left.appendChild(nav);

  // Right stage
  const right = el("div","panel right");
  const stage = el("div","stage");

  // Views
  const views = {};
  function makeHome(){
    const v = el("div","view");
    v.dataset.view = "home";
    v.innerHTML = `
      <div style="display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:12px">
        <div>
          <div style="font-size:22px;font-weight:850;letter-spacing:.2px">Ci — центр</div>
          <div style="color:rgba(255,255,255,.55);font-size:13px;margin-top:4px">Переходи активні. Анімації. Навігація. Ci-чат overlay.</div>
        </div>
        <span class="badge">UI vNext</span>
      </div>
      <div class="grid">
        ${ROUTES.filter(r=>r.id!=="home").map((r,i)=>`
          <div class="card ${i%2===0?"gold":""}">
            <div class="h">
              <b>${r.label}</b>
              <span class="badge">${r.badge}</span>
            </div>
            <p>${r.desc}</p>
            <a class="go" href="${r.path}">Відкрити →</a>
          </div>
        `).join("")}
      </div>
      <div style="margin-top:14px;display:flex;gap:10px;flex-wrap:wrap">
        <button class="iconbtn" id="healthBtn">Перевірка API</button>
        <button class="iconbtn" id="openChatBtn">Ci-чат</button>
      </div>
      <div id="healthOut" style="margin-top:10px;color:rgba(255,255,255,.62);font-size:12px"></div>
    `;
    return v;
  }

  function makeModule(id, title, hint){
    const v = el("div","view");
    v.dataset.view = id;
    v.innerHTML = `
      <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:12px">
        <div>
          <div style="font-size:22px;font-weight:850">${title}</div>
          <div style="margin-top:6px;color:rgba(255,255,255,.55);font-size:13px">${hint}</div>
        </div>
        <span class="badge">${id}</span>
      </div>

      <div style="margin-top:14px" class="grid">
        <div class="card">
          <div class="h"><b>Дія</b><span class="badge">in</span></div>
          <p>Швидка кнопка для наступного кроку в цьому модулі.</p>
          <button class="go" data-action="demo">Запустити →</button>
        </div>
        <div class="card gold">
          <div class="h"><b>Стан</b><span class="badge">+/−</span></div>
          <p>Маркер присутності: є / нема. Контрольні точки по модулю.</p>
          <button class="go" data-action="marker">Контроль →</button>
        </div>
        <div class="card">
          <div class="h"><b>Дані</b><span class="badge">api</span></div>
          <p>Перевірка доступності API /health та /registry.</p>
          <button class="go" data-action="ping">Ping API →</button>
        </div>
      </div>

      <div style="margin-top:14px">
        <div class="hint">API: <span style="font-weight:700">${API}</span></div>
        <div id="out_${id}" style="margin-top:8px;color:rgba(255,255,255,.62);font-size:12px"></div>
      </div>
    `;
    return v;
  }

  views.home = makeHome();
  views.kazkar = makeModule("kazkar","Казкар","Минуле. Памʼять. Історії. Досвід.");
  views.legend = makeModule("legend","✨ Легенда сі","Ядро символів, бібліотека сенсів, структурні маркери.");
  views.podija = makeModule("podija","ПоДія","Майбутнє. Ініціації. Запуски.");
  views.nastrij = makeModule("nastrij","Настрій","Стан «зараз». Емоційні реакції і хвиля.");
  views.malya = makeModule("malya","Маля","Ідеї. Альтернативи. Творчість.");
  views.calendar = makeModule("calendar","Календар","Ритми. Вузли часу. Було / Є / Буде.");
  views.gallery = makeModule("gallery","Галерея","Фото, історії, слайдери, макети.");

  Object.values(views).forEach(v=>stage.appendChild(v));

  right.appendChild(stage);

  shell.appendChild(left);
  shell.appendChild(right);

  // Splash
  const splash = el("div","splash");
  splash.innerHTML = `
    <div class="slash"></div>
    <div class="flow"></div>
    <div class="splashCenter">
      <img src="icons/ci.svg" alt="Ci" />
      <b>Ci</b>
      <span>було → є → буде</span>
    </div>
  `;

  // Drawer (Ci Chat overlay)
  const mask = el("div","drawerMask");
  const drawer = el("div","drawer");
  drawer.innerHTML = `
    <div class="drawerHead">
      <b>Ci — чат</b>
      <div style="display:flex;gap:8px;align-items:center">
        <button class="iconbtn" id="btnHealth" title="API /health">/health</button>
        <button class="iconbtn" id="btnClose" title="Close">✕</button>
      </div>
    </div>
    <div class="drawerBody">
      <div class="chatlog" id="chatlog">
        <div class="msg">
          <div class="meta">Ci</div>
          <div class="bubble">Готовий. Вибери модуль або напиши команду.</div>
        </div>
      </div>
      <div class="composer">
        <input id="msg" placeholder="Повідомлення для Ci…" autocomplete="off" />
        <button id="send">Надіслати</button>
      </div>
      <div class="hint">POST ${API}/chat (якщо доступно). Якщо ні — працює як локальний лог.</div>
    </div>
  `;

  // Mobile FAB
  const fab = el("button","ciFab");
  fab.id = "ciFab";
  fab.innerHTML = `<img src="icons/ci.svg" alt="Ci">`;

  root.appendChild(top);
  root.appendChild(shell);
  root.appendChild(splash);
  root.appendChild(mask);
  root.appendChild(drawer);
  root.appendChild(fab);

  // Router
  function currentRoute(){
    const h = location.hash || "#/";
    const r = ROUTES.find(x => x.path === h);
    return r ? r.id : "home";
  }
  function setActive(){
    const id = currentRoute();
    // nav active
    nav.querySelectorAll("a").forEach(a=>{
      a.classList.toggle("active", a.dataset.route === id);
    });
    // views
    Object.values(views).forEach(v=>{
      v.classList.toggle("on", v.dataset.view === id || (id==="home" && v.dataset.view==="home"));
    });
    // subtle top title
    const r = ROUTES.find(x=>x.id===id) || ROUTES[0];
    t.querySelector("b").textContent = "Cimeika";
    t.querySelector("span").textContent = r.label;
  }

  window.addEventListener("hashchange", setActive);
  setActive();

  // Splash off
  setTimeout(()=>splash.classList.add("off"), 980);
  setTimeout(()=>splash.remove(), 1550);

  // Drawer handlers
  function openDrawer(){
    mask.classList.add("on");
    drawer.classList.add("on");
    setTimeout(()=>document.getElementById("msg")?.focus(), 60);
  }
  function closeDrawer(){
    mask.classList.remove("on");
    drawer.classList.remove("on");
  }
  document.getElementById("ciBtnTop").addEventListener("click", openDrawer);
  fab.addEventListener("click", openDrawer);
  mask.addEventListener("click", closeDrawer);
  drawer.querySelector("#btnClose").addEventListener("click", closeDrawer);

  // Chat send
  function addMsg(who, text){
    const log = document.getElementById("chatlog");
    const m = el("div","msg" + (who==="me" ? " me": ""));
    m.innerHTML = `<div class="meta">${who==="me" ? "Ви" : "Ci"}</div><div class="bubble"></div>`;
    m.querySelector(".bubble").textContent = text;
    log.appendChild(m);
    log.scrollTop = log.scrollHeight;
  }

  async function postChat(text){
    try{
      const res = await fetch(API + "/chat", {
        method:"POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({ input: text })
      });
      if(!res.ok) throw new Error("HTTP " + res.status);
      const data = await res.json();
      // Flexible parse
      const out = (data.output_text || data.text || data.reply || data.message || JSON.stringify(data)).toString();
      addMsg("ci", out);
    }catch(e){
      addMsg("ci", "⚠️ API недоступне для /chat. Локальний режим. " + (e && e.message ? e.message : ""));
    }
  }

  document.getElementById("send").addEventListener("click", ()=>{
    const inp = document.getElementById("msg");
    const text = (inp.value || "").trim();
    if(!text) return;
    inp.value = "";
    addMsg("me", text);
    postChat(text);
  });
  document.getElementById("msg").addEventListener("keydown",(e)=>{
    if(e.key==="Enter") document.getElementById("send").click();
  });

  // Health checks
  async function health(where){
    try{
      const r = await fetch(API + "/health");
      const j = await r.json();
      const s = "OK: " + JSON.stringify(j);
      if(where) where.textContent = s;
      addMsg("ci", s);
    }catch(e){
      const s = "⚠️ /health недоступний: " + (e && e.message ? e.message : "");
      if(where) where.textContent = s;
      addMsg("ci", s);
    }
  }

  // Home buttons
  setTimeout(()=>{
    const hb = document.getElementById("healthBtn");
    const ob = document.getElementById("openChatBtn");
    const out = document.getElementById("healthOut");
    hb && hb.addEventListener("click", ()=>health(out));
    ob && ob.addEventListener("click", openDrawer);
  }, 0);

  // Module buttons
  function bindModuleActions(){
    document.querySelectorAll('[data-action="ping"]').forEach(btn=>{
      btn.addEventListener("click", async ()=>{
        const view = btn.closest(".view");
        const id = view.dataset.view;
        const out = document.getElementById("out_"+id);
        try{
          const r = await fetch(API + "/registry");
          const j = await r.json();
          out.textContent = "REGISTRY OK: " + JSON.stringify(j).slice(0,600);
        }catch(e){
          out.textContent = "⚠️ REGISTRY ERR: " + (e && e.message ? e.message : "");
        }
      });
    });
    document.querySelectorAll('[data-action="demo"]').forEach(btn=>{
      btn.addEventListener("click", ()=>{
        const view = btn.closest(".view");
        const id = view.dataset.view;
        const out = document.getElementById("out_"+id);
        out.textContent = "OK: дія зафіксована (UI). Наступне — підв’язати модульні API.";
      });
    });
    document.querySelectorAll('[data-action="marker"]').forEach(btn=>{
      btn.addEventListener("click", ()=>{
        const view = btn.closest(".view");
        const id = view.dataset.view;
        const out = document.getElementById("out_"+id);
        out.textContent = "+ контрольна точка закрита (UI).";
      });
    });
  }
  bindModuleActions();

})();
