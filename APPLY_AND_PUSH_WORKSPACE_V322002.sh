#!/usr/bin/env bash
set -euo pipefail
TARGET="${1:-$HOME/Downloads/sustainable-catalyst-workspace}"
HERE="$(cd "$(dirname "$0")" && pwd)"; PAYLOAD="$HERE/payload"
[[ -d "$TARGET/.git" ]] || { echo "ERROR: Workspace git repository not found: $TARGET" >&2; exit 1; }
[[ -d "$PAYLOAD" ]] || { echo "ERROR: v3.22.0.2 payload missing: $PAYLOAD" >&2; exit 1; }
python3 "$HERE/APPLY_WORKSPACE_V322002.py" "$TARGET" --payload "$PAYLOAD"
cd "$TARGET"
python3 VALIDATE_WORKSPACE_V322002.py "$TARGET"
python3 scripts/generate_typed_client_contracts_v322002.py --check
python3 -m py_compile backend/app/config.py backend/app/client_contracts.py backend/app/polyglot.py backend/neural-runtime/service.py
if python3 -c 'import torch, numpy' >/dev/null 2>&1; then
  PYTHONPATH=backend python3 -m pytest -q \
    backend/tests/test_neural_runtime_foundation_v32000.py \
    backend/tests/test_neural_dataset_interchange_v32100.py \
    backend/tests/test_neural_training_runtime_v32200.py \
    backend/tests/test_neural_training_runtime_v322001.py \
    backend/tests/test_neural_training_runtime_v322002.py
else
  echo "NOTE: local PyTorch/NumPy unavailable; hardened identity/cache training certification will run in the Contabo Docker runtime."
fi
if command -v php >/dev/null 2>&1; then
  php -l wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php
  php -l wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php
  php -l wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-deployment.php
fi
git status --short
git add -A
if git diff --cached --quiet; then echo "No repository changes to commit."; else git commit -m "Workspace v3.22.0.2 — Hardened Neural Runtime Identity & Cache Repair"; fi
if git rev-parse -q --verify refs/tags/v3.22.0.2 >/dev/null; then
  [[ "$(git rev-list -n 1 v3.22.0.2)" == "$(git rev-parse HEAD)" ]] || { echo "ERROR: tag v3.22.0.2 exists on another commit" >&2; exit 1; }
else
  git tag -a v3.22.0.2 -m "Workspace v3.22.0.2 — Hardened Neural Runtime Identity & Cache Repair"
fi
git push origin HEAD
git push origin v3.22.0.2
echo "PASS: Workspace v3.22.0.2 applied, validated, committed, pushed, and tagged"
