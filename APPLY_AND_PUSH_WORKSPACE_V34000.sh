#!/usr/bin/env bash
set -Eeuo pipefail
TARGET="${1:-$HOME/Downloads/sustainable-catalyst-workspace}"; ROOT="$(cd "$(dirname "$0")" && pwd)"
python3 "$ROOT/APPLY_WORKSPACE_V34000.py" "$TARGET"
python3 "$ROOT/VALIDATE_WORKSPACE_V34000.py" "$TARGET"
PY=""
for C in "${SC_WORKSPACE_PYTHON:-}" python3.12 /opt/homebrew/opt/python@3.12/bin/python3.12 python3; do
 [[ -n "$C" ]] || continue
 if command -v "$C" >/dev/null 2>&1 && "$C" - <<'PYCODE' >/dev/null 2>&1
import fastapi,pydantic,pytest,torch,numpy
PYCODE
 then PY="$C"; break; fi
done
if [[ -n "$PY" ]]; then
 echo "WORKSPACE_V34000_TEST_PYTHON=$($PY --version 2>&1)"
 cd "$TARGET/backend"
 "$PY" -m pytest -q \
  tests/test_neural_gnn_runtime_foundation_v33300.py \
  tests/test_neural_gnn_training_runtime_v33400.py \
  tests/test_neural_gnn_evaluation_explainability_embeddings_v33500.py \
  tests/test_neural_computer_vision_remote_sensing_v33600.py \
  tests/test_neural_temporal_sequence_models_v33700.py \
  tests/test_neural_multimodal_runtime_v33800.py \
  tests/test_neural_symbolic_research_intelligence_v33900.py \
  tests/test_neural_symbolic_artifact_persistence_v339001.py \
  tests/test_reproducible_deep_learning_research_packages_v34000.py
else
 echo 'NOTE: compatible local Python test environment unavailable; executable certification will run in Contabo Docker.'
fi
if command -v php >/dev/null 2>&1; then php -l "$TARGET/wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php"; php -l "$TARGET/wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php"; fi
"$ROOT/PACKAGE_WORKSPACE_V34000.sh" "$TARGET" "$ROOT"
cd "$TARGET"; git add -A
if ! git diff --cached --quiet; then git commit -m 'Workspace v3.40.0 — Reproducible Deep Learning Research Packages'; fi
git push origin HEAD:main
if git rev-parse -q --verify refs/tags/v3.40.0 >/dev/null; then [[ "$(git rev-list -n1 v3.40.0)" == "$(git rev-parse HEAD)" ]] || { echo 'ERROR: existing v3.40.0 tag points elsewhere' >&2; exit 1; }; else git tag -a v3.40.0 -m 'Workspace v3.40.0 — Reproducible Deep Learning Research Packages'; fi
git push origin v3.40.0
echo 'PASS: Workspace v3.40.0 applied, validated, packaged, committed, pushed, and tagged'
