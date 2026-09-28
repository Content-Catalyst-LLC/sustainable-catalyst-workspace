#!/usr/bin/env bash
set -Eeuo pipefail
TARGET="${1:-$HOME/Downloads/sustainable-catalyst-workspace}"
OUT="${2:-$(pwd)}"
[[ -d "$TARGET/backend" ]] || { echo "ERROR: Workspace backend missing: $TARGET/backend" >&2; exit 1; }
mkdir -p "$OUT"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT

BACKEND_ZIP="$OUT/sustainable-catalyst-workspace-backend-v3.33.0.zip"
PLUGIN_ZIP="$OUT/sustainable-catalyst-workspace-v3.33.0-wordpress-plugin.zip"
REPO_ZIP="$OUT/sustainable-catalyst-workspace-v3.33.0-repository.zip"
rm -f "$BACKEND_ZIP" "$PLUGIN_ZIP" "$REPO_ZIP"
(
  cd "$TARGET/backend"
  zip -qr "$BACKEND_ZIP" . -x '*.pyc' '__pycache__/*' '*/__pycache__/*'
)
if [[ -d "$TARGET/wordpress/sustainable-catalyst-workspace" ]]; then
  (
    cd "$TARGET/wordpress"
    zip -qr "$PLUGIN_ZIP" sustainable-catalyst-workspace -x '*/.DS_Store' '*.pyc' '*/__pycache__/*'
  )
fi
(
  cd "$TARGET"
  zip -qr "$REPO_ZIP" . -x '.git/*' '.git/**' 'dist/*' '*.pyc' '*/__pycache__/*' '*/.DS_Store'
)

echo "PACKAGED_WORKSPACE_V33300_BACKEND=$BACKEND_ZIP"
[[ -f "$PLUGIN_ZIP" ]] && echo "PACKAGED_WORKSPACE_V33300_WORDPRESS=$PLUGIN_ZIP"
echo "PACKAGED_WORKSPACE_V33300_REPOSITORY=$REPO_ZIP"
