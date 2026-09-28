#!/usr/bin/env bash
set -euo pipefail
REPO="${1:-$PWD}"; OUT="${2:-$PWD/dist-v3.29.0}"
REPO="$(cd "$REPO" && pwd)"; mkdir -p "$OUT"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
python3 "$REPO/VALIDATE_WORKSPACE_V32900.py" "$REPO"
python3 "$REPO/scripts/generate_typed_client_contracts_v32900.py" --check
mkdir -p "$TMP/backend" "$TMP/plugin/sustainable-catalyst-workspace" "$TMP/repository"
rsync -a --exclude '.env' --exclude '__pycache__' --exclude '.pytest_cache' --exclude '*.pyc' "$REPO/backend/" "$TMP/backend/"
rsync -a --exclude '__pycache__' --exclude '.pytest_cache' --exclude '*.pyc' "$REPO/wordpress/sustainable-catalyst-workspace/" "$TMP/plugin/sustainable-catalyst-workspace/"
rsync -a --exclude '.git' --exclude '.env' --exclude '__pycache__' --exclude '.pytest_cache' --exclude '*.pyc' "$REPO/" "$TMP/repository/"
(cd "$TMP/backend" && zip -qr "$OUT/sustainable-catalyst-workspace-backend-v3.29.0.zip" .)
(cd "$TMP/plugin" && zip -qr "$OUT/sustainable-catalyst-workspace-v3.29.0-wordpress-plugin.zip" sustainable-catalyst-workspace)
(cd "$TMP/repository" && zip -qr "$OUT/sustainable-catalyst-workspace-v3.29.0-repository.zip" .)
echo "PASS: Workspace v3.29.0 backend, WordPress, and repository packages created in $OUT"
