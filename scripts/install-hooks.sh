#!/bin/bash
# Install InGit Git hooks

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GIT_HOOKS_DIR="$(git rev-parse --git-dir)/hooks"

echo "🔧 Installing InGit Git hooks..."

# Copy hooks
cp "$SCRIPT_DIR/hooks/pre-commit" "$GIT_HOOKS_DIR/pre-commit"
cp "$SCRIPT_DIR/hooks/post-commit" "$GIT_HOOKS_DIR/post-commit"

# Make executable
chmod +x "$GIT_HOOKS_DIR/pre-commit"
chmod +x "$GIT_HOOKS_DIR/post-commit"

echo "✅ Git hooks installed successfully!"
echo ""
echo "Installed hooks:"
echo "  - pre-commit: YAML validation, file size checks"
echo "  - post-commit: Auto-close tasks, link commits"
