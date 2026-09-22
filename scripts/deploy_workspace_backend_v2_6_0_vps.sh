#!/usr/bin/env bash
set -euo pipefail

ZIP_PATH="${1:-/tmp/sustainable-catalyst-workspace-backend-v2.6.0.zip}"
BASE="/opt/sustainable-catalyst"
NEW="$BASE/sustainable-catalyst-workspace-backend-v2.6.0"

[[ -f "$ZIP_PATH" ]] || { echo "ERROR: backend ZIP not found: $ZIP_PATH" >&2; exit 1; }
ENV_SOURCE=""
for candidate in \
  "$BASE/sustainable-catalyst-workspace-backend-v2.5.0/.env" \
  "$BASE/sustainable-catalyst-workspace-backend-v2.4.0/.env" \
  "$BASE/sustainable-catalyst-workspace-backend-v2.3.0/.env" \
  "$BASE/sustainable-catalyst-workspace-backend-v2.2.0/.env" \
  "$BASE/sustainable-catalyst-workspace-backend-v2.1.0/.env"
do
  [[ -f "$candidate" ]] && { ENV_SOURCE="$candidate"; break; }
done
[[ -n "$ENV_SOURCE" ]] || { echo "ERROR: no prior Workspace backend .env found under $BASE" >&2; exit 1; }
docker ps --format '{{.Names}}' | grep -qx sc-postgres || { echo "ERROR: sc-postgres is not running." >&2; exit 1; }
docker volume inspect sc-workspace-data >/dev/null 2>&1 || docker volume create sc-workspace-data >/dev/null

echo "=== WORKSPACE BACKEND v2.6.0 UPGRADE ==="
echo "Credential source: $(dirname "$ENV_SOURCE")"
rm -rf "$NEW"
unzip -q "$ZIP_PATH" -d "$BASE"
cp "$ENV_SOURCE" "$NEW/.env"
chmod 600 "$NEW/.env"
cd "$NEW"
cp docker-compose.example.yml docker-compose.yml

grep -q '^SC_WORKSPACE_MAX_RUNTIME_ADAPTERS_PER_ACCOUNT=' .env || echo 'SC_WORKSPACE_MAX_RUNTIME_ADAPTERS_PER_ACCOUNT=250' >> .env
for name in CORE LAB WORKBENCH DECISION_STUDIO LIBRARY SITE_INTELLIGENCE; do
  grep -q "^SC_WORKSPACE_ROUTE_${name}_URL=" .env || echo "SC_WORKSPACE_ROUTE_${name}_URL=" >> .env
  grep -q "^SC_WORKSPACE_ROUTE_${name}_TOKEN=" .env || echo "SC_WORKSPACE_ROUTE_${name}_TOKEN=" >> .env
done

PG_ADMIN_USER="$(docker inspect sc-postgres --format '{{range .Config.Env}}{{println .}}{{end}}' | awk -F= '$1=="POSTGRES_USER"{print $2}' | tail -1)"
PG_ADMIN_USER="${PG_ADMIN_USER:-postgres}"
echo "=== APPLY ADDITIVE POSTGRESQL MIGRATIONS ==="
for migration in migrations/002_persistence_hardening.sql migrations/003_background_jobs_orchestration.sql migrations/004_dataset_model_execution_run_registry.sql migrations/005_reproducible_execution_environments.sql migrations/006_runtime_adapter_reproduction_verification.sql; do
  echo "Applying ${migration}"
  docker exec -i sc-postgres psql -U "$PG_ADMIN_USER" -d sc_workspace -v ON_ERROR_STOP=1 < "$migration" >/dev/null
  echo "PASS: ${migration}"
done

echo "=== VERIFY v2.6 REGISTRY PRIVILEGES ==="
docker exec -i sc-postgres psql -U "$PG_ADMIN_USER" -d sc_workspace -v ON_ERROR_STOP=1 -tAc \
  "SELECT count(*) FROM information_schema.role_table_grants WHERE grantee='sc_workspace' AND table_name IN ('workspace_runtime_adapter_heads','workspace_runtime_adapter_revisions','workspace_reproduction_plans','workspace_reproduction_verifications') AND privilege_type='INSERT';" \
  | grep -q '^4$' || { echo 'ERROR: sc_workspace v2.6 registry INSERT privileges are incomplete.' >&2; exit 1; }
echo "PASS: v2.6 registry privileges"

docker rm -f sc-workspace-worker 2>/dev/null || true
docker rm -f sc-workspace-backend 2>/dev/null || true

echo "=== BUILD + START v2.6.0 API AND WORKER ==="
docker compose --env-file .env -f docker-compose.yml up -d --build

for i in $(seq 1 30); do
  code="$(curl -sS -o /tmp/sc-workspace-v260-health.json -w '%{http_code}' http://127.0.0.1:8094/health 2>/dev/null || true)"
  echo "health attempt $i: HTTP ${code:-000}"
  [[ "$code" == "200" ]] && break
  sleep 2
done
python3 -m json.tool /tmp/sc-workspace-v260-health.json
python3 - <<'PY'
import json
d=json.load(open('/tmp/sc-workspace-v260-health.json'))
assert d.get('ok') is True and d.get('version')=='2.6.0'
for key in ('runtimeAdapterRegistry','runtimeCompatibilityChecks','reproductionPlans','reproductionVerification'):
    assert d.get(key) is True, key
assert d.get('arbitraryCodeExecution') is False
PY

curl -fsS http://127.0.0.1:8094/ready | python3 -m json.tool
set -a; . ./.env; set +a
AUTH=( -H "Authorization: Bearer ${SC_WORKSPACE_SERVICE_TOKEN}" -H "X-SC-User-ID: 999999999999" )

curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/capabilities >/tmp/sc-workspace-v260-capabilities.json
python3 - <<'PY'
import json
d=json.load(open('/tmp/sc-workspace-v260-capabilities.json'))
for key in ('runtimeAdapterRegistry','runtimeAdapterRevisionHistory','runtimeCompatibilityChecks','reproductionPlans','reproductionVerification','deterministicRerunComparison'):
    assert d.get(key) is True, key
assert d.get('arbitraryCodeExecution') is False
assert d.get('comparisonMode')=='metadata-and-content-digests'
print('PASS: v2.6 capabilities')
PY

for i in $(seq 1 20); do
  curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/worker/status >/tmp/sc-workspace-v260-worker.json
  python3 - <<'PY' && break || true
import json
d=json.load(open('/tmp/sc-workspace-v260-worker.json'))
raise SystemExit(0 if any(x.get('version')=='2.6.0' and x.get('status') in ('idle','running') for x in d.get('items',[])) else 1)
PY
  sleep 2
done

STAMP="$(date +%s)"
ENV_ID="deploy-v260-env-${STAMP}"; ADAPTER_ID="deploy-v260-python-${STAMP}"
DATASET_ID="deploy-v260-dataset-${STAMP}"; MODEL_ID="deploy-v260-model-${STAMP}"; PARAM_ID="deploy-v260-params-${STAMP}"
RUN1="deploy-v260-original-${STAMP}"; RUN2="deploy-v260-reproduction-${STAMP}"

cat >/tmp/v260-env.json <<JSON
{"schema":"sc-workspace-execution-environment/1.0","environmentId":"${ENV_ID}","name":"v2.6 smoke environment","runtime":{"language":"python","version":"3.12"},"dependencies":{"manager":"pip","manifest":"requirements.txt"},"container":{"image":"python:3.12-slim"},"system":{"os":"linux","architecture":"x86_64"},"randomSeeds":{"python":42},"expectedRevision":0}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/v260-env.json http://127.0.0.1:8094/v1/execution-environments >/tmp/v260-env-created.json

cat >/tmp/v260-adapter.json <<JSON
{"schema":"sc-workspace-runtime-adapter/1.0","adapterId":"${ADAPTER_ID}","name":"Python 3.12 metadata adapter","runtimeFamily":"python","runtimeVersion":"3.12","adapterType":"metadata","dependencyManagers":["pip"],"container":{"image":"python:3.12-slim"},"capabilities":["workspace.echo"],"configuration":{"strictContainerIdentity":true},"expectedRevision":0}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/v260-adapter.json http://127.0.0.1:8094/v1/runtime-adapters >/tmp/v260-adapter-created.json

cat >/tmp/v260-compat.json <<JSON
{"schema":"sc-workspace-runtime-compatibility-check/1.0","environmentRef":{"environmentId":"${ENV_ID}","revision":1}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/v260-compat.json http://127.0.0.1:8094/v1/runtime-adapters/${ADAPTER_ID}/compatibility >/tmp/v260-compat-result.json
python3 - <<'PY'
import json
d=json.load(open('/tmp/v260-compat-result.json')); assert d['compatible'] is True; assert d['readiness']=='ready'; assert d['executionPerformed'] is False
print('PASS: runtime/environment compatibility ready')
PY

cat >/tmp/v260-dataset.json <<JSON
{"schema":"sc-workspace-dataset-record/1.0","datasetId":"${DATASET_ID}","name":"v2.6 smoke dataset","datasetType":"table","sourceKind":"generated","expectedRevision":0}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/v260-dataset.json http://127.0.0.1:8094/v1/datasets >/dev/null
cat >/tmp/v260-model.json <<JSON
{"schema":"sc-workspace-model-record/1.0","modelId":"${MODEL_ID}","name":"v2.6 smoke model","modelKind":"custom","executionTarget":"workspace","executionOperation":"workspace.echo","expectedRevision":0}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/v260-model.json http://127.0.0.1:8094/v1/models >/dev/null
cat >/tmp/v260-params.json <<JSON
{"schema":"sc-workspace-parameter-set/1.0","parameterSetId":"${PARAM_ID}","modelId":"${MODEL_ID}","name":"v2.6 smoke params","parameters":{"value":42},"expectedRevision":0}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/v260-params.json http://127.0.0.1:8094/v1/parameter-sets >/dev/null

run_and_wait () {
  local RID="$1" KEY="$2"
  cat >/tmp/v260-run.json <<JSON
{"schema":"sc-workspace-execution-run/1.0","runId":"${RID}","name":"v2.6 reproduction smoke","datasetRefs":[{"datasetId":"${DATASET_ID}"}],"modelRef":{"modelId":"${MODEL_ID}"},"parameterSetRef":{"parameterSetId":"${PARAM_ID}"},"environmentRef":{"environmentId":"${ENV_ID}","revision":1},"runtimeAdapterRef":{"adapterId":"${ADAPTER_ID}","revision":1},"idempotencyKey":"${KEY}-run"}
JSON
  curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/v260-run.json http://127.0.0.1:8094/v1/runs >/tmp/v260-run-created.json
  cat >/tmp/v260-job.json <<JSON
{"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.echo","executionRunId":"${RID}","priority":9,"maxAttempts":1,"idempotencyKey":"${KEY}-job","payload":{"value":42,"version":"2.6.0"}}
JSON
  curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/v260-job.json http://127.0.0.1:8094/v1/jobs >/tmp/v260-job-created.json
  JOB_ID="$(python3 -c "import json; print(json.load(open('/tmp/v260-job-created.json'))['item']['jobId'])")"
  STATUS=""
  for i in $(seq 1 30); do
    curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/jobs/${JOB_ID} >/tmp/v260-job-status.json
    STATUS="$(python3 -c "import json; print(json.load(open('/tmp/v260-job-status.json'))['item']['status'])")"
    [[ "$STATUS" == "succeeded" ]] && break
    [[ "$STATUS" =~ ^(failed|blocked|cancelled)$ ]] && break
    sleep 1
  done
  [[ "$STATUS" == "succeeded" ]] || { echo "ERROR: smoke job ${JOB_ID} ended ${STATUS}" >&2; exit 1; }
  cat >/tmp/v260-output.json <<JSON
{"schema":"sc-workspace-execution-run-output/1.0","outputId":"primary","role":"result","label":"deterministic smoke output","mediaType":"application/json","sha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","bytes":42}
JSON
  curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/v260-output.json http://127.0.0.1:8094/v1/runs/${RID}/outputs >/dev/null
}

run_and_wait "$RUN1" "deploy-v260-original-${STAMP}"

cat >/tmp/v260-plan.json <<JSON
{"schema":"sc-workspace-reproduction-plan/1.0","originalRunId":"${RUN1}","runtimeAdapterRef":{"adapterId":"${ADAPTER_ID}","revision":1},"notes":"deployment smoke reproduction plan"}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/v260-plan.json http://127.0.0.1:8094/v1/reproduction-plans >/tmp/v260-plan-created.json
python3 - <<'PY'
import json
d=json.load(open('/tmp/v260-plan-created.json'))['item']; assert d['compatibility']['compatible'] is True; assert len(d['fingerprint'])==64
print('PASS: reproduction plan frozen')
PY

run_and_wait "$RUN2" "deploy-v260-reproduction-${STAMP}"

cat >/tmp/v260-verify.json <<JSON
{"schema":"sc-workspace-reproduction-verification/1.0","originalRunId":"${RUN1}","reproductionRunId":"${RUN2}"}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/v260-verify.json http://127.0.0.1:8094/v1/reproduction-verifications >/tmp/v260-verify-created.json
python3 - <<'PY'
import json
d=json.load(open('/tmp/v260-verify-created.json'))['item']
assert d['classification']=='exact', d
assert all(d[k] is True for k in ('exactInputs','exactEnvironment','exactRuntimeAdapter','exactOutputs'))
assert d['details']['comparisonMode']=='metadata-and-content-digests'
assert d['details']['comparisonExecuted'] is False
print('PASS: exact reproduction verification receipt')
PY

echo "=== CONTAINERS ==="
docker ps --filter name=sc-workspace --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
echo "PASS: Workspace backend v2.6.0 API + worker + runtime adapter registry + reproduction verification are running."
