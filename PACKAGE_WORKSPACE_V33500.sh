#!/usr/bin/env bash
set -Eeuo pipefail
TARGET="${1:-$HOME/Downloads/sustainable-catalyst-workspace}"; OUT="${2:-$(pwd)}"; [[ -d "$TARGET/backend" ]] || { echo "ERROR: Workspace backend missing" >&2; exit 1; }; mkdir -p "$OUT"
B="$OUT/sustainable-catalyst-workspace-backend-v3.35.0.zip"; P="$OUT/sustainable-catalyst-workspace-v3.35.0-wordpress-plugin.zip"; R="$OUT/sustainable-catalyst-workspace-v3.35.0-repository.zip"; rm -f "$B" "$P" "$R"
(cd "$TARGET/backend" && zip -qr "$B" . -x '*.pyc' '__pycache__/*' '*/__pycache__/*')
if [[ -d "$TARGET/wordpress/sustainable-catalyst-workspace" ]]; then (cd "$TARGET/wordpress" && zip -qr "$P" sustainable-catalyst-workspace -x '*/.DS_Store' '*.pyc' '*/__pycache__/*'); fi
(cd "$TARGET" && zip -qr "$R" . -x '.git/*' '.git/**' 'dist/*' '*.pyc' '*/__pycache__/*' '*/.DS_Store')
echo "PACKAGED_WORKSPACE_V33500_BACKEND=$B"; [[ -f "$P" ]] && echo "PACKAGED_WORKSPACE_V33500_WORDPRESS=$P"; echo "PACKAGED_WORKSPACE_V33500_REPOSITORY=$R"
