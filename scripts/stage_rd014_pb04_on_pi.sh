#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ssh catalyst-persistent 'mkdir -p "$HOME/rd014-pb04-stage/backend/app" "$HOME/rd014-pb04-stage/tests"'
scp "$ROOT/backend/app/rd014_publication_records.py" catalyst-persistent:~/rd014-pb04-stage/backend/app/
scp "$ROOT/backend/tests/test_rd014_publication_records.py" catalyst-persistent:~/rd014-pb04-stage/tests/test_rd014_publications.py
scp "$ROOT/docs/RD-01.4-PB04-TEST-REQUIREMENTS.txt" catalyst-persistent:~/rd014-pb04-stage/requirements-test.txt
ssh catalyst-persistent 'bash -se' <<'PI'
set -euo pipefail
cd "$HOME/rd014-pb04-stage"
python3 -m venv .venv
PIP_CONFIG_FILE=/dev/null PIP_INDEX_URL=https://pypi.org/simple PIP_DEFAULT_TIMEOUT=120 PIP_RETRIES=8 .venv/bin/python -m pip install -q --disable-pip-version-check -r requirements-test.txt
.venv/bin/python -m pytest -q tests/test_rd014_publications.py --disable-warnings
.venv/bin/python -m py_compile backend/app/rd014_publication_records.py
echo PB04_PI_STAGE=PASS
echo PB04_PRODUCTION_CHANGES=NONE
PI
