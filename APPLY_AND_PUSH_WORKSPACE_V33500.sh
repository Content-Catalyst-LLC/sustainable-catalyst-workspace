#!/usr/bin/env bash
set -Eeuo pipefail
TARGET="${1:-$HOME/Downloads/sustainable-catalyst-workspace}"; HERE="$(cd "$(dirname "$0")" && pwd)"
[[ -d "$TARGET/.git" ]] || { echo "ERROR: Workspace git repository not found: $TARGET" >&2; exit 1; }
python3 "$HERE/APPLY_WORKSPACE_V33500.py" "$TARGET" --release-root "$HERE"
python3 "$HERE/VALIDATE_WORKSPACE_V33500.py" "$TARGET"
python3 -m py_compile "$TARGET/backend/app/config.py" "$TARGET/backend/app/main.py" "$TARGET/backend/app/polyglot.py" "$TARGET/backend/neural-runtime/service.py"
if python3 -c 'import torch,numpy,fastapi,pytest' >/dev/null 2>&1; then
  PYTHONPATH="$TARGET/backend" python3 -m pytest -q \
    "$TARGET/backend/tests/test_neural_gnn_runtime_foundation_v33300.py" \
    "$TARGET/backend/tests/test_neural_gnn_training_runtime_v33400.py" \
    "$TARGET/backend/tests/test_neural_gnn_evaluation_explainability_embeddings_v33500.py"
else echo "NOTE: local neural test dependencies unavailable; executable v3.35 certification will run in Contabo Docker."; fi
if command -v php >/dev/null 2>&1 && [[ -f "$TARGET/wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php" ]]; then php -l "$TARGET/wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php"; php -l "$TARGET/wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php"; fi
"$HERE/PACKAGE_WORKSPACE_V33500.sh" "$TARGET" "$HERE"
cd "$TARGET"; git status --short; git add -A
if git diff --cached --quiet; then echo "No repository changes to commit."; else git commit -m "Workspace v3.35.0 — GNN Evaluation, Explainability & Graph Embeddings"; fi
if git rev-parse -q --verify refs/tags/v3.35.0 >/dev/null; then [[ "$(git rev-list -n 1 v3.35.0)" == "$(git rev-parse HEAD)" ]] || { echo "ERROR: tag v3.35.0 exists on another commit" >&2; exit 1; }; else git tag -a v3.35.0 -m "Workspace v3.35.0 — GNN Evaluation, Explainability & Graph Embeddings"; fi
git push origin HEAD; git push origin v3.35.0
echo "PASS: Workspace v3.35.0 applied, validated, packaged, committed, pushed, and tagged"
