#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$HOME/Downloads/sustainable-catalyst-workspace}"
OUT="${2:-$PWD}"
cd "$ROOT"
rm -f "$OUT/sustainable-catalyst-workspace-backend-v3.39.0.1.zip" "$OUT/sustainable-catalyst-workspace-v3.39.0.1-wordpress-plugin.zip" "$OUT/sustainable-catalyst-workspace-v3.39.0.1-repository.zip"
( cd backend && zip -qr "$OUT/sustainable-catalyst-workspace-backend-v3.39.0.1.zip" . )
( cd wordpress && zip -qr "$OUT/sustainable-catalyst-workspace-v3.39.0.1-wordpress-plugin.zip" sustainable-catalyst-workspace )
zip -qr "$OUT/sustainable-catalyst-workspace-v3.39.0.1-repository.zip" . -x '.git/*' '.workspace-release-backups/*'
echo "PACKAGED_WORKSPACE_V339001_BACKEND=$OUT/sustainable-catalyst-workspace-backend-v3.39.0.1.zip"
echo "PACKAGED_WORKSPACE_V339001_WORDPRESS=$OUT/sustainable-catalyst-workspace-v3.39.0.1-wordpress-plugin.zip"
echo "PACKAGED_WORKSPACE_V339001_REPOSITORY=$OUT/sustainable-catalyst-workspace-v3.39.0.1-repository.zip"
