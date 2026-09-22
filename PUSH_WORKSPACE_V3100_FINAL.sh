#!/usr/bin/env bash
set -euo pipefail

ARCHIVE="${1:-}"
TARGET="${2:-$HOME/Downloads/sustainable-catalyst-workspace}"
[[ -n "$ARCHIVE" && -f "$ARCHIVE" ]] || { echo "ERROR: repository ZIP required" >&2; exit 1; }
[[ -d "$TARGET/.git" ]] || { echo "ERROR: target Git checkout not found: $TARGET" >&2; exit 1; }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
unzip -q "$ARCHIVE" -d "$TMP"
SRC="$(find "$TMP" -mindepth 1 -maxdepth 1 -type d | head -1)"
[[ -n "$SRC" ]] || { echo "ERROR: repository archive did not contain a top-level directory" >&2; exit 1; }

cd "$TARGET"
git fetch origin --tags
git checkout main
git pull --ff-only origin main

# Keep Git metadata and local-only ignored material; make tracked working tree match release archive.
rsync -a --delete --exclude='.git/' --exclude='.env' --exclude='__pycache__/' --exclude='.pytest_cache/' "$SRC/" "$TARGET/"

python3 -m py_compile backend/app/*.py
php -l wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php >/dev/null
php -l wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php >/dev/null
bash -n backend/deploy_workspace_backend_v3_1_0_vps.sh
PYTHONPATH=backend python3 scripts/validate_platform_core_v3_runtime_integration_v3100.py

if git rev-parse -q --verify refs/tags/v3.1.0 >/dev/null; then
  echo "ERROR: local tag v3.1.0 already exists" >&2; exit 1
fi
if git ls-remote --exit-code --tags origin refs/tags/v3.1.0 >/dev/null 2>&1; then
  echo "ERROR: remote tag v3.1.0 already exists" >&2; exit 1
fi

git add -A
git commit -m "Build Workspace v3.1.0 Platform Core v3 Unified Research Runtime Integration"
git push origin main
git tag -a v3.1.0 -m "Workspace v3.1.0 Platform Core v3 Unified Research Runtime Integration"
git push origin v3.1.0

echo "PASS - Workspace v3.1.0 pushed successfully"
git log -1 --oneline
git tag --points-at HEAD
