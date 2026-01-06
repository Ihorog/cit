#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

CIT_DIR="${CIT_DIR:-$HOME/cimeika/cit}"
UI_DIR="$CIT_DIR/ui"
UI_PORT="${UI_PORT:-8010}"
API_PORT="${API_PORT:-8790}"

say(){ printf "\n=== %s ===\n" "$1"; }
ts(){ date -u +"%Y%m%dT%H%M%SZ"; }

[ -d "$UI_DIR" ] || { echo "ERR: ui dir not found: $UI_DIR"; exit 1; }

B="$UI_DIR/_bak_$(ts)"
mkdir -p "$B"

say "0) BACKUP"
for f in index.html app.js styles.css; do
  if [ -f "$UI_DIR/$f" ]; then
    cp -f "$UI_DIR/$f" "$B/$f"
    echo "BACKUP: $f -> $B/$f"
  fi
done

say "1) WRITE ui/index.html"
cat > "$UI_DIR/index.html" <<'HTML'
<!doctype html>
<html lang="uk">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="theme-color" content="#0B2340" />
  <title>CIT • Cimeika</title>
  <link rel="manifest" href="./manifest.webmanifest" />
  <link rel="stylesheet" href="./styles.css" />
</head>
<body>
  <div id="app"></div>
  <script defer src="./app.js"></script>
</body>
</html>
HTML

say "2) WRITE ui/styles.css (canon + transitions + drawer)"
cat > "$UI_DIR/styles.css" <<'CSS'
:root{
  --navy:#0B2340;
  --azure:#1FA4FF;
  --sky:#87D3FF;
  --gold:#FFC34D;
  --amber:#FFA72B;
  --cream:#FFE6B3;
  --graphite:#1F2937;
  --silver:#64748B;

  --bg: radial-gradient(1200px 700px at 20% 10%, rgba(31,164,255,.18), transparent 60%),
        radial-gradient(900px 600px at 80% 30%, rgba(255,195,77,.18), transparent 60%),
        linear-gradient(35deg, #1FA4FF 0%, #87D3FF 42%, #FFC34D 100%);
  --panel: rgba(255,255,255,.78);
  --panel2: rgba(255,255,255,.62);
  --stroke: rgba(15, 23, 42, .08);
  --shadow: 0 18px 50px rgba(2, 6, 23, .18);
  --shadow2: 0 10px 24px rgba(2, 6, 23, .14);
  --radius: 18px;
  --radius2: 24px;
  --t: 220ms;
}

*{box-sizing:border-box}
html,body{height:100%}
body{
  margin:0;
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial, "Noto Sans", "Liberation Sans", sans-serif;
  color:#0F172A;
  background: #0b2340;
}
#app{
  min-height:100vh;
  background: var(--bg);
  padding: 18px;
}

.shell{
  max-width: 980px;
  margin: 0 auto;
  min-height: calc(100vh - 36px);
  border-radius: var(--radius2);
  background: rgba(255,255,255,.14);
  border: 1px solid rgba(255,255,255,.22);
  box-shadow: var(--shadow);
  overflow:hidden;
  position:relative;
}

.topbar{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:12px;
  padding: 14px 14px;
  border-bottom: 1px solid rgba(255,255,255,.24);
  background: rgba(255,255,255,.16);
  backdrop-filter: blur(10px);
}

.brand{
  display:flex;
  align-items:center;
  gap:10px;
  min-width:0;
}
.brand .title{
  font-weight: 800;
  letter-spacing:.2px;
  white-space:nowrap;
}
.pills{
  display:flex;
  gap:8px;
  flex-wrap:wrap;
  justify-content:flex-end;
}
.pill{
  appearance:none;
  border: 1px solid rgba(15,23,42,.14);
  background: rgba(255,255,255,.58);
  color: rgba(15,23,42,.86);
  padding: 7px 10px;
  border-radius: 999px;
  cursor:pointer;
  transition: transform var(--t), background var(--t), border-color var(--t);
  font-weight: 650;
  font-size: 13px;
}
.pill:hover{ transform: translateY(-1px); background: rgba(255,255,255,.72); }
.pill[aria-current="page"]{
  border-color: rgba(31,164,255,.55);
  background: rgba(31,164,255,.16);
}

.main{
  display:grid;
  grid-template-columns: 1fr;
  padding: 16px;
  gap: 14px;
}

.card{
  border-radius: var(--radius);
  background: var(--panel);
  border: 1px solid var(--stroke);
  box-shadow: var(--shadow2);
  padding: 14px;
  backdrop-filter: blur(10px);
}

.grid{
  display:grid;
  grid-template-columns: repeat(2, minmax(0,1fr));
  gap: 12px;
}
@media (min-width: 760px){
  .grid{ grid-template-columns: repeat(3, minmax(0,1fr)); }
}

.tile{
  user-select:none;
  border-radius: 16px;
  background: rgba(255,255,255,.62);
  border: 1px solid rgba(15,23,42,.10);
  padding: 12px;
  cursor:pointer;
  transition: transform var(--t), background var(--t), border-color var(--t), box-shadow var(--t);
  min-height: 92px;
  display:flex;
  flex-direction:column;
  justify-content:space-between;
}
.tile:hover{
  transform: translateY(-2px);
  background: rgba(255,255,255,.74);
  box-shadow: 0 14px 28px rgba(2,6,23,.16);
}
.tile .h{
  font-weight: 820;
  letter-spacing: .2px;
}
.tile .d{
  font-size: 12.5px;
  color: rgba(15,23,42,.68);
  margin-top: 6px;
}
.tile.active{
  border-color: rgba(255,195,77,.55);
  background: rgba(255,195,77,.14);
}

.page{
  position:relative;
  min-height: 420px;
}
.pageHeader{
  display:flex;
  align-items:flex-start;
  justify-content:space-between;
  gap: 12px;
}
.pageHeader h1{
  margin:0;
  font-size: 22px;
  letter-spacing: .2px;
}
.pageHeader .meta{
  margin-top:6px;
  font-size: 13px;
  color: rgba(15,23,42,.70);
}
.kbtn{
  appearance:none;
  border: 1px solid rgba(15,23,42,.14);
  background: rgba(255,255,255,.68);
  border-radius: 12px;
  padding: 10px 12px;
  cursor:pointer;
  transition: transform var(--t), background var(--t);
  font-weight: 750;
}
.kbtn:hover{ transform: translateY(-1px); background: rgba(255,255,255,.78); }

.animIn{
  animation: in var(--t) ease-out both;
}
.animOut{
  animation: out var(--t) ease-in both;
}
@keyframes in{
  from{ opacity:0; transform: translateY(8px); filter: blur(2px); }
  to  { opacity:1; transform: translateY(0); filter: blur(0); }
}
@keyframes out{
  from{ opacity:1; transform: translateY(0); filter: blur(0); }
  to  { opacity:0; transform: translateY(-6px); filter: blur(2px); }
}

/* Ci Drawer */
.drawerBack{
  position:absolute;
  inset:0;
  background: rgba(2,6,23,.42);
  opacity:0;
  pointer-events:none;
  transition: opacity var(--t);
}
.drawer{
  position:absolute;
  top: 10px;
  right: 10px;
  width: min(520px, calc(100% - 20px));
  height: calc(100% - 20px);
  border-radius: 22px;
  background: rgba(255,255,255,.84);
  border: 1px solid rgba(255,255,255,.30);
  box-shadow: var(--shadow);
  transform: translateX(18px) scale(.98);
  opacity:0;
  pointer-events:none;
  transition: transform var(--t), opacity var(--t);
  backdrop-filter: blur(12px);
  display:flex;
  flex-direction:column;
  overflow:hidden;
}
.drawerTop{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:10px;
  padding: 12px 12px;
  border-bottom: 1px solid rgba(15,23,42,.10);
  background: rgba(255,255,255,.70);
}
.drawerTitle{
  display:flex; align-items:center; gap:10px;
  font-weight: 850;
}
.ciDot{
  width: 34px; height: 34px;
  border-radius: 999px;
  background: linear-gradient(35deg, rgba(31,164,255,.95), rgba(135,211,255,.95), rgba(255,195,77,.95));
  box-shadow: 0 10px 20px rgba(2,6,23,.18);
  border: 1px solid rgba(255,255,255,.55);
}
.drawerBody{
  padding: 12px;
  display:flex;
  flex-direction:column;
  gap:10px;
  min-height:0;
  flex:1;
}
.chatLog{
  flex:1;
  min-height: 180px;
  overflow:auto;
  border-radius: 16px;
  border: 1px solid rgba(15,23,42,.10);
  background: rgba(255,255,255,.62);
  padding: 10px;
}
.msg{ margin: 0 0 10px 0; }
.msg .r{
  font-size: 12px;
  color: rgba(15,23,42,.64);
  margin-bottom: 3px;
  font-weight: 750;
}
.msg .t{
  white-space: pre-wrap;
  line-height: 1.35;
}
.chatForm{
  display:flex;
  gap:10px;
}
.chatInput{
  flex:1;
  border-radius: 14px;
  border: 1px solid rgba(15,23,42,.14);
  background: rgba(255,255,255,.78);
  padding: 10px 12px;
  font-size: 14px;
  outline:none;
}
.chatSend{
  border-radius: 14px;
  border: 1px solid rgba(15,23,42,.14);
  background: rgba(31,164,255,.22);
  padding: 10px 12px;
  font-weight: 850;
  cursor:pointer;
}
.chatSend:hover{ background: rgba(31,164,255,.28); }

.drawerOpen .drawerBack{ opacity: 1; pointer-events:auto; }
.drawerOpen .drawer{ opacity:1; pointer-events:auto; transform: translateX(0) scale(1); }

/* Floating Ci button (mobile-first) */
.fab{
  position: fixed;
  right: 18px;
  bottom: 18px;
  width: 58px;
  height: 58px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,.55);
  background: linear-gradient(35deg, rgba(31,164,255,.95), rgba(135,211,255,.95), rgba(255,195,77,.95));
  box-shadow: 0 18px 40px rgba(2,6,23,.26);
  cursor:pointer;
  display:flex;
  align-items:center;
  justify-content:center;
  font-weight: 950;
  letter-spacing:.2px;
}
.fab:active{ transform: translateY(1px); }

.small{
  font-size: 12px;
  color: rgba(15,23,42,.64);
}
CSS

say "3) WRITE ui/app.js (router + transitions + Ci drawer chat)"
cat > "$UI_DIR/app.js" <<'JS'
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
JS

say "4) SMOKE TEST (local file presence + route strings)"
grep -q "#/kazkar" "$UI_DIR/app.js"
grep -q "Казкар" "$UI_DIR/app.js"
grep -q "✨Легенда сі" "$UI_DIR/app.js"
grep -q "ПоДія" "$UI_DIR/app.js"
grep -q "Настрій" "$UI_DIR/app.js"
grep -q "Маля" "$UI_DIR/app.js"
grep -q "Календар" "$UI_DIR/app.js"
grep -q "Галерея" "$UI_DIR/app.js"

say "5) RESTART UI ONLY (keep API running)"
kill_port(){
  local port="$1"
  if command -v ss >/dev/null 2>&1; then
    ss -ltnp 2>/dev/null | awk -v p=":$port" '$4 ~ p {print $NF}' \
      | sed -n 's/.*pid=\([0-9]\+\).*/\1/p' | sort -u \
      | while read -r pid; do [ -n "$pid" ] && kill -9 "$pid" 2>/dev/null || true; done
  fi
}
kill_port "$UI_PORT" || true

cd "$CIT_DIR"
nohup python3 -m http.server "$UI_PORT" --bind 127.0.0.1 -d "ui" > ".ui.$UI_PORT.log" 2>&1 &
echo $! > ".ui.$UI_PORT.pid"
sleep 0.7

say "6) VERIFY HTTP"
code(){ curl -m 2 -sS -o /dev/null -w "%{http_code}" "$1" 2>/dev/null || echo "ERR"; }
printf "UI     -> %s\n" "$(code "http://127.0.0.1:$UI_PORT/")"
printf "UI+API -> %s\n" "$(code "http://127.0.0.1:$UI_PORT/?api=http://127.0.0.1:$API_PORT")"
printf "API    -> %s\n" "$(code "http://127.0.0.1:$API_PORT/health")"

say "DONE"
echo "UI: http://127.0.0.1:$UI_PORT/#/"
echo "Kazkar: http://127.0.0.1:$UI_PORT/#/kazkar"
echo "Legend: http://127.0.0.1:$UI_PORT/#/legend"
echo "Ci Drawer uses api= param if provided"
