#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python=${1:?Pass an absolute path to the Python interpreter with Workspace requirements and pytest installed}
evidence=${2:?Pass an evidence output directory}
mkdir -p "$evidence"
evidence=$(cd "$evidence" && pwd)
scratch=$(mktemp -d /tmp/sc-repro.XXXXXXXX)
image=$(docker image inspect --format '{{.Id}}' "${SC_REPRODUCTION_POSTGRES_IMAGE:-postgres:16-alpine}")
container=$(docker run --rm -d -p 127.0.0.1::5432 -e POSTGRES_USER=sc_repro_test -e POSTGRES_PASSWORD=disposable-synthetic-only "$image")
trap 'docker rm -f "$container" >/dev/null; rm -rf "$scratch"' EXIT
for i in {1..60}; do
  if docker exec "$container" pg_isready -h 127.0.0.1 -U sc_repro_test >/dev/null; then break; fi
  sleep 1
done
endpoint=$(docker port "$container" 5432/tcp)
docker image inspect --format '{{.Id}} {{json .RepoDigests}} {{.Os}}/{{.Architecture}}' "$image" > "$evidence/postgres-image.txt"
docker exec "$container" psql -U sc_repro_test -Atc 'SHOW server_version' > "$evidence/postgres-version.txt"
git rev-parse HEAD > "$evidence/source-commit.txt"
"$python" --version > "$evidence/python-version.txt"
"$python" -m pip freeze > "$evidence/python-dependencies.txt"
env -i PATH="$PATH" PYTHONPATH="$PWD/backend" SC_REPRODUCTION_TEST_POSTGRES=1 \
  SC_WORKSPACE_DATABASE_URL="postgresql+psycopg://sc_repro_test:disposable-synthetic-only@$endpoint/sc_repro_test" \
  SC_WORKSPACE_OBJECT_STORAGE_ROOT="$scratch/objects" SC_WORKSPACE_SERVICE_TOKEN=isolated-replay-test-token \
  "$python" -m pytest -vv --disable-warnings --junitxml="$evidence/test-results.xml" \
  backend/tests/test_reproduction_integrity_postgres.py \
  backend/tests/test_scientific_execution_provenance_workspace_v3400.py \
  backend/tests/test_cross_runtime_verification_v2170.py | tee "$evidence/pytest-log.txt"
