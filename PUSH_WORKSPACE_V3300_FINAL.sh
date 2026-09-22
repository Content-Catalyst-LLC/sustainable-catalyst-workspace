#!/usr/bin/env bash
set -euo pipefail
REPO_ZIP="${1:?repository zip required}"
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT
unzip -q "$REPO_ZIP" -d "$WORK"
SRC="$WORK/sustainable-catalyst-workspace-v3.3.0"
[[ -d "$SRC" ]] || { echo "ERROR: v3.3.0 repository root missing from archive" >&2; exit 1; }
TARGET="${SC_WORKSPACE_REPO:-$HOME/Downloads/sustainable-catalyst-workspace}"
if [[ ! -d "$TARGET/.git" ]]; then git clone https://github.com/Content-Catalyst-LLC/sustainable-catalyst-workspace.git "$TARGET"; fi
cd "$TARGET"
git checkout main
git pull --ff-only origin main
rsync -a --delete --exclude '.git/' "$SRC/" "$TARGET/"
chmod +x PUSH_WORKSPACE_V3300_FINAL.sh deploy_workspace_backend_v3_3_0_vps.sh backend/deploy_workspace_backend_v3_3_0_vps.sh scripts/validate_research_session_object_binding_runtime_v3300.py scripts/generate_typed_client_contracts_v3300.py
VENV="$WORK/venv"
python3 -m venv "$VENV"
"$VENV/bin/python" -m pip install -q --upgrade pip
"$VENV/bin/python" -m pip install -q -r backend/requirements.txt
"$VENV/bin/python" -m pip install -q pytest
"$VENV/bin/python" -m pip install -q pytest
PYTHONPATH="$TARGET/backend" "$VENV/bin/python" scripts/validate_research_session_object_binding_runtime_v3300.py
PYTHONPATH="$TARGET/backend" "$VENV/bin/python" scripts/generate_typed_client_contracts_v3300.py --check
PYTHONPATH="$TARGET/backend" "$VENV/bin/python" -m pytest -q backend/tests/test_research_session_object_binding_runtime_v3300.py
"$VENV/bin/python" -m compileall -q backend/app
php -l wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php >/dev/null
php -l wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php >/dev/null
node --check wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-research-session-bindings-v3300.js
node --check wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-typed-client-v3300.js
bash -n deploy_workspace_backend_v3_3_0_vps.sh
git add -A
if ! git diff --cached --quiet; then git commit -m "Build Workspace v3.3.0 Research Session & Object Binding Runtime"; fi
git push origin main
if git rev-parse v3.3.0 >/dev/null 2>&1; then echo 'Tag v3.3.0 already exists locally'; else git tag -a v3.3.0 -m "Workspace v3.3.0 Research Session & Object Binding Runtime"; fi
git push origin v3.3.0
echo 'PASS - Workspace v3.3.0 pushed successfully'
git log -1 --oneline --decorate
git tag --points-at HEAD
