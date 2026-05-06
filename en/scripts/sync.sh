#!/usr/bin/env bash
# One-shot launcher for English workflow docs sync.
#
# Usage from a target project:
#   curl -fsSL https://raw.githubusercontent.com/wlvh/coding-workflow/main/en/scripts/sync.sh | bash
#
# This launcher uses the English template source family under `en/` and installs
# selected templates into canonical target paths such as `AGENTS.md`,
# `TESTING.md`, and `.github/pull_request_template.md`.

set -euo pipefail

FINAL_CHECK=0
if [ $# -eq 1 ] && [ "$1" = "--final" ]; then
  FINAL_CHECK=1
elif [ $# -ne 0 ]; then
  echo "Unknown arg: $1"
  exit 2
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Error: $(pwd) is not inside a git worktree."
  exit 1
fi
REPO_ROOT="$(git rev-parse --show-toplevel)"

UPSTREAM_PARENT=""
cleanup() {
  if [ -n "$UPSTREAM_PARENT" ]; then
    rm -rf "$UPSTREAM_PARENT"
  fi
}
trap cleanup EXIT

if [ -n "${CODING_WORKFLOW_UPSTREAM_DIR:-}" ]; then
  UPSTREAM_DIR="$(cd "$CODING_WORKFLOW_UPSTREAM_DIR" && pwd)"
else
  UPSTREAM_PARENT="$(mktemp -d "${TMPDIR:-/tmp}/coding-workflow-XXXXXX")"
  echo "Cloning wlvh/coding-workflow..."
  # Shallow clone keeps the one-shot launcher fast; the Python script pins the
  # resolved HEAD before reading every upstream template.
  git clone --quiet --depth=1 --single-branch \
    https://github.com/wlvh/coding-workflow.git "$UPSTREAM_PARENT/cw"
  UPSTREAM_DIR="$UPSTREAM_PARENT/cw"
fi

export REPO_ROOT
export UPSTREAM_DIR
export CODING_WORKFLOW_LANGUAGE=en
python3 "$UPSTREAM_DIR/scripts/sync_coding_workflow.py"

if [ "$FINAL_CHECK" -eq 1 ]; then
  python3 "$UPSTREAM_DIR/scripts/sync_coding_workflow.py" \
    --check-final PR_BODY.md
elif [ -f "$REPO_ROOT/PR_BODY.md" ]; then
  python3 "$UPSTREAM_DIR/scripts/sync_coding_workflow.py" \
    --update-pr-body PR_BODY.md
else
  echo "PR_BODY.md not found; use .coding_workflow/diffs/pr_body_skeleton.md when drafting the sync PR body."
fi
