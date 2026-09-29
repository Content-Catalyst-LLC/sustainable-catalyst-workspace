#!/usr/bin/env bash
set -Eeuo pipefail
TARGET="${1:-$HOME/Downloads/sustainable-catalyst-workspace}"; OUT="${2:-$(pwd)}"
cd "$TARGET"
rm -f "$OUT/sustainable-catalyst-workspace-backend-v3.40.0.zip" "$OUT/sustainable-catalyst-workspace-v3.40.0-wordpress-plugin.zip" "$OUT/sustainable-catalyst-workspace-v3.40.0-repository.zip"
( cd backend && zip -qr "$OUT/sustainable-catalyst-workspace-backend-v3.40.0.zip" . -x '*.pyc' '__pycache__/*' '.pytest_cache/*' )
( cd wordpress && zip -qr "$OUT/sustainable-catalyst-workspace-v3.40.0-wordpress-plugin.zip" sustainable-catalyst-workspace )
zip -qr "$OUT/sustainable-catalyst-workspace-v3.40.0-repository.zip" . -x '.git/*' '.workspace-release-backups/*' '*.pyc' '*/__pycache__/*' '*/.pytest_cache/*'
echo "PACKAGED_WORKSPACE_V34000_BACKEND=$OUT/sustainable-catalyst-workspace-backend-v3.40.0.zip"
echo "PACKAGED_WORKSPACE_V34000_WORDPRESS=$OUT/sustainable-catalyst-workspace-v3.40.0-wordpress-plugin.zip"
echo "PACKAGED_WORKSPACE_V34000_REPOSITORY=$OUT/sustainable-catalyst-workspace-v3.40.0-repository.zip"
