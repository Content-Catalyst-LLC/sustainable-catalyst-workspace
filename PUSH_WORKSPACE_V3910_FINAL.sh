#!/usr/bin/env bash
set -euo pipefail
REPO_ZIP="${1:?repository zip required}"
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT
unzip -q "$REPO_ZIP" -d "$WORK"
SRC="$WORK/sustainable-catalyst-workspace-v3.9.1"
[[ -d "$SRC" ]] || { echo "ERROR: v3.9.1 repository root missing from archive" >&2; exit 1; }
TARGET="${SC_WORKSPACE_REPO:-$HOME/Downloads/sustainable-catalyst-workspace}"
if [[ ! -d "$TARGET/.git" ]]; then
  git clone https://github.com/Content-Catalyst-LLC/sustainable-catalyst-workspace.git "$TARGET"
fi
cd "$TARGET"
git checkout main
git pull --ff-only origin main
if [[ -n "$(git status --porcelain)" ]]; then
  echo "ERROR: Workspace repository is not clean before v3.9.1 promotion" >&2
  git status --short
  exit 1
fi
rsync -a --delete --exclude '.git/' --exclude '.pytest_cache/' --exclude '__pycache__/' "$SRC/" "$TARGET/"
chmod +x PUSH_WORKSPACE_V3910_FINAL.sh deploy_workspace_backend_v3_9_1_vps.sh scripts/generate_typed_client_contracts_v3910.py

VENV="$WORK/venv"
python3 -m venv "$VENV"
"$VENV/bin/python" -m pip install -q --upgrade pip
"$VENV/bin/python" -m pip install -q -r backend/requirements.txt pytest

echo "=== WORKSPACE v3.9.1 RELEASE VALIDATION ==="
PYTHONPATH="$TARGET/backend" "$VENV/bin/python" -m pytest -q \
  backend/tests/test_catalyst_analytics_r_provider_promotion_v3910.py \
  backend/tests/test_investigation_timeline_workspace_v3900.py
PYTHONPATH="$TARGET/backend" "$VENV/bin/python" scripts/generate_typed_client_contracts_v3910.py --check
"$VENV/bin/python" -m compileall -q backend/app backend/r-runtime/service.py
php -l wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php >/dev/null
php -l wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php >/dev/null
node --check wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-catalyst-analytics-r-v3910.js
node --check wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-typed-client-v3910.js
node --check wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-investigation-timeline-v3900.js
bash -n deploy_workspace_backend_v3_9_1_vps.sh

grep -q '^Version: 2.2.0$' backend/r-runtime/vendor/catalystanalyticsr/DESCRIPTION
grep -q 'sc.analytics-r.statistical-diagnostics-validation.v1' backend/r-runtime/vendor/catalystanalyticsr/R/core_computational_provider.R
grep -q 'service_version: str = "3.9.1"' backend/app/config.py

git add -A
if git diff --cached --quiet; then
  echo "ERROR: no v3.9.1 changes staged" >&2
  exit 1
fi
git commit -m "Build Workspace v3.9.1 Catalyst Analytics R v2.2 Provider Promotion"
git push origin main
if git rev-parse v3.9.1 >/dev/null 2>&1; then
  echo "ERROR: tag v3.9.1 already exists locally" >&2
  exit 1
fi
git tag -a v3.9.1 -m "Workspace v3.9.1 Catalyst Analytics R v2.2 Provider Promotion"
git push origin v3.9.1

echo "PASS - Workspace v3.9.1 pushed successfully"
git log -1 --oneline --decorate
git tag --points-at HEAD
