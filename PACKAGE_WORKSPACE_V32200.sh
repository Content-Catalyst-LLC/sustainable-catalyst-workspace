#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(cd "$(dirname "$0")" && pwd)}"; OUT="${2:-$ROOT/dist-v3.22.0}"
mkdir -p "$OUT"; cd "$ROOT"
python3 VALIDATE_WORKSPACE_V32200.py "$ROOT"
python3 scripts/generate_typed_client_contracts_v32200.py --check
find . -type d -name '__pycache__' -prune -exec rm -rf {} + 2>/dev/null || true; rm -rf .pytest_cache
(cd wordpress && zip -qr "$OUT/sustainable-catalyst-workspace-v3.22.0-wordpress-plugin.zip" sustainable-catalyst-workspace)
(cd backend && zip -qr "$OUT/sustainable-catalyst-workspace-backend-v3.22.0.zip" . -x '**/__pycache__/*' '.pytest_cache/*' '.env')
zip -qr "$OUT/sustainable-catalyst-workspace-v3.22.0-repository.zip" . -x '.git/*' 'dist-v3.22.0/*' '**/__pycache__/*' '.pytest_cache/*' '**/.env' '_build_v3220.py'
echo "Created v3.22.0 package set in $OUT"
