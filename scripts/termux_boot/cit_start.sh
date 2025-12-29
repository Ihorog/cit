#!/data/data/com.termux/files/usr/bin/bash

# Script to start the CIT server on boot via Termux Boot.
#
# Copy this script into $HOME/.termux/boot/ if you have Termux Boot
# installed.  It will run automatically when your device boots.

set -e

# Change to the location where the repository is cloned
APP_DIR="$HOME/cit"
cd "$APP_DIR" || exit 1

# Export any required environment variables
if [ -f .env ]; then
  # shellcheck source=/dev/null
  . .env
fi

export PORT=${PORT:-8790}

echo "[CIT] Starting server on port $PORT…"

nohup python server/cit_server.py >/dev/null 2>&1 &
echo "[CIT] CIT server started with PID $!"
