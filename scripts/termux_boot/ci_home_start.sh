#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

cd "$HOME/cit"

# Підтягуємо .env якщо є
[ -f "$HOME/.ci_home.env" ] && set -a && . "$HOME/.ci_home.env" && set +a || true

# 1) Recovery (idempotent)
bash home_node/ci_recovery_full.sh

# 2) Start sync loop (120s)
LOCAL_BASE="${LOCAL_BASE:-$HOME/cimeika}"
mkdir -p "$LOCAL_BASE/bin" "$LOCAL_BASE/logs"
cat > "$LOCAL_BASE/bin/ci_sync_loop.sh" <<'LOOP'
#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
while true; do
  REMOTE_NAME="${REMOTE_NAME:-keenetik}" REMOTE_ROOT="${REMOTE_ROOT:-ci}" LOCAL_BASE="${LOCAL_BASE:-$HOME/cimeika}" \
    bash "$HOME/cit/home_node/ci_sync_loop.sh" >>"$LOCAL_BASE/logs/ci_sync_loop.log" 2>&1 || true
  sleep 120
done
LOOP
chmod +x "$LOCAL_BASE/bin/ci_sync_loop.sh"

if pgrep -f "ci_sync_loop.sh" >/dev/null 2>&1; then
  echo "SYNC_LOOP_ALREADY_RUNNING"
else
  nohup bash "$LOCAL_BASE/bin/ci_sync_loop.sh" >/dev/null 2>&1 &
fi

echo "OK"
