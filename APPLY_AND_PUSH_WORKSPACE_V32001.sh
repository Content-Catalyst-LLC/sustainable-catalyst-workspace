#!/usr/bin/env bash
set -euo pipefail
TARGET="${1:-$HOME/Downloads/sustainable-catalyst-workspace}"
HERE="$(cd "$(dirname "$0")" && pwd)"
PAYLOAD="$HERE/payload"
[[ -d "$TARGET/.git" ]] || { echo "ERROR: Workspace git repository not found: $TARGET" >&2; exit 1; }
[[ -d "$PAYLOAD" ]] || { echo "ERROR: v3.20.0.1 payload missing: $PAYLOAD" >&2; exit 1; }
python3 "$HERE/APPLY_WORKSPACE_V32001.py" "$TARGET" --payload "$PAYLOAD"
cd "$TARGET"
python3 VALIDATE_WORKSPACE_V32001.py "$TARGET"
python3 -m py_compile backend/app/config.py backend/app/main.py backend/neural-runtime/service.py

if command -v php >/dev/null 2>&1; then
  php -l wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php
  php -l wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php
  php -l wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-deployment.php
fi

git status --short
git add -A
if git diff --cached --quiet; then
  echo "No repository changes to commit."
else
  git commit -m "Workspace v3.20.0.1 — Stable Server Package & Asset Coherence Repair"
fi
if git rev-parse -q --verify refs/tags/v3.20.0.1 >/dev/null; then
  TAG_COMMIT="$(git rev-list -n 1 v3.20.0.1)"
  HEAD_COMMIT="$(git rev-parse HEAD)"
  [[ "$TAG_COMMIT" == "$HEAD_COMMIT" ]] || { echo "ERROR: tag v3.20.0.1 already exists on a different commit" >&2; exit 1; }
else
  git tag -a v3.20.0.1 -m "Workspace v3.20.0.1 — Stable Server Package & Asset Coherence Repair"
fi
git push origin HEAD
git push origin v3.20.0.1

echo "PASS: Workspace v3.20.0.1 applied, validated, committed, pushed, and tagged"
