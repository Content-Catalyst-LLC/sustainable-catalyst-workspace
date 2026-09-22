#!/usr/bin/env bash
set -euo pipefail
REPO="${1:-$HOME/Downloads/sustainable-catalyst-workspace}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[[ -d "$REPO/.git" ]] || { echo "ERROR: Git repository not found: $REPO" >&2; exit 1; }
cd "$REPO"
V="$(grep -E '^[[:space:]]*\*[[:space:]]*Version:' wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php | awk '{print $3}' | head -1)"
[[ "$V" == "2.25.0" ]] || { echo "ERROR: expected Workspace v2.25.0 baseline, found $V" >&2; exit 1; }
[[ -z "$(git status --porcelain)" ]] || { echo "ERROR: repository has uncommitted changes" >&2; exit 1; }
cp -a "$HERE/patch/." "$REPO/"
python3 scripts/validate_server_side_notebook_artifact_orchestration_v2260.py
PYTHONPATH=backend python3 -m pytest -q backend/tests
if command -v php >/dev/null 2>&1; then find wordpress/sustainable-catalyst-workspace -name '*.php' -print0 | xargs -0 -n1 php -l >/dev/null; fi
if command -v node >/dev/null 2>&1; then node --check wordpress/sustainable-catalyst-workspace/assets/js/workspace-v2.26.0.js >/dev/null; fi
find . -type d \( -name '__pycache__' -o -name '.pytest_cache' \) -prune -exec rm -rf {} +
find . -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
git add -A
git commit -m "Workspace v2.26.0 — Server-Side Notebook & Artifact Orchestration"
git tag -a v2.26.0 -m "Workspace v2.26.0 — Server-Side Notebook & Artifact Orchestration"
git push origin HEAD:main
git push origin v2.26.0
echo "PASS: Workspace v2.26.0 applied, validated, committed, pushed, and tagged."
