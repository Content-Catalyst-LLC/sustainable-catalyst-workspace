#!/usr/bin/env bash
# Resume the Reporting Studio fixture suite after the successful G1 PostgreSQL checks.
# Runs only on the developer Mac; no Docker/production/database changes.
set -euo pipefail
cd "$(dirname "$0")/.."
test -d .venv-g1 || { echo "Missing .venv-g1 from previous run"; exit 1; }
command -v node >/dev/null || { echo "Node.js required: brew install node"; exit 1; }
command -v npm >/dev/null || { echo "npm required"; exit 1; }
node -e "if(Number(process.versions.node.split('.')[0])<22)process.exit(2)"
. .venv-g1/bin/activate
python -m pip install -r backend/requirements-reporting.txt jsonschema >/dev/null
npm ci --prefix backend/reporting_math --ignore-scripts --omit=dev
export PYTHONPATH="$PWD/backend:$PWD/backend/tests"
unset SC_RECOVERY_TEST_DATABASE_URL SC_RECOVERY_PG_CONTAINER
echo "=== Pinned local reporting math and heatmap dependencies ==="
node -e "require('./backend/reporting_math/node_modules/mathjax-full/js/mathjax.js');require('./backend/reporting_math/node_modules/jsdom');console.log('Node dependencies PASS')"
echo "=== Reporting Studio local fixture tests ==="
python -m pytest -q backend/tests/test_research_reporting.py
echo "G1 REPORTING FIXTURE TESTS PASS. PostgreSQL tests already passed in prior execution; this rerun does not repeat them."
