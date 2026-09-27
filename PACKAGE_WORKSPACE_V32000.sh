#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(cd "$(dirname "$0")" && pwd)}"
OUT="${2:-$ROOT/dist-v3.20.0}"
mkdir -p "$OUT"
cd "$ROOT"
find . -type d -name '__pycache__' -prune -exec rm -rf {} + 2>/dev/null || true
rm -rf .pytest_cache
(cd backend && zip -qr "$OUT/sustainable-catalyst-workspace-backend-v3.20.0.zip" . -x '.env' '**/__pycache__/*' '.pytest_cache/*')
zip -qr "$OUT/sustainable-catalyst-workspace-v3.20.0-wordpress-plugin.zip" wordpress/sustainable-catalyst-workspace
zip -qr "$OUT/sustainable-catalyst-workspace-v3.20.0-repository.zip" . -x '.git/*' 'dist-v3.20.0/*' '**/__pycache__/*' '.pytest_cache/*'
echo "Created package set in $OUT"
