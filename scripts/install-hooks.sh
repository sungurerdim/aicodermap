#!/usr/bin/env sh
# One-shot installer for project git hooks. Points git at scripts/hooks/ via
# core.hooksPath so hooks travel with the repo and a fresh clone gets them
# after running this script once.
#
# Usage: bash scripts/install-hooks.sh
# Safe to re-run; idempotent.

set -e

REPO_ROOT="$(git rev-parse --show-toplevel)"
HOOKS_DIR="scripts/hooks"

if [ ! -d "$REPO_ROOT/$HOOKS_DIR" ]; then
  echo "✗ $HOOKS_DIR does not exist; nothing to install." >&2
  exit 1
fi

# Ensure every hook file is executable on the local filesystem.
chmod +x "$REPO_ROOT/$HOOKS_DIR"/* 2>/dev/null || true

git -C "$REPO_ROOT" config core.hooksPath "$HOOKS_DIR"

echo "✓ git hooks active via core.hooksPath = $HOOKS_DIR"
echo "  installed hooks:"
for h in "$REPO_ROOT/$HOOKS_DIR"/*; do
  [ -f "$h" ] || continue
  basename "$h" | sed 's/^/    - /'
done
echo ""
echo "  To uninstall: git config --unset core.hooksPath"
