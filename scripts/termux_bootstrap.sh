#!/data/data/com.termux/files/usr/bin/bash

# Bootstrap script to prepare the Termux environment for CIT.
#
# This script installs required packages, clones the repository (if not
# already present), and can be extended to enable rclone or other services.
# Run it once after installing Termux.

set -e

echo "[CIT] Updating Termux packages…"
pkg update -y && pkg upgrade -y

echo "[CIT] Installing dependencies…"
pkg install -y git python termux-services

REPO_DIR="$HOME/cit"
if [ ! -d "$REPO_DIR" ]; then
  echo "[CIT] Cloning the repository into $REPO_DIR"
  git clone https://github.com/Ihorog/cit.git "$REPO_DIR"
fi

echo "[CIT] Setup complete.  Remember to set OPENAI_API_KEY before starting the server."
