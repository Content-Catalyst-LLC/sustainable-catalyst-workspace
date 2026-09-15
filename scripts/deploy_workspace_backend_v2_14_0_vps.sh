#!/usr/bin/env bash
set -euo pipefail

ZIP_PATH="${1:-/tmp/sustainable-catalyst-workspace-backend-v2.14.0.zip}"
BASE="/opt/sustainable-catalyst"
NEW="$BASE/sustainable-catalyst-workspace-backend-v2.14.0"

[[ -f "$ZIP_PATH" ]] || { echo "ERROR: backend ZIP not found: $ZIP_PATH" >&2; exit 1; }
ENV_SOURCE=""
for candidate in \
  "$BASE/sustainable-catalyst-workspace-backend-v2.14.0/.env" \
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
JULIA_TOKEN="$(awk -F= '$1=="SC_WORKSPACE_RUNTIME_JULIA_TOKEN"{sub(/^[^=]*=/,""); print; exit}' .env)"
if [[ -z "$JULIA_TOKEN" ]]; then
  JULIA_TOKEN="$(openssl rand -hex 32)"
fi
set_env_value SC_WORKSPACE_RUNTIME_JULIA_TOKEN "$JULIA_TOKEN"
set_env_value SC_WORKSPACE_RUNTIME_JULIA_URL "http://sc-workspace-julia-runtime:8091/v1/execute"
set_env_value SC_WORKSPACE_JULIA_TIMEOUT_SECONDS "60"
set_env_value SC_WORKSPACE_MAX_NUMERICAL_SIMULATION_RECEIPTS_PER_ACCOUNT "5000"
for kv in \
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
  migrations/013_r_statistical_econometric_runtime.sql \
  migrations/014_julia_simulation_numerical_runtime.sql
do
  echo "Applying $migration"
  docker exec -i sc-postgres psql -U "$PG_ADMIN_USER" -d sc_workspace -v ON_ERROR_STOP=1 < "$migration" >/dev/null
done

docker exec -i sc-postgres psql -U "$PG_ADMIN_USER" -d sc_workspace -tAc \
  "SELECT count(*) FROM information_schema.role_table_grants WHERE grantee='sc_workspace' AND table_name='workspace_statistical_model_receipts' AND privilege_type='INSERT';" \
  | grep -q '^1$' || { echo 'ERROR: statistical model receipt privilege missing' >&2; exit 1; }
echo 'PASS: v2.14 statistical model receipt registry + privileges'

docker exec -i sc-postgres psql -U "$PG_ADMIN_USER" -d sc_workspace -tAc \
  "SELECT count(*) FROM information_schema.role_table_grants WHERE grantee='sc_workspace' AND table_name='workspace_numerical_simulation_receipts' AND privilege_type='INSERT';" \
  | grep -q '^1$' || { echo 'ERROR: numerical simulation receipt privilege missing' >&2; exit 1; }
echo 'PASS: v2.14 numerical simulation receipt registry + privileges'


docker rm -f sc-workspace-julia-runtime sc-workspace-r-runtime sc-workspace-worker sc-workspace-backend 2>/dev/null || true
docker compose --env-file .env -f docker-compose.yml up -d --build

for i in $(seq 1 75); do
  code="$(curl -sS -o /tmp/sc-workspace-v2140-health.json -w '%{http_code}' http://127.0.0.1:8094/health 2>/dev/null || true)"
  echo "health attempt $i: HTTP ${code:-000}"
  [[ "$code" == 200 ]] && break
  sleep 2
done
python3 - <<'PY'
import json
d=json.load(open('/tmp/sc-workspace-v2140-health.json'))
assert d['ok'] is True and d['version']=='2.14.0', d
for k in ('polyglotScientificRuntimeFabric','rStatisticalEconometricRuntime','juliaSimulationNumericalRuntime','numericalSimulationReceipts'):
    assert d[k] is True, (k,d.get(k))
assert d['rRuntimeConfigured'] is True, d
assert d['juliaRuntimeConfigured'] is True, d
assert d['juliaRuntimeBoundedOperations']==8, d
assert d['arbitraryCodeExecution'] is False
print('PASS: v2.14 Julia simulation/numerical health identity')
PY

for i in $(seq 1 60); do
  if docker exec sc-workspace-backend python -c "import httpx,sys; r=httpx.get('http://sc-workspace-julia-runtime:8091/health',timeout=2); sys.exit(0 if r.status_code==200 and r.json().get('ok') is True else 1)" 2>/dev/null; then
    echo "Julia runtime health attempt $i: ready"
    break
  fi
  echo "Julia runtime health attempt $i: not ready"
  sleep 2
  [[ "$i" -lt 60 ]] || { echo 'ERROR: Julia runtime did not become ready' >&2; exit 1; }
done

set -a; . ./.env; set +a
AUTH=(-H "Authorization: Bearer ${SC_WORKSPACE_SERVICE_TOKEN}" -H "X-SC-User-ID: 999999999999")
curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/polyglot/runtimes >/tmp/sc-workspace-v2140-runtimes.json
python3 - <<'PY'
import json
d=json.load(open('/tmp/sc-workspace-v2140-runtimes.json'))
j=next(x for x in d['items'] if x['language']=='julia')
assert j['configured'] is True and j['serviceCredentialConfigured'] is True, j
assert j['runtime']=='julia-simulation-numerical', j
assert len(j['operations'])==8, j
assert j['arbitraryCodeExecution'] is False
print('PASS: Julia runtime registered + configured with eight bounded operations')
PY

curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/polyglot/runtimes/julia/status >/tmp/sc-workspace-v2140-j-status.json
python3 - <<'PY'
import json
d=json.load(open('/tmp/sc-workspace-v2140-j-status.json'))['item']
assert d['configured'] is True and d['available'] is True, d
assert d['runtime']=='julia-simulation-numerical', d
assert len(d['operations'])==8, d
assert d['arbitraryCodeExecution'] is False
print('PASS: Julia runtime service health + bounded operation registry')
PY

STAMP="$(date +%s)"
cat >/tmp/sc-workspace-v2140-j-job.json <<JSON
{"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.polyglot.julia.ode-linear-rk4","priority":8,"maxAttempts":1,"idempotencyKey":"deploy-v2140-j-ode-${STAMP}","payload":{"A":[[-1.0]],"initialState":[1.0],"forcing":[0.0],"dt":0.1,"steps":10}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' -d @/tmp/sc-workspace-v2140-j-job.json http://127.0.0.1:8094/v1/jobs >/tmp/sc-workspace-v2140-j-created.json
JOB_ID="$(python3 - <<'PY'
import json; print(json.load(open('/tmp/sc-workspace-v2140-j-created.json'))['item']['jobId'])
PY
)"
for i in $(seq 1 75); do
  curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${JOB_ID}" >/tmp/sc-workspace-v2140-j-job-state.json
  status="$(python3 - <<'PY'
import json; print(json.load(open('/tmp/sc-workspace-v2140-j-job-state.json'))['item']['status'])
PY
)"
  echo "Julia ODE attempt $i: $status"
  [[ "$status" =~ ^(succeeded|failed|blocked|cancelled)$ ]] && break
  sleep 1
done
python3 - <<'PY'
import json
d=json.load(open('/tmp/sc-workspace-v2140-j-job-state.json'))
assert d['item']['status']=='succeeded', d
r=d['result']['polyglot']['result']['remote']['result']
assert r['kind']=='linear-ode' and r['solver']=='rk4', r
v=float(r['finalState'][0]); assert 0.36 < v < 0.38, v
assert d['result']['numericalSimulationReceiptId'], d['result']
assert len(d['result']['resultSha256'])==64
print('PASS: durable Julia RK4 linear ODE produced exp(-1)-equivalent state')
print('PASS: Julia result artifact + polyglot receipt + numerical simulation receipt persisted')
PY

curl -fsS "${AUTH[@]}" 'http://127.0.0.1:8094/v1/numerical-simulation-receipts?limit=25' >/tmp/sc-workspace-v2140-num-receipts.json
python3 - <<'PY'
import json
job=json.load(open('/tmp/sc-workspace-v2140-j-job-state.json'))['item']['jobId']
d=json.load(open('/tmp/sc-workspace-v2140-num-receipts.json'))
row=next((x for x in d['items'] if x['jobId']==job),None)
assert row and row['language']=='julia' and row['modelKind']=='linear-ode', (row,d)
assert row['solver']=='rk4' and row['steps']==10, row
print('PASS: numerical simulation receipt discoverable through API')
PY

docker inspect sc-workspace-worker --format '{{.HostConfig.ReadonlyRootfs}} {{.HostConfig.PidsLimit}} {{.HostConfig.Memory}} {{.HostConfig.NanoCpus}} {{json .HostConfig.CapDrop}} {{json .HostConfig.SecurityOpt}}'   | grep -q '^true 256 2147483648 2000000000 .*ALL.*no-new-privileges'   || { echo 'ERROR: Workspace worker sandbox mismatch' >&2; exit 1; }
echo 'PASS: Workspace worker sandbox preserved'

docker inspect sc-workspace-julia-runtime --format '{{.HostConfig.ReadonlyRootfs}} {{.HostConfig.PidsLimit}} {{.HostConfig.Memory}} {{.HostConfig.NanoCpus}} {{json .HostConfig.CapDrop}} {{json .HostConfig.SecurityOpt}}'   | grep -q '^true 128 2147483648 2000000000 .*ALL.*no-new-privileges'   || { echo 'ERROR: Julia runtime sandbox mismatch' >&2; exit 1; }
[[ -z "$(docker port sc-workspace-julia-runtime 2>/dev/null || true)" ]] || { echo 'ERROR: Julia runtime unexpectedly exposes a host port' >&2; exit 1; }
J_NET="$(docker inspect sc-workspace-julia-runtime --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}}{{end}}')"
docker network inspect "$J_NET" --format '{{.Internal}}' | grep -q '^true$' || { echo 'ERROR: Julia runtime network is not internal-only' >&2; exit 1; }
echo 'PASS: Julia runtime is read-only + 2 CPU + 2 GiB + 128 PID + cap-drop ALL + no-new-privileges + internal-only network'

echo 'PASS: Workspace backend v2.14.0 API + worker + R runtime + Julia simulation/numerical runtime are running.'
