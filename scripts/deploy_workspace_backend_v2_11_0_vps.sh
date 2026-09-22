#!/usr/bin/env bash
set -euo pipefail

ZIP_PATH="${1:-/tmp/sustainable-catalyst-workspace-backend-v2.11.0.zip}"
BASE="/opt/sustainable-catalyst"
NEW="$BASE/sustainable-catalyst-workspace-backend-v2.11.0"

[[ -f "$ZIP_PATH" ]] || { echo "ERROR: backend ZIP not found: $ZIP_PATH" >&2; exit 1; }
ENV_SOURCE=""
for candidate in \
  "$BASE/sustainable-catalyst-workspace-backend-v2.11.0/.env" \
  "$BASE/sustainable-catalyst-workspace-backend-v2.10.0/.env" \
  "$BASE/sustainable-catalyst-workspace-backend-v2.9.0/.env" \
  "$BASE/sustainable-catalyst-workspace-backend-v2.8.0/.env" \
  "$BASE/sustainable-catalyst-workspace-backend-v2.7.0/.env" \
  "$BASE/sustainable-catalyst-workspace-backend-v2.6.0/.env" \
  "$BASE/sustainable-catalyst-workspace-backend-v2.5.0/.env" \
  "$BASE/sustainable-catalyst-workspace-backend-v2.4.0/.env" \
  "$BASE/sustainable-catalyst-workspace-backend-v2.3.0/.env" \
  "$BASE/sustainable-catalyst-workspace-backend-v2.2.0/.env" \
  "$BASE/sustainable-catalyst-workspace-backend-v2.1.0/.env"
do
  [[ -f "$candidate" ]] && { ENV_SOURCE="$candidate"; break; }
done
[[ -n "$ENV_SOURCE" ]] || { echo "ERROR: no prior Workspace backend .env found under $BASE" >&2; exit 1; }
ENV_SNAPSHOT="$(mktemp)"
cp "$ENV_SOURCE" "$ENV_SNAPSHOT"
chmod 600 "$ENV_SNAPSHOT"
trap 'rm -f "$ENV_SNAPSHOT"' EXIT

docker ps --format '{{.Names}}' | grep -qx sc-postgres || { echo "ERROR: sc-postgres is not running." >&2; exit 1; }
docker volume inspect sc-workspace-data >/dev/null 2>&1 || docker volume create sc-workspace-data >/dev/null

echo "=== WORKSPACE BACKEND v2.11.0 — PYTHON SCIENTIFIC COMPUTE RUNTIME ==="
echo "Credential source: $(dirname "$ENV_SOURCE")"
rm -rf "$NEW"
unzip -q "$ZIP_PATH" -d "$BASE"
cp "$ENV_SNAPSHOT" "$NEW/.env"
chmod 600 "$NEW/.env"
cd "$NEW"
cp docker-compose.example.yml docker-compose.yml

# Preserve existing secrets and routes; add only non-secret v2.11 defaults when absent.
for kv in \
  'SC_WORKSPACE_COMPUTE_MAX_ROWS=50000' \
  'SC_WORKSPACE_COMPUTE_MAX_COLUMNS=256' \
  'SC_WORKSPACE_COMPUTE_MAX_MATRIX_DIMENSION=512' \
  'SC_WORKSPACE_COMPUTE_MAX_SYMBOLIC_CHARS=4000' \
  'SC_WORKSPACE_COMPUTE_MAX_SYMBOLIC_OPERATIONS=2000' \
  'SC_WORKSPACE_COMPUTE_MAX_OPTIMIZER_ITERATIONS=1000' \
  'SC_WORKSPACE_COMPUTE_MAX_POLYNOMIAL_DEGREE=256' \
  'SC_WORKSPACE_COMPUTE_MAX_RESULT_BYTES=10485760'
do
  name="${kv%%=*}"
  grep -q "^${name}=" .env || echo "$kv" >> .env
done
if ! grep -q '^SC_WORKSPACE_RUNTIME_ATTESTATION_TOKEN=' .env || [[ -z "$(awk -F= '$1=="SC_WORKSPACE_RUNTIME_ATTESTATION_TOKEN"{print $2}' .env | tail -1)" ]]; then
  printf 'SC_WORKSPACE_RUNTIME_ATTESTATION_TOKEN=%s\n' "$(openssl rand -hex 32)" >> .env
fi
for name in CORE LAB WORKBENCH DECISION_STUDIO LIBRARY SITE_INTELLIGENCE; do
  grep -q "^SC_WORKSPACE_ROUTE_${name}_URL=" .env || echo "SC_WORKSPACE_ROUTE_${name}_URL=" >> .env
  grep -q "^SC_WORKSPACE_ROUTE_${name}_TOKEN=" .env || echo "SC_WORKSPACE_ROUTE_${name}_TOKEN=" >> .env
done

PG_ADMIN_USER="$(docker inspect sc-postgres --format '{{range .Config.Env}}{{println .}}{{end}}' | awk -F= '$1=="POSTGRES_USER"{print $2}' | tail -1)"
PG_ADMIN_USER="${PG_ADMIN_USER:-postgres}"
echo "=== APPLY ADDITIVE POSTGRESQL MIGRATIONS ==="
for migration in \
  migrations/002_persistence_hardening.sql \
  migrations/003_background_jobs_orchestration.sql \
  migrations/004_dataset_model_execution_run_registry.sql \
  migrations/005_reproducible_execution_environments.sql \
  migrations/006_runtime_adapter_reproduction_verification.sql \
  migrations/007_controlled_runtime_handoffs.sql \
  migrations/008_execution_policy_resource_budgets_sandboxing.sql \
  migrations/009_runtime_enforcement_telemetry_attestations.sql \
  migrations/010_attestation_verification_compliance_runtime_trust.sql \
  migrations/011_python_scientific_compute_runtime.sql
do
  echo "Applying ${migration}"
  docker exec -i sc-postgres psql -U "$PG_ADMIN_USER" -d sc_workspace -v ON_ERROR_STOP=1 < "$migration" >/dev/null
  echo "PASS: ${migration}"
done

echo "=== VERIFY v2.11 COMPUTE RECEIPT REGISTRY ==="
docker exec -i sc-postgres psql -U "$PG_ADMIN_USER" -d sc_workspace -v ON_ERROR_STOP=1 -tAc \
  "SELECT count(*) FROM information_schema.role_table_grants WHERE grantee='sc_workspace' AND table_name='workspace_compute_execution_receipts' AND privilege_type='INSERT';" \
  | grep -q '^1$' || { echo 'ERROR: sc_workspace compute receipt INSERT privilege is missing.' >&2; exit 1; }
echo "PASS: v2.11 compute receipt registry + privileges"

docker rm -f sc-workspace-worker 2>/dev/null || true
docker rm -f sc-workspace-backend 2>/dev/null || true

echo "=== BUILD + START v2.11.0 API AND SCIENTIFIC WORKER ==="
docker compose --env-file .env -f docker-compose.yml up -d --build

for i in $(seq 1 45); do
  code="$(curl -sS -o /tmp/sc-workspace-v2110-health.json -w '%{http_code}' http://127.0.0.1:8094/health 2>/dev/null || true)"
  echo "health attempt $i: HTTP ${code:-000}"
  [[ "$code" == "200" ]] && break
  sleep 2
done
python3 -m json.tool /tmp/sc-workspace-v2110-health.json
python3 - <<'PY'
import json
d=json.load(open('/tmp/sc-workspace-v2110-health.json'))
assert d.get('ok') is True and d.get('version')=='2.11.0'
for key in ('pythonScientificComputeRuntime','scientificComputeOperationRegistry','computeResultArtifacts','computeExecutionReceipts','computeProgressEvents','boundedScientificOperationsOnly'):
    assert d.get(key) is True, key
assert d.get('arbitraryCodeExecution') is False
print('PASS: v2.11 scientific compute health identity')
PY

curl -fsS http://127.0.0.1:8094/ready | python3 -m json.tool
set -a; . ./.env; set +a
AUTH=( -H "Authorization: Bearer ${SC_WORKSPACE_SERVICE_TOKEN}" -H "X-SC-User-ID: 999999999999" )

curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/capabilities >/tmp/sc-workspace-v2110-capabilities.json
python3 - <<'PY'
import json
d=json.load(open('/tmp/sc-workspace-v2110-capabilities.json'))
for key in ('pythonScientificComputeRuntime','scientificComputeOperationRegistry','computeResultArtifacts','computeExecutionReceipts','computeProgressEvents','computeCancellationChecks','boundedScientificOperationsOnly'):
    assert d.get(key) is True, key
assert d.get('scientificComputeEngines')==['numpy','pandas','scipy','sympy']
assert d.get('arbitraryCodeExecution') is False
print('PASS: v2.11 scientific compute capabilities')
PY

curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/compute/operations >/tmp/sc-workspace-v2110-ops.json
python3 - <<'PY'
import json
d=json.load(open('/tmp/sc-workspace-v2110-ops.json'))
ops={x['operation'] for x in d.get('items',[])}
required={'workspace.compute.describe','workspace.compute.transform','workspace.compute.linear-algebra','workspace.compute.symbolic','workspace.compute.integrate-series','workspace.compute.optimize-quadratic','workspace.compute.roots-polynomial'}
assert required <= ops
assert d.get('arbitraryCodeExecution') is False
print('PASS: seven bounded scientific operations registered')
PY

for i in $(seq 1 30); do
  curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/worker/status >/tmp/sc-workspace-v2110-worker.json
  python3 - <<'PY' && break || true
import json
d=json.load(open('/tmp/sc-workspace-v2110-worker.json'))
raise SystemExit(0 if any(x.get('version')=='2.11.0' and x.get('status') in ('idle','running') for x in d.get('items',[])) else 1)
PY
  sleep 2
done
python3 - <<'PY'
import json
d=json.load(open('/tmp/sc-workspace-v2110-worker.json'))
assert any(x.get('version')=='2.11.0' and x.get('status') in ('idle','running') for x in d.get('items',[]))
print('PASS: v2.11 scientific worker heartbeat')
PY

STAMP="$(date +%s)"
cat >/tmp/sc-workspace-v2110-job.json <<JSON
{
  "schema":"sc-workspace-job-request/1.0",
  "jobType":"workspace-task",
  "targetProduct":"workspace",
  "operation":"workspace.compute.linear-algebra",
  "priority":8,
  "maxAttempts":1,
  "idempotencyKey":"deploy-v2110-linear-${STAMP}",
  "payload":{"action":"solve","a":[[2,0],[0,4]],"b":[6,8]}
}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' -d @/tmp/sc-workspace-v2110-job.json http://127.0.0.1:8094/v1/jobs >/tmp/sc-workspace-v2110-created.json
JOB_ID="$(python3 - <<'PY'
import json
print(json.load(open('/tmp/sc-workspace-v2110-created.json'))['item']['jobId'])
PY
)"
echo "Created compute job: $JOB_ID"

for i in $(seq 1 45); do
  curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${JOB_ID}" >/tmp/sc-workspace-v2110-job-state.json
  status="$(python3 - <<'PY'
import json
print(json.load(open('/tmp/sc-workspace-v2110-job-state.json'))['item']['status'])
PY
)"
  echo "compute attempt $i: ${status}"
  [[ "$status" =~ ^(succeeded|failed|blocked|cancelled)$ ]] && break
  sleep 1
done
python3 - <<'PY'
import json
d=json.load(open('/tmp/sc-workspace-v2110-job-state.json'))
assert d['item']['status']=='succeeded', d
assert d['result']['result']['solution']==[3.0,2.0], d['result']
sc=d['result']['scientificCompute']
assert sc['engine']=='numpy'
assert len(sc['resultArtifact']['sha256'])==64
assert sc['receipt']['jobId']==d['item']['jobId']
print('PASS: durable NumPy linear-algebra job produced [3.0, 2.0]')
print('PASS: compute result persisted as content-addressed artifact + receipt')
PY

curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${JOB_ID}/events" >/tmp/sc-workspace-v2110-events.json
python3 - <<'PY'
import json
d=json.load(open('/tmp/sc-workspace-v2110-events.json'))
progress=[x for x in d.get('items',[]) if x.get('eventType')=='progress']
assert progress, d
assert max(x.get('progress',0) for x in progress) >= 90
print('PASS: scientific compute progress events recorded')
PY

curl -fsS "${AUTH[@]}" 'http://127.0.0.1:8094/v1/compute/receipts?limit=25' >/tmp/sc-workspace-v2110-receipts.json
python3 - <<'PY'
import json
j=json.load(open('/tmp/sc-workspace-v2110-job-state.json'))['item']['jobId']
d=json.load(open('/tmp/sc-workspace-v2110-receipts.json'))
assert any(x.get('jobId')==j and x.get('operation')=='workspace.compute.linear-algebra' for x in d.get('items',[]))
print('PASS: compute execution receipt discoverable through API')
PY

echo "=== WORKER SANDBOX ==="
docker inspect sc-workspace-worker --format 'ReadonlyRootfs={{.HostConfig.ReadonlyRootfs}} PidsLimit={{.HostConfig.PidsLimit}} Memory={{.HostConfig.Memory}} NanoCpus={{.HostConfig.NanoCpus}} CapDrop={{json .HostConfig.CapDrop}} SecurityOpt={{json .HostConfig.SecurityOpt}}'
docker inspect sc-workspace-worker --format '{{.HostConfig.ReadonlyRootfs}} {{.HostConfig.PidsLimit}} {{.HostConfig.Memory}} {{.HostConfig.NanoCpus}} {{json .HostConfig.CapDrop}} {{json .HostConfig.SecurityOpt}}' \
  | grep -q '^true 256 2147483648 2000000000 .*ALL.*no-new-privileges' \
  || { echo 'ERROR: v2.11 worker sandbox envelope does not match release contract.' >&2; exit 1; }
echo "PASS: scientific worker is read-only-root + 2 CPU + 2 GiB + 256 PID + cap-drop ALL + no-new-privileges"

echo "=== CONTAINERS ==="
docker ps --filter name=sc-workspace --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
echo "PASS: Workspace backend v2.11.0 API + worker + Python scientific compute runtime are running."
