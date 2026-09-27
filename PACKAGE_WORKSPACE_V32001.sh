#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(cd "$(dirname "$0")" && pwd)}"
OUT="${2:-$ROOT/dist-v3.20.0.1}"
mkdir -p "$OUT"
cd "$ROOT"
python3 VALIDATE_WORKSPACE_V32001.py "$ROOT"
find . -type d -name '__pycache__' -prune -exec rm -rf {} + 2>/dev/null || true
rm -rf .pytest_cache

(cd wordpress && zip -qr "$OUT/sustainable-catalyst-workspace-v3.20.0.1-wordpress-plugin.zip" sustainable-catalyst-workspace)
zip -qr "$OUT/sustainable-catalyst-workspace-v3.20.0.1-repository.zip" . \
  -x '.git/*' 'dist-v3.20.0.1/*' '**/__pycache__/*' '.pytest_cache/*'

echo "Created v3.20.0.1 package set in $OUT"
