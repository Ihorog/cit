#!/usr/bin/env bash
set -euo pipefail

echo "KILL: python server/cit_server.py (all)"
PIDS="$(ps -A -o pid,args | grep -E 'python .*server/cit_server\.py' | grep -v grep | awk '{print $1}' || true)"

if [ -z "${PIDS:-}" ]; then
  echo "NO CIT PIDS FOUND"
else
  echo "$PIDS" | xargs -r kill -9 || true
  echo "KILLED: $(echo "$PIDS" | tr '\n' ' ')"
fi

# clean stale pidfile(s)
rm -f logs/cit_8794.pid 2>/dev/null || true

echo "DONE"
