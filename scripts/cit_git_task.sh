#!/usr/bin/env bash
# cit_git_task.sh - Execute Copilot-generated patches via structured tasks
# 
# Usage: ./scripts/cit_git_task.sh <task_spec_file>
#
# Task spec should be JSON with fields:
# - repo: target repository
# - component: target component directory
# - files: array of file paths
# - patch: unified diff patch to apply
# - commit_message: commit message for the changes

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

# Validate required fields in task spec
validate_task_spec() {
    local spec_file="$1"
    
    if [[ ! -f "$spec_file" ]]; then
        log_error "Task spec file not found: $spec_file"
        return 1
    fi
    
    # Check if jq is available
    if ! command -v jq &> /dev/null; then
        log_error "jq is required but not installed"
        return 1
    fi
    
    # Validate required fields
    local required_fields=("repo" "component" "files" "commit_message")
    for field in "${required_fields[@]}"; do
        if ! jq -e ".$field" "$spec_file" > /dev/null 2>&1; then
            log_error "Required field missing: $field"
            return 1
        fi
    done
    
    log_info "Task spec validation passed"
    return 0
}

# Apply patch to working tree
apply_patch() {
    local patch_file="$1"
    
    if [[ ! -f "$patch_file" ]]; then
        log_warn "No patch file provided, skipping patch application"
        return 0
    fi
    
    log_info "Applying patch: $patch_file"
    
    # Try to apply patch
    if git apply --check "$patch_file" 2>&1; then
        git apply "$patch_file"
        log_info "Patch applied successfully"
        return 0
    else
        log_error "Patch failed to apply cleanly"
        git apply --check "$patch_file" 2>&1 || true
        return 1
    fi
}

# Create feature branch and commit changes
commit_changes() {
    local spec_file="$1"
    
    local repo=$(jq -r '.repo' "$spec_file")
    local component=$(jq -r '.component' "$spec_file")
    local commit_message=$(jq -r '.commit_message' "$spec_file")
    
    # Create feature branch name
    local branch_name="copilot/task-$(date +%Y%m%d-%H%M%S)"
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_error "Not in a git repository"
        return 1
    fi
    
    # Create and checkout feature branch
    log_info "Creating feature branch: $branch_name"
    if ! git checkout -b "$branch_name" 2>&1; then
        log_error "Failed to create branch"
        return 1
    fi
    
    # Add files mentioned in spec
    log_info "Staging files for commit"
    local files=$(jq -r '.files[]' "$spec_file")
    while IFS= read -r file; do
        if [[ -f "$REPO_ROOT/$file" ]]; then
            git add "$REPO_ROOT/$file"
            log_info "Staged: $file"
        else
            log_warn "File not found: $file"
        fi
    done <<< "$files"
    
    # Commit changes
    log_info "Committing changes"
    if git commit -m "$commit_message" 2>&1; then
        log_info "Changes committed successfully"
        log_info "Branch: $branch_name"
        log_info "Use 'git push origin $branch_name' to push changes"
        return 0
    else
        log_error "Commit failed"
        return 1
    fi
}

# Main execution
main() {
    if [[ $# -lt 1 ]]; then
        log_error "Usage: $0 <task_spec_file> [patch_file]"
        exit 1
    fi
    
    local spec_file="$1"
    local patch_file="${2:-}"
    
    log_info "CIT Git Task Execution"
    log_info "======================"
    log_info "Task spec: $spec_file"
    log_info "Repo root: $REPO_ROOT"
    echo
    
    # Validate task spec
    if ! validate_task_spec "$spec_file"; then
        exit 1
    fi
    
    # Apply patch if provided
    if [[ -n "$patch_file" ]]; then
        if ! apply_patch "$patch_file"; then
            exit 1
        fi
    fi
    
    # Commit changes
    if ! commit_changes "$spec_file"; then
        exit 1
    fi
    
    log_info "Task execution completed successfully"
}

main "$@"
