# Cimeika · Nodes Registry (контрольні точки)

## Samsung Home Node (Termux)
- CI Core:
  - GET  /status  -> OK/paths
  - GET  /health  -> ok
  - POST /store?type=texts|gallery|voice&name=<file>  (data-binary)

## Keenetic Vault
- WebDAV: https://cimeiniy.keenetic.link/webdav/
- Root: /webdav/ci/
- rclone remote: keenetik:ci/

## SMB (локальний ПК)
- Share/Host: Keenetic-6759
- Workgroup: WORKGROUP
- Disk label: NO NAME / CIMEIKA_VAULT
- Призначення: тільки LAN-доступ для Windows/Mac (не для інтернету)

