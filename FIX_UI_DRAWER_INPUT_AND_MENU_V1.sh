#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

CIT_DIR="/data/data/com.termux/files/home/cimeika/cit"
UI_DIR="$CIT_DIR/ui"
UI_PORT="${UI_PORT:-8010}"
API_PORT="${API_PORT:-8790}"
TS="$(date -u +%Y%m%dT%H%M%SZ)"

say(){ printf "\n=== %s ===\n" "$1"; }
code(){ curl -m 2 -sS -o /dev/null -w "%{http_code}" "$1" 2>/dev/null || echo "ERR"; }

say "0) PRECHECK"
[ -d "$UI_DIR" ] || { echo "UI dir missing: $UI_DIR"; exit 1; }
[ -f "$UI_DIR/index.html" ] || { echo "Missing: $UI_DIR/index.html"; exit 1; }

say "1) BACKUP"
mkdir -p "$CIT_DIR/_bak_ui/$TS"
cp -f "$UI_DIR/index.html"  "$CIT_DIR/_bak_ui/$TS/index.html"
cp -f "$UI_DIR/styles.css"  "$CIT_DIR/_bak_ui/$TS/styles.css" 2>/dev/null || true
cp -f "$UI_DIR/app.js"      "$CIT_DIR/_bak_ui/$TS/app.js" 2>/dev/null || true
echo "backup -> $CIT_DIR/_bak_ui/$TS"

say "2) PATCH CSS (drawer fixed input + safe areas + scroll)"
touch "$UI_DIR/styles.css"

# Append only once (guard marker)
if ! grep -q "CIMEIKA_FIX_DRAWER_V1" "$UI_DIR/styles.css"; then
cat >> "$UI_DIR/styles.css" <<'CSS'

/* === CIMEIKA_FIX_DRAWER_V1 ===
   Fix: chat drawer too tall, input offscreen; make body scroll sane; add safe-area; keep input visible.
*/
html, body { height: 100%; }
body { overflow: hidden; }

/* Generic drawer selectors (supports several id/class variants) */
#ciDrawer, #ci-drawer, #drawer, .ciDrawer, .ci-drawer, .drawer, [data-ci-drawer], [data-drawer]{
  max-height: 92vh;
  height: auto;
  overflow: hidden;
}

/* Inner content should scroll */
#ciDrawer .drawer-body, #ci-drawer .drawer-body, #drawer .drawer-body, .drawer .drawer-body,
#ciDrawer .content, #ci-drawer .content, #drawer .content, .drawer .content,
#ciDrawer [data-body], #ci-drawer [data-body], #drawer [data-body], .drawer [data-body]{
  overflow: auto;
  -webkit-overflow-scrolling: touch;
  max-height: calc(92vh - 84px);
  padding-bottom: calc(86px + env(safe-area-inset-bottom));
}

/* Chat list scroll area */
#ciDrawer .chat-log, #ci-drawer .chat-log, #drawer .chat-log, .drawer .chat-log,
#ciDrawer .messages, #ci-drawer .messages, #drawer .messages, .drawer .messages,
#ciDrawer [data-chat-log], #ci-drawer [data-chat-log], #drawer [data-chat-log], .drawer [data-chat-log]{
  overflow: auto;
  -webkit-overflow-scrolling: touch;
  max-height: calc(92vh - 140px);
  padding-bottom: 16px;
}

/* Input bar: sticky bottom, always visible */
#ciDrawer .chat-input, #ci-drawer .chat-input, #drawer .chat-input, .drawer .chat-input,
#ciDrawer .inputbar, #ci-drawer .inputbar, #drawer .inputbar, .drawer .inputbar,
#ciDrawer form, #ci-drawer form, #drawer form, .drawer form,
#ciDrawer [data-input], #ci-drawer [data-input], #drawer [data-input], .drawer [data-input]{
  position: sticky;
  bottom: 0;
  z-index: 50;
  backdrop-filter: blur(10px);
  padding-bottom: env(safe-area-inset-bottom);
}

/* Inputs should not expand beyond drawer width */
#ciDrawer textarea, #ci-drawer textarea, #drawer textarea, .drawer textarea,
#ciDrawer input[type="text"], #ci-drawer input[type="text"], #drawer input[type="text"], .drawer input[type="text"]{
  max-width: 100%;
}

/* When virtual keyboard opens (Android), allow breathing space */
@supports (height: 100dvh){
  #ciDrawer, #ci-drawer, #drawer, .drawer, [data-ci-drawer], [data-drawer]{ max-height: 92dvh; }
  #ciDrawer .drawer-body, #ci-drawer .drawer-body, #drawer .drawer-body, .drawer .drawer-body{
    max-height: calc(92dvh - 84px);
  }
}

/* Hide duplicated navigation block (the one titled "Навігація") */
section[data-dup-nav="1"]{ display:none !important; }

CSS
fi

say "3) PATCH JS (mark duplicate 'Навігація' section, keep only top navigation)"
# We patch ui/app.js if exists; otherwise patch inline script in index.html
if [ -f "$UI_DIR/app.js" ]; then
  TARGET="$UI_DIR/app.js"
else
  TARGET="$UI_DIR/index.html"
fi

if ! grep -q "CIMEIKA_FIX_DUP_NAV_V1" "$TARGET"; then
cat >> "$TARGET" <<'JS'

/* === CIMEIKA_FIX_DUP_NAV_V1 ===
   Remove duplicated nav block titled "Навігація" (cards) if top nav already exists.
   Also tries to ensure drawer scroll areas compute correctly.
*/
(function(){
  function textNorm(s){ return (s||"").replace(/\s+/g," ").trim().toLowerCase(); }

  function markDupNav(){
    const candidates = Array.from(document.querySelectorAll("h1,h2,h3,div,span,p"));
    const navHead = candidates.find(el => textNorm(el.textContent) === "навігація");
    if(!navHead) return;

    // Find nearest section/container
    let box = navHead;
    for(let i=0;i<6 && box;i++){
      if(box.tagName && (box.tagName.toLowerCase()==="section" || box.classList.contains("card") || box.classList.contains("panel"))) break;
      box = box.parentElement;
    }
    if(!box) box = navHead.parentElement;

    // Only hide if there is already a top navigation row with module links
    const topHasLinks = Array.from(document.querySelectorAll("a,button"))
      .some(x => ["казкар","легенда","подія","настрій","маля","календар","галерея","ci"].includes(textNorm(x.textContent)));

    if(topHasLinks && box){
      box.setAttribute("data-dup-nav","1");
    }
  }

  function fixDrawerHeights(){
    const drawers = document.querySelectorAll("#ciDrawer,#ci-drawer,#drawer,.drawer,.ci-drawer,[data-ci-drawer],[data-drawer]");
    drawers.forEach(d=>{
      // force repaint for mobile
      d.style.maxHeight = "92vh";
    });
  }

  function runAll(){
    try{ markDupNav(); }catch(e){}
    try{ fixDrawerHeights(); }catch(e){}
  }

  if(document.readyState==="loading"){
    document.addEventListener("DOMContentLoaded", runAll);
  } else runAll();

  window.addEventListener("hashchange", runAll, {passive:true});
  window.addEventListener("resize", runAll, {passive:true});
})();
JS
fi

say "4) STOP (ports ${API_PORT}/${UI_PORT})"
pkill -f "cit_server.py" 2>/dev/null || true
pkill -f "http.server ${UI_PORT}" 2>/dev/null || true
sleep 0.6

say "5) START API"
cd "$CIT_DIR"
nohup python3 server/cit_server.py > ".api.${API_PORT}.log" 2>&1 &
echo $! > ".api.${API_PORT}.pid"
sleep 0.9

say "6) START UI"
nohup python3 -m http.server "$UI_PORT" --bind 127.0.0.1 -d "ui" > ".ui.${UI_PORT}.log" 2>&1 &
echo $! > ".ui.${UI_PORT}.pid"
sleep 0.8

say "7) VERIFY HTTP"
printf "UI     -> %s\n" "$(code "http://127.0.0.1:${UI_PORT}/")"
printf "UI+API -> %s\n" "$(code "http://127.0.0.1:${UI_PORT}/?api=http://127.0.0.1:${API_PORT}")"
printf "API    -> %s\n" "$(code "http://127.0.0.1:${API_PORT}/health")"
printf "REG    -> %s\n" "$(code "http://127.0.0.1:${API_PORT}/registry")"

say "8) CHECK PATCH PRESENT"
grep -q "CIMEIKA_FIX_DRAWER_V1" "$UI_DIR/styles.css" && echo "CSS patch: OK" || echo "CSS patch: MISSING"
grep -q "CIMEIKA_FIX_DUP_NAV_V1" "$TARGET" && echo "JS patch: OK" || echo "JS patch: MISSING"

say "9) READY"
echo "UI: http://127.0.0.1:${UI_PORT}/#/"
echo "Malya: http://127.0.0.1:${UI_PORT}/#/malya"
echo "Kazkar: http://127.0.0.1:${UI_PORT}/#/kazkar"
echo "Legend: http://127.0.0.1:${UI_PORT}/#/legend"
echo "Logs: $CIT_DIR/.ui.${UI_PORT}.log , $CIT_DIR/.api.${API_PORT}.log"
