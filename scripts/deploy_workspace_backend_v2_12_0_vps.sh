#!/usr/bin/env bash
set -euo pipefail
ZIP_PATH="${1:-/tmp/sustainable-catalyst-workspace-backend-v2.12.0.zip}"
BASE="/opt/sustainable-catalyst"
NEW="$BASE/sustainable-catalyst-workspace-backend-v2.12.0"
[[ -f "$ZIP_PATH" ]] || { echo "ERROR: backend ZIP not found: $ZIP_PATH" >&2; exit 1; }
ENV_SOURCE=""
for candidate in \
  "$BASE/sustainable-catalyst-workspace-backend-v2.12.0/.env" \
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
do [[ -f "$candidate" ]] && { ENV_SOURCE="$candidate"; break; }; done
[[ -n "$ENV_SOURCE" ]] || { echo "ERROR: no prior Workspace backend .env found" >&2; exit 1; }
SNAP="$(mktemp)"; cp "$ENV_SOURCE" "$SNAP"; chmod 600 "$SNAP"; trap 'rm -f "$SNAP"' EXIT

docker ps --format '{{.Names}}' | grep -qx sc-postgres || { echo "ERROR: sc-postgres is not running." >&2; exit 1; }
docker volume inspect sc-workspace-data >/dev/null 2>&1 || docker volume create sc-workspace-data >/dev/null
rm -rf "$NEW"; unzip -q "$ZIP_PATH" -d "$BASE"; cp "$SNAP" "$NEW/.env"; chmod 600 "$NEW/.env"; cd "$NEW"; cp docker-compose.example.yml docker-compose.yml
for kv in \
 'SC_WORKSPACE_RUNTIME_R_URL=' 'SC_WORKSPACE_RUNTIME_R_TOKEN=' \
 'SC_WORKSPACE_RUNTIME_JULIA_URL=' 'SC_WORKSPACE_RUNTIME_JULIA_TOKEN=' \
 'SC_WORKSPACE_RUNTIME_WASM_URL=' 'SC_WORKSPACE_RUNTIME_WASM_TOKEN=' \
 'SC_WORKSPACE_POLYGLOT_TIMEOUT_SECONDS=45' \
 'SC_WORKSPACE_POLYGLOT_MAX_EXCHANGE_ROWS=50000' \
 'SC_WORKSPACE_POLYGLOT_MAX_EXCHANGE_COLUMNS=256' \
 'SC_WORKSPACE_POLYGLOT_MAX_PAYLOAD_BYTES=10485760'
do name="${kv%%=*}"; grep -q "^${name}=" .env || echo "$kv" >> .env; done
PG_ADMIN_USER="$(docker inspect sc-postgres --format '{{range .Config.Env}}{{println .}}{{end}}' | awk -F= '$1=="POSTGRES_USER"{print $2}' | tail -1)"; PG_ADMIN_USER="${PG_ADMIN_USER:-postgres}"
for migration in migrations/002_persistence_hardening.sql migrations/003_background_jobs_orchestration.sql migrations/004_dataset_model_execution_run_registry.sql migrations/005_reproducible_execution_environments.sql migrations/006_runtime_adapter_reproduction_verification.sql migrations/007_controlled_runtime_handoffs.sql migrations/008_execution_policy_resource_budgets_sandboxing.sql migrations/009_runtime_enforcement_telemetry_attestations.sql migrations/010_attestation_verification_compliance_runtime_trust.sql migrations/011_python_scientific_compute_runtime.sql migrations/012_polyglot_scientific_runtime_fabric.sql; do
 echo "Applying $migration"; docker exec -i sc-postgres psql -U "$PG_ADMIN_USER" -d sc_workspace -v ON_ERROR_STOP=1 < "$migration" >/dev/null; done

docker exec -i sc-postgres psql -U "$PG_ADMIN_USER" -d sc_workspace -tAc "SELECT count(*) FROM information_schema.role_table_grants WHERE grantee='sc_workspace' AND table_name='workspace_polyglot_execution_receipts' AND privilege_type='INSERT';" | grep -q '^1$' || { echo 'ERROR: polyglot receipt privilege missing' >&2; exit 1; }
echo 'PASS: v2.12 polyglot receipt registry + privileges'

docker rm -f sc-workspace-worker sc-workspace-backend 2>/dev/null || true
docker compose --env-file .env -f docker-compose.yml up -d --build
for i in $(seq 1 45); do code="$(curl -sS -o /tmp/sc-workspace-v2120-health.json -w '%{http_code}' http://127.0.0.1:8094/health 2>/dev/null || true)"; echo "health attempt $i: HTTP ${code:-000}"; [[ "$code" == 200 ]] && break; sleep 2; done
python3 - <<'PY'
import json
d=json.load(open('/tmp/sc-workspace-v2120-health.json'))
assert d['ok'] is True and d['version']=='2.12.0'
for k in ('polyglotScientificRuntimeFabric','arrowCompatibleInterchange','polyglotExecutionReceipts'): assert d[k] is True,k
assert d['polyglotLanguages']==['python','r','julia','sql','wasm']
assert d['arbitraryCodeExecution'] is False
print('PASS: v2.12 polyglot health identity')
PY
set -a; . ./.env; set +a
AUTH=(-H "Authorization: Bearer ${SC_WORKSPACE_SERVICE_TOKEN}" -H "X-SC-User-ID: 999999999999")
curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/polyglot/runtimes >/tmp/sc-workspace-v2120-runtimes.json
python3 - <<'PY'
import json
d=json.load(open('/tmp/sc-workspace-v2120-runtimes.json')); langs={x['language'] for x in d['items']}; assert langs=={'python','sql','r','julia','wasm'}
for x in d['items']: assert x['arbitraryCodeExecution'] is False and x['clientSuppliedRuntimeUrlAllowed'] is False
print('PASS: five-language runtime catalog')
PY
STAMP="$(date +%s)"
cat >/tmp/sc-workspace-v2120-job.json <<JSON
{"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.polyglot.sql.aggregate","priority":8,"maxAttempts":1,"idempotencyKey":"deploy-v2120-sql-${STAMP}","payload":{"rows":[{"x":2},{"x":4},{"x":6}],"column":"x","aggregate":"avg"}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' -d @/tmp/sc-workspace-v2120-job.json http://127.0.0.1:8094/v1/jobs >/tmp/sc-workspace-v2120-created.json
JOB_ID="$(python3 - <<'PY'
import json; print(json.load(open('/tmp/sc-workspace-v2120-created.json'))['item']['jobId'])
PY
)"
for i in $(seq 1 45); do curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${JOB_ID}" >/tmp/sc-workspace-v2120-job-state.json; status="$(python3 - <<'PY'
import json; print(json.load(open('/tmp/sc-workspace-v2120-job-state.json'))['item']['status'])
PY
)"; echo "sql attempt $i: $status"; [[ "$status" =~ ^(succeeded|failed|blocked|cancelled)$ ]] && break; sleep 1; done
python3 - <<'PY'
import json
d=json.load(open('/tmp/sc-workspace-v2120-job-state.json')); assert d['item']['status']=='succeeded',d; assert d['result']['polyglot']['result']['value']==4.0,d['result']; assert len(d['result']['resultSha256'])==64
print('PASS: durable bounded SQL runtime produced avg=4.0')
print('PASS: polyglot result artifact + receipt persisted')
PY
curl -fsS "${AUTH[@]}" 'http://127.0.0.1:8094/v1/polyglot/receipts?limit=25' >/tmp/sc-workspace-v2120-receipts.json
python3 - <<'PY'
import json
j=json.load(open('/tmp/sc-workspace-v2120-job-state.json'))['item']['jobId']; d=json.load(open('/tmp/sc-workspace-v2120-receipts.json')); assert any(x['jobId']==j and x['language']=='sql' for x in d['items'])
print('PASS: polyglot execution receipt discoverable')
PY
docker inspect sc-workspace-worker --format '{{.HostConfig.ReadonlyRootfs}} {{.HostConfig.PidsLimit}} {{.HostConfig.Memory}} {{.HostConfig.NanoCpus}} {{json .HostConfig.CapDrop}} {{json .HostConfig.SecurityOpt}}' | grep -q '^true 256 2147483648 2000000000 .*ALL.*no-new-privileges' || { echo 'ERROR: worker sandbox mismatch' >&2; exit 1; }
echo 'PASS: polyglot worker sandbox preserved'
echo 'PASS: Workspace backend v2.12.0 API + worker + polyglot scientific runtime fabric are running.'
