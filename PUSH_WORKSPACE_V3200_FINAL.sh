#!/usr/bin/env bash
set -euo pipefail
REPO_ZIP="${1:?repository zip required}"
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT
unzip -q "$REPO_ZIP" -d "$WORK"
SRC="$WORK/sustainable-catalyst-workspace-v3.2.0"
TARGET="${SC_WORKSPACE_REPO:-$HOME/Downloads/sustainable-catalyst-workspace}"
if [[ ! -d "$TARGET/.git" ]]; then git clone https://github.com/Content-Catalyst-LLC/sustainable-catalyst-workspace.git "$TARGET"; fi
cd "$TARGET"
git checkout main
git pull --ff-only origin main
rsync -a --delete --exclude '.git/' "$SRC/" "$TARGET/"
python3 scripts/validate_unified_research_project_context_v3200.py
python3 -m compileall -q backend/app
php -l wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php >/dev/null
php -l wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php >/dev/null
node --check wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-unified-research-context-v3200.js
git add -A
if ! git diff --cached --quiet; then git commit -m "Build Workspace v3.2.0 Unified Research Project Context"; fi
git push origin main
if git rev-parse v3.2.0 >/dev/null 2>&1; then echo 'Tag v3.2.0 already exists locally'; else git tag -a v3.2.0 -m "Workspace v3.2.0 Unified Research Project Context"; fi
git push origin v3.2.0
echo 'PASS - Workspace v3.2.0 pushed successfully'
git log -1 --oneline --decorate
git tag --points-at HEAD
