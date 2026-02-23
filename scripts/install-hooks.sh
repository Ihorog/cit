#!/bin/bash

set -e

# Install git hooks
cp scripts/hooks/pre-commit .git/hooks/pre-commit
cp scripts/hooks/post-checkout .git/hooks/post-checkout
cp scripts/hooks/commit-msg .git/hooks/commit-msg
chmod +x .git/hooks/pre-commit .git/hooks/post-checkout .git/hooks/commit-msg
