#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

[ -d ".git" ] || exit 0
[ -d "scripts/hooks" ] || exit 0

mkdir -p .git/hooks

for h in pre-commit post-checkout commit-msg; do
  src="scripts/hooks/$h"
  dst=".git/hooks/$h"
  [ -f "$src" ] || continue
  install -m 0755 "$src" "$dst"
done

echo "[CIT] Git hooks installed"
