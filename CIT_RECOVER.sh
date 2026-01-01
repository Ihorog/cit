#!/usr/bin/env bash
set -e

echo "[1] Abort rebase if exists"
git rebase --abort 2>/dev/null || true

echo "[2] Fetch origin"
git fetch origin

echo "[3] Reset local main to origin/main"
git checkout -B main origin/main
git reset --hard origin/main

echo "[4] Cleanup forbidden files"
rm -f .env .env.* *.bak *.backup* 2>/dev/null || true
rm -rf data db dist 2>/dev/null || true

echo "[5] Ensure .gitignore"
cat > .gitignore <<'GIT'
.env
.env.*
*.bak
*.backup*
*.db
data/
db/
logs/
dist/
__pycache__/
*.pyc
.DS_Store
GIT

echo "[6] Install minimal GitHub automation"

mkdir -p .github/workflows docs scripts ui

cat > .github/workflows/ci.yml <<'YML'
name: ci
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: python -m py_compile server/cit_server.py
YML

cat > .env.example <<'ENV'
CIT_PORT=8794
OPENAI_API_KEY=
ENV

touch scripts/.keep ui/.keep

echo "[7] Commit and push"
git add .github .gitignore .env.example scripts ui
git commit -m "ops: recover repo and add automation" || true
git push origin main

echo "OK DONE"
