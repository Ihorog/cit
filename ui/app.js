(() => {
  const qs = (s, r=document) => r.querySelector(s);
  const el = (tag, attrs={}, kids=[]) => {
    const n = document.createElement(tag);
    Object.entries(attrs).forEach(([k,v]) => {
      if (k === "class") n.className = v;
      else if (k === "html") n.innerHTML = v;
      else if (k.startsWith("on") && typeof v === "function") n.addEventListener(k.slice(2), v);
      else n.setAttribute(k, v);
    });
    kids.forEach(k => n.appendChild(k));
    return n;
  };

  const BUILD = (window.__CIT_BUILD__ || "dev");
  const DEFAULT_API = "http://127.0.0.1:8790";
  const api = new URLSearchParams(location.search).get("api") || DEFAULT_API;

  // IMPORTANT: dev-mode stability — unregister SW to avoid "nothing changed"
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.getRegistrations().then(rs => rs.forEach(r => r.unregister())).catch(()=>{});
  }

  const routes = {
    "/":        { title:"Cimeika",   key:"home",    desc:"центр, маршрути, запуск" },
    "/kazkar":  { title:"Казкар",    key:"kazkar",  desc:"історії, памʼять, архів", tag:"земля" },
    "/legend":  { title:"✨ Легенда сі", key:"legend", desc:"символіка, база сенсів", tag:"ядро" },
    "/podiya":  { title:"ПоДія",     key:"podiya",  desc:"плани, запуск, події", tag:"вогонь" },
    "/nastriy": { title:"Настрій",   key:"nastriy", desc:"стан, емоції, вода", tag:"вода" },
    "/malya":   { title:"Маля",      key:"malya",   desc:"ідеї, альтернативи", tag:"повітря" },
    "/kalendar":{ title:"Календар",  key:"kalendar",desc:"вузли часу, було/є/буде", tag:"час" },
    "/galereya": { title:"Галерея",   key:"galereya", desc:"слайдер, історії, макети друку", tag:"медіа" },
    "/ci":      { title:"Ci",        key:"ci",      desc:"контроль, інтеграції, виклики", tag:"центр" },
  };

  const cards = [
    { path:"/kazkar",   k:"Казкар",     d:"історії, памʼять, архів", tag:"земля" },
    { path:"/legend",   k:"✨ Легенда сі", d:"символіка, база сенсів", tag:"ядро" },
    { path:"/podiya",   k:"ПоДія",      d:"плани, запуск, події", tag:"вогонь" },
    { path:"/nastriy",  k:"Настрій",    d:"стан, емоції, вода", tag:"вода" },
    { path:"/malya",    k:"Маля",       d:"ідеї, альтернативи", tag:"повітря" },
    { path:"/kalendar", k:"Календар",   d:"вузли часу, було/є/буде", tag:"час" },
    { path:"/galereya",  k:"Галерея",    d:"слайдер, історії, макети друку", tag:"медіа" },
    { path:"/ci",       k:"Ci",         d:"контроль, інтеграції, виклики", tag:"центр" },
  ];

  const setHash = (p) => { location.hash = "#"+p; };
  const getPath = () => (location.hash || "#/").slice(1) || "/";

  const intro = qs("#intro");
  const hideIntro = () => { if (!intro) return; setTimeout(()=> intro.classList.add("hidden"), 900); };

  const app = qs("#app");
  const topbar = el("div", { class:"topbar" }, [
    el("div", { class:"brand" }, [
      el("img", { src:"./icons/icon-192.png", alt:"Ci", onerror: (e)=>{ e.target.style.display="none"; } }),
      el("div", {}, [
        el("div", { class:"title", html:"Cimeika" }),
        el("div", { class:"sub", id:"subtitle", html:"Ci · Казкар · ПоДія · Настрій · Маля · Календар · Галерея" })
      ])
    ]),
    el("div", { class:"pills" }, [
      el("div", { class:"pill", id:"apiPill", html:"API: …" }),
      el("div", { class:"pill", id:"lanPill", html:"LAN: …" }),
      el("div", { class:"pill", id:"buildPill", html:"BUILD: …" }),
    ])
  ]);

  const left = el("div", { class:"panel stage" });
  const right = el("div", { class:"panel stage" });

  const shell = el("div", { class:"shell" }, [left, right]);

  app.appendChild(topbar);
  app.appendChild(shell);

  // Drawer (Ci chat placeholder shell; API integration kept minimal)
  const drawer = el("div", { class:"drawer", id:"drawer" }, [
    el("div", { class:"drawerHeader" }, [
      el("div", { class:"left" }, [
        el("div", { class:"ciDot" }),
        el("div", {}, [
          el("div", { class:"h", html:"Ci" }),
          el("small", { id:"drawerHint", html:"чат-дровер без втрати контексту" })
        ])
      ]),
      el("button", { class:"btn", id:"closeDrawer", html:"Закрити" })
    ]),
    el("div", { class:"drawerBody" }, [
      el("div", { class:"kpi" }, [
        el("div", { class:"pill", id:"drawerApi", html:"API: …" }),
        el("div", { class:"pill", id:"drawerRoute", html:"ROUTE: …" }),
        el("div", { class:"pill", id:"drawerBuild", html:"BUILD: …" }),
      ]),
      el("div", { class:"card", style:"cursor:default" }, [
        el("div", { class:"k", html:"Контакт з Ci" }),
        el("div", { class:"d", html:"UI готовий. Далі підключаємо /chat, файли, галерею, календар." })
      ])
    ])
  ]);
  document.body.appendChild(drawer);

  const openDrawer = () => drawer.classList.add("open");
  const closeDrawer = () => drawer.classList.remove("open");
  qs("#closeDrawer")?.addEventListener("click", closeDrawer);
  document.addEventListener("keydown", (e)=> { if (e.key==="Escape") closeDrawer(); });

  const renderLeft = (path) => {
    left.innerHTML = "";
    const r = routes[path] || routes["/"];
    left.appendChild(el("div", { class:"panelHeader" }, [
      el("div", { class:"h", html:r.title }),
      el("div", { class:"pill", html:(r.tag || " ") })
    ]));
    const body = el("div", { class:"stageBody fadeIn" });

    const hero = el("div", { class:"hero" }, [
      el("div", { class:"arc" }),
      el("div", { class:"heroHint", html:"Натисни Ci — відкриє чат-дровер без втрати контексту." }),
      el("div", { class:"routeMark", html:("#"+path) }),
      el("div", { class:"centerCi", id:"centerCi" }, [
        el("img", { src:"./icons/icon-192.png", alt:"Ci" })
      ])
    ]);
    hero.querySelector("#centerCi")?.addEventListener("click", () => {
      qs("#drawerRoute").textContent = "ROUTE: "+("#"+path);
      openDrawer();
    });

    body.appendChild(hero);

    const grid = el("div", { class:"grid" });
    // On Kazkar screen show Legend + Malya as in your screenshot, else show full map
    const list = (path==="/kazkar") ? [
      { path:"/legend", k:"✨ Легенда сі", d:"ядро Казкаря", tag:"ядро" },
      { path:"/malya",  k:"Маля", d:"ідеї / повітря", tag:"повітря" },
    ] : cards;

    list.forEach(c => {
      const card = el("div", { class:"card" }, [
        el("div", { class:"k", html:c.k }),
        el("div", { class:"d", html:c.d }),
        el("div", { class:"tag", html:c.tag || "" }),
      ]);
      card.addEventListener("click", () => setHash(c.path));
      grid.appendChild(card);
    });

    body.appendChild(grid);
    left.appendChild(body);
  };

  const renderRight = (path) => {
    right.innerHTML = "";
    const r = routes[path] || routes["/"];
    right.appendChild(el("div", { class:"panelHeader" }, [
      el("div", { class:"h", html:"Навігація" }),
      el("div", { class:"pill", html:"#"+(r.key || "home") })
    ]));
    const body = el("div", { class:"stageBody fadeIn" });

    const g = el("div", { class:"grid" });
    cards.forEach(c => {
      const card = el("div", { class:"card" }, [
        el("div", { class:"k", html:c.k }),
        el("div", { class:"d", html:c.d }),
        el("div", { class:"tag", html:c.tag || "" }),
      ]);
      card.addEventListener("click", () => setHash(c.path));
      g.appendChild(card);
    });
    body.appendChild(g);

    // Self-check block
    body.appendChild(el("div", { class:"card", style:"cursor:default" }, [
      el("div", { class:"k", html:"Self-check" }),
      el("div", { class:"d", id:"selfcheck", html:"…" }),
    ]));

    right.appendChild(body);
  };

  const updatePills = async () => {
    qs("#buildPill").textContent = "BUILD: "+BUILD;
    qs("#drawerBuild").textContent = "BUILD: "+BUILD;
    try {
      const h = await fetch(api.replace(/\/$/,"") + "/health", { cache:"no-store" });
      const j = await h.json().catch(()=> ({}));
      const ok = (j && (j.ok===true || j.status==="ok" || j.ok==="true")) ? "OK" : "ERR";
      qs("#apiPill").textContent = "API: "+ok+" · "+(j.model || "");
      qs("#drawerApi").textContent = "API: "+ok+" · "+(j.model || "");
    } catch {
      qs("#apiPill").textContent = "API: ERR";
      qs("#drawerApi").textContent = "API: ERR";
    }

    // LAN hint (best-effort)
    try{
      // Display local hostname/ip if browser provides (usually 127.0.0.1 in your current screenshot)
      qs("#lanPill").textContent = "LAN: "+location.hostname;
    }catch{
      qs("#lanPill").textContent = "LAN: ?";
    }
  };

  const render = async () => {
    const path = getPath();
    document.title = "Cimeika — " + (routes[path]?.title || "Ci");
    renderLeft(path);
    renderRight(path);
    qs("#drawerRoute").textContent = "ROUTE: "+("#"+path);

    await updatePills();

    const sc = qs("#selfcheck");
    if (sc){
      sc.innerHTML =
        "route=" + ("#"+path) + "<br/>" +
        "api=" + api + "<br/>" +
        "build=" + BUILD + "<br/>" +
        "tip: якщо «нічого не змінилось» — очисти кеш вкладки або перезавантаж (оновлено через build-id).";
    }
  };

  window.addEventListener("hashchange", render);
  hideIntro();
  render();
})();

/* CI_DRAWER_FIX_VH_2026: normalize drawer structure for CSS targeting */
(function(){
  function tagDrawer(){
    const d =
      document.getElementById('ciDrawer') ||
      document.querySelector('.ci-drawer') ||
      document.querySelector('[data-ci="drawer"]');
    if(!d) return;

    // mark root
    if(!d.classList.contains('ci-drawer')) d.classList.add('ci-drawer');
    if(!d.getAttribute('data-ci')) d.setAttribute('data-ci','drawer');

    // try find inner/head/body/compose, otherwise create wrappers safely
    let inner = d.querySelector('.drawer-inner,.ci-drawer-inner');
    if(!inner){
      inner = document.createElement('div');
      inner.className = 'drawer-inner ci-drawer-inner';
      // move all children into inner
      while(d.firstChild) inner.appendChild(d.firstChild);
      d.appendChild(inner);
    } else {
      inner.classList.add('drawer-inner','ci-drawer-inner');
    }

    // head/body/compose tagging
    const head = inner.querySelector('.drawer-head,.ci-drawer-head') || inner.firstElementChild;
    if(head) head.classList.add('drawer-head','ci-drawer-head');

    // body: prefer chat log container
    const body =
      inner.querySelector('.drawer-body,.ci-drawer-body,.chat-body') ||
      inner.querySelector('[data-role="messages"]') ||
      inner.querySelector('.messages') ||
      (head && head.nextElementSibling) ||
      inner;
    if(body) body.classList.add('drawer-body','ci-drawer-body','chat-body');

    // compose: prefer input area
    const compose =
      inner.querySelector('.drawer-compose,.ci-drawer-compose,.chat-compose') ||
      inner.querySelector('[data-role="composer"]') ||
      inner.querySelector('.composer') ||
      inner.querySelector('form') ||
      inner.querySelector('textarea')?.closest('div') ||
      null;
    if(compose) compose.classList.add('drawer-compose','ci-drawer-compose','chat-compose');
  }

  // run now + on route changes
  window.addEventListener('load', tagDrawer);
  setTimeout(tagDrawer, 400);
  setTimeout(tagDrawer, 1200);

  // observe DOM changes when drawer opens
  const mo = new MutationObserver(()=>tagDrawer());
  mo.observe(document.documentElement, {subtree:true, childList:true});
})();

/* ======================= CI_LAUNCH_V1_BEGIN ======================= */
/* Non-destructive injector:
   - Auto day/night atmosphere (no visible switches)
   - Make Ci logo x2
   - Launch overlay animation on Ci logo click
   - Does NOT change existing routes/layout. */

(function CiLaunchV1(){
  const D = document;
  const W = window;

  function prefersReducedMotion(){
    try { return W.matchMedia && W.matchMedia('(prefers-reduced-motion: reduce)').matches; }
    catch(e){ return false; }
  }

  function applyDayNight(){
    const h = new Date().getHours();
    const nightByTime = (h >= 20 || h < 6);
    const nightByScheme = (() => {
      try { return W.matchMedia && W.matchMedia('(prefers-color-scheme: dark)').matches; }
      catch(e){ return false; }
    })();

    const isNight = nightByTime || nightByScheme;
    D.documentElement.classList.toggle('ci-night', isNight);
    D.documentElement.classList.toggle('ci-day', !isNight);
    D.body && D.body.classList.toggle('ci-night', isNight);
    D.body && D.body.classList.toggle('ci-day', !isNight);

    // depth always on (легка глибина/об’єм)
    D.body && D.body.classList.add('ci-depth');
  }

  function ensureStarfield(){
    if (D.querySelector('.ci-starfield')) return;
    const sf = D.createElement('div');
    sf.className = 'ci-starfield';
    D.body.appendChild(sf);
  }

  function findCiLogo(){
    // максимально обережно: шукаємо існуючий img (alt="Ci" або icon-192.png)
    const candidates = [
      'img[alt="Ci"]',
      'img[src*="icon-192.png"]',
      'img[src*="icons/icon-192.png"]',
      'img[src*="Ci.png"]',
      'img[src*="ci.png"]'
    ];
    for (const sel of candidates){
      const el = D.querySelector(sel);
      if (el) return el;
    }
    return null;
  }

  function attachLogoEnhancements(logo){
    if (!logo) return;
    logo.classList.add('ci-logo'); // CSS робить x2
    // не перехоплюємо поведінку, лише додаємо handler
    logo.style.cursor = 'pointer';
  }

  function createOverlay(){
    const overlay = D.createElement('div');
    overlay.id = 'ciLaunchOverlay';

    // flash layers
    const flash1 = D.createElement('div');
    flash1.className = 'ci-flash';
    const flash2 = D.createElement('div');
    flash2.className = 'ci-flash ci-flash-warm';

    // split
    const top = D.createElement('div');
    top.className = 'ci-split-top';
    const bottom = D.createElement('div');
    bottom.className = 'ci-split-bottom';

    // fracture
    const fracture = D.createElement('div');
    fracture.className = 'ci-fracture';

    // perimeter svg
    const per = D.createElement('div');
    per.className = 'ci-perimeter';
    per.innerHTML = `
      <svg viewBox="0 0 100 100" preserveAspectRatio="none">
        <defs>
          <linearGradient id="ciBlueGrad" x1="0" y1="1" x2="0" y2="0">
            <stop offset="0%" stop-color="#1FA4FF"/>
            <stop offset="100%" stop-color="#87D3FF"/>
          </linearGradient>
          <linearGradient id="ciGoldGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#FFC34D"/>
            <stop offset="100%" stop-color="#FFA72B"/>
          </linearGradient>
        </defs>

        <!-- border path (rectangle) -->
        <path id="ciBorder" d="M 2 2 L 98 2 L 98 98 L 2 98 Z" />
        <path id="ciBlue" class="ci-path" d="M 2 98 L 2 2 L 98 2 L 98 50"
              stroke="url(#ciBlueGrad)" />
        <path id="ciGold" class="ci-path" d="M 98 50 L 98 98 L 2 98"
              stroke="url(#ciGoldGrad)" />
      </svg>
    `;

    overlay.appendChild(top);
    overlay.appendChild(bottom);
    overlay.appendChild(per);
    overlay.appendChild(fracture);
    overlay.appendChild(flash1);
    overlay.appendChild(flash2);

    return { overlay, flash1, flash2, fracture, top, bottom, per };
  }

  function animateSequence(originX, originY, done){
    const reduced = prefersReducedMotion();

    // блок взаємодії на час анімації
    D.body.classList.add('ci-busy');
    D.body.classList.add('ci-preveal');

    const { overlay, flash1, flash2, fracture, per } = createOverlay();
    D.body.appendChild(overlay);

    const t0 = performance.now();

    // helper
    function at(ms, fn){ W.setTimeout(fn, ms); }

    // 0) primary flash
    at(0, () => {
      flash1.animate(
        [{opacity: 0},{opacity: reduced ? 0.20 : 1},{opacity:0}],
        {duration: reduced ? 120 : 40, easing: 'linear'}
      );
    });

    // 1) diagonal fracture wedge (from logo)
    at(20, () => {
      const angleDeg = 35;
      fracture.style.left = (originX|0) + 'px';
      fracture.style.top  = (originY|0) + 'px';
      fracture.style.transform = `rotate(${angleDeg}deg) translate(-6px, -140px)`;
      fracture.style.opacity = '1';
      fracture.animate(
        [
          { width: '2px', opacity: 0.0 },
          { width: reduced ? '12px' : '26px', opacity: 1.0 },
          { width: reduced ? '8px' : '18px', opacity: 0.0 }
        ],
        { duration: reduced ? 420 : 120, easing: 'cubic-bezier(0.16, 1, 0.3, 1)' }
      );
    });

    // 2) perimeter flows (100ms..1000ms)
    at(100, () => {
      const blue = overlay.querySelector('#ciBlue');
      const gold = overlay.querySelector('#ciGold');
      if (blue && gold){
        // stroke-dash animation
        const lenBlue = 300; // fixed for viewBox
        const lenGold = 220;

        blue.style.strokeDasharray = String(lenBlue);
        blue.style.strokeDashoffset = String(lenBlue);

        gold.style.strokeDasharray = String(lenGold);
        gold.style.strokeDashoffset = String(lenGold);

        blue.animate(
          [
            { strokeDashoffset: lenBlue, opacity: 0.0 },
            { strokeDashoffset: 0, opacity: 1.0 }
          ],
          { duration: reduced ? 520 : 900, easing: 'cubic-bezier(0.22, 1, 0.36, 1)' }
        );

        gold.animate(
          [
            { strokeDashoffset: lenGold, opacity: 0.0 },
            { strokeDashoffset: 0, opacity: 1.0 }
          ],
          { duration: reduced ? 520 : 900, easing: 'cubic-bezier(0.22, 1, 0.36, 1)' }
        );
      }
    });

    // 3) convergence warm flash (≈1000ms)
    at(reduced ? 520 : 1000, () => {
      flash2.animate(
        [{opacity: 0},{opacity: reduced ? 0.20 : 0.92},{opacity:0}],
        {duration: reduced ? 160 : 60, easing: 'linear'}
      );
    });

    // 4) UI materialization window (1100..1600ms)
    at(reduced ? 650 : 1100, () => {
      D.body.classList.add('ci-reveal'); // CSS витягує компоненти
    });

    // 5) end state (~1800ms)
    at(reduced ? 900 : 1800, () => {
      try { overlay.remove(); } catch(e){}
      D.body.classList.remove('ci-busy');
      D.body.classList.remove('ci-preveal');
      // ci-reveal залишаємо на body як стабільний “об’єм”, це не змінює layout
      if (typeof done === 'function') done();
    });
  }

  function bindLaunchToLogo(){
    const logo = findCiLogo();
    if (!logo) return false;

    attachLogoEnhancements(logo);

    let locked = false;
    logo.addEventListener('click', (ev) => {
      if (locked) return;
      locked = true;

      const r = logo.getBoundingClientRect();
      const originX = r.left + r.width/2;
      const originY = r.top  + r.height/2;

      animateSequence(originX, originY, () => { locked = false; });
    }, { passive: true });

    return true;
  }

  function boot(){
    // apply theme + starfield
    applyDayNight();
    ensureStarfield();

    // bind to logo (retry a few times in case UI mounts late)
    let tries = 0;
    const timer = W.setInterval(() => {
      tries++;
      const ok = bindLaunchToLogo();
      if (ok || tries > 20) W.clearInterval(timer);
    }, 250);
  }

  if (D.readyState === 'loading'){
    D.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
/* ======================= CI_LAUNCH_V1_END ========================= */

