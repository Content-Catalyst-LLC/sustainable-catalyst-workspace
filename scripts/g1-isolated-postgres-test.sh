#!/usr/bin/env bash
# Runs only on a developer Mac with Docker Desktop; never contacts production.
set -euo pipefail
cd "$(dirname "$0")/.."
command -v docker >/dev/null
command -v python3.12 >/dev/null || { echo "Python 3.12 required (brew install python@3.12)"; exit 1; }
test -f backend/tests/test_wxr_private_projects.py
if docker container inspect sc-g1-cert-pg >/dev/null 2>&1; then
  echo "STOP: sc-g1-cert-pg already exists; refusing to reuse or delete any database."
  exit 1
fi
docker run -d --name sc-g1-cert-pg --network sc-reporting-g1-net -p 127.0.0.1:55432:5432 \
  -e POSTGRES_USER=recovery_test -e POSTGRES_PASSWORD=sc_g1_disposable_only \
  -e POSTGRES_DB=sc_recovery_test \
  --health-cmd='pg_isready -U recovery_test -d sc_recovery_test' \
  --health-interval=3s --health-retries=20 postgres:18 >/dev/null
for attempt in $(seq 1 30); do
  status="$(docker inspect -f '{{.State.Health.Status}}' sc-g1-cert-pg)"
  [ "$status" = healthy ] && break
  sleep 2
done
[ "$(docker inspect -f '{{.State.Health.Status}}' sc-g1-cert-pg)" = healthy ] || { docker logs --tail 30 sc-g1-cert-pg; exit 1; }
docker exec sc-g1-cert-pg psql -U recovery_test -d sc_recovery_test -v ON_ERROR_STOP=1 \
  -c 'CREATE DATABASE sc_recovery_rehearsal OWNER recovery_test;' >/dev/null
if [ ! -d .venv-g1 ]; then python3.12 -m venv .venv-g1; fi
. .venv-g1/bin/activate
python -m pip install -r backend/requirements.txt pytest >/dev/null
export SC_RECOVERY_TEST_DATABASE_URL='postgresql+psycopg://recovery_test:sc_g1_disposable_only@127.0.0.1:55432/sc_recovery_test'
export SC_RECOVERY_PG_CONTAINER=sc-g1-cert-pg
export PYTHONPATH="$PWD/backend:$PWD/backend/tests"
echo "=== G1 PostgreSQL concurrent saves and DB/object restore ==="
python -m pytest -q backend/tests/test_wxr_private_projects.py::test_postgres_concurrent_duplicate_upload_serializes
echo "=== G1 controlled recovery and authorization (PostgreSQL) ==="
python -m pytest -q backend/tests/test_controlled_recovery.py
echo "=== G1 signed-session project authorization (SQLite fixture) ==="
unset SC_RECOVERY_TEST_DATABASE_URL SC_RECOVERY_PG_CONTAINER
python -m pytest -q backend/tests/test_wxr_private_projects.py -k 'not postgres'
echo "=== G1 Reporting Studio integration and authorization (SQLite fixture) ==="
python -m pytest -q backend/tests/test_research_reporting.py
echo "G1 TEST COMMANDS PASS; validate full logs and cleanup separately."
echo "The disposable sc-g1-cert-pg container is still running for inspection."
