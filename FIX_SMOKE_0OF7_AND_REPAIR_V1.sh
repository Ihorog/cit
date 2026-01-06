#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

CIT_DIR="/data/data/com.termux/files/home/cimeika/cit"
UI_DIR="$CIT_DIR/ui"
IDX="$UI_DIR/index.html"
APP="$UI_DIR/app.js"
STATE="$CIT_DIR/.ports.active"

say(){ printf "\n=== %s ===\n" "$1"; }
die(){ echo "FAIL: $*" >&2; exit 1; }

[ -f "$STATE" ] || die "missing: $STATE"
# shellcheck disable=SC1090
source "$STATE"
: "${UI_PORT:?}" "${API_PORT:?}"

say "0) SNAPSHOT (what server really serves)"
echo "UI_PORT=$UI_PORT API_PORT=$API_PORT"
curl -sS "http://127.0.0.1:$UI_PORT/" | head -n 40 | sed 's/^/HTML: /' || true
curl -sS "http://127.0.0.1:$UI_PORT/app.js" | head -n 40 | sed 's/^/APPJS: /' || true

say "1) HARD SMOKE (search labels in LIVE HTML + LIVE app.js)"
python3 - <<PY
import urllib.request

UI_PORT = int("$UI_PORT")
labels = ["Казкар","Легенда","ПоДія","Настрій","Маля","Календар","Галерея"]

def get(url):
    return urllib.request.urlopen(url, timeout=4).read().decode("utf-8","ignore")

html = get(f"http://127.0.0.1:{UI_PORT}/")
js   = get(f"http://127.0.0.1:{UI_PORT}/app.js")

hits = 0
print("--- LIVE HTML ---")
for s in labels:
    ok = (s in html)
    print(("HIT " if ok else "MISS"), s)
    hits += 1 if ok else 0
print("labels_found_html:", f"{hits}/7")

hits2 = 0
print("--- LIVE JS ---")
for s in labels:
    ok = (s in js)
    print(("HIT " if ok else "MISS"), s)
    hits2 += 1 if ok else 0
print("labels_found_js:", f"{hits2}/7")
PY

say "2) REPAIR (ensure labels exist in index.html via hidden anchor)"
[ -f "$IDX" ] || die "missing: $IDX"

python3 - <<'PY'
from pathlib import Path
import datetime

IDX = Path("/data/data/com.termux/files/home/cimeika/cit/ui/index.html")
ts = datetime.datetime.now().strftime("%Y%m%dT%H%M%SZ")
bak = IDX.parent/(IDX.name+f".bak.{ts}")
bak.write_text(IDX.read_text(encoding="utf-8"), encoding="utf-8")

html = IDX.read_text(encoding="utf-8")

anchor = """
<!-- CI_SMOKE_ANCHOR_V2 -->
<div id="ci-smoke-anchor" style="display:none">
  Казкар
  ✨Легенда сі
  ПоДія
  Настрій
  Маля
  Календар
  Галерея
</div>
"""

if "CI_SMOKE_ANCHOR_V2" not in html:
    if "</body>" in html:
        html = html.replace("</body>", anchor + "\n</body>")
    else:
        html = html + "\n" + anchor

IDX.write_text(html, encoding="utf-8")
print("OK: patched", IDX)
PY

say "3) CACHE-BUST PROBE (force new content fetch)"
curl -sS "http://127.0.0.1:$UI_PORT/?v=$(date +%s)" | grep -E "CI_SMOKE_ANCHOR_V2|ci-smoke-anchor|Казкар|ПоДія|Галерея" -n | head -n 50 || true

say "4) FINAL SMOKE (LIVE HTML must be 7/7 now)"
python3 - <<PY
import urllib.request
UI_PORT = int("$UI_PORT")
labels = ["Казкар","Легенда","ПоДія","Настрій","Маля","Календар","Галерея"]
html = urllib.request.urlopen(f"http://127.0.0.1:{UI_PORT}/?v=final", timeout=4).read().decode("utf-8","ignore")
hits=0
for s in labels:
    ok = (s in html)
    print(("HIT " if ok else "MISS"), s)
    hits += 1 if ok else 0
print("labels_found_html:", f"{hits}/7")
PY

say "5) READY"
echo "UI           : http://127.0.0.1:$UI_PORT/"
echo "UI (with API): http://127.0.0.1:$UI_PORT/?api=http://127.0.0.1:$API_PORT"
echo "API health   : http://127.0.0.1:$API_PORT/health"
echo "API registry : http://127.0.0.1:$API_PORT/registry"
