#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

# ===== FIXED PATHS =====
CIT_DIR="/data/data/com.termux/files/home/cimeika/cit"
PYFILE="$CIT_DIR/server/cit_server.py"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP="$CIT_DIR/server/cit_server.py.bak.${TS}"

say(){ printf "\n=== %s ===\n" "$1"; }

say "0) PRECHECK (absolute paths)"
echo "CIT_DIR : $CIT_DIR"
echo "PYFILE  : $PYFILE"

if [ ! -d "$CIT_DIR" ]; then
  echo "ERR: CIT_DIR not found: $CIT_DIR"
  exit 1
fi

if [ ! -f "$PYFILE" ]; then
  echo "ERR: PYFILE not found: $PYFILE"
  echo "HINT: listing $CIT_DIR/server/"
  ls -la "$CIT_DIR/server" || true
  exit 1
fi

say "1) BACKUP"
cp -f "$PYFILE" "$BACKUP"
echo "BACKUP -> $BACKUP"

say "2) PATCH (python, absolute path only)"
python3 - <<PY
from pathlib import Path

PYFILE = Path(r"$PYFILE")
text = PYFILE.read_text(encoding="utf-8")

# --- PLACEHOLDER: тут має бути твій реальний patch-алгоритм ---
# Якщо ти вже маєш готовий text2 у своєму патчі — встав його логіку сюди.
# Для контролю зараз робимо "no-op" перевірку, що файл читається/пишеться.
text2 = text

PYFILE.write_text(text2, encoding="utf-8")
print("OK: patched", PYFILE)
PY

say "3) DONE"
