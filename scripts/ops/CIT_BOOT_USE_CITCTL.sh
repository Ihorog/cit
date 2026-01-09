#!/usr/bin/env bash
set -euo pipefail

BOOT_DIR="$HOME/.termux/boot"
mkdir -p "$BOOT_DIR"

cat > "$BOOT_DIR/cit_autoboot_8794.sh" <<'SH'
#!/data/data/com.termux/files/usr/bin/sh
cd "$HOME/cimeika/cit" || exit 0
./citctl.sh start
SH

chmod +x "$BOOT_DIR/cit_autoboot_8794.sh"
echo "OK: Boot now starts CIT only via citctl"
