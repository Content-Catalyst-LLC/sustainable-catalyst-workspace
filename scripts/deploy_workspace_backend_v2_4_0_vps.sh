#!/usr/bin/env bash
set -euo pipefail

ZIP_PATH="${1:-/tmp/sustainable-catalyst-workspace-backend-v2.4.0.zip}"
BASE="/opt/sustainable-catalyst"
NEW="$BASE/sustainable-catalyst-workspace-backend-v2.4.0"

if [[ ! -f "$ZIP_PATH" ]]; then
  echo "ERROR: backend zip not found: $ZIP_PATH" >&2
  exit 1
fi

ENV_SOURCE=""
for candidate in \
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

echo "=== WORKSPACE BACKEND v2.4.0 UPGRADE ==="
echo "Credential source: $(dirname "$ENV_SOURCE")"
rm -rf "$NEW"
unzip -q "$ZIP_PATH" -d "$BASE"
cp "$ENV_SOURCE" "$NEW/.env"
chmod 600 "$NEW/.env"

cd "$NEW"
cp docker-compose.example.yml docker-compose.yml

# Add v2.4.0 quota knobs only when absent. Existing credentials and routes are preserved.
grep -q '^SC_WORKSPACE_MAX_DATASETS_PER_ACCOUNT=' .env || echo 'SC_WORKSPACE_MAX_DATASETS_PER_ACCOUNT=500' >> .env
grep -q '^SC_WORKSPACE_MAX_MODELS_PER_ACCOUNT=' .env || echo 'SC_WORKSPACE_MAX_MODELS_PER_ACCOUNT=250' >> .env
grep -q '^SC_WORKSPACE_MAX_PARAMETER_SETS_PER_ACCOUNT=' .env || echo 'SC_WORKSPACE_MAX_PARAMETER_SETS_PER_ACCOUNT=1000' >> .env
grep -q '^SC_WORKSPACE_MAX_EXECUTION_RUNS_PER_ACCOUNT=' .env || echo 'SC_WORKSPACE_MAX_EXECUTION_RUNS_PER_ACCOUNT=5000' >> .env

# Keep route variables additive for older backends that did not yet define them.
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
  migrations/004_dataset_model_execution_run_registry.sql
do
  echo "Applying ${migration}"
  docker exec -i sc-postgres \
    psql -U "$PG_ADMIN_USER" -d sc_workspace -v ON_ERROR_STOP=1 \
    < "$migration" >/dev/null
  echo "PASS: ${migration}"
done

echo "=== STOP PRIOR WORKSPACE API / WORKER ==="
docker rm -f sc-workspace-worker 2>/dev/null || true
docker rm -f sc-workspace-backend 2>/dev/null || true

echo "=== BUILD + START v2.4.0 API AND WORKER ==="
docker compose --env-file .env -f docker-compose.yml up -d --build

echo "=== WAIT FOR API HEALTH ==="
for i in $(seq 1 30); do
  code="$(curl -sS -o /tmp/sc-workspace-v240-health.json -w '%{http_code}' http://127.0.0.1:8094/health 2>/dev/null || true)"
  echo "attempt $i: HTTP ${code:-000}"
  [[ "$code" == "200" ]] && break
  sleep 2
done
python3 -m json.tool /tmp/sc-workspace-v240-health.json
python3 - <<'PY'
import json
p='/tmp/sc-workspace-v240-health.json'
d=json.load(open(p))
assert d.get('ok') is True
assert d.get('version') == '2.4.0'
assert d.get('datasetRegistry') is True
assert d.get('modelRegistry') is True
assert d.get('executionRunRegistry') is True
PY

echo "=== READINESS ==="
curl -fsS http://127.0.0.1:8094/ready | python3 -m json.tool

set -a
. ./.env
set +a
AUTH=( -H "Authorization: Bearer ${SC_WORKSPACE_SERVICE_TOKEN}" -H "X-SC-User-ID: 999999999999" )

echo "=== CAPABILITIES ==="
curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/capabilities > /tmp/sc-workspace-v240-capabilities.json
python3 -m json.tool /tmp/sc-workspace-v240-capabilities.json
python3 - <<'PY'
import json
d=json.load(open('/tmp/sc-workspace-v240-capabilities.json'))
for key in ('datasetRegistry','modelRegistry','parameterSetRegistry','executionRunRegistry','jobExecutionRunLinkage','reproducibilityFingerprints'):
    assert d.get(key) is True, key
PY

echo "=== WORKER HEARTBEAT ==="
for i in $(seq 1 20); do
  curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/worker/status > /tmp/sc-workspace-v240-worker.json
  if python3 - <<'PY'
import json
d=json.load(open('/tmp/sc-workspace-v240-worker.json'))
raise SystemExit(0 if any(x.get('version')=='2.4.0' and x.get('status') in ('idle','running') for x in d.get('items',[])) else 1)
PY
  then break; fi
  echo "waiting for v2.4.0 worker heartbeat: $i"
  sleep 2
done
python3 -m json.tool /tmp/sc-workspace-v240-worker.json

STAMP="$(date +%s)"
DATASET_ID="deploy-v240-dataset-${STAMP}"
MODEL_ID="deploy-v240-model-${STAMP}"
PARAM_ID="deploy-v240-params-${STAMP}"
RUN_ID="deploy-v240-run-${STAMP}"

cat > /tmp/sc-workspace-v240-dataset.json <<JSON
{"schema":"sc-workspace-dataset-record/1.0","datasetId":"${DATASET_ID}","name":"v2.4 deployment smoke dataset","datasetType":"table","sourceKind":"generated","expectedRevision":0,"metadata":{"deploymentSmoke":true}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/sc-workspace-v240-dataset.json http://127.0.0.1:8094/v1/datasets > /tmp/sc-workspace-v240-dataset-created.json
python3 -m json.tool /tmp/sc-workspace-v240-dataset-created.json

cat > /tmp/sc-workspace-v240-model.json <<JSON
{"schema":"sc-workspace-model-record/1.0","modelId":"${MODEL_ID}","name":"v2.4 deployment smoke model","modelKind":"custom","executionTarget":"workspace","executionOperation":"workspace.echo","expectedRevision":0,"metadata":{"deploymentSmoke":true}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/sc-workspace-v240-model.json http://127.0.0.1:8094/v1/models > /tmp/sc-workspace-v240-model-created.json
python3 -m json.tool /tmp/sc-workspace-v240-model-created.json

cat > /tmp/sc-workspace-v240-params.json <<JSON
{"schema":"sc-workspace-parameter-set/1.0","parameterSetId":"${PARAM_ID}","modelId":"${MODEL_ID}","name":"v2.4 deployment smoke parameters","parameters":{"value":42},"expectedRevision":0,"metadata":{"deploymentSmoke":true}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/sc-workspace-v240-params.json http://127.0.0.1:8094/v1/parameter-sets > /tmp/sc-workspace-v240-params-created.json
python3 -m json.tool /tmp/sc-workspace-v240-params-created.json

cat > /tmp/sc-workspace-v240-run.json <<JSON
{"schema":"sc-workspace-execution-run/1.0","runId":"${RUN_ID}","name":"v2.4 deployment smoke run","datasetRefs":[{"datasetId":"${DATASET_ID}"}],"modelRef":{"modelId":"${MODEL_ID}"},"parameterSetRef":{"parameterSetId":"${PARAM_ID}"},"environment":{"smoke":true},"idempotencyKey":"deploy-v240-run-${STAMP}"}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/sc-workspace-v240-run.json http://127.0.0.1:8094/v1/runs > /tmp/sc-workspace-v240-run-created.json
python3 -m json.tool /tmp/sc-workspace-v240-run-created.json
python3 - <<'PY'
import json
d=json.load(open('/tmp/sc-workspace-v240-run-created.json'))['item']
assert d['targetProduct']=='workspace'
assert d['operation']=='workspace.echo'
assert d['datasetRefs'][0]['revision']==1
assert len(d['inputFingerprint'])==64
PY

cat > /tmp/sc-workspace-v240-job.json <<JSON
{"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.echo","executionRunId":"${RUN_ID}","priority":9,"maxAttempts":1,"idempotencyKey":"deploy-v240-job-${STAMP}","payload":{"deploymentSmoke":true,"version":"2.4.0"}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/sc-workspace-v240-job.json http://127.0.0.1:8094/v1/jobs > /tmp/sc-workspace-v240-job-created.json
JOB_ID="$(python3 - <<'PY'
import json
print(json.load(open('/tmp/sc-workspace-v240-job-created.json'))['item']['jobId'])
PY
)"

echo "=== LINKED JOB/RUN SMOKE: ${JOB_ID} / ${RUN_ID} ==="
STATUS=""
for i in $(seq 1 30); do
  curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${JOB_ID}" > /tmp/sc-workspace-v240-job-status.json
  STATUS="$(python3 - <<'PY'
import json
print(json.load(open('/tmp/sc-workspace-v240-job-status.json'))['item']['status'])
PY
)"
  echo "job ${JOB_ID}: ${STATUS}"
  [[ "$STATUS" == "succeeded" ]] && break
  [[ "$STATUS" == "failed" || "$STATUS" == "blocked" || "$STATUS" == "cancelled" ]] && break
  sleep 1
done
[[ "$STATUS" == "succeeded" ]] || { echo "ERROR: linked smoke job did not succeed" >&2; exit 1; }

curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/runs/${RUN_ID}" > /tmp/sc-workspace-v240-run-final.json
python3 -m json.tool /tmp/sc-workspace-v240-run-final.json
python3 - <<'PY'
import json
d=json.load(open('/tmp/sc-workspace-v240-run-final.json'))['item']
assert d['status']=='succeeded'
assert d['progress']==100
assert d['jobId']
assert len(d['reproducibilityFingerprint'])==64
PY

OUTPUT_SHA="$(printf 'workspace-v2.4.0-deployment-smoke' | sha256sum | awk '{print $1}')"
cat > /tmp/sc-workspace-v240-output.json <<JSON
{"schema":"sc-workspace-execution-run-output/1.0","outputId":"smoke-result","role":"result","label":"Deployment smoke output","mediaType":"text/plain","sha256":"${OUTPUT_SHA}","bytes":33,"metadata":{"deploymentSmoke":true}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/sc-workspace-v240-output.json "http://127.0.0.1:8094/v1/runs/${RUN_ID}/outputs" > /tmp/sc-workspace-v240-output-created.json
python3 -m json.tool /tmp/sc-workspace-v240-output-created.json

curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/runs/${RUN_ID}" > /tmp/sc-workspace-v240-run-with-output.json
python3 - <<'PY'
import json
before=json.load(open('/tmp/sc-workspace-v240-run-final.json'))['item']['reproducibilityFingerprint']
after=json.load(open('/tmp/sc-workspace-v240-run-with-output.json'))['item']['reproducibilityFingerprint']
assert before != after
assert len(after)==64
print('PASS: registered output changed reproducibility fingerprint')
PY

echo "=== CONTAINERS ==="
docker ps --filter name=sc-workspace --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
echo "PASS: Workspace backend v2.4.0 API + worker + dataset/model/run registry are running."
