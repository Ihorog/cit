#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

echo "[1/9] cd ~"
cd ~

echo "[2/9] пакети"
pkg update -y >/dev/null || true
pkg install -y rclone curl coreutils openssh python >/dev/null

# === Параметри (редагуються через env або .env) ===
REMOTE_NAME="${REMOTE_NAME:-keenetik}"
WEBDAV_URL="${WEBDAV_URL:-https://cimeiniy.keenetic.link/webdav/}"
WEBDAV_USER="${WEBDAV_USER:-Cimeika}"
WEBDAV_PASS="${WEBDAV_PASS:-}"

LOCAL_BASE="${LOCAL_BASE:-$HOME/cimeika}"
LOCAL_DB="${LOCAL_DB:-$HOME/cimeika/db/cimeika.db}"

echo "[3/9] rclone remote: ${REMOTE_NAME}"
mkdir -p "$HOME/.config/rclone"
if ! rclone listremotes | grep -q "^${REMOTE_NAME}:"; then
  if [ -z "${WEBDAV_PASS}" ]; then
    echo "ERROR: WEBDAV_PASS is empty. Export WEBDAV_PASS and rerun."
    exit 2
  fi

  rclone config create "${REMOTE_NAME}" webdav \
    url "${WEBDAV_URL%/}/" \
    vendor other \
    user "${WEBDAV_USER}" \
    pass "${WEBDAV_PASS}" >/dev/null
fi

echo "[4/9] WebDAV check (HTTP 207)"
# PROPFIND -> 207 очікувано
code="$(curl -s -o /dev/null -w '%{http_code}' -u "${WEBDAV_USER}:${WEBDAV_PASS}" -X PROPFIND "${WEBDAV_URL%/}/" -H 'Depth: 1' || true)"
if [ "${code}" != "207" ]; then
  echo "ERROR: WebDAV PROPFIND expected 207, got ${code}"
  exit 3
fi

echo "[5/9] ensure vault структури"
rclone mkdir "${REMOTE_NAME}:ci" >/dev/null || true
for d in backups credentials db gallery logs texts voice test; do
  rclone mkdir "${REMOTE_NAME}:ci/${d}" >/dev/null || true
done

echo "[6/9] I/O test"
tmpf="$HOME/ci_test.txt"
echo "ci test $(date -u)" > "$tmpf"
rclone copy "$tmpf" "${REMOTE_NAME}:ci/logs" >/dev/null
rclone deletefile "${REMOTE_NAME}:ci/logs/ci_test.txt" >/dev/null || true
rm -f "$tmpf" || true

echo "[7/9] локальна структура Ci"
mkdir -p "$LOCAL_BASE/db" "$LOCAL_BASE/data/texts" "$LOCAL_BASE/data/gallery" "$LOCAL_BASE/data/voice" "$LOCAL_BASE/logs" "$LOCAL_BASE/bin"
touch "$LOCAL_DB"
echo "LOCAL_DB_OK ${LOCAL_DB}"

echo "[8/9] старт ci_core (background)"
CI_HOST="${CI_HOST:-0.0.0.0}"
CI_PORT="${CI_PORT:-8787}"

# якщо вже працює — не стартуємо повторно
if pgrep -f "python.*ci_core.py" >/dev/null 2>&1; then
  echo "CI_CORE_ALREADY_RUNNING"
else
  nohup env CI_HOST="$CI_HOST" CI_PORT="$CI_PORT" python "$HOME/cit/home_node/ci_core.py" \
    >"$LOCAL_BASE/logs/ci_core.stdout.log" 2>&1 &
  sleep 1
fi

echo "[9/9] контрольний зліпок"
echo "---"
echo "REMOTE=${REMOTE_NAME}:"
echo "WEBDAV=${WEBDAV_URL%/}/"
echo "USER=${WEBDAV_USER}"
echo "LOCAL_BASE=${LOCAL_BASE}"
echo "LOCAL_DB=${LOCAL_DB}"
echo "---"
rclone lsd "${REMOTE_NAME}:ci" || true
rclone size "${REMOTE_NAME}:ci" || true
echo "OK"
