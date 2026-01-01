#!/usr/bin/env bash
set -euo pipefail

PORT=8794
HEXPORT="$(printf '%04X' "$PORT" | tr '[:upper:]' '[:lower:]')"   # 226a
echo "PORT=$PORT HEX=$HEXPORT"

# Find socket inode(s) for LISTEN on this port (IPv4 + IPv6)
INODES="$(
  { cat /proc/net/tcp 2>/dev/null || true; } \
  | awk -v p=":$HEXPORT" '$4=="0A" && index($2,p){print $10}' \
  | sort -u
)"

INODES6="$(
  { cat /proc/net/tcp6 2>/dev/null || true; } \
  | awk -v p=":$HEXPORT" '$4=="0A" && index($2,p){print $10}' \
  | sort -u
)"

INODES="$(printf "%s\n%s\n" "$INODES" "$INODES6" | sed '/^$/d' | sort -u)"

if [ -z "${INODES:-}" ]; then
  echo "NO LISTEN socket inode found for :$PORT"
  echo "Quick reachability test:"
  (curl -sS --max-time 2 "http://127.0.0.1:$PORT/health" && echo) || echo "curl failed"
  exit 0
fi

echo "LISTEN inodes:"
echo "$INODES" | sed 's/^/  - /'

echo
echo "Mapping inode -> PID/command (may take ~2-10s)..."

FOUND=0
for inode in $INODES; do
  # scan /proc/*/fd symlinks for socket:[inode]
  for pid in /proc/[0-9]*; do
    pidnum="${pid#/proc/}"
    # skip inaccessible
    [ -r "$pid/fd" ] || continue
    if ls -l "$pid/fd" 2>/dev/null | grep -q "socket:\[$inode\]"; then
      cmd="$(tr '\0' ' ' < "$pid/cmdline" 2>/dev/null | sed 's/[[:space:]]\+$//')"
      echo "inode=$inode -> PID=$pidnum -> $cmd"
      FOUND=1
    fi
  done
done

[ "$FOUND" -eq 1 ] || echo "inode(s) found, but PID mapping blocked by permissions."
