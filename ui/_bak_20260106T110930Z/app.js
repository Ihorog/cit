(() => {
  "use strict";

  const qs = (s, r=document) => r.querySelector(s);
  const qsa = (s, r=document) => Array.from(r.querySelectorAll(s));

  const ROUTES = [
    { key: "home",     hash: "#/",         title: "Cimeika",        desc: "Головний вузол доступу" },
    { key: "kazkar",   hash: "#/kazkar",   title: "Казкар",         desc: "Пам’ять і історії" },
    { key: "legend",   hash: "#/legend",   title: "✨Легенда сі",    desc: "Сенсова бібліотека" },
    { key: "podija",   hash: "#/podija",   title: "ПоДія",          desc: "Події та запуск" },
    { key: "nastrij",  hash: "#/nastrij",  title: "Настрій",        desc: "Стан і фон" },
    { key: "malya",    hash: "#/malya",    title: "Маля",           desc: "Ідеї та варіанти" },
    { key: "calendar", hash: "#/calendar", title: "Календар",       desc: "Планування" },
    { key: "gallery",  hash: "#/gallery",  title: "Галерея",        desc: "Візуальний архів" },
  ];

  function getApiBase(){
    const u = new URL(window.location.href);
    const api = u.searchParams.get("api");
    return api || "http://127.0.0.1:8790";
  }

  function routeFromHash(){
    const h = window.location.hash || "#/";
    const hit = ROUTES.find(r => r.hash === h);
    return hit || ROUTES[0];
  }

  function el(tag, attrs={}, children=[]){
    const n = document.createElement(tag);
    for (const [k,v] of Object.entries(attrs)){
      if (k === "class") n.className = v;
      else if (k.startsWith("on") && typeof v === "function") n.addEventListener(k.slice(2), v);
      else if (k === "html") n.innerHTML = v;
      else if (v === true) n.setAttribute(k, "");
      else if (v !== false && v != null) n.setAttribute(k, String(v));
    }
    for (const c of children){
      if (c == null) continue;
      n.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
    }
    return n;
  }

  function renderShell(){
    const app = qs("#app");
    app.innerHTML = "";

    const shell = el("div", { class: "shell", id:"shell" }, [
      el("div", { class:"topbar" }, [
        el("div", { class:"brand" }, [
          el("div", { class:"ciDot", title:"Ci" }),
          el("div", { class:"title" }, ["CIT • ", el("span", { class:"small" }, ["Cimeika"])])
        ]),
        el("div", { class:"pills", id:"pills" })
      ]),
      el("div", { class:"main" }, [
        el("div", { class:"card page", id:"page" })
      ]),

      // Drawer overlay inside shell
      el("div", { class:"drawerBack", id:"drawerBack" }),
      el("div", { class:"drawer", id:"drawer" }, [
        el("div", { class:"drawerTop" }, [
          el("div", { class:"drawerTitle" }, [ el("div",{class:"ciDot"}), "Ci" ]),
          el("button", { class:"kbtn", id:"drawerClose", type:"button" }, ["Закрити"])
        ]),
        el("div", { class:"drawerBody" }, [
          el("div", { class:"small", id:"apiMeta" }),
          el("div", { class:"chatLog", id:"chatLog" }),
          el("form", { class:"chatForm", id:"chatForm" }, [
            el("input", { class:"chatInput", id:"chatInput", placeholder:"Повідомлення…", autocomplete:"off" }),
            el("button", { class:"chatSend", type:"submit" }, ["Надіслати"])
          ])
        ])
      ])
    ]);

    const fab = el("button", { class:"fab", id:"fab", type:"button", title:"Ci" }, ["Ci"]);

    app.appendChild(shell);
    app.appendChild(fab);

    // Pills
    const pills = qs("#pills");
    ROUTES.filter(r=>r.key!=="home").forEach(r=>{
      const b = el("button", {
        class:"pill",
        type:"button",
        "data-hash": r.hash,
        onclick: () => { window.location.hash = r.hash; }
      }, [r.title]);
      pills.appendChild(b);
    });

    // Drawer controls
    const back = qs("#drawerBack");
    const close = qs("#drawerClose");
    const fabBtn = qs("#fab");

    const openDrawer = () => qs("#shell").classList.add("drawerOpen");
    const closeDrawer = () => qs("#shell").classList.remove("drawerOpen");

    back.addEventListener("click", closeDrawer);
    close.addEventListener("click", closeDrawer);
    fabBtn.addEventListener("click", openDrawer);

    setupChat();

    return shell;
  }

  function setActivePills(route){
    qsa(".pill").forEach(p => {
      const h = p.getAttribute("data-hash");
      if (h === route.hash) p.setAttribute("aria-current","page");
      else p.removeAttribute("aria-current");
    });
  }

  function pageHome(){
    const grid = el("div", { class:"grid" });
    ROUTES.filter(r=>r.key!=="home").forEach(r=>{
      const t = el("div", {
        class:"tile",
        role:"button",
        tabindex:"0",
        onclick: () => window.location.hash = r.hash,
        onkeydown: (e) => { if (e.key === "Enter") window.location.hash = r.hash; }
      }, [
        el("div", { class:"h" }, [r.title]),
        el("div", { class:"d" }, [r.desc])
      ]);
      grid.appendChild(t);
    });

    return el("div", {}, [
      el("div", { class:"pageHeader" }, [
        el("div", {}, [
          el("h1", {}, ["Користувацький інтерфейс"]),
          el("div", { class:"meta" }, ["7 модулів • активні переходи • Ci доступний всюди"])
        ]),
        el("button", { class:"kbtn", type:"button", onclick: () => qs("#shell").classList.add("drawerOpen") }, ["Ci"])
      ]),
      el("div", { style:"height:10px" }),
      grid
    ]);
  }

  function pageGeneric(route){
    return el("div", {}, [
      el("div", { class:"pageHeader" }, [
        el("div", {}, [
          el("h1", {}, [route.title]),
          el("div", { class:"meta" }, [route.desc])
        ]),
        el("button", { class:"kbtn", type:"button", onclick: () => window.location.hash = "#/" }, ["На головну"])
      ]),
      el("div", { style:"height:12px" }),
      el("div", { class:"card", style:"background:rgba(255,255,255,.62); box-shadow:none; border:1px solid rgba(15,23,42,.10)" }, [
        el("div", { class:"small" }, [
          "Дія: тут підключаються компоненти модуля (контент/сервіси/інтеракції).",
          "\nCi → чат/команди доступні через кнопку Ci."
        ])
      ])
    ]);
  }

  let animLock = false;

  function renderRoute(next){
    const page = qs("#page");
    const current = page.firstElementChild;

    const make = () => {
      if (next.key === "home") return pageHome();
      return pageGeneric(next);
    };

    const incoming = make();
    incoming.classList.add("animIn");

    if (!current){
      page.innerHTML = "";
      page.appendChild(incoming);
      return;
    }

    if (animLock) return;
    animLock = true;

    current.classList.remove("animIn");
    current.classList.add("animOut");

    // after out -> swap
    setTimeout(() => {
      page.innerHTML = "";
      page.appendChild(incoming);
      animLock = false;
    }, 230);
  }

  function setupChat(){
    const apiBase = getApiBase();
    qs("#apiMeta").textContent = `API: ${apiBase}`;

    const log = qs("#chatLog");
    const form = qs("#chatForm");
    const input = qs("#chatInput");

    const addMsg = (role, text) => {
      const wrap = document.createElement("div");
      wrap.className = "msg";
      const r = document.createElement("div");
      r.className = "r";
      r.textContent = role;
      const t = document.createElement("div");
      t.className = "t";
      t.textContent = text;
      wrap.appendChild(r);
      wrap.appendChild(t);
      log.appendChild(wrap);
      log.scrollTop = log.scrollHeight;
    };

    addMsg("system", "Ci готовий. Відкрий будь-який модуль або дай команду.");

    async function send(text){
      addMsg("user", text);

      const payload = { message: text };
      try{
        const res = await fetch(`${apiBase}/api/chat`, {
          method:"POST",
          headers:{ "Content-Type":"application/json" },
          body: JSON.stringify(payload)
        });

        if (!res.ok){
          addMsg("error", `HTTP ${res.status}`);
          return;
        }

        const data = await res.json().catch(() => null);
        // tolerant parsing
        const out =
          (data && (data.reply || data.text || data.output_text || data.message)) ||
          (typeof data === "string" ? data : JSON.stringify(data));

        addMsg("assistant", out || "(empty)");
      }catch(e){
        addMsg("error", String(e && e.message ? e.message : e));
      }
    }

    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const text = (input.value || "").trim();
      if (!text) return;
      input.value = "";
      send(text);
    });
  }

  function init(){
    renderShell();

    const apply = () => {
      const r = routeFromHash();
      setActivePills(r);
      renderRoute(r);
    };

    window.addEventListener("hashchange", apply);
    if (!window.location.hash) window.location.hash = "#/";
    apply();
  }

  document.addEventListener("DOMContentLoaded", init);
})();
