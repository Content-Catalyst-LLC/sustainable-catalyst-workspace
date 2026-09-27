#!/usr/bin/env bash
set -euo pipefail
ZIP="${1:-$HOME/sustainable-catalyst-workspace-v3.22.0-wordpress-plugin.zip}"; WP="${2:-$HOME/public_html}"
[[ -f "$ZIP" ]] || { echo "ERROR: plugin zip not found: $ZIP" >&2; exit 1; }
[[ -d "$WP/wp-content/plugins" ]] || { echo "ERROR: WordPress plugins directory not found" >&2; exit 1; }
TARGET="$WP/wp-content/plugins/sustainable-catalyst-workspace"; BACKUP="$HOME/sustainable-catalyst-workspace-backup-$(date +%Y%m%d-%H%M%S)"
[[ -d "$TARGET" ]] && cp -a "$TARGET" "$BACKUP"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT; unzip -q "$ZIP" -d "$TMP"
[[ -f "$TMP/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php" ]] || { echo "ERROR: malformed plugin archive" >&2; exit 1; }
rm -rf "$TARGET"; cp -a "$TMP/sustainable-catalyst-workspace" "$TARGET"
cd "$WP"; wp cache flush || true; wp transient delete --all || true
wp eval '$p=SC_Workspace_Deployment_Hardening::preflight(); echo json_encode($p,JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES).PHP_EOL; if(empty($p["ok"])) { exit(1); }'
echo "PASS: Workspace WordPress v3.22.0 installed with stable-package preflight clean"
echo "Backup: $BACKUP"
