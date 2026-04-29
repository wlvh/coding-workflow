#!/usr/bin/env bash
# One-shot launcher for workflow docs sync.
#
# Usage from a target project:
#   curl -fsSL https://raw.githubusercontent.com/wlvh/coding-workflow/main/scripts/sync.sh | bash
#
# What this does:
#   1. Verifies current dir is a git repo with clean worktree
#   2. Shallow-clones wlvh/coding-workflow at the current default-branch HEAD
#   3. Runs sync_coding_workflow.py with UPSTREAM_DIR pointing at the clone
#   4. Cleans up the clone on exit

set -euo pipefail

if [ $# -ne 0 ]; then
  echo "Unknown arg: $1"
  exit 2
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Error: $(pwd) is not inside a git worktree."
  exit 1
fi
REPO_ROOT="$(git rev-parse --show-toplevel)"

UPSTREAM_PARENT="$(mktemp -d "${TMPDIR:-/tmp}/coding-workflow-XXXXXX")"
trap 'rm -rf "$UPSTREAM_PARENT"' EXIT

echo "Cloning wlvh/coding-workflow..."
# Shallow clone keeps the one-shot launcher fast; the Python script pins the
# resolved HEAD before reading every upstream template.
git clone --quiet --depth=1 --single-branch \
  https://github.com/wlvh/coding-workflow.git "$UPSTREAM_PARENT/cw"

export REPO_ROOT
export UPSTREAM_DIR="$UPSTREAM_PARENT/cw"
python3 "$UPSTREAM_DIR/scripts/sync_coding_workflow.py"
