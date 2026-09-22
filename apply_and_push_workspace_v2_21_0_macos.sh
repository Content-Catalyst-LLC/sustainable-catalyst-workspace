#!/usr/bin/env bash
set -euo pipefail
REPO="${1:-$HOME/Downloads/sustainable-catalyst-workspace}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PATCH_DIR="$SCRIPT_DIR/patch"
[[ -d "$REPO/.git" ]] || { echo "ERROR: Git repository not found: $REPO" >&2; exit 1; }
[[ -d "$PATCH_DIR" ]] || { echo "ERROR: patch directory missing" >&2; exit 1; }
cd "$REPO"
git fetch --tags origin
[[ "$(git branch --show-current)" == "main" ]] || { echo "ERROR: expected main branch" >&2; exit 1; }
[[ -z "$(git status --porcelain)" ]] || { echo "ERROR: repository has uncommitted changes" >&2; git status --short; exit 1; }
git rev-parse -q --verify refs/tags/v2.20.0 >/dev/null || { echo "ERROR: required baseline tag v2.20.0 is not present" >&2; exit 1; }
if git rev-parse -q --verify refs/tags/v2.21.0 >/dev/null; then echo "ERROR: v2.21.0 tag already exists" >&2; exit 1; fi
rsync -a "$PATCH_DIR/" "$REPO/"
chmod +x scripts/deploy_workspace_backend_v2_21_0_vps.sh backend/deploy_workspace_backend_v2_21_0_vps.sh || true
python3 scripts/validate_optimization_parameter_search_v2210.py
PYTHONPATH=backend python3 -m pytest -q backend/tests
if command -v php >/dev/null 2>&1; then find wordpress/sustainable-catalyst-workspace -name '*.php' -print0 | xargs -0 -n1 php -l >/dev/null; fi
find . -type d \( -name '__pycache__' -o -name '.pytest_cache' \) -prune -exec rm -rf {} +
find . -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
git add -A
git commit -m "Workspace v2.21.0 — Optimization & Parameter Search Runtime"
git tag -a v2.21.0 -m "Workspace v2.21.0 — Optimization & Parameter Search Runtime"
git push origin HEAD:main
git push origin v2.21.0
echo "PASS: Workspace v2.21.0 applied, validated, committed, pushed, and tagged."
