#!/bin/bash
# smoke_ci_orchestrator.sh — Smoke orchestrator for CIT + ciwiki integration
# Resolves CIT repo root, verifies sibling ciwiki clone, runs build + checks.
# Exit codes: 0 = success, 1 = failures, 2 = missing prerequisites

set -euo pipefail

# Resolve CIT repo root (directory containing this script's parent)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CIT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
CIWIKI_ROOT="${CIT_ROOT}/../ciwiki"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_ok()   { echo -e "${GREEN}✅ $*${NC}"; }
log_err()  { echo -e "${RED}❌ $*${NC}" >&2; }
log_warn() { echo -e "${YELLOW}⚠️  $*${NC}"; }

echo "🔍 CIT Smoke Orchestrator"
echo "========================="
echo "CIT root:    ${CIT_ROOT}"
echo "ciwiki root: ${CIWIKI_ROOT}"
echo ""

# --- Prerequisite: sibling ciwiki clone must exist ---
if [ ! -d "${CIWIKI_ROOT}" ]; then
  log_err "Sibling ciwiki clone not found at ${CIWIKI_ROOT}"
  log_err "Clone it first: git clone https://github.com/Ihorog/ciwiki ../ciwiki"
  exit 2
fi
log_ok "ciwiki clone found"

# --- Run legend build inside ciwiki (if script exists) ---
BUILD_SCRIPT="${CIWIKI_ROOT}/scripts/legend/build_legend.py"
if [ -f "${BUILD_SCRIPT}" ]; then
  echo "🔨 Running legend build in ciwiki..."
  python3 "${BUILD_SCRIPT}"
  log_ok "legend build completed"
else
  log_warn "build_legend.py not found at ${BUILD_SCRIPT}; skipping"
fi

# --- Verify ciwiki legend index ---
LEGEND_INDEX="${CIWIKI_ROOT}/api/v1/legend/index.json"
if [ ! -f "${LEGEND_INDEX}" ]; then
  log_err "Legend index not found: ${LEGEND_INDEX}"
  log_err "Ensure build_legend.py completed successfully and generated the index."
  exit 1
fi
log_ok "Legend index exists: ${LEGEND_INDEX}"

# --- Run CIT repo check ---
REPO_CHECK="${CIT_ROOT}/scripts/repo_check.sh"
if [ -f "${REPO_CHECK}" ]; then
  echo "🔍 Running CIT repo check..."
  bash "${REPO_CHECK}"
  log_ok "repo_check.sh passed"
else
  log_warn "scripts/repo_check.sh not found; skipping"
fi

echo ""
log_ok "Smoke orchestrator completed successfully"
exit 0
