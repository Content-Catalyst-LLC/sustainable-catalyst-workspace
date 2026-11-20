#!/usr/bin/env bash
set -euo pipefail
repo=$(cd "$(dirname "$0")/.." && pwd)
cd "$repo"
python=${1:?Pass the absolute path to a Python 3.12 venv with backend requirements and pytest installed}
evidence=${2:?Pass an output directory for execution evidence}
mkdir -p "$evidence"
evidence=$(cd "$evidence" && pwd)
scratch=$(mktemp -d /tmp/sc-run.XXXXXXXX)
container=
pg_bin=
cleanup() {
  if [[ -n "$container" ]]; then
    docker rm -f "$container" >/dev/null
  elif [[ -n "$pg_bin" ]]; then
    "$pg_bin/pg_ctl" -D "$scratch/db" -m fast stop >/dev/null 2>&1 || true
  fi
  rm -rf "$scratch"
}
trap cleanup EXIT
if [[ -n "${SC_RUN_VERIFY_POSTGRES_IMAGE:-}" ]]; then
  image_id=$(docker image inspect --format '{{.Id}}' "$SC_RUN_VERIFY_POSTGRES_IMAGE")
  docker image inspect --format '{{.Id}} {{json .RepoDigests}} {{.Os}}/{{.Architecture}}' "$image_id" > "$evidence/postgres-image.txt"
  container=$(docker run --rm -d -p 127.0.0.1::5432 \
    -e POSTGRES_USER=sc_run_verify -e POSTGRES_DB=postgres \
    -e POSTGRES_PASSWORD=disposable-synthetic-only "$image_id")
  endpoint=$(docker port "$container" 5432/tcp)
  dsn="postgresql+psycopg://sc_run_verify:disposable-synthetic-only@$endpoint/postgres"
  for _ in {1..60}; do
    if docker exec "$container" pg_isready -h 127.0.0.1 -U sc_run_verify -d postgres >/dev/null; then
      break
    fi
    sleep 1
  done
  docker exec "$container" psql -U sc_run_verify -d postgres -Atc 'SHOW server_version' > "$evidence/postgres-version.txt"
else
  pg_bin=$(pg_config --bindir)
  mkdir "$scratch/socket"
  "$pg_bin/initdb" -D "$scratch/db" -U sc_run_verify -A trust --no-locale -E UTF8 > "$evidence/initdb.log"
  "$pg_bin/pg_ctl" -D "$scratch/db" -l "$scratch/postgres.log" \
    -o "-c listen_addresses='' -c unix_socket_directories=$scratch/socket -c unix_socket_permissions=0700" -w start
  dsn="postgresql+psycopg://sc_run_verify@/postgres?host=$scratch/socket"
  "$pg_bin/psql" -h "$scratch/socket" -U sc_run_verify -d postgres -Atc 'SHOW server_version' > "$evidence/postgres-version.txt"
fi
run_python() {
  env -i PATH="$PATH" PYTHONPATH="$repo/backend" \
    SC_WORKSPACE_ENVIRONMENT=test \
    SC_WORKSPACE_AUTO_CREATE_SCHEMA=false \
    SC_WORKSPACE_DATABASE_URL="$dsn" \
    SC_WORKSPACE_OBJECT_STORAGE_ROOT="$scratch/objects" \
    SC_WORKSPACE_SERVICE_TOKEN=local-synthetic-service-token \
    SC_WORKSPACE_SESSION_SIGNING_SECRET=local-synthetic-signing-secret-for-tests-only \
    SC_WORKSPACE_CORS_ALLOWED_ORIGINS=https://workspace.test \
    SC_WORKSPACE_SESSION_REVOCATION_ENFORCED=true \
    SC_RUN_VERIFY_EVIDENCE="$evidence" "$python" "$@"
}
git rev-parse HEAD > "$evidence/source-commit.txt"
run_python --version > "$evidence/python-version.txt"
run_python -m pip freeze > "$evidence/python-dependencies.txt"
run_python -m app.migrate_security | tee "$evidence/schema.txt"
run_python -m app.init_db | tee -a "$evidence/schema.txt"
run_python -m pytest -q -ra --disable-warnings backend/tests/test_sc_run_verify01_postgres.py --junitxml="$evidence/integration.xml" | tee "$evidence/integration.log"
