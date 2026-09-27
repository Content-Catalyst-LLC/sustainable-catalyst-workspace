#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(cd "$(dirname "$0")" && pwd)}"; OUT="${2:-$ROOT/dist-v3.22.0.1}"
rm -rf "$OUT"; mkdir -p "$OUT"
cd "$ROOT"
python3 VALIDATE_WORKSPACE_V322001.py "$ROOT"
python3 scripts/generate_typed_client_contracts_v322001.py --check
(cd wordpress && zip -qr "$OUT/sustainable-catalyst-workspace-v3.22.0.1-wordpress-plugin.zip" sustainable-catalyst-workspace)
(cd backend && zip -qr "$OUT/sustainable-catalyst-workspace-backend-v3.22.0.1.zip" . -x '**/__pycache__/*' '.pytest_cache/*' '.env')
zip -qr "$OUT/sustainable-catalyst-workspace-v3.22.0.1-repository.zip" . -x '.git/*' 'dist-v3.22.0.1/*' '**/__pycache__/*' '.pytest_cache/*' '**/.env'
echo "Created v3.22.0.1 package set in $OUT"
