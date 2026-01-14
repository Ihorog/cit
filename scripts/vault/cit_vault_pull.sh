#!/usr/bin/env bash
set -euo pipefail
cd ~/cimeika/cit
# Pull from WebDAV -> local vault
rclone sync keenetic_webdav:/ vault/local \
  --create-empty-src-dirs \
  --cache-dir vault/cache \
  --log-file logs/rclone_webdav_pull.log \
  --log-level INFO
echo "OK: PULL webdav -> vault/local"
