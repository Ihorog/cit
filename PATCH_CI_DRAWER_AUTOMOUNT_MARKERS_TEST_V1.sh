#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

UI="http://127.0.0.1:8010"
JS="ui/assets/ci_drawer.js"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
LOG="logs/audit/patch_drawer_automount_${TS}.log"
OUT="logs/audit/static_drawer_audit_FIXED_${TS}.md"
mkdir -p logs/audit

[ -f "$JS" ] || { echo "NO FILE: $JS"; exit 1; }
cp -f "$JS" "$JS.bak.$TS"

python - <<'PY' | tee "$LOG"
import re
path="ui/assets/ci_drawer.js"
s=open(path,"r",encoding="utf-8",errors="ignore").read()

s = s.replace(
  "const overlay = el('div', { class:'drawerOverlay', id:'ciOverlay' });",
  "const overlay = el('div', { class:'drawerOverlay', id:'ciOverlay', 'data-ci-drawer':'overlay', 'data-ci-registry': `${API}/registry` });"
)
s = s.replace(
  "const drawer  = el('div', { class:'drawer', id:'ciDrawer' });",
  "const drawer  = el('div', { class:'drawer', id:'ciDrawer', 'data-ci-drawer':'panel', 'data-ci-registry': `${API}/registry` });"
)

if "CIT_CANON_AUTOMOUNT_V1" not in s:
  hook = r"""
  // === CIT_CANON_AUTOMOUNT_V1 ===
  function canonAutoMount(){
    try{
      if (document.getElementById('ciDrawer')) return; // already mounted
      mountDrawer();
    }catch(e){}
  }
  if (document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', canonAutoMount);
  } else {
    canonAutoMount();
  }
  // === /CIT_CANON_AUTOMOUNT_V1 ===
"""
  s = re.sub(r"\n\s*window\.CI_MOUNT_DRAWER\s*=\s*mountDrawer;\s*\n\}\)\(\);\s*$",
             "\n  window.CI_MOUNT_DRAWER = mountDrawer;\n" + hook + "\n})();\n", s, flags=re.S)

open(path,"w",encoding="utf-8").write(s)
print("PATCH_OK")
PY

# restart UI (canon)
source "/data/data/com.termux/files/home/cimeika/cit/bin/ui_restart.sh"
ui_restart | tee -a "$LOG" || true

PAGES=( "/" "/pages/ci.html" "/pages/kazkar.html" "/pages/legend_ci.html" "/pages/podija.html" "/pages/nastrij.html" "/pages/malya.html" "/pages/calendar.html" "/pages/gallery.html" )

echo "# Static Drawer Audit (FIXED patterns)" > "$OUT"
echo "" >> "$OUT"
echo "- Time (UTC): $TS" >> "$OUT"
echo "- UI: $UI" >> "$OUT"
echo "" >> "$OUT"

echo "## 1) Page includes" >> "$OUT"
echo '| page | http | ci_drawer.js |' >> "$OUT"
echo '|---|---:|---:|' >> "$OUT"
for p in "${PAGES[@]}"; do
  code="$(curl -s -o /dev/null -w "%{http_code}" "$UI$p" || echo "000")"
  html="$(curl -sS "$UI$p" 2>/dev/null | head -c 400000)"
  inc_js="$(printf "%s" "$html" | grep -Eci 'ci_drawer\.js' || true)"
  echo "| \`$p\` | $code | $inc_js |" >> "$OUT"
done
echo "" >> "$OUT"

echo "## 2) Drawer JS markers (REAL strings)" >> "$OUT"
echo '| marker | found |' >> "$OUT"
echo '|---|---:|' >> "$OUT"
for m in "CIT_CANON_AUTOMOUNT_V1" "DOMContentLoaded" "readyState" "data-ci-drawer" "id:'ciDrawer'" "id:'ciOverlay'" "class:'drawer'" "class:'drawerOverlay'"; do
  hit="$(grep -Fci "$m" "$JS" 2>/dev/null || true)"
  echo "| \`$m\` | $hit |" >> "$OUT"
done

echo "" >> "$OUT"
echo "DONE: $OUT"
sed -n '1,220p' "$OUT"
