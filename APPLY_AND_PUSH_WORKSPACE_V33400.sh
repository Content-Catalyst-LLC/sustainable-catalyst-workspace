#!/usr/bin/env bash
set -Eeuo pipefail
TARGET="${1:-$HOME/Downloads/sustainable-catalyst-workspace}"; HERE="$(cd "$(dirname "$0")" && pwd)"; PAYLOAD="$HERE/payload"
[[ -d "$TARGET/.git" ]] || { echo "ERROR: Workspace git repository not found: $TARGET" >&2; exit 1; }
python3 "$HERE/APPLY_WORKSPACE_V33400.py" "$TARGET" --payload "$PAYLOAD"
python3 "$HERE/VALIDATE_WORKSPACE_V33400.py" "$TARGET"
python3 -m py_compile "$TARGET/backend/app/config.py" "$TARGET/backend/app/client_contracts.py" "$TARGET/backend/app/main.py" "$TARGET/backend/app/polyglot.py" "$TARGET/backend/neural-runtime/service.py"
if python3 -c 'import torch,numpy,fastapi,pytest' >/dev/null 2>&1; then PYTHONPATH="$TARGET/backend" python3 -m pytest -q "$TARGET/backend/tests/test_neural_gnn_training_runtime_v33400.py"; else echo "NOTE: local neural test dependencies unavailable; executable certification will run in Contabo Docker."; fi
if [[ -f "$TARGET/scripts/generate_typed_client_contracts_v33400.py" ]]; then
  python3 "$TARGET/scripts/generate_typed_client_contracts_v33400.py"
  python3 "$TARGET/scripts/generate_typed_client_contracts_v33400.py" --check
fi
if command -v php >/dev/null 2>&1 && [[ -f "$TARGET/wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php" ]]; then php -l "$TARGET/wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php"; php -l "$TARGET/wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php"; fi
"$HERE/PACKAGE_WORKSPACE_V33400.sh" "$TARGET" "$HERE"
cd "$TARGET"; git status --short; git add -A
if git diff --cached --quiet; then echo "No repository changes to commit."; else git commit -m "Workspace v3.34.0 — Graph Neural Network Training Runtime"; fi
if git rev-parse -q --verify refs/tags/v3.34.0 >/dev/null; then [[ "$(git rev-list -n 1 v3.34.0)" == "$(git rev-parse HEAD)" ]] || { echo "ERROR: tag v3.34.0 exists on another commit" >&2; exit 1; }; else git tag -a v3.34.0 -m "Workspace v3.34.0 — Graph Neural Network Training Runtime"; fi
git push origin HEAD; git push origin v3.34.0
echo "PASS: Workspace v3.34.0 applied, validated, packaged, committed, pushed, and tagged"
