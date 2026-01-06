#!/data/data/com.termux/files/usr/bin/bash
set -e

ROOT="/data/data/com.termux/files/home/cimeika/cit"
UI="$ROOT/ui"
ASSETS="$UI/assets"
LOG="$ROOT/logs"

cd "$ROOT" || exit 1
mkdir -p "$ASSETS" "$LOG"

echo "=== [0] STOP old UI server (best-effort) ==="
pkill -f "python -m http.server 8010" 2>/dev/null || true

echo "=== [1] ENSURE ASSETS (ci.png) ==="
TARGET="$ASSETS/ci.png"
TMP="$ASSETS/.ci.tmp"

# 1) Try GitHub Contents API (resolves moved/renamed paths)
python - <<'PY' > "$TMP" || true
import json, urllib.request, re
url = "https://api.github.com/repos/Ihorog/media/contents/"
req = urllib.request.Request(url, headers={"User-Agent":"CIT-UIv2"})
data = json.loads(urllib.request.urlopen(req, timeout=15).read().decode("utf-8"))
cands=[]
for it in data:
    if it.get("type")!="file": 
        continue
    name = it.get("name","")
    if not re.search(r'\.(png|webp|jpg|jpeg)$', name, re.I):
        continue
    if re.search(r'\bci\b', name, re.I) or re.search(r'ci', name, re.I):
        cands.append(it.get("download_url"))
print(cands[0] if cands else "")
PY

DL_URL="$(cat "$TMP" 2>/dev/null || true)"
rm -f "$TMP" 2>/dev/null || true

if [ -n "${DL_URL:-}" ]; then
  echo "DOWNLOAD: $DL_URL"
  if curl -fsSL --max-time 25 "$DL_URL" -o "$TARGET"; then
    echo "OK: saved $TARGET"
  else
    echo "WARN: download failed"
  fi
fi

# 2) If still missing/empty — search locally and copy
if [ ! -s "$TARGET" ]; then
  FOUND="$(find "$ROOT" -maxdepth 6 -type f \( -iname 'Ci.png' -o -iname 'ci.png' -o -iname '*ci*.png' \) 2>/dev/null | head -n 1 || true)"
  if [ -n "${FOUND:-}" ]; then
    cp -f "$FOUND" "$TARGET"
    echo "OK: copied from $FOUND -> $TARGET"
  fi
fi

# 3) If still missing — create fallback SVG (marked fallback)
FALLBACK="$ASSETS/ci_fallback.svg"
if [ ! -s "$TARGET" ]; then
  cat > "$FALLBACK" <<'SVG'
<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#1FA4FF"/>
      <stop offset="0.5" stop-color="#87D3FF"/>
      <stop offset="1" stop-color="#FFC34D"/>
    </linearGradient>
  </defs>
  <rect width="100%" height="100%" rx="96" fill="rgba(0,0,0,0)"/>
  <circle cx="256" cy="256" r="190" fill="url(#g)" opacity="0.18"/>
  <circle cx="256" cy="256" r="150" fill="url(#g)" opacity="0.25"/>
  <text x="50%" y="52%" text-anchor="middle" font-family="system-ui,Segoe UI,Arial" font-size="140" fill="url(#g)" font-weight="700">Ci</text>
  <text x="50%" y="78%" text-anchor="middle" font-family="system-ui,Segoe UI,Arial" font-size="22" fill="#64748B">fallback</text>
</svg>
SVG
  echo "FALLBACK: $FALLBACK"
fi

echo "=== [2] PATCH index.html to use ci.png OR fallback ==="
# Replace any src/href to Ci.png/ci.png with assets/ci.png; if missing, use JS swap to fallback.
INDEX="$UI/index.html"
if [ -f "$INDEX" ]; then
  # normalize references
  sed -i -E "s#(src|href)=\"([^\"]*(Ci|ci)\.png)\"#\\1=\"assets/ci.png\"#g" "$INDEX" || true

  # inject fallback swapper once
  if ! grep -q "CI_LOGO_FALLBACK_SWAP" "$INDEX"; then
    sed -i -E "s#</body>#<script>/*CI_LOGO_FALLBACK_SWAP*/(function(){var img=document.querySelectorAll('img');for(var i=0;i<img.length;i++){var el=img[i];if((el.getAttribute('src')||'').indexOf('assets/ci.png')!==-1){el.onerror=function(){this.src='assets/ci_fallback.svg'};}}\n})();</script>\n</body>#g" "$INDEX" || true
  fi
fi

echo "=== [3] START UI :8010 ==="
cd "$UI" || exit 1
nohup python -m http.server 8010 --bind 127.0.0.1 > "$LOG/ui_8010.log" 2>&1 &
sleep 0.4

echo "=== [4] VERIFY ==="
echo -n "UI: "; curl -sS --max-time 2 -I http://127.0.0.1:8010/ | head -n 1 || echo "UI DOWN"
echo -n "ASSET(ci.png): "; curl -sS --max-time 2 -I http://127.0.0.1:8010/assets/ci.png | head -n 1 || echo "NO ci.png"
echo -n "ASSET(fallback): "; curl -sS --max-time 2 -I http://127.0.0.1:8010/assets/ci_fallback.svg | head -n 1 || echo "NO fallback"
echo
echo "READY: http://127.0.0.1:8010/"
