#!/usr/bin/env bash
# Mac operator entry point: one command completes both remaining operational gates
# and, with explicit --deploy confirmation, invokes the guarded Studio cutover.
# Run only with synthetic staging fixtures and encrypted off-host backup storage.
set -Eeuo pipefail
MODE="${1:---check}"
case "$MODE" in --check|--deploy) ;; *) echo 'usage: sc_cite01_operator.sh [--check|--deploy]' >&2; exit 64;; esac
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
for key in \
  SC_CITE01_WORKSPACE_URL SC_CITE01_RESEARCH_URL \
  SC_CITE01_SYNTHETIC_PROJECT_ID SC_CITE01_SYNTHETIC_SOURCE_ID \
  SC_CITE01_SYNTHETIC_RESEARCH_AREA SC_CITE01_SYNTHETIC_RESEARCH_PROJECT_KEY \
  SC_CITE01_VERIFIED_PUBLIC_LIBRARY_ID \
  SC_CITE01_WS_OWNER_A_HEADERS SC_CITE01_WS_OWNER_B_HEADERS \
  SC_CITE01_RH_OWNER_A_HEADERS SC_CITE01_RH_OWNER_B_HEADERS \
  SC_CITE01_BACKUP_DIR SC_CITE01_INTEGRATION_RECEIPT
do
  [[ -n "${!key:-}" ]] || { echo "NO-GO: required local environment variable $key is missing" >&2; exit 1; }
done
[[ "${SC_CITE01_ACCEPT_STAGING:-}" == SYNTHETIC_STAGING_ONLY ]] ||
  { echo 'NO-GO: explicit synthetic staging authorization required' >&2; exit 1; }
[[ "${SC_CITE01_RECOVERY_AUTHORIZATION:-}" == READ_ONLY_PRODUCTION_TO_OFFHOST ]] ||
  { echo 'NO-GO: explicit off-host backup authorization required' >&2; exit 1; }
echo '=== Live staging Workspace -> Research citation acceptance ==='
python3 "$HERE/sc_cite01_integration_gate.py"
echo '=== Independent off-host backup and isolated restore acceptance ==='
python3 "$HERE/sc_cite01_recovery_gate.py"
export SC_CITE01_RECOVERY_RECEIPT="${SC_CITE01_BACKUP_DIR}/sc-cite01-recovery.json"
echo '=== Release receipt verification and guarded Studio cutover ==='
bash "$HERE/sc_cite01_release.sh" "$MODE"
