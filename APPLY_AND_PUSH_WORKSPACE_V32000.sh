#!/usr/bin/env bash
set -euo pipefail
TARGET="${1:-$HOME/Downloads/sustainable-catalyst-workspace}"
HERE="$(cd "$(dirname "$0")" && pwd)"
PAYLOAD="$HERE/payload"
[[ -d "$TARGET/.git" ]] || { echo "ERROR: Workspace git repository not found: $TARGET" >&2; exit 1; }
[[ -d "$PAYLOAD" ]] || { echo "ERROR: v3.20.0 payload missing: $PAYLOAD" >&2; exit 1; }
python3 "$HERE/APPLY_WORKSPACE_V32000.py" "$TARGET" --payload "$PAYLOAD"
cd "$TARGET"
find . -type d -name '__pycache__' -prune -exec rm -rf {} + 2>/dev/null || true
rm -rf .pytest_cache
python3 -m py_compile backend/app/config.py backend/app/polyglot.py backend/app/routing.py backend/app/main.py backend/neural-runtime/service.py
python3 scripts/generate_typed_client_contracts_v32000.py --check
if python3 - <<'PY' >/dev/null 2>&1
import torch
PY
then
  echo "=== LOCAL TARGETED TESTS (PyTorch available) ==="
  PYTHONPATH=backend python3 -m pytest -q \
    backend/tests/test_neural_runtime_foundation_v32000.py \
    backend/tests/test_ml_runtime_v2150.py \
    backend/tests/test_ml_runtime_operations_v2150.py \
    backend/tests/test_predictive_investigation_workspace_v31900.py
else
  echo "NOTE: local PyTorch not installed; neural runtime execution validation will run in the VPS Docker service."
fi

git status --short
git add -A
if git diff --cached --quiet; then
  echo "No repository changes to commit."
else
  git commit -m "Workspace v3.20.0 — Neural Runtime Foundation & PyTorch Adapter"
fi
if git rev-parse -q --verify refs/tags/v3.20.0 >/dev/null; then
  TAG_COMMIT="$(git rev-list -n 1 v3.20.0)"
  HEAD_COMMIT="$(git rev-parse HEAD)"
  [[ "$TAG_COMMIT" == "$HEAD_COMMIT" ]] || { echo "ERROR: tag v3.20.0 already exists on a different commit" >&2; exit 1; }
else
  git tag -a v3.20.0 -m "Workspace v3.20.0 — Neural Runtime Foundation & PyTorch Adapter"
fi
git push origin HEAD
git push origin v3.20.0

echo "PASS: Workspace v3.20.0 applied, committed, pushed, and tagged"
