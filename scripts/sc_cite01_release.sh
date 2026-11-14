#!/usr/bin/env bash
# SC-CITE-01 verified release orchestration (Mac/operator side).
# This does NOT rerun the prior 28 unit/contract tests. It requires independently
# executed LIVE staging integration + off-host restore, then uses the existing
# Contabo Studio cutover script. It never invokes the unsafe shared-volume stage.
set -Eeuo pipefail
MODE="${1:---check}"
case "$MODE" in --check|--deploy|--status) ;; *) echo "usage: $0 [--check|--deploy|--status]" >&2; exit 64;; esac
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SSH_TARGET="${SC_CITE01_SSH_TARGET:-catalystadmin@94.72.113.77}"
[[ "$SSH_TARGET" =~ ^[A-Za-z0-9_.-]+@[A-Za-z0-9_.-]+$ ]] || { echo 'Invalid SSH target' >&2; exit 1; }
IMAGE='sc-workspace-reporting:candidate-43be67f'
LIVE='sc-workspace-reporting-live'
ssh_do() { ssh -o BatchMode=yes -o StrictHostKeyChecking=yes "$SSH_TARGET" "$1"; }
die() { echo "NO-GO: $*" >&2; exit 1; }
live_state() {
  ssh_do "docker inspect $LIVE --format '{{.Id}} {{.Config.Image}}'"
}
health() {
  ssh_do 'test "$(curl -sS -o /dev/null -w "%{http_code}" --max-time 5 http://127.0.0.1:20080/health)" = 200'
}
if [[ "$MODE" == --status ]]; then
  live_state
  health || die 'Studio health check failed'
  echo 'PASS: current Studio healthy'
  exit 0
fi

python3 "$HERE/sc_cite01_verify_receipts.py" || die 'Real staging/recovery evidence incomplete'
BASELINE="$(live_state)" || die 'Cannot inspect live Studio'
[[ "$BASELINE" == *'sc-workspace-reporting:prod-5e354cba'* ]] ||
  die 'Live Studio changed since release plan; new baseline acceptance required'
health || die 'Production Studio unhealthy before cutover'
# A Studio cutover alone is not a full Citation Studio release. Require the
# production Research API to load the frozen-bibliography editorial contract.
ssh_do "docker exec rhprod02-research-research-api-1 python -c 'from app import editorial as e; assert getattr(e, \"BIBLIOGRAPHY_SCHEMA\", None) == \"sc-publication-bibliography/1.0\"'" ||
  die 'Research production does not have the required frozen-bibliography contract; deploy Research separately first'
IMAGE_ID="$(ssh_do "docker image inspect '$IMAGE' --format '{{.Id}}'")" ||
  die 'Expected candidate image is not on Contabo'
[[ "$IMAGE_ID" == sha256:* ]] || die 'Candidate image identifier invalid'
[[ "$(live_state)" == "$BASELINE" ]] || die 'Live Studio changed during preflight'
echo "GO-CANDIDATE | live=$BASELINE | image=$IMAGE_ID"
if [[ "$MODE" == --check ]]; then
  echo 'No production changes performed.'
  exit 0
fi
[[ -t 0 ]] || die 'Production cutover requires a real interactive operator terminal'
printf '%s\n' "Deploy exact image $IMAGE ($IMAGE_ID) using the existing protected Studio release script."
read -r -p "Type DEPLOY SC-CITE-01: " ACK
[[ "$ACK" == 'DEPLOY SC-CITE-01' ]] || die 'Operator declined cutover'
[[ "$(live_state)" == "$BASELINE" ]] || die 'Live Studio changed before cutover'
[[ "$(ssh_do "docker image inspect '$IMAGE' --format '{{.Id}}'")" == "$IMAGE_ID" ]] ||
  die 'Candidate tag changed during cutover preflight'

# The existing release script takes a fresh on-host backup and preserves a
# renamed old live container for rollback. The independent off-host restore
# was mandatory above, not assumed from this script.
ssh_do "bash \$HOME/sc-sci02/rd/studio.sh cutover '$IMAGE'" ||
  die 'Cutover command failed (existing script attempts automatic restore)'
rollback() {
  echo 'Post-cutover verification failed: invoking reviewed rollback' >&2
  ssh_do 'bash $HOME/sc-sci02/rd/studio.sh rollback' || die 'URGENT: automatic rollback failed'
  die 'Release rolled back; inspect production logs'
}
health || rollback
NEW_IMAGE="$(ssh_do "docker inspect $LIVE --format '{{.Config.Image}}'")" || rollback
[[ "$NEW_IMAGE" == "$IMAGE" ]] || rollback
# Unauthenticated requests must remain denied. No user data is queried.
for path in \
  '/v1/private-research/reporting-studio/publication/citations/projects/synthetic-release-probe' \
  '/v1/private-research/reporting-studio/publication/citations/library/search?q=synthetic'
do
  status="$(ssh_do "curl -sS -o /dev/null -w '%{http_code}' --max-time 5 'http://127.0.0.1:20080$path'")" || rollback
  [[ "$status" == 401 || "$status" == 403 ]] || rollback
done
echo 'DEPLOYED: Studio candidate healthy and Citation Studio authorization enforced.'
echo 'The Research production service requires its own release/cutover and owner-verified browser acceptance.'
