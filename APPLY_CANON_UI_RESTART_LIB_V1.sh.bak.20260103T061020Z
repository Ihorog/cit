#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

cd /data/data/com.termux/files/home/cimeika/cit || exit 1

TS="$(date -u +%Y%m%dT%H%M%SZ)"
LOG="logs/apply_canon_ui_restart_lib_${TS}.log"
mkdir -p logs bin

echo "== APPLY_CANON_UI_RESTART_LIB_V1 ==" | tee "$LOG"
echo "TS=$TS" | tee -a "$LOG"
echo "ROOT=$(pwd)" | tee -a "$LOG"

# 1) Write canonical library
cat > bin/ui_restart.sh <<'EOF'
#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ui_restart() {
  local UI_PORT="${UI_PORT:-8010}"
  local UI_HOST="${UI_HOST:-127.0.0.1}"
  local ROOT="${UI_ROOT:-/data/data/com.termux/files/home/cimeika/cit/ui}"
  local LOGDIR="${UI_LOGDIR:-/data/data/com.termux/files/home/cimeika/cit/logs}"
  local LOGFILE="$LOGDIR/ui_${UI_PORT}.log"

  mkdir -p "$LOGDIR" || return 1

  local pids
  pids="$(ps -A -o pid,args | grep -E "python -m http\.server ${UI_PORT}\b" | grep -v grep | awk '{print $1}' || true)"
  if [ -n "${pids:-}" ]; then
    for pid in $pids; do kill -9 "$pid" 2>/dev/null || true; done
  fi
  sleep 0.2

  cd "$ROOT" || return 2
  nohup python -m http.server "$UI_PORT" --bind "$UI_HOST" > "$LOGFILE" 2>&1 &
  sleep 0.4

  curl -sS --max-time 2 -I "http://$UI_HOST:$UI_PORT/" | head -n 1
}
EOF
chmod +x bin/ui_restart.sh
echo "OK: bin/ui_restart.sh written" | tee -a "$LOG"

# 2) Patch all .sh that reference http.server 8010
FILES="$(grep -RIl --include='*.sh' -E 'python -m http\.server 8010|http\.server 8010' . || true)"
if [ -z "$FILES" ]; then
  echo "NO *.sh files referencing http.server 8010 (nothing to patch)" | tee -a "$LOG"
else
  echo "FILES_TO_PATCH:" | tee -a "$LOG"
  echo "$FILES" | tee -a "$LOG"

  while IFS= read -r f; do
    [ -f "$f" ] || continue
    cp -f "$f" "$f.bak.$TS"

    FILE="$f" python - <<'PY'
import os, re
path=os.environ["FILE"]
s=open(path,"r",encoding="utf-8",errors="ignore").read()

src_line='source "/data/data/com.termux/files/home/cimeika/cit/bin/ui_restart.sh"'
if src_line not in s:
    if s.startswith("#!"):
        parts=s.splitlines(True)
        parts.insert(1, src_line+"\n")
        s="".join(parts)
    else:
        s=src_line+"\n"+s

# replace restart commands with ui_restart
s=re.sub(r'(?m)^\s*nohup\s+python\s+-m\s+http\.server\s+8010\b.*\n', 'ui_restart\n', s)
s=re.sub(r'(?m)^\s*python\s+-m\s+http\.server\s+8010\b.*\n', 'ui_restart\n', s)
s=re.sub(r'(?m)^\s*pkill\s+-f\s+["\']python\s+-m\s+http\.server\s+8010["\'].*\n', '', s)

open(path,"w",encoding="utf-8").write(s)
print("PATCHED", path)
PY

    echo "PATCHED: $f (backup: $f.bak.$TS)" | tee -a "$LOG"
  done <<< "$FILES"
fi

# 3) Test: run ui_restart now
echo "" | tee -a "$LOG"
echo "== TEST ui_restart ==" | tee -a "$LOG"
source "/data/data/com.termux/files/home/cimeika/cit/bin/ui_restart.sh"
ui_restart | tee -a "$LOG" || true

echo "" | tee -a "$LOG"
echo "== PROCS ==" | tee -a "$LOG"
ps -A -o pid,args | grep -E "python -m http\.server 8010\b" | grep -v grep | tee -a "$LOG" || true

echo "" | tee -a "$LOG"
echo "DONE. LOG: $LOG" | tee -a "$LOG"
