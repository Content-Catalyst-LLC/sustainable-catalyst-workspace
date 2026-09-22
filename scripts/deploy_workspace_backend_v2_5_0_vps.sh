#!/usr/bin/env bash
set -euo pipefail

ZIP_PATH="${1:-/tmp/sustainable-catalyst-workspace-backend-v2.5.0.zip}"
BASE="/opt/sustainable-catalyst"
NEW="$BASE/sustainable-catalyst-workspace-backend-v2.5.0"

if [[ ! -f "$ZIP_PATH" ]]; then
  echo "ERROR: backend ZIP not found: $ZIP_PATH" >&2
  exit 1
fi

ENV_SOURCE=""
for candidate in \
  "$BASE/sustainable-catalyst-workspace-backend-v2.4.0/.env" \
  "$BASE/sustainable-catalyst-workspace-backend-v2.3.0/.env" \
  "$BASE/sustainable-catalyst-workspace-backend-v2.2.0/.env" \
  "$BASE/sustainable-catalyst-workspace-backend-v2.1.0/.env"
do
  if [[ -f "$candidate" ]]; then ENV_SOURCE="$candidate"; break; fi
done
if [[ -z "$ENV_SOURCE" ]]; then
  echo "ERROR: no prior Workspace backend .env found under $BASE" >&2
  exit 1
fi

if ! docker ps --format '{{.Names}}' | grep -qx 'sc-postgres'; then
  echo "ERROR: sc-postgres is not running." >&2
  exit 1
fi

if ! docker volume inspect sc-workspace-data >/dev/null 2>&1; then
  docker volume create sc-workspace-data >/dev/null
fi

echo "=== WORKSPACE BACKEND v2.5.0 UPGRADE ==="
echo "Credential source: $(dirname "$ENV_SOURCE")"
rm -rf "$NEW"
unzip -q "$ZIP_PATH" -d "$BASE"
cp "$ENV_SOURCE" "$NEW/.env"
chmod 600 "$NEW/.env"

cd "$NEW"
cp docker-compose.example.yml docker-compose.yml

grep -q '^SC_WORKSPACE_MAX_EXECUTION_ENVIRONMENTS_PER_ACCOUNT=' .env || echo 'SC_WORKSPACE_MAX_EXECUTION_ENVIRONMENTS_PER_ACCOUNT=500' >> .env
for name in CORE LAB WORKBENCH DECISION_STUDIO LIBRARY SITE_INTELLIGENCE; do
  grep -q "^SC_WORKSPACE_ROUTE_${name}_URL=" .env || echo "SC_WORKSPACE_ROUTE_${name}_URL=" >> .env
  grep -q "^SC_WORKSPACE_ROUTE_${name}_TOKEN=" .env || echo "SC_WORKSPACE_ROUTE_${name}_TOKEN=" >> .env
done

echo "=== APPLY ADDITIVE POSTGRESQL MIGRATIONS ==="
PG_ADMIN_USER="$(
  docker inspect sc-postgres \
    --format '{{range .Config.Env}}{{println .}}{{end}}' \
  | awk -F= '$1=="POSTGRES_USER"{print $2}' \
  | tail -1
)"
PG_ADMIN_USER="${PG_ADMIN_USER:-postgres}"
echo "PostgreSQL admin role: ${PG_ADMIN_USER}"

for migration in \
  migrations/002_persistence_hardening.sql \
  migrations/003_background_jobs_orchestration.sql \
  migrations/004_dataset_model_execution_run_registry.sql \
  migrations/005_reproducible_execution_environments.sql
do
  echo "Applying ${migration}"
  docker exec -i sc-postgres \
    psql -U "$PG_ADMIN_USER" -d sc_workspace -v ON_ERROR_STOP=1 \
    < "$migration" >/dev/null
  echo "PASS: ${migration}"
done

echo "=== VERIFY REGISTRY PRIVILEGES ==="
docker exec -i sc-postgres psql -U "$PG_ADMIN_USER" -d sc_workspace -v ON_ERROR_STOP=1 -tAc \
  "SELECT count(*) FROM information_schema.role_table_grants WHERE grantee='sc_workspace' AND table_name IN ('workspace_dataset_heads','workspace_model_heads','workspace_execution_runs','workspace_execution_environment_heads') AND privilege_type='INSERT';" \
  | grep -q '^4$' || { echo 'ERROR: sc_workspace registry INSERT privileges are incomplete.' >&2; exit 1; }
echo "PASS: v2.4/v2.5 registry privileges"

echo "=== STOP PRIOR WORKSPACE API / WORKER ==="
docker rm -f sc-workspace-worker 2>/dev/null || true
docker rm -f sc-workspace-backend 2>/dev/null || true

echo "=== BUILD + START v2.5.0 API AND WORKER ==="
docker compose --env-file .env -f docker-compose.yml up -d --build

echo "=== WAIT FOR API HEALTH ==="
for i in $(seq 1 30); do
  code="$(curl -sS -o /tmp/sc-workspace-v250-health.json -w '%{http_code}' http://127.0.0.1:8094/health 2>/dev/null || true)"
  echo "attempt $i: HTTP ${code:-000}"
  [[ "$code" == "200" ]] && break
  sleep 2
done
python3 -m json.tool /tmp/sc-workspace-v250-health.json
python3 - <<'PYHEALTH'
import json
d=json.load(open('/tmp/sc-workspace-v250-health.json'))
assert d.get('ok') is True
assert d.get('version') == '2.5.0'
for key in ('executionEnvironmentRegistry','dependencyManifests','runtimeVersionCapture','randomSeedCapture'):
    assert d.get(key) is True, key
PYHEALTH

echo "=== READINESS ==="
curl -fsS http://127.0.0.1:8094/ready | python3 -m json.tool

set -a
. ./.env
set +a
AUTH=( -H "Authorization: Bearer ${SC_WORKSPACE_SERVICE_TOKEN}" -H "X-SC-User-ID: 999999999999" )

echo "=== CAPABILITIES ==="
curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/capabilities > /tmp/sc-workspace-v250-capabilities.json
python3 -m json.tool /tmp/sc-workspace-v250-capabilities.json
python3 - <<'PYCAPS'
import json
d=json.load(open('/tmp/sc-workspace-v250-capabilities.json'))
for key in ('executionEnvironmentRegistry','executionEnvironmentRevisionHistory','dependencyManifests','dependencyLockArtifacts','containerIdentityCapture','runtimeVersionCapture','randomSeedCapture'):
    assert d.get(key) is True, key
assert d.get('secretEnvironmentValuesCaptured') is False
PYCAPS

echo "=== WORKER HEARTBEAT ==="
for i in $(seq 1 20); do
  curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/worker/status > /tmp/sc-workspace-v250-worker.json
  if python3 - <<'PYWORKER'
import json
d=json.load(open('/tmp/sc-workspace-v250-worker.json'))
raise SystemExit(0 if any(x.get('version')=='2.5.0' and x.get('status') in ('idle','running') for x in d.get('items',[])) else 1)
PYWORKER
  then break; fi
  echo "waiting for v2.5.0 worker heartbeat: $i"
  sleep 2
done
python3 -m json.tool /tmp/sc-workspace-v250-worker.json

STAMP="$(date +%s)"
ENV_ID="deploy-v250-env-${STAMP}"
DATASET_ID="deploy-v250-dataset-${STAMP}"
MODEL_ID="deploy-v250-model-${STAMP}"
PARAM_ID="deploy-v250-params-${STAMP}"
RUN_ID="deploy-v250-run-${STAMP}"

echo "=== CREATE EXECUTION ENVIRONMENT ==="
cat > /tmp/sc-workspace-v250-environment.json <<JSONENV
{"schema":"sc-workspace-execution-environment/1.0","environmentId":"${ENV_ID}","name":"v2.5 deployment smoke environment","runtime":{"language":"python","version":"3.12"},"dependencies":{"manager":"pip","manifest":"requirements.txt"},"container":{"image":"python:3.12-slim","digest":"deployment-smoke"},"system":{"os":"linux","architecture":"x86_64"},"hardware":{"cpuClass":"generic"},"randomSeeds":{"python":42},"environmentVariableNames":["OMP_NUM_THREADS"],"configuration":{"deterministic":true},"expectedRevision":0,"metadata":{"deploymentSmoke":true}}
JSONENV
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/sc-workspace-v250-environment.json http://127.0.0.1:8094/v1/execution-environments > /tmp/sc-workspace-v250-environment-created.json
python3 -m json.tool /tmp/sc-workspace-v250-environment-created.json
ENV_FP="$(python3 - <<'PYENVFP'
import json
x=json.load(open('/tmp/sc-workspace-v250-environment-created.json'))['item']
assert x['revision']==1
assert len(x['fingerprint'])==64
assert x['secretsCaptured'] is False
print(x['fingerprint'])
PYENVFP
)"

cat > /tmp/sc-workspace-v250-dataset.json <<JSONDATA
{"schema":"sc-workspace-dataset-record/1.0","datasetId":"${DATASET_ID}","name":"v2.5 deployment smoke dataset","datasetType":"table","sourceKind":"generated","expectedRevision":0,"metadata":{"deploymentSmoke":true}}
JSONDATA
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/sc-workspace-v250-dataset.json http://127.0.0.1:8094/v1/datasets >/tmp/sc-workspace-v250-dataset-created.json

cat > /tmp/sc-workspace-v250-model.json <<JSONMODEL
{"schema":"sc-workspace-model-record/1.0","modelId":"${MODEL_ID}","name":"v2.5 deployment smoke model","modelKind":"custom","executionTarget":"workspace","executionOperation":"workspace.echo","expectedRevision":0,"metadata":{"deploymentSmoke":true}}
JSONMODEL
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/sc-workspace-v250-model.json http://127.0.0.1:8094/v1/models >/tmp/sc-workspace-v250-model-created.json

cat > /tmp/sc-workspace-v250-params.json <<JSONPARAM
{"schema":"sc-workspace-parameter-set/1.0","parameterSetId":"${PARAM_ID}","modelId":"${MODEL_ID}","name":"v2.5 deployment smoke parameters","parameters":{"value":42},"expectedRevision":0,"metadata":{"deploymentSmoke":true}}
JSONPARAM
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/sc-workspace-v250-params.json http://127.0.0.1:8094/v1/parameter-sets >/tmp/sc-workspace-v250-params-created.json

echo "=== CREATE ENVIRONMENT-PINNED EXECUTION RUN ==="
cat > /tmp/sc-workspace-v250-run.json <<JSONRUN
{"schema":"sc-workspace-execution-run/1.0","runId":"${RUN_ID}","name":"v2.5 deployment smoke run","datasetRefs":[{"datasetId":"${DATASET_ID}"}],"modelRef":{"modelId":"${MODEL_ID}"},"parameterSetRef":{"parameterSetId":"${PARAM_ID}"},"environmentRef":{"environmentId":"${ENV_ID}","revision":1},"environment":{"capture":"deployment-smoke"},"idempotencyKey":"deploy-v250-run-${STAMP}"}
JSONRUN
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/sc-workspace-v250-run.json http://127.0.0.1:8094/v1/runs > /tmp/sc-workspace-v250-run-created.json
python3 -m json.tool /tmp/sc-workspace-v250-run-created.json
python3 - <<PYRUN
import json
d=json.load(open('/tmp/sc-workspace-v250-run-created.json'))['item']
assert d['environmentRef']['environmentId']=='${ENV_ID}'
assert d['environmentRef']['revision']==1
assert d['environmentFingerprint']=='${ENV_FP}'
assert len(d['inputFingerprint'])==64
PYRUN

cat > /tmp/sc-workspace-v250-job.json <<JSONJOB
{"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.echo","executionRunId":"${RUN_ID}","priority":9,"maxAttempts":1,"idempotencyKey":"deploy-v250-job-${STAMP}","payload":{"deploymentSmoke":true,"version":"2.5.0"}}
JSONJOB
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/sc-workspace-v250-job.json http://127.0.0.1:8094/v1/jobs > /tmp/sc-workspace-v250-job-created.json
JOB_ID="$(python3 - <<'PYJOB'
import json
print(json.load(open('/tmp/sc-workspace-v250-job-created.json'))['item']['jobId'])
PYJOB
)"

echo "=== LINKED JOB/RUN SMOKE: ${JOB_ID} / ${RUN_ID} ==="
STATUS=""
for i in $(seq 1 30); do
  curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${JOB_ID}" > /tmp/sc-workspace-v250-job-status.json
  STATUS="$(python3 - <<'PYSTATUS'
import json
print(json.load(open('/tmp/sc-workspace-v250-job-status.json'))['item']['status'])
PYSTATUS
)"
  echo "job ${JOB_ID}: ${STATUS}"
  [[ "$STATUS" == "succeeded" ]] && break
  [[ "$STATUS" == "failed" || "$STATUS" == "blocked" || "$STATUS" == "cancelled" ]] && break
  sleep 1
done
[[ "$STATUS" == "succeeded" ]] || { echo "ERROR: linked smoke job did not succeed" >&2; exit 1; }

curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/runs/${RUN_ID}" > /tmp/sc-workspace-v250-run-final.json
python3 - <<PYFINAL
import json
d=json.load(open('/tmp/sc-workspace-v250-run-final.json'))['item']
assert d['status']=='succeeded'
assert d['environmentFingerprint']=='${ENV_FP}'
assert d['environmentRef']['revision']==1
print('PASS: execution run retained frozen environment revision/fingerprint')
PYFINAL

echo "=== CONTAINERS ==="
docker ps --filter name=sc-workspace --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
echo "PASS: Workspace backend v2.5.0 API + worker + reproducible execution environment registry are running."
