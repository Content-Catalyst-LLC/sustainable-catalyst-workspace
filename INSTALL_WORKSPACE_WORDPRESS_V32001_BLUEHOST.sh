#!/usr/bin/env bash
set -euo pipefail
ZIP="${1:-$HOME/sustainable-catalyst-workspace-v3.20.0.1-wordpress-plugin.zip}"
WP_ROOT="${2:-$HOME/public_html}"
PLUGIN="$WP_ROOT/wp-content/plugins/sustainable-catalyst-workspace"
STAMP="$(date +%Y%m%d-%H%M%S)"
TMP="/tmp/sc-workspace-v32001-$STAMP"
BACKUP="$WP_ROOT/wp-content/plugins/sustainable-catalyst-workspace.backup-$STAMP"

[[ -f "$ZIP" ]] || { echo "ERROR: plugin ZIP not found: $ZIP" >&2; exit 1; }
[[ -d "$WP_ROOT/wp-content/plugins" ]] || { echo "ERROR: WordPress root not found: $WP_ROOT" >&2; exit 1; }
mkdir -p "$TMP"
unzip -q "$ZIP" -d "$TMP"
SRC="$TMP/sustainable-catalyst-workspace"
[[ -d "$SRC" ]] || { echo "ERROR: plugin directory missing inside ZIP: $SRC" >&2; exit 1; }

if [[ -d "$PLUGIN" ]]; then
  cp -a "$PLUGIN" "$BACKUP"
  echo "BACKUP=$BACKUP"
fi
mkdir -p "$PLUGIN"
cp -a "$SRC"/. "$PLUGIN"/

php -l "$PLUGIN/sustainable-catalyst-workspace.php"
php -l "$PLUGIN/includes/class-sc-workspace.php"
php -l "$PLUGIN/includes/class-sc-workspace-deployment.php"

cd "$WP_ROOT"
wp cache flush || true
wp transient delete --all || true
wp eval '
$preflight = SC_Workspace_Deployment_Hardening::preflight();
echo json_encode($preflight, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . PHP_EOL;
if (empty($preflight["ok"])) { exit(3); }
'

echo "PASS: Workspace WordPress v3.20.0.1 installed and stable-package preflight passed"
