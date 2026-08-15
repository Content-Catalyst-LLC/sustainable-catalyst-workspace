#!/bin/bash
set -euo pipefail
BASE="${1:-https://sustainablecatalyst.com}"
BASE="${BASE%/}"
fail(){ echo "FAIL - $*" >&2; exit 1; }
command -v curl >/dev/null 2>&1 || fail "curl is required"
health="$(curl -fsS "$BASE/wp-json/sc-workspace/v1/health")"
cert="$(curl -fsS "$BASE/wp-json/sc-workspace/v1/production-certification-contract")"
deploy="$(curl -fsS "$BASE/wp-json/sc-workspace/v1/deployment-hardening-contract")"
printf '%s' "$health" | grep -Eq '"(version|workspace_version)"[[:space:]]*:[[:space:]]*"0\.82\.1"' || fail "live health does not identify v0.82.1"
printf '%s' "$cert" | grep -Eq '"workspace_version"[[:space:]]*:[[:space:]]*"0\.82\.1"' || fail "production certification contract does not identify v0.82.1"
printf '%s' "$deploy" | grep -Eq '"workspace_version"[[:space:]]*:[[:space:]]*"0\.82\.1"' || fail "deployment hardening contract does not identify v0.82.1"
echo 'PASS - live REST identity reports Workspace v0.82.1'
echo 'FIELD - public page, cache coherence, local-project preservation, and v0.81.0 rollback/reinstall rehearsal still require explicit production checks.'
