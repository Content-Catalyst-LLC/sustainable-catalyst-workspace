#!/usr/bin/env bash
set -euo pipefail

ZIP_PATH="${1:-/tmp/sustainable-catalyst-workspace-backend-v2.13.0.zip}"
BASE="/opt/sustainable-catalyst"
NEW="$BASE/sustainable-catalyst-workspace-backend-v2.13.0"

[[ -f "$ZIP_PATH" ]] || { echo "ERROR: backend ZIP not found: $ZIP_PATH" >&2; exit 1; }
ENV_SOURCE=""
for candidate in \
  "$BASE/sustainable-catalyst-workspace-backend-v2.13.0/.env" \
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
do
  [[ -f "$candidate" ]] && { ENV_SOURCE="$candidate"; break; }
done
[[ -n "$ENV_SOURCE" ]] || { echo "ERROR: no prior Workspace backend .env found" >&2; exit 1; }

SNAP="$(mktemp)"
cp "$ENV_SOURCE" "$SNAP"
chmod 600 "$SNAP"
trap 'rm -f "$SNAP"' EXIT

docker ps --format '{{.Names}}' | grep -qx sc-postgres || { echo "ERROR: sc-postgres is not running." >&2; exit 1; }
docker volume inspect sc-workspace-data >/dev/null 2>&1 || docker volume create sc-workspace-data >/dev/null

rm -rf "$NEW"
unzip -q "$ZIP_PATH" -d "$BASE"
cp "$SNAP" "$NEW/.env"
chmod 600 "$NEW/.env"
cd "$NEW"
cp docker-compose.example.yml docker-compose.yml

set_env_value() {
  local key="$1" value="$2"
  if grep -q "^${key}=" .env; then
    sed -i "s|^${key}=.*$|${key}=${value}|" .env
  else
    printf '%s=%s\n' "$key" "$value" >> .env
  fi
}

# v2.13 makes R a real internal runtime service. Preserve an existing token;
# generate one only when v2.12 had no R runtime credential configured.
R_TOKEN="$(awk -F= '$1=="SC_WORKSPACE_RUNTIME_R_TOKEN"{sub(/^[^=]*=/,""); print; exit}' .env)"
if [[ -z "$R_TOKEN" ]]; then
  R_TOKEN="$(openssl rand -hex 32)"
fi
set_env_value SC_WORKSPACE_RUNTIME_R_TOKEN "$R_TOKEN"
set_env_value SC_WORKSPACE_RUNTIME_R_URL "http://sc-workspace-r-runtime:8090/v1/execute"
set_env_value SC_WORKSPACE_R_TIMEOUT_SECONDS "40"
set_env_value SC_WORKSPACE_MAX_STATISTICAL_MODEL_RECEIPTS_PER_ACCOUNT "5000"
for kv in \
 'SC_WORKSPACE_RUNTIME_JULIA_URL=' 'SC_WORKSPACE_RUNTIME_JULIA_TOKEN=' \
 'SC_WORKSPACE_RUNTIME_WASM_URL=' 'SC_WORKSPACE_RUNTIME_WASM_TOKEN=' \
 'SC_WORKSPACE_POLYGLOT_TIMEOUT_SECONDS=45' \
 'SC_WORKSPACE_POLYGLOT_MAX_EXCHANGE_ROWS=50000' \
 'SC_WORKSPACE_POLYGLOT_MAX_EXCHANGE_COLUMNS=256' \
 'SC_WORKSPACE_POLYGLOT_MAX_PAYLOAD_BYTES=10485760'
do
  name="${kv%%=*}"
  grep -q "^${name}=" .env || echo "$kv" >> .env
done

PG_ADMIN_USER="$(docker inspect sc-postgres --format '{{range .Config.Env}}{{println .}}{{end}}' | awk -F= '$1=="POSTGRES_USER"{print $2}' | tail -1)"
PG_ADMIN_USER="${PG_ADMIN_USER:-postgres}"
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
  migrations/011_python_scientific_compute_runtime.sql \
  migrations/012_polyglot_scientific_runtime_fabric.sql \
  migrations/013_r_statistical_econometric_runtime.sql
do
  echo "Applying $migration"
  docker exec -i sc-postgres psql -U "$PG_ADMIN_USER" -d sc_workspace -v ON_ERROR_STOP=1 < "$migration" >/dev/null
done

docker exec -i sc-postgres psql -U "$PG_ADMIN_USER" -d sc_workspace -tAc \
  "SELECT count(*) FROM information_schema.role_table_grants WHERE grantee='sc_workspace' AND table_name='workspace_statistical_model_receipts' AND privilege_type='INSERT';" \
  | grep -q '^1$' || { echo 'ERROR: statistical model receipt privilege missing' >&2; exit 1; }
echo 'PASS: v2.13 statistical model receipt registry + privileges'

docker rm -f sc-workspace-r-runtime sc-workspace-worker sc-workspace-backend 2>/dev/null || true
docker compose --env-file .env -f docker-compose.yml up -d --build

for i in $(seq 1 60); do
  code="$(curl -sS -o /tmp/sc-workspace-v2130-health.json -w '%{http_code}' http://127.0.0.1:8094/health 2>/dev/null || true)"
  echo "health attempt $i: HTTP ${code:-000}"
  [[ "$code" == 200 ]] && break
  sleep 2
done
python3 - <<'PY'
import json
d=json.load(open('/tmp/sc-workspace-v2130-health.json'))
assert d['ok'] is True and d['version']=='2.13.0', d
for k in ('polyglotScientificRuntimeFabric','rStatisticalEconometricRuntime','statisticalModelReceipts'):
    assert d[k] is True, (k,d.get(k))
assert d['rRuntimeConfigured'] is True, d
assert d['rRuntimeBoundedOperations']==8, d
assert d['arbitraryCodeExecution'] is False
print('PASS: v2.13 R statistical/econometric health identity')
PY

# R sidecar must be reachable only on the internal runtime network.
for i in $(seq 1 45); do
  if docker exec sc-workspace-backend python -c "import httpx,sys; r=httpx.get('http://sc-workspace-r-runtime:8090/health',timeout=2); sys.exit(0 if r.status_code==200 and r.json().get('ok') is True else 1)" 2>/dev/null; then
    echo "R runtime health attempt $i: ready"
    break
  fi
  echo "R runtime health attempt $i: not ready"
  sleep 2
  [[ "$i" -lt 45 ]] || { echo 'ERROR: R runtime did not become ready' >&2; exit 1; }
done

set -a; . ./.env; set +a
AUTH=(-H "Authorization: Bearer ${SC_WORKSPACE_SERVICE_TOKEN}" -H "X-SC-User-ID: 999999999999")
curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/polyglot/runtimes >/tmp/sc-workspace-v2130-runtimes.json
python3 - <<'PY'
import json
d=json.load(open('/tmp/sc-workspace-v2130-runtimes.json'))
r=next(x for x in d['items'] if x['language']=='r')
assert r['configured'] is True and r['serviceCredentialConfigured'] is True, r
assert r['runtime']=='r-statistical-econometric', r
assert len(r['operations'])==8, r
assert r['arbitraryCodeExecution'] is False
print('PASS: R runtime registered + configured with eight bounded operations')
PY

curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/polyglot/runtimes/r/status >/tmp/sc-workspace-v2130-r-status.json
python3 - <<'PY'
import json
d=json.load(open('/tmp/sc-workspace-v2130-r-status.json'))['item']
assert d['configured'] is True and d['available'] is True, d
assert d['runtime']=='r-statistical-econometric', d
assert len(d['operations'])==8, d
assert d['arbitraryCodeExecution'] is False
print('PASS: R runtime service health + bounded operation registry')
PY

STAMP="$(date +%s)"
cat >/tmp/sc-workspace-v2130-r-job.json <<JSON
{"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.polyglot.r.linear-model","priority":8,"maxAttempts":1,"idempotencyKey":"deploy-v2130-r-lm-${STAMP}","payload":{"rows":[{"x":1,"y":3.1},{"x":2,"y":4.9},{"x":3,"y":7.2},{"x":4,"y":8.8},{"x":5,"y":11.1},{"x":6,"y":12.9}],"outcome":"y","predictors":["x"]}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' -d @/tmp/sc-workspace-v2130-r-job.json http://127.0.0.1:8094/v1/jobs >/tmp/sc-workspace-v2130-r-created.json
JOB_ID="$(python3 - <<'PY'
import json; print(json.load(open('/tmp/sc-workspace-v2130-r-created.json'))['item']['jobId'])
PY
)"
for i in $(seq 1 60); do
  curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${JOB_ID}" >/tmp/sc-workspace-v2130-r-job-state.json
  status="$(python3 - <<'PY'
import json; print(json.load(open('/tmp/sc-workspace-v2130-r-job-state.json'))['item']['status'])
PY
)"
  echo "R model attempt $i: $status"
  [[ "$status" =~ ^(succeeded|failed|blocked|cancelled)$ ]] && break
  sleep 1
done
python3 - <<'PY'
import json
d=json.load(open('/tmp/sc-workspace-v2130-r-job-state.json'))
assert d['item']['status']=='succeeded', d
r=d['result']['polyglot']['result']['remote']['result']
assert r['kind']=='linear-model', r
coefs={x['term']:x['estimate'] for x in r['coefficients']}
assert 1.8 < float(coefs['x']) < 2.2, coefs
assert float(r['metrics']['rSquared']) > .99, r['metrics']
assert d['result']['statisticalModelReceiptId'], d['result']
assert len(d['result']['resultSha256'])==64
print('PASS: durable R linear model executed through polyglot worker')
print('PASS: R result artifact + polyglot receipt + statistical model receipt persisted')
PY

curl -fsS "${AUTH[@]}" 'http://127.0.0.1:8094/v1/statistical-model-receipts?limit=25' >/tmp/sc-workspace-v2130-stat-receipts.json
python3 - <<'PY'
import json
job=json.load(open('/tmp/sc-workspace-v2130-r-job-state.json'))['item']['jobId']
d=json.load(open('/tmp/sc-workspace-v2130-stat-receipts.json'))
row=next((x for x in d['items'] if x['jobId']==job),None)
assert row and row['language']=='r' and row['modelKind']=='linear-model', (row,d)
assert row['outcome']=='y' and row['predictors']==['x'], row
print('PASS: statistical model receipt discoverable through API')
PY

# Existing Workspace worker sandbox remains intact.
docker inspect sc-workspace-worker --format '{{.HostConfig.ReadonlyRootfs}} {{.HostConfig.PidsLimit}} {{.HostConfig.Memory}} {{.HostConfig.NanoCpus}} {{json .HostConfig.CapDrop}} {{json .HostConfig.SecurityOpt}}' \
  | grep -q '^true 256 2147483648 2000000000 .*ALL.*no-new-privileges' \
  || { echo 'ERROR: Workspace worker sandbox mismatch' >&2; exit 1; }
echo 'PASS: Workspace worker sandbox preserved'

# R runtime has a tighter independent sandbox and no published host ports.
docker inspect sc-workspace-r-runtime --format '{{.HostConfig.ReadonlyRootfs}} {{.HostConfig.PidsLimit}} {{.HostConfig.Memory}} {{.HostConfig.NanoCpus}} {{json .HostConfig.CapDrop}} {{json .HostConfig.SecurityOpt}}' \
  | grep -q '^true 128 1073741824 1500000000 .*ALL.*no-new-privileges' \
  || { echo 'ERROR: R runtime sandbox mismatch' >&2; exit 1; }
[[ -z "$(docker port sc-workspace-r-runtime 2>/dev/null || true)" ]] || { echo 'ERROR: R runtime unexpectedly exposes a host port' >&2; exit 1; }
R_NET="$(docker inspect sc-workspace-r-runtime --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}}{{end}}')"
docker network inspect "$R_NET" --format '{{.Internal}}' | grep -q '^true$' || { echo 'ERROR: R runtime network is not internal-only' >&2; exit 1; }
echo 'PASS: R runtime is read-only + 1.5 CPU + 1 GiB + 128 PID + cap-drop ALL + no-new-privileges + internal-only network'

echo 'PASS: Workspace backend v2.13.0 API + worker + R statistical/econometric runtime are running.'
