#!/usr/bin/env bash
set -euo pipefail

cd ~/cimeika/cit
mkdir -p vault/local vault/cache logs

# deps
pkg install -y rclone >/dev/null

# ===== WebDAV (FACT: URL given) =====
# https://cimeiniy.keenetic.link/webdav/
# NOTE: will prompt for user/pass once via rclone config if not provided
if ! rclone listremotes | grep -q '^keenetic_webdav:'; then
  rclone config create keenetic_webdav webdav \
    url "https://cimeiniy.keenetic.link/webdav/" \
    vendor other >/dev/null
fi

# ===== SMB (🔧 SIMULATION: needs IP/user/pass) =====
# You MUST set these before using SMB:
# export SMB_HOST="192.168.1.1"   (Keenetic LAN IP)
# export SMB_USER="..."
# export SMB_PASS="..."
# export SMB_SHARE="CIMEIKA_VAULT" (or actual share name)
if ! rclone listremotes | grep -q '^keenetic_smb:'; then
  if [ -n "${SMB_HOST:-}" ] && [ -n "${SMB_USER:-}" ] && [ -n "${SMB_PASS:-}" ] && [ -n "${SMB_SHARE:-}" ]; then
    rclone config create keenetic_smb smb \
      host "$SMB_HOST" user "$SMB_USER" pass "$SMB_PASS" \
      domain "WORKGROUP" >/dev/null
  else
    echo "🔧 SMB not configured (missing SMB_HOST/SMB_USER/SMB_PASS/SMB_SHARE). Skipping."
  fi
fi

# ===== Helper scripts =====
cat > cit_vault_pull.sh <<'SH'
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
SH
chmod +x cit_vault_pull.sh

cat > cit_vault_push.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail
cd ~/cimeika/cit
# Push local vault -> WebDAV
rclone sync vault/local keenetic_webdav:/ \
  --cache-dir vault/cache \
  --log-file logs/rclone_webdav_push.log \
  --log-level INFO
echo "OK: PUSH vault/local -> webdav"
SH
chmod +x cit_vault_push.sh

cat > cit_vault_ls.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail
cd ~/cimeika/cit
rclone lsf keenetic_webdav:/ --max-depth 2 | head -n 200
SH
chmod +x cit_vault_ls.sh

echo "OK: CONNECTORS installed"
echo "Commands:"
echo "  ./cit_vault_ls.sh"
echo "  ./cit_vault_pull.sh"
echo "  ./cit_vault_push.sh"
