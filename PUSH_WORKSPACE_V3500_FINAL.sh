#!/usr/bin/env bash
set -euo pipefail
REPO_ZIP="${1:?repository zip required}"
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT
unzip -q "$REPO_ZIP" -d "$WORK"
SRC="$WORK/sustainable-catalyst-workspace-v3.5.0"
[[ -d "$SRC" ]] || { echo "ERROR: v3.5.0 repository root missing from archive" >&2; exit 1; }
TARGET="${SC_WORKSPACE_REPO:-$HOME/Downloads/sustainable-catalyst-workspace}"
if [[ ! -d "$TARGET/.git" ]]; then git clone https://github.com/Content-Catalyst-LLC/sustainable-catalyst-workspace.git "$TARGET"; fi
cd "$TARGET"
git checkout main
git pull --ff-only origin main
rm -rf catalystanalyticsr
rsync -a --delete --exclude '.git/' "$SRC/" "$TARGET/"
chmod +x PUSH_WORKSPACE_V3500_FINAL.sh deploy_workspace_backend_v3_5_0_vps.sh backend/deploy_workspace_backend_v3_5_0_vps.sh scripts/validate_catalyst_analytics_r_runtime_adapter_v3500.py scripts/generate_typed_client_contracts_v3500.py
VENV="$WORK/venv"
python3 -m venv "$VENV"
"$VENV/bin/python" -m pip install -q --upgrade pip
"$VENV/bin/python" -m pip install -q -r backend/requirements.txt
"$VENV/bin/python" -m pip install -q pytest
PYTHONPATH="$TARGET/backend" "$VENV/bin/python" scripts/validate_catalyst_analytics_r_runtime_adapter_v3500.py
PYTHONPATH="$TARGET/backend" "$VENV/bin/python" scripts/generate_typed_client_contracts_v3500.py --check
PYTHONPATH="$TARGET/backend" "$VENV/bin/python" -m pytest -q backend/tests/test_catalyst_analytics_r_runtime_adapter_v3500.py backend/tests/test_registry.py
"$VENV/bin/python" -m compileall -q backend/app
php -l wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php >/dev/null
php -l wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php >/dev/null
node --check wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-catalyst-analytics-r-v3500.js
node --check wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-typed-client-v3500.js
node --check wordpress/sustainable-catalyst-workspace/assets/js/workspace-v3.5.0.js
bash -n deploy_workspace_backend_v3_5_0_vps.sh
[[ ! -e catalystanalyticsr ]] || { echo 'ERROR: accidental catalystanalyticsr gitlink/directory present' >&2; exit 1; }
git add -A
if ! git diff --cached --quiet; then git commit -m "Build Workspace v3.5.0 Catalyst Analytics R Runtime Adapter"; fi
git push origin main
if git rev-parse v3.5.0 >/dev/null 2>&1; then echo 'Tag v3.5.0 already exists locally'; else git tag -a v3.5.0 -m "Workspace v3.5.0 Catalyst Analytics R Runtime Adapter"; fi
git push origin v3.5.0
echo 'PASS - Workspace v3.5.0 pushed successfully'
git log -1 --oneline --decorate
git tag --points-at HEAD
