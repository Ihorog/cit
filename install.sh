# --- CIT 111: auto-install git hooks (best-effort) --- 
if [ -d ".git" ] && [ -f "scripts/install-hooks.sh" ]; then
  bash scripts/install-hooks.sh || true
fi

