#!/usr/bin/env bash
# Isolated PB05 v3 browser staging from Mac. No production deployment.
set -euo pipefail
umask 077
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REMOTE='catalystadmin@94.72.113.77'
ZIP="$HOME/Downloads/RD-01.4-PB04-Wexford-Two-Publication-Integration-2026-11-03.zip"
[[ -f "$ZIP" ]] || { echo 'PB05_REQUIRED_PB04_TESTED_ZIP=NOT_FOUND' >&2; exit 2; }
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
unzip -p "$ZIP" RD-01.4-PB04-Wexford-Two-Publication-Integration/backend/app/rd014_publication_records.py \
  > "$TMP/rd014_publication_records.py"
SHA="$(shasum -a 256 "$TMP/rd014_publication_records.py" | awk '{print $1}')"
[[ "$SHA" == '480fa0e797101a1f9662eb5d89de7391ff417bd17936e2e405bee1cac32b4f9c' ]] || {
  echo 'PB05_TESTED_PB04_ZIP_DRIFT=FAIL' >&2; exit 3;
}
scp -q "$ROOT/scripts/PB05_ARCHIVE_FAILED_STAGE_ON_CONTABO.sh" "$REMOTE:~/PB05_ARCHIVE_FAILED_STAGE_ON_CONTABO.sh"
ssh -T "$REMOTE" 'bash "$HOME/PB05_ARCHIVE_FAILED_STAGE_ON_CONTABO.sh"'
ssh -T "$REMOTE" 'mkdir -p "$HOME/rd014-pb05-browser-stage/scripts" "$HOME/rd014-pb05-browser-stage/source"'
scp -q "$TMP/rd014_publication_records.py" "$REMOTE:~/rd014-pb05-browser-stage/"
scp -q "$ROOT/source/pb05_browser_stage.py" "$ROOT/source/pb05_tcp_forward.py" "$REMOTE:~/rd014-pb05-browser-stage/source/"
scp -q "$ROOT/scripts/prepare_overlays.py" "$ROOT/scripts/PB05_START_ON_CONTABO.sh" "$ROOT/scripts/PB05_STOP_TEST_STACK_ON_CONTABO.sh" "$REMOTE:~/rd014-pb05-browser-stage/scripts/"
ssh -T "$REMOTE" 'bash "$HOME/rd014-pb05-browser-stage/scripts/PB05_START_ON_CONTABO.sh"'
