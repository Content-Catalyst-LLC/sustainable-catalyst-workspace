#!/usr/bin/env bash
set -euo pipefail
BASE="${1:-https://sustainablecatalyst.com}"
BASE="${BASE%/}"
health="$(curl -fsSL --max-time 20 "$BASE/wp-json/sc-workspace/v1/health")"
cert="$(curl -fsSL --max-time 20 "$BASE/wp-json/sc-workspace/v1/production-certification-contract")"
printf '%s' "$health" | grep -Eq '"(version|workspace_version)"[[:space:]]*:[[:space:]]*"0\.82\.0"' || { echo 'FAIL - live health does not identify v0.82.0'; exit 1; }
printf '%s' "$cert" | grep -Eq '"workspace_version"[[:space:]]*:[[:space:]]*"0\.82\.0"' || { echo 'FAIL - production certification contract does not identify v0.82.0'; exit 1; }
printf '%s' "$cert" | grep -q '"production_certification_requires_live_field_checks":true' || { echo 'FAIL - live certification boundary missing'; exit 1; }
echo 'PASS - live REST identity reports Workspace v0.82.0'
echo 'NOTE - public-page, cache, project-preservation, and rollback rehearsal checks remain manual.'
