#!/usr/bin/env bash
# Archive an unsuccessful PB05-only staging directory, never delete user data.
# Refuse if any live PB05 resources or completed-stage record exist.
set -euo pipefail
umask 077
STAGE="$HOME/rd014-pb05-browser-stage"
if [[ ! -d "$STAGE" ]]; then
  echo 'PB05_PREVIOUS_STAGE=NOT_FOUND'
  exit 0
fi
for name in sc-pb05-browser-app sc-pb05-browser-db sc-pb05-browser-proxy; do
  if docker container inspect "$name" >/dev/null 2>&1; then
    echo "PB05_RESTART_HOLD_CONTAINER_PRESENT=$name" >&2; exit 3
  fi
done
for name in sc-pb05-browser-objects sc-pb05-browser-pgdata; do
  if docker volume inspect "$name" >/dev/null 2>&1; then
    echo "PB05_RESTART_HOLD_VOLUME_PRESENT=$name" >&2; exit 3
  fi
done
if docker network inspect sc-pb05-browser-net >/dev/null 2>&1 || docker network inspect sc-pb05-browser-edge-net >/dev/null 2>&1; then
  echo 'PB05_RESTART_HOLD_NETWORK_PRESENT=YES' >&2; exit 3
fi
if [[ -f "$STAGE/secrets/stage-names" ]]; then
  echo 'PB05_RESTART_HOLD_PREVIOUS_START_RECORD_PRESENT=YES' >&2; exit 3
fi
STAMP="$(date -u +%Y%m%dT%H%M%SZ)-$$"
TARGET="$HOME/rd014-pb05-browser-stage-failed-$STAMP"
[[ ! -e "$TARGET" ]] || { echo 'PB05_RESTART_ARCHIVE_COLLISION=YES' >&2; exit 4; }
chmod 700 "$STAGE"
mv -- "$STAGE" "$TARGET"
echo 'PB05_PREVIOUS_FAILED_STAGE=ARCHIVED_NOT_DELETED'
echo 'PB05_PRIOR_TEST_SECRETS=NOT_PRINTED'
echo 'PB05_PRODUCTION_CHANGES=NONE'
