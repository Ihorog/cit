#!/usr/bin/env bash
set -euo pipefail
cd ~/cimeika/cit
rclone lsf keenetic_webdav:/ --max-depth 2 | head -n 200
