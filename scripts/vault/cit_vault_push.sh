#!/usr/bin/env bash
set -euo pipefail
cd ~/cimeika/cit

# Push local vault -> WebDAV
rclone sync vault/local keenetic_webdav:/ \
  --create-empty-src-dirs \
  --cache-dir vault/cache \
  --log-file logs/rclone_webdav_push.log \
  --log-level INFO

echo "OK: PUSH local -> WebDAV"
