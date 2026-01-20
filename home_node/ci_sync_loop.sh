#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

REMOTE_NAME="${REMOTE_NAME:-keenetik}"
REMOTE_ROOT="${REMOTE_ROOT:-ci}"
LOCAL_BASE="${LOCAL_BASE:-$HOME/cimeika}"
LOG="${LOCAL_BASE}/logs/sync.log"

mkdir -p "${LOCAL_BASE}/logs" "${LOCAL_BASE}/db" "${LOCAL_BASE}/data/texts" "${LOCAL_BASE}/data/gallery" "${LOCAL_BASE}/data/voice"

ts(){ date -u +%Y-%m-%dT%H:%M:%SZ; }

echo "SYNC_START $(ts)" >> "$LOG"

# DB
[ -f "${LOCAL_BASE}/db/cimeika.db" ] && rclone copy "${LOCAL_BASE}/db/cimeika.db" "${REMOTE_NAME}:${REMOTE_ROOT}/db" >/dev/null || true

# logs
rclone copy "${LOCAL_BASE}/logs" "${REMOTE_NAME}:${REMOTE_ROOT}/logs" --include "*.log" >/dev/null || true
rclone copy "${LOCAL_BASE}/logs" "${REMOTE_NAME}:${REMOTE_ROOT}/logs" --include "*.stdout.log" >/dev/null || true

# texts/gallery/voice (як каркас)
rclone mkdir "${REMOTE_NAME}:${REMOTE_ROOT}/texts" >/dev/null || true
rclone mkdir "${REMOTE_NAME}:${REMOTE_ROOT}/gallery" >/dev/null || true
rclone mkdir "${REMOTE_NAME}:${REMOTE_ROOT}/voice" >/dev/null || true

echo "SYNC_DONE  $(ts)" >> "$LOG"
