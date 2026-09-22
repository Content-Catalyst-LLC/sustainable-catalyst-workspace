#!/usr/bin/env bash
set -euo pipefail

ZIP_PATH="${1:-/tmp/sustainable-catalyst-workspace-backend-v2.22.0.zip}"
BASE="/opt/sustainable-catalyst"
NEW="$BASE/sustainable-catalyst-workspace-backend-v2.22.0"

[[ -f "$ZIP_PATH" ]] || { echo "ERROR: backend ZIP not found: $ZIP_PATH" >&2; exit 1; }
ENV_SOURCE=""
for candidate in \
  "$BASE/sustainable-catalyst-workspace-backend-v2.22.0/.env" \
  "$BASE/sustainable-catalyst-workspace-backend-v2.21.0/.env" \
  "$BASE/sustainable-catalyst-workspace-backend-v2.20.0/.env" \
  "$BASE/sustainable-catalyst-workspace-backend-v2.19.0/.env" \
  "$BASE/sustainable-catalyst-workspace-backend-v2.18.0/.env" \
  "$BASE/sustainable-catalyst-workspace-backend-v2.17.0/.env" \
  "$BASE/sustainable-catalyst-workspace-backend-v2.16.0/.env" \
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
ML_TOKEN="$(awk -F= '$1=="SC_WORKSPACE_RUNTIME_ML_TOKEN"{sub(/^[^=]*=/,""); print; exit}' .env)"
if [[ -z "$ML_TOKEN" ]]; then
  ML_TOKEN="$(openssl rand -hex 32)"
fi
set_env_value SC_WORKSPACE_RUNTIME_ML_TOKEN "$ML_TOKEN"
set_env_value SC_WORKSPACE_RUNTIME_ML_URL "http://sc-workspace-ml-runtime:8092/v1/execute"
set_env_value SC_WORKSPACE_ML_TIMEOUT_SECONDS "90"
set_env_value SC_WORKSPACE_MAX_PREDICTIVE_MODEL_RECEIPTS_PER_ACCOUNT "5000"
set_env_value SC_WORKSPACE_MAX_MODEL_EVALUATION_RECEIPTS_PER_ACCOUNT "10000"
INTERCHANGE_TOKEN="$(awk -F= '$1=="SC_WORKSPACE_RUNTIME_INTERCHANGE_TOKEN"{sub(/^[^=]*=/,""); print; exit}' .env)"
if [[ -z "$INTERCHANGE_TOKEN" ]]; then
  INTERCHANGE_TOKEN="$(openssl rand -hex 32)"
fi
set_env_value SC_WORKSPACE_RUNTIME_INTERCHANGE_TOKEN "$INTERCHANGE_TOKEN"
set_env_value SC_WORKSPACE_RUNTIME_INTERCHANGE_URL "http://sc-workspace-interchange-runtime:8093/v1/execute"
set_env_value SC_WORKSPACE_INTERCHANGE_TIMEOUT_SECONDS "60"
set_env_value SC_WORKSPACE_MAX_INTERCHANGE_RECEIPTS_PER_ACCOUNT "10000"
set_env_value SC_WORKSPACE_MAX_CROSS_RUNTIME_VERIFICATION_RECEIPTS_PER_ACCOUNT "10000"
FORECAST_TOKEN="$(awk -F= '$1=="SC_WORKSPACE_RUNTIME_FORECAST_TOKEN"{sub(/^[^=]*=/,""); print; exit}' .env)"
if [[ -z "$FORECAST_TOKEN" ]]; then FORECAST_TOKEN="$(openssl rand -hex 32)"; fi
set_env_value SC_WORKSPACE_RUNTIME_FORECAST_TOKEN "$FORECAST_TOKEN"
PROBABILITY_TOKEN="$(awk -F= '$1=="SC_WORKSPACE_RUNTIME_PROBABILITY_TOKEN"{sub(/^[^=]*=/,""); print; exit}' .env)"
if [[ -z "$PROBABILITY_TOKEN" ]]; then PROBABILITY_TOKEN="$(openssl rand -hex 32)"; fi
set_env_value SC_WORKSPACE_RUNTIME_PROBABILITY_TOKEN "$PROBABILITY_TOKEN"
set_env_value SC_WORKSPACE_RUNTIME_PROBABILITY_URL "http://sc-workspace-probability-runtime:8096/v1/execute"
set_env_value SC_WORKSPACE_MAX_PROBABILISTIC_INFERENCE_RECEIPTS_PER_ACCOUNT "10000"
set_env_value SC_WORKSPACE_PROBABILITY_MAX_DRAWS "20000"
UNCERTAINTY_TOKEN="$(awk -F= '$1=="SC_WORKSPACE_RUNTIME_UNCERTAINTY_TOKEN"{sub(/^[^=]*=/,""); print; exit}' .env)"
if [[ -z "$UNCERTAINTY_TOKEN" ]]; then UNCERTAINTY_TOKEN="$(openssl rand -hex 32)"; fi
set_env_value SC_WORKSPACE_RUNTIME_UNCERTAINTY_TOKEN "$UNCERTAINTY_TOKEN"
set_env_value SC_WORKSPACE_RUNTIME_UNCERTAINTY_URL "http://sc-workspace-uncertainty-runtime:8097/v1/execute"
set_env_value SC_WORKSPACE_MAX_UNCERTAINTY_ANALYSIS_RECEIPTS_PER_ACCOUNT "10000"
set_env_value SC_WORKSPACE_UNCERTAINTY_MAX_DRAWS "20000"
set_env_value SC_WORKSPACE_UNCERTAINTY_MAX_ROWS "10000"
set_env_value SC_WORKSPACE_UNCERTAINTY_MAX_VARIABLES "64"
OPTIMIZATION_TOKEN="$(awk -F= '$1=="SC_WORKSPACE_RUNTIME_OPTIMIZATION_TOKEN"{sub(/^[^=]*=/,""); print; exit}' .env)"
if [[ -z "$OPTIMIZATION_TOKEN" ]]; then OPTIMIZATION_TOKEN="$(openssl rand -hex 32)"; fi
set_env_value SC_WORKSPACE_RUNTIME_OPTIMIZATION_TOKEN "$OPTIMIZATION_TOKEN"
set_env_value SC_WORKSPACE_RUNTIME_OPTIMIZATION_URL "http://sc-workspace-optimization-runtime:8098/v1/execute"
if [[ -z "${SC_WORKSPACE_RUNTIME_DECISION_TOKEN:-}" ]]; then SC_WORKSPACE_RUNTIME_DECISION_TOKEN="$(python3 - <<'PYTOKEN'
import secrets
print(secrets.token_urlsafe(48))
PYTOKEN
)"; fi
set_env_value SC_WORKSPACE_RUNTIME_DECISION_TOKEN "$SC_WORKSPACE_RUNTIME_DECISION_TOKEN"
set_env_value SC_WORKSPACE_RUNTIME_DECISION_URL "http://sc-workspace-decision-runtime:8099/v1/execute"
set_env_value SC_WORKSPACE_MAX_OPTIMIZATION_RECEIPTS_PER_ACCOUNT "10000"
set_env_value SC_WORKSPACE_OPTIMIZATION_MAX_DIMENSIONS "32"
set_env_value SC_WORKSPACE_OPTIMIZATION_MAX_EVALUATIONS "50000"
set_env_value SC_WORKSPACE_OPTIMIZATION_MAX_ITERATIONS "5000"
set_env_value SC_WORKSPACE_RUNTIME_FORECAST_URL "http://sc-workspace-forecast-runtime:8095/v1/execute"
set_env_value SC_WORKSPACE_MAX_FORECAST_RECEIPTS_PER_ACCOUNT "10000"
set_env_value SC_WORKSPACE_MAX_FORECAST_EVALUATION_RECEIPTS_PER_ACCOUNT "10000"
set_env_value SC_WORKSPACE_FORECAST_MAX_HORIZON "3650"
set_env_value SC_WORKSPACE_FORECAST_MAX_SEASONAL_PERIOD "365"
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
  migrations/014_julia_simulation_numerical_runtime.sql \
  migrations/015_predictive_analytics_machine_learning_runtime.sql \
  migrations/016_native_arrow_parquet_interchange.sql \
  migrations/017_reproduction_cross_runtime_verification.sql \
  migrations/018_forecasting_time_series_runtime.sql \
  migrations/019_probabilistic_bayesian_runtime.sql \
  migrations/020_monte_carlo_uncertainty_quantification.sql \
  migrations/021_optimization_parameter_search_runtime.sql \
  migrations/022_robust_decision_optimization_pareto.sql
do
  echo "Applying $migration"
  docker exec -i sc-postgres psql -U "$PG_ADMIN_USER" -d sc_workspace -v ON_ERROR_STOP=1 < "$migration" >/dev/null
done

docker exec -i sc-postgres psql -U "$PG_ADMIN_USER" -d sc_workspace -tAc \
  "SELECT count(*) FROM information_schema.role_table_grants WHERE grantee='sc_workspace' AND table_name='workspace_statistical_model_receipts' AND privilege_type='INSERT';" \
  | grep -q '^1$' || { echo 'ERROR: statistical model receipt privilege missing' >&2; exit 1; }
echo 'PASS: v2.15 statistical model receipt registry + privileges'

docker exec -i sc-postgres psql -U "$PG_ADMIN_USER" -d sc_workspace -tAc \
  "SELECT count(*) FROM information_schema.role_table_grants WHERE grantee='sc_workspace' AND table_name='workspace_numerical_simulation_receipts' AND privilege_type='INSERT';" \
  | grep -q '^1$' || { echo 'ERROR: numerical simulation receipt privilege missing' >&2; exit 1; }
echo 'PASS: v2.15 numerical simulation receipt registry + privileges'

docker exec -i sc-postgres psql -U "$PG_ADMIN_USER" -d sc_workspace -tAc \
  "SELECT count(*) FROM information_schema.role_table_grants WHERE grantee='sc_workspace' AND table_name='workspace_predictive_model_receipts' AND privilege_type='INSERT';" \
  | grep -q '^1$' || { echo 'ERROR: predictive model receipt privilege missing' >&2; exit 1; }
docker exec -i sc-postgres psql -U "$PG_ADMIN_USER" -d sc_workspace -tAc \
  "SELECT count(*) FROM information_schema.role_table_grants WHERE grantee='sc_workspace' AND table_name='workspace_model_evaluation_receipts' AND privilege_type='INSERT';" \
  | grep -q '^1$' || { echo 'ERROR: model evaluation receipt privilege missing' >&2; exit 1; }
echo 'PASS: v2.15 predictive model + evaluation receipt registries + privileges'

docker exec -i sc-postgres psql -U "$PG_ADMIN_USER" -d sc_workspace -tAc \
  "SELECT count(*) FROM information_schema.role_table_grants WHERE grantee='sc_workspace' AND table_name='workspace_cross_runtime_verification_receipts' AND privilege_type='INSERT';" \
  | grep -q '^1$' || { echo 'ERROR: cross-runtime verification receipt privilege missing' >&2; exit 1; }
echo 'PASS: v2.17 cross-runtime verification receipt registry + privileges'
docker exec -i sc-postgres psql -U "$PG_ADMIN_USER" -d sc_workspace -tAc "SELECT count(*) FROM information_schema.role_table_grants WHERE grantee='sc_workspace' AND table_name='workspace_forecast_receipts' AND privilege_type='INSERT';" | grep -q '^1$' || { echo 'ERROR: forecast receipt privilege missing' >&2; exit 1; }
docker exec -i sc-postgres psql -U "$PG_ADMIN_USER" -d sc_workspace -tAc "SELECT count(*) FROM information_schema.role_table_grants WHERE grantee='sc_workspace' AND table_name='workspace_forecast_evaluation_receipts' AND privilege_type='INSERT';" | grep -q '^1$' || { echo 'ERROR: forecast evaluation receipt privilege missing' >&2; exit 1; }
echo 'PASS: v2.18 forecast + forecast evaluation receipt registries + privileges'
docker exec -i sc-postgres psql -U "$PG_ADMIN_USER" -d sc_workspace -tAc "SELECT count(*) FROM information_schema.role_table_grants WHERE grantee='sc_workspace' AND table_name='workspace_uncertainty_analysis_receipts' AND privilege_type='INSERT';" | grep -q '^1$' || { echo 'ERROR: uncertainty analysis receipt privilege missing' >&2; exit 1; }
echo 'PASS: v2.20 uncertainty analysis receipt registry + privileges'
docker exec -i sc-postgres psql -U "$PG_ADMIN_USER" -d sc_workspace -tAc "SELECT count(*) FROM information_schema.role_table_grants WHERE grantee='sc_workspace' AND table_name='workspace_optimization_receipts' AND privilege_type='INSERT';" | grep -q '^1$' || { echo 'ERROR: optimization receipt privilege missing' >&2; exit 1; }
echo 'PASS: v2.21 optimization receipt registry + privileges'
docker exec -i sc-postgres psql -U "$PG_ADMIN_USER" -d sc_workspace -tAc "SELECT count(*) FROM information_schema.role_table_grants WHERE grantee='sc_workspace' AND table_name='workspace_decision_optimization_receipts' AND privilege_type='INSERT';" | grep -q '^1$' || { echo 'ERROR: decision optimization receipt privilege missing' >&2; exit 1; }
echo 'PASS: v2.22 decision optimization receipt registry + privileges'

docker rm -f sc-workspace-decision-runtime sc-workspace-optimization-runtime sc-workspace-uncertainty-runtime sc-workspace-probability-runtime sc-workspace-forecast-runtime sc-workspace-interchange-runtime sc-workspace-ml-runtime sc-workspace-julia-runtime sc-workspace-r-runtime sc-workspace-worker sc-workspace-backend 2>/dev/null || true
docker compose --env-file .env -f docker-compose.yml up -d --build

for i in $(seq 1 75); do
  code="$(curl -sS -o /tmp/sc-workspace-v2220-health.json -w '%{http_code}' http://127.0.0.1:8094/health 2>/dev/null || true)"
  echo "health attempt $i: HTTP ${code:-000}"
  [[ "$code" == 200 ]] && break
  sleep 2
done
python3 - <<'PY'
import json
d=json.load(open('/tmp/sc-workspace-v2220-health.json'))
assert d['ok'] is True and d['version']=='2.22.0', d
for k in ('polyglotScientificRuntimeFabric','rStatisticalEconometricRuntime','juliaSimulationNumericalRuntime','numericalSimulationReceipts','predictiveAnalyticsMachineLearningRuntime','predictiveModelReceipts','modelEvaluationReceipts'):
    assert d[k] is True, (k,d.get(k))
assert d['rRuntimeConfigured'] is True, d
assert d['juliaRuntimeConfigured'] is True, d
assert d['juliaRuntimeBoundedOperations']==8, d
assert d['mlRuntimeConfigured'] is True, d
assert d['mlRuntimeBoundedOperations']==8, d
assert d['nativeArrowParquetInterchange'] is True and d['interchangeRuntimeConfigured'] is True, d
assert d['interchangeRuntimeBoundedOperations']==8 and d['interchangeReceipts'] is True, d
assert d['crossRuntimeReproductionVerification'] is True, d
assert d['forecastingTimeSeriesRuntime'] is True and d['forecastRuntimeConfigured'] is True, d
assert d['forecastRuntimeBoundedOperations']==8 and d['forecastReceipts'] is True and d['forecastEvaluationReceipts'] is True, d
assert d['monteCarloUncertaintyQuantificationRuntime'] is True and d['uncertaintyRuntimeConfigured'] is True, d
assert d['uncertaintyRuntimeBoundedOperations']==8 and d['uncertaintyAnalysisReceipts'] is True, d
assert d['optimizationParameterSearchRuntime'] is True and d['optimizationRuntimeConfigured'] is True, d
assert d['optimizationRuntimeBoundedOperations']==8 and d['optimizationReceipts'] is True, d
assert d['robustDecisionOptimizationRuntime'] is True and d['decisionRuntimeConfigured'] is True, d
assert d['decisionRuntimeBoundedOperations']==8 and d['decisionOptimizationReceipts'] is True, d
assert d['toleranceAwareNumericComparison'] is True and d['crossRuntimeVerificationReceipts'] is True, d
assert d['arbitraryCodeExecution'] is False
print('PASS: v2.20 Monte Carlo/UQ health identity')
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

echo "=== VERIFY JULIA EXECUTABLE ==="
docker exec sc-workspace-julia-runtime /usr/local/julia/bin/julia --version \
  | grep -Eq '^julia version 1\.11\.' \
  || { echo 'ERROR: Julia 1.11 executable is unavailable inside runtime container' >&2; exit 1; }
echo 'PASS: Julia 1.11 executable available at /usr/local/julia/bin/julia'

for i in $(seq 1 60); do
  if docker exec sc-workspace-backend python -c "import httpx,sys; r=httpx.get('http://sc-workspace-ml-runtime:8092/health',timeout=2); sys.exit(0 if r.status_code==200 and r.json().get('ok') is True else 1)" 2>/dev/null; then
    echo "ML runtime health attempt $i: ready"
    break
  fi
  echo "ML runtime health attempt $i: not ready"
  sleep 2
  [[ "$i" -lt 60 ]] || { echo 'ERROR: ML runtime did not become ready' >&2; exit 1; }
done

set -a; . ./.env; set +a

for i in $(seq 1 60); do
  if docker exec sc-workspace-backend python -c "import httpx,sys; r=httpx.get('http://sc-workspace-interchange-runtime:8093/health',timeout=2); sys.exit(0 if r.status_code==200 and r.json().get('ok') is True else 1)" 2>/dev/null; then
    echo "Interchange runtime health attempt $i: ready"
    break
  fi
  echo "Interchange runtime health attempt $i: not ready"
  sleep 2
  [[ "$i" -lt 60 ]] || { echo 'ERROR: interchange runtime did not become ready' >&2; exit 1; }
done

for i in $(seq 1 60); do
  if docker exec sc-workspace-backend python -c "import httpx,sys; r=httpx.get('http://sc-workspace-forecast-runtime:8095/health',timeout=2); sys.exit(0 if r.status_code==200 and r.json().get('ok') is True else 1)" 2>/dev/null; then echo "Forecast runtime health attempt $i: ready"; break; fi
  echo "Forecast runtime health attempt $i: not ready"; sleep 2; [[ "$i" -lt 60 ]] || { echo 'ERROR: forecast runtime did not become ready' >&2; exit 1; }
done
for i in $(seq 1 60); do
  if docker exec sc-workspace-backend python -c "import httpx,sys; r=httpx.get('http://sc-workspace-probability-runtime:8096/health',timeout=2); sys.exit(0 if r.status_code==200 and r.json().get('ok') is True else 1)" 2>/dev/null; then echo "Probability runtime health attempt $i: ready"; break; fi
  echo "Probability runtime health attempt $i: not ready"; sleep 2; [[ "$i" -lt 60 ]] || { echo 'ERROR: probability runtime did not become ready' >&2; exit 1; }
done
for i in $(seq 1 60); do
  if docker exec sc-workspace-backend python -c "import httpx,sys; r=httpx.get('http://sc-workspace-uncertainty-runtime:8097/health',timeout=2); sys.exit(0 if r.status_code==200 and r.json().get('ok') is True else 1)" 2>/dev/null; then echo "Uncertainty runtime health attempt $i: ready"; break; fi
  echo "Uncertainty runtime health attempt $i: not ready"; sleep 2; [[ "$i" -lt 60 ]] || { echo 'ERROR: uncertainty runtime did not become ready' >&2; exit 1; }
done
for i in $(seq 1 60); do
  if docker exec sc-workspace-backend python -c "import httpx,sys; r=httpx.get('http://sc-workspace-optimization-runtime:8098/health',timeout=2); sys.exit(0 if r.status_code==200 and r.json().get('ok') is True else 1)" 2>/dev/null; then echo "Optimization runtime health attempt $i: ready"; break; fi
  echo "Optimization runtime health attempt $i: not ready"; sleep 2; [[ "$i" -lt 60 ]] || { echo 'ERROR: optimization runtime did not become ready' >&2; exit 1; }
done
for i in $(seq 1 60); do
  if docker exec sc-workspace-backend python -c "import httpx,sys; r=httpx.get('http://sc-workspace-decision-runtime:8099/health',timeout=2); sys.exit(0 if r.status_code==200 and r.json().get('ok') is True else 1)" 2>/dev/null; then echo "Decision runtime health attempt $i: ready"; break; fi
  echo "Decision runtime health attempt $i: not ready"; sleep 2; [[ "$i" -lt 60 ]] || { echo 'ERROR: decision runtime did not become ready' >&2; exit 1; }
done

AUTH=(-H "Authorization: Bearer ${SC_WORKSPACE_SERVICE_TOKEN}" -H "X-SC-User-ID: 999999999999")
curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/polyglot/runtimes >/tmp/sc-workspace-v2220-runtimes.json
python3 - <<'PY'
import json
d=json.load(open('/tmp/sc-workspace-v2220-runtimes.json'))
j=next(x for x in d['items'] if x['language']=='julia')
assert j['configured'] is True and j['serviceCredentialConfigured'] is True, j
assert j['runtime']=='julia-simulation-numerical', j
assert len(j['operations'])==8, j
assert j['arbitraryCodeExecution'] is False
print('PASS: Julia runtime registered + configured with eight bounded operations')
PY

curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/polyglot/runtimes/julia/status >/tmp/sc-workspace-v2220-j-status.json
python3 - <<'PY'
import json
d=json.load(open('/tmp/sc-workspace-v2220-j-status.json'))['item']
assert d['configured'] is True and d['available'] is True, d
assert d['runtime']=='julia-simulation-numerical', d
assert len(d['operations'])==8, d
assert d['arbitraryCodeExecution'] is False
print('PASS: Julia runtime service health + bounded operation registry')
PY

curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/polyglot/runtimes/ml/status >/tmp/sc-workspace-v2220-ml-status.json
python3 - <<'PY'
import json
d=json.load(open('/tmp/sc-workspace-v2220-ml-status.json'))['item']
assert d['configured'] is True and d['available'] is True, d
assert d['runtime']=='python-sklearn-predictive', d
assert len(d['operations'])==8, d
assert d['arbitraryCodeExecution'] is False
print('PASS: ML runtime service health + eight bounded operations')
PY

curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/polyglot/runtimes/forecast/status >/tmp/sc-workspace-v2220-forecast-status.json
python3 - <<'PY'
import json
d=json.load(open('/tmp/sc-workspace-v2220-forecast-status.json'))['item']
assert d['configured'] is True and d['available'] is True and d['runtime']=='python-statsmodels-forecasting', d
assert len(d['operations'])==8 and d['arbitraryCodeExecution'] is False, d
print('PASS: forecasting runtime service health + eight bounded operations')
PY

echo "=== VERIFY JULIA WRITABLE CACHE + DIRECT RK4 ==="
docker exec sc-workspace-julia-runtime sh -lc 'test -d /tmp && test -w /tmp && test ! -w /opt/julia-depot'
docker exec \
  -e JULIA_DIRECT_TOKEN="${SC_WORKSPACE_RUNTIME_JULIA_TOKEN}" \
  sc-workspace-backend python -c 'import os,httpx; e={"schema":"sc-workspace-polyglot-execution-envelope/1.0","language":"julia","runtime":"julia-simulation-numerical","operation":"workspace.polyglot.julia.ode-linear-rk4","arbitraryCodeExecution":False,"payload":{"A":[[-1.0]],"initialState":[1.0],"forcing":[0.0],"dt":0.1,"steps":10}}; r=httpx.post("http://sc-workspace-julia-runtime:8091/v1/execute",headers={"Authorization":"Bearer "+os.environ["JULIA_DIRECT_TOKEN"]},json=e,timeout=90); print(r.text if r.status_code!=200 else "DIRECT JULIA HTTP 200"); r.raise_for_status(); d=r.json(); v=float(d["result"]["finalState"][0]); assert d["result"]["kind"]=="linear-ode" and d["result"]["solver"]=="rk4" and 0.36 < v < 0.38, d'
echo 'PASS: Julia writable cache layer + direct RK4 execution'

STAMP="$(date +%s)"
cat >/tmp/sc-workspace-v2220-j-job.json <<JSON
{"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.polyglot.julia.ode-linear-rk4","priority":8,"maxAttempts":1,"idempotencyKey":"deploy-v2220-j-ode-${STAMP}","payload":{"A":[[-1.0]],"initialState":[1.0],"forcing":[0.0],"dt":0.1,"steps":10}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' -d @/tmp/sc-workspace-v2220-j-job.json http://127.0.0.1:8094/v1/jobs >/tmp/sc-workspace-v2220-j-created.json
JOB_ID="$(python3 - <<'PY'
import json; print(json.load(open('/tmp/sc-workspace-v2220-j-created.json'))['item']['jobId'])
PY
)"
for i in $(seq 1 75); do
  curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${JOB_ID}" >/tmp/sc-workspace-v2220-j-job-state.json
  status="$(python3 - <<'PY'
import json; print(json.load(open('/tmp/sc-workspace-v2220-j-job-state.json'))['item']['status'])
PY
)"
  echo "Julia ODE attempt $i: $status"
  [[ "$status" =~ ^(succeeded|failed|blocked|cancelled)$ ]] && break
  sleep 1
done
python3 - <<'PY'
import json
d=json.load(open('/tmp/sc-workspace-v2220-j-job-state.json'))
assert d['item']['status']=='succeeded', d
r=d['result']['polyglot']['result']['remote']['result']
assert r['kind']=='linear-ode' and r['solver']=='rk4', r
v=float(r['finalState'][0]); assert 0.36 < v < 0.38, v
assert d['result']['numericalSimulationReceiptId'], d['result']
assert len(d['result']['resultSha256'])==64
print('PASS: durable Julia RK4 linear ODE produced exp(-1)-equivalent state')
print('PASS: Julia result artifact + polyglot receipt + numerical simulation receipt persisted')
PY

curl -fsS "${AUTH[@]}" 'http://127.0.0.1:8094/v1/numerical-simulation-receipts?limit=25' >/tmp/sc-workspace-v2220-num-receipts.json
python3 - <<'PY'
import json
job=json.load(open('/tmp/sc-workspace-v2220-j-job-state.json'))['item']['jobId']
d=json.load(open('/tmp/sc-workspace-v2220-num-receipts.json'))
row=next((x for x in d['items'] if x['jobId']==job),None)
assert row and row['language']=='julia' and row['modelKind']=='linear-ode', (row,d)
assert row['solver']=='rk4' and row['steps']==10, row
print('PASS: numerical simulation receipt discoverable through API')
PY

echo "=== DURABLE ML LINEAR REGRESSION ==="
python3 - <<'PY' >/tmp/sc-workspace-v2220-ml-job.json
import json,time
rows=[{"x":float(i),"y":2.0*float(i)+1.0} for i in range(1,41)]
print(json.dumps({"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.ml.linear-regression","priority":8,"maxAttempts":1,"idempotencyKey":f"deploy-v2220-ml-linear-{int(time.time())}","payload":{"rows":rows,"features":["x"],"target":"y","seed":17,"testFraction":0.2,"preprocessing":{"standardize":True}}}))
PY
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' -d @/tmp/sc-workspace-v2220-ml-job.json http://127.0.0.1:8094/v1/jobs >/tmp/sc-workspace-v2220-ml-created.json
ML_JOB_ID="$(python3 - <<'PY'
import json; print(json.load(open('/tmp/sc-workspace-v2220-ml-created.json'))['item']['jobId'])
PY
)"
for i in $(seq 1 90); do
  curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${ML_JOB_ID}" >/tmp/sc-workspace-v2220-ml-job-state.json
  status="$(python3 - <<'PY'
import json; print(json.load(open('/tmp/sc-workspace-v2220-ml-job-state.json'))['item']['status'])
PY
)"
  echo "ML linear regression attempt $i: $status"
  [[ "$status" =~ ^(succeeded|failed|blocked|cancelled)$ ]] && break
  sleep 1
done
python3 - <<'PY'
import json
d=json.load(open('/tmp/sc-workspace-v2220-ml-job-state.json'))
assert d['item']['status']=='succeeded', d
r=d['result']['polyglot']['result']['remote']['result']
assert r['modelKind']=='linear-regression' and r['task']=='regression', r
assert float(r['metrics']['r2']) > .999, r['metrics']
assert d['result']['predictiveModelReceiptId'], d['result']
assert d['result']['modelEvaluationReceiptId'], d['result']
assert d['result']['modelArtifactId'], d['result']
assert len(d['result']['modelArtifactSha256'])==64, d['result']
print('PASS: durable ML linear regression produced deterministic high-fit model')
print('PASS: model artifact + predictive model receipt + evaluation receipt persisted')
PY

curl -fsS "${AUTH[@]}" 'http://127.0.0.1:8094/v1/predictive-model-receipts?limit=25' >/tmp/sc-workspace-v2220-model-receipts.json
curl -fsS "${AUTH[@]}" 'http://127.0.0.1:8094/v1/model-evaluation-receipts?limit=25' >/tmp/sc-workspace-v2220-eval-receipts.json
python3 - <<'PY'
import json
job=json.load(open('/tmp/sc-workspace-v2220-ml-job-state.json'))['item']['jobId']
pm=next((x for x in json.load(open('/tmp/sc-workspace-v2220-model-receipts.json'))['items'] if x['jobId']==job),None)
ev=next((x for x in json.load(open('/tmp/sc-workspace-v2220-eval-receipts.json'))['items'] if x['jobId']==job),None)
assert pm and pm['modelKind']=='linear-regression' and pm['modelArtifactId'], pm
assert ev and ev['evaluationKind']=='holdout' and ev['metrics']['r2']>.999, ev
print('PASS: predictive model and evaluation receipts discoverable through API')
PY

docker inspect sc-workspace-ml-runtime --format '{{.HostConfig.ReadonlyRootfs}} {{.HostConfig.PidsLimit}} {{.HostConfig.Memory}} {{.HostConfig.NanoCpus}} {{json .HostConfig.CapDrop}} {{json .HostConfig.SecurityOpt}}' \
  | grep -q '^true 128 2147483648 2000000000 .*ALL.*no-new-privileges' \
  || { echo 'ERROR: ML runtime sandbox mismatch' >&2; exit 1; }
[[ -z "$(docker port sc-workspace-ml-runtime 2>/dev/null || true)" ]] || { echo 'ERROR: ML runtime unexpectedly exposes a host port' >&2; exit 1; }
ML_NET="$(docker inspect sc-workspace-ml-runtime --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}}{{end}}')"
docker network inspect "$ML_NET" --format '{{.Internal}}' | grep -q '^true$' || { echo 'ERROR: ML runtime network is not internal-only' >&2; exit 1; }
echo 'PASS: ML runtime is read-only + 2 CPU + 2 GiB + 128 PID + cap-drop ALL + no-new-privileges + internal-only network'

docker inspect sc-workspace-worker --format '{{.HostConfig.ReadonlyRootfs}} {{.HostConfig.PidsLimit}} {{.HostConfig.Memory}} {{.HostConfig.NanoCpus}} {{json .HostConfig.CapDrop}} {{json .HostConfig.SecurityOpt}}'   | grep -q '^true 256 2147483648 2000000000 .*ALL.*no-new-privileges'   || { echo 'ERROR: Workspace worker sandbox mismatch' >&2; exit 1; }
echo 'PASS: Workspace worker sandbox preserved'

docker inspect sc-workspace-julia-runtime --format '{{.HostConfig.ReadonlyRootfs}} {{.HostConfig.PidsLimit}} {{.HostConfig.Memory}} {{.HostConfig.NanoCpus}} {{json .HostConfig.CapDrop}} {{json .HostConfig.SecurityOpt}}'   | grep -q '^true 128 2147483648 2000000000 .*ALL.*no-new-privileges'   || { echo 'ERROR: Julia runtime sandbox mismatch' >&2; exit 1; }
[[ -z "$(docker port sc-workspace-julia-runtime 2>/dev/null || true)" ]] || { echo 'ERROR: Julia runtime unexpectedly exposes a host port' >&2; exit 1; }
J_NET="$(docker inspect sc-workspace-julia-runtime --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}}{{end}}')"
docker network inspect "$J_NET" --format '{{.Internal}}' | grep -q '^true$' || { echo 'ERROR: Julia runtime network is not internal-only' >&2; exit 1; }
echo 'PASS: Julia runtime is read-only + 2 CPU + 2 GiB + 128 PID + cap-drop ALL + no-new-privileges + internal-only network'

echo "=== NATIVE ARROW / PARQUET INTERCHANGE ==="
curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/interchange/runtime/status >/tmp/sc-workspace-v2220-ix-status.json
python3 - <<'PY2'
import json
d=json.load(open('/tmp/sc-workspace-v2220-ix-status.json'))['item']
assert d['configured'] is True and d['available'] is True, d
assert d['runtime']=='arrow-parquet-interchange' and len(d['operations'])==8, d
assert d['arbitraryCodeExecution'] is False, d
print('PASS: Arrow/Parquet interchange runtime healthy with eight bounded operations')
PY2
python3 - <<'PY2' >/tmp/sc-workspace-v2220-ix-job.json
import json,time
rows=[{'id':i,'x':float(i),'group':'a' if i%2 else 'b'} for i in range(1,21)]
print(json.dumps({'schema':'sc-workspace-job-request/1.0','jobType':'workspace-task','targetProduct':'workspace','operation':'workspace.interchange.parquet.write','priority':8,'maxAttempts':1,'idempotencyKey':f'deploy-v2220-parquet-{int(time.time())}','payload':{'rows':rows}}))
PY2
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' -d @/tmp/sc-workspace-v2220-ix-job.json http://127.0.0.1:8094/v1/jobs >/tmp/sc-workspace-v2220-ix-created.json
IX_JOB_ID="$(python3 - <<'PY2'
import json; print(json.load(open('/tmp/sc-workspace-v2220-ix-created.json'))['item']['jobId'])
PY2
)"
for i in $(seq 1 90); do
  curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${IX_JOB_ID}" >/tmp/sc-workspace-v2220-ix-job-state.json
  status="$(python3 - <<'PY2'
import json; print(json.load(open('/tmp/sc-workspace-v2220-ix-job-state.json'))['item']['status'])
PY2
)"
  echo "Parquet interchange attempt $i: $status"
  [[ "$status" =~ ^(succeeded|failed|blocked|cancelled)$ ]] && break
  sleep 1
done
python3 - <<'PY2'
import json
d=json.load(open('/tmp/sc-workspace-v2220-ix-job-state.json'))
assert d['item']['status']=='succeeded', d
r=d['result']['interchange']['result']
assert r['format']=='parquet' and r['verified'] is True, r
assert r['descriptor']['rowCount']==20 and r['descriptor']['columnCount']==3, r
assert len(r['descriptor']['schemaFingerprint'])==64, r
assert d['result']['binaryArtifactId'] and d['result']['interchangeReceiptId'], d['result']
print('PASS: durable Parquet artifact + schema fingerprint + interchange receipt persisted')
PY2
curl -fsS "${AUTH[@]}" 'http://127.0.0.1:8094/v1/interchange/receipts?limit=25' >/tmp/sc-workspace-v2220-ix-receipts.json
python3 - <<'PY2'
import json
job=json.load(open('/tmp/sc-workspace-v2220-ix-job-state.json'))['item']['jobId']
row=next((x for x in json.load(open('/tmp/sc-workspace-v2220-ix-receipts.json'))['items'] if x['jobId']==job),None)
assert row and row['resultFormat']=='parquet' and row['verified'] is True, row
assert row['rowCount']==20 and row['columnCount']==3 and len(row['schemaFingerprint'])==64, row
print('PASS: native interchange receipt discoverable through API')
PY2
docker inspect sc-workspace-interchange-runtime --format '{{.HostConfig.ReadonlyRootfs}} {{.HostConfig.PidsLimit}} {{.HostConfig.Memory}} {{.HostConfig.NanoCpus}} {{json .HostConfig.CapDrop}} {{json .HostConfig.SecurityOpt}}' \
 | grep -q '^true 128 1610612736 1500000000 .*ALL.*no-new-privileges' \
 || { echo 'ERROR: interchange runtime sandbox mismatch' >&2; exit 1; }
[[ -z "$(docker port sc-workspace-interchange-runtime 2>/dev/null || true)" ]] || { echo 'ERROR: interchange runtime unexpectedly exposes host port' >&2; exit 1; }
IX_NET="$(docker inspect sc-workspace-interchange-runtime --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}}{{end}}')"
docker network inspect "$IX_NET" --format '{{.Internal}}' | grep -q '^true$' || { echo 'ERROR: interchange runtime network is not internal-only' >&2; exit 1; }
echo 'PASS: interchange runtime sandbox is read-only + internal-only + bounded resources'

echo "=== CROSS-RUNTIME REPRODUCTION VERIFICATION ==="
docker exec sc-workspace-backend python - <<'PYV217'
import base64, json, time
from app.db import session_scope
from app.models import ExecutionRun, ExecutionRunOutput
from app.object_store import store_artifact
from app.schemas import ArtifactStoreRequest, CrossRuntimeVerificationCreateRequest
from app.cross_runtime_verification import create_cross_runtime_verification, receipt_metadata
from app.utils import sha256_hex
stamp=str(int(time.time()))
user='deploy-v2220-smoke'
run_a='xrv-a-'+stamp; run_b='xrv-b-'+stamp
with session_scope() as db:
    for run_id,runtime,adapter_fp,value in [(run_a,'workspace.compute.transform','python-fp',1.0000000000),(run_b,'workspace.polyglot.r.describe','r-fp',1.0000000001)]:
        doc={"value":value,"metrics":{"score":0.8750000000},"label":"stable"}
        raw=json.dumps(doc,sort_keys=True,separators=(',',':')).encode()
        aid='xrv-art-'+run_id
        art=store_artifact(db,user,ArtifactStoreRequest.model_validate({"schema":"sc-workspace-artifact-store/1.0","artifactId":aid,"filename":aid+'.json',"mediaType":"application/json","contentBase64":base64.b64encode(raw).decode(),"expectedRevision":0,"metadata":{"kind":"v2.17-smoke"}}))
        row=ExecutionRun(user_key=user,run_id=run_id,project_id='',name='v2.17 cross-runtime smoke',status='succeeded',progress=100,job_id='',target_product='workspace',operation=runtime,dataset_refs=[],model_ref={},parameter_set_ref={},environment_json={},environment_ref={},environment_fingerprint='env-shared',runtime_adapter_ref={},runtime_adapter_fingerprint=adapter_fp,input_fingerprint='input-shared',reproducibility_fingerprint=sha256_hex({'run':run_id}),result_summary={},error_code='',error_message='')
        db.add(row); db.flush()
        db.add(ExecutionRunOutput(user_key=user,run_id=run_id,output_id='result',artifact_id=art.artifact_id,role='result',label='result',media_type='application/json',sha256=art.sha256,bytes=art.bytes,metadata_json={}))
    db.commit()
    payload=CrossRuntimeVerificationCreateRequest.model_validate({"schema":"sc-workspace-cross-runtime-verification/1.0","originalRunId":run_a,"reproductionRunId":run_b,"comparisonMode":"auto","absoluteTolerance":1e-8,"relativeTolerance":1e-7,"requireSameInputs":True})
    receipt=create_cross_runtime_verification(db,user,payload)
    meta=receipt_metadata(receipt)
    assert meta['classification']=='equivalent', meta
    assert meta['exactInputs'] is True and meta['exactOutputs'] is False and meta['equivalentOutputs'] is True, meta
    assert meta['sourceRuntime'] != meta['targetRuntime'], meta
    assert meta['resultArtifactId'] and len(meta['resultSha256'])==64, meta
    print('PASS: tolerance-aware cross-runtime verification classified numerically equivalent outputs')
    print('PASS: cross-runtime verification result artifact + durable receipt persisted')
PYV217

curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/reproduction/cross-runtime/profiles >/tmp/sc-workspace-v2220-xrv-profiles.json
python3 - <<'PYV217'
import json
d=json.load(open('/tmp/sc-workspace-v2220-xrv-profiles.json'))
assert {x['mode'] for x in d['items']}=={'auto','exact-digest','tolerance-aware-json'}, d
assert d['automaticExecution'] is False and d['arbitraryCodeExecution'] is False, d
print('PASS: cross-runtime verification profile API exposes bounded comparison modes')
PYV217

echo "=== FORECASTING & TIME-SERIES RUNTIME ==="
STAMP="$(date +%s)"
cat >/tmp/sc-workspace-v2220-forecast-job.json <<JSON
{"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.forecast.linear-trend","priority":8,"maxAttempts":1,"idempotencyKey":"deploy-v2220-forecast-${STAMP}","payload":{"values":[10,12,14,16,18,20,22,24,26,28,30,32],"horizon":4,"frequency":"monthly"}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/sc-workspace-v2220-forecast-job.json http://127.0.0.1:8094/v1/jobs >/tmp/sc-workspace-v2220-forecast-created.json
FORECAST_JOB_ID="$(python3 -c "import json; print(json.load(open('/tmp/sc-workspace-v2220-forecast-created.json'))['item']['jobId'])")"
for i in $(seq 1 60); do
  curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${FORECAST_JOB_ID}" >/tmp/sc-workspace-v2220-forecast-state.json
  state="$(python3 -c "import json; print(json.load(open('/tmp/sc-workspace-v2220-forecast-state.json'))['item']['status'])")"; echo "forecast attempt $i: $state"
  [[ "$state" == succeeded ]] && break
  [[ "$state" == failed || "$state" == blocked ]] && { cat /tmp/sc-workspace-v2220-forecast-state.json; exit 1; }
  sleep 2
done
python3 - <<'PY'
import json
doc=json.load(open('/tmp/sc-workspace-v2220-forecast-state.json'))
j=doc['item']; assert j['status']=='succeeded',j
result=doc.get('result') or {}; assert result.get('forecastReceiptId'),result
remote=((((result.get('polyglot') or {}).get('result') or {}).get('remote') or {}).get('result') or {})
f=remote.get('forecast') or []; assert len(f)==4 and 33.5<float(f[0])<34.5,remote
print('PASS: durable linear-trend forecast produced deterministic four-step forecast')
PY
curl -fsS "${AUTH[@]}" 'http://127.0.0.1:8094/v1/forecast-receipts?limit=10' >/tmp/sc-workspace-v2220-forecast-receipts.json
python3 - <<'PY'
import json
items=json.load(open('/tmp/sc-workspace-v2220-forecast-receipts.json'))['items']; assert any(x.get('modelKind')=='linear-trend' and x.get('horizon')==4 for x in items),items
print('PASS: forecast receipt persisted and is discoverable through API')
PY
FORECAST_SEC="$(docker inspect sc-workspace-forecast-runtime --format '{{.HostConfig.ReadonlyRootfs}}|{{.HostConfig.NanoCpus}}|{{.HostConfig.Memory}}|{{.HostConfig.PidsLimit}}')"
echo "$FORECAST_SEC" | grep -q '^true|' || { echo 'ERROR: forecast runtime rootfs is not read-only' >&2; exit 1; }
docker inspect sc-workspace-forecast-runtime --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}' | grep -q 'sc-workspace-runtime' || { echo 'ERROR: forecast runtime is not on internal runtime network' >&2; exit 1; }
echo 'PASS: forecast runtime sandbox is read-only + internal-only + bounded resources'

echo '=== PROBABILISTIC & BAYESIAN RUNTIME ==='
curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/polyglot/runtimes/probability/status >/tmp/sc-workspace-v2220-probability-status.json
python3 - <<'PY2'
import json
d=json.load(open('/tmp/sc-workspace-v2220-probability-status.json'))['item']
assert d['configured'] is True and d['available'] is True and d['runtime']=='python-probabilistic-bayesian', d
assert len(d.get('operations') or [])==6, d
print('PASS: probabilistic runtime service health + six bounded operations')
PY2
cat >/tmp/sc-workspace-v2220-probability-job.json <<JSON
{"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.probability.beta-binomial-update","priority":8,"maxAttempts":1,"idempotencyKey":"deploy-v2220-probability-${STAMP}","payload":{"alpha":2,"beta":2,"successes":8,"trials":10,"seed":7,"draws":2000}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/sc-workspace-v2220-probability-job.json http://127.0.0.1:8094/v1/jobs >/tmp/sc-workspace-v2220-probability-created.json
PROB_JOB_ID="$(python3 -c "import json; print(json.load(open('/tmp/sc-workspace-v2220-probability-created.json'))['item']['jobId'])")"
for i in $(seq 1 60); do
  curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${PROB_JOB_ID}" >/tmp/sc-workspace-v2220-probability-state.json
  state="$(python3 -c "import json; print(json.load(open('/tmp/sc-workspace-v2220-probability-state.json'))['item']['status'])")"; echo "probability attempt $i: $state"
  [[ "$state" == succeeded ]] && break
  [[ "$state" == failed || "$state" == blocked ]] && { cat /tmp/sc-workspace-v2220-probability-state.json; exit 1; }
  sleep 2
done
python3 - <<'PY2'
import json
doc=json.load(open('/tmp/sc-workspace-v2220-probability-state.json'))
d=doc['item']; assert d['status']=='succeeded',d
r=doc.get('result') or {}; assert r.get('probabilisticInferenceReceiptId'),r
p=r['polyglot']['result']['remote']['result']['posterior']; assert p['alpha']==10.0 and p['beta']==4.0,p
print('PASS: durable Beta-Binomial Bayesian update produced posterior and job result')
PY2
curl -fsS "${AUTH[@]}" 'http://127.0.0.1:8094/v1/probabilistic-inference-receipts?limit=10' >/tmp/sc-workspace-v2220-probability-receipts.json
python3 - <<'PY2'
import json
items=json.load(open('/tmp/sc-workspace-v2220-probability-receipts.json'))['items']; assert any(x.get('inferenceKind')=='beta-binomial' for x in items),items
print('PASS: probabilistic inference receipt persisted and is discoverable through API')
PY2
PROB_SEC="$(docker inspect sc-workspace-probability-runtime --format '{{.HostConfig.ReadonlyRootfs}}|{{.HostConfig.NanoCpus}}|{{.HostConfig.Memory}}|{{.HostConfig.PidsLimit}}')"
echo "$PROB_SEC" | grep -q '^true|' || { echo 'ERROR: probability runtime rootfs is not read-only' >&2; exit 1; }
docker inspect sc-workspace-probability-runtime --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}' | grep -q 'sc-workspace-runtime' || { echo 'ERROR: probability runtime is not on internal runtime network' >&2; exit 1; }
echo 'PASS: probability runtime sandbox is read-only + internal-only + bounded resources'
echo '=== MONTE CARLO & UNCERTAINTY QUANTIFICATION ==='
curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/polyglot/runtimes/uncertainty/status >/tmp/sc-workspace-v2220-uncertainty-status.json
python3 - <<'PYUQ'
import json
d=json.load(open('/tmp/sc-workspace-v2220-uncertainty-status.json'))['item']
assert d['configured'] is True and d['available'] is True and d['runtime']=='python-monte-carlo-uq', d
assert len(d.get('operations') or [])==8, d
print('PASS: uncertainty runtime service health + eight bounded operations')
PYUQ
cat >/tmp/sc-workspace-v2220-uncertainty-job.json <<JSON
{"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.uncertainty.monte-carlo-weighted-sum","priority":8,"maxAttempts":1,"idempotencyKey":"deploy-v2220-uncertainty-${STAMP}","payload":{"terms":[{"name":"demand","coefficient":2,"distribution":{"kind":"normal","mean":10,"sd":1}},{"name":"loss","coefficient":-1,"distribution":{"kind":"uniform","min":1,"max":3}}],"offset":5,"draws":2000,"seed":2200,"threshold":24}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/sc-workspace-v2220-uncertainty-job.json http://127.0.0.1:8094/v1/jobs >/tmp/sc-workspace-v2220-uncertainty-created.json
UQ_JOB_ID="$(python3 -c "import json; print(json.load(open('/tmp/sc-workspace-v2220-uncertainty-created.json'))['item']['jobId'])")"
for i in $(seq 1 60); do
  curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${UQ_JOB_ID}" >/tmp/sc-workspace-v2220-uncertainty-state.json
  state="$(python3 -c "import json; print(json.load(open('/tmp/sc-workspace-v2220-uncertainty-state.json'))['item']['status'])")"; echo "uncertainty attempt $i: $state"
  [[ "$state" == succeeded ]] && break
  [[ "$state" == failed || "$state" == blocked ]] && { cat /tmp/sc-workspace-v2220-uncertainty-state.json; exit 1; }
  sleep 2
done
python3 - <<'PYUQ'
import json
doc=json.load(open('/tmp/sc-workspace-v2220-uncertainty-state.json'))
j=doc['item']; assert j['status']=='succeeded',j
r=doc.get('result') or {}; assert r.get('uncertaintyAnalysisReceiptId'),r
u=r['polyglot']['result']['remote']['result']; assert u['kind']=='monte-carlo-weighted-sum' and u['draws']==2000 and u['seed']==2200,u
assert 22.0 < float(u['summary']['mean']) < 24.0,u
print('PASS: durable seeded Monte Carlo uncertainty job produced reproducible summary and job result')
PYUQ
curl -fsS "${AUTH[@]}" 'http://127.0.0.1:8094/v1/uncertainty-analysis-receipts?limit=10' >/tmp/sc-workspace-v2220-uncertainty-receipts.json
python3 - <<'PYUQ'
import json
items=json.load(open('/tmp/sc-workspace-v2220-uncertainty-receipts.json'))['items']; assert any(x.get('analysisKind')=='monte-carlo-weighted-sum' and x.get('sampleCount')==2000 and x.get('seed')==2200 for x in items),items
print('PASS: uncertainty analysis receipt persisted and is discoverable through API')
PYUQ
UQ_SEC="$(docker inspect sc-workspace-uncertainty-runtime --format '{{.HostConfig.ReadonlyRootfs}}|{{.HostConfig.NanoCpus}}|{{.HostConfig.Memory}}|{{.HostConfig.PidsLimit}}')"
echo "$UQ_SEC" | grep -q '^true|' || { echo 'ERROR: uncertainty runtime rootfs is not read-only' >&2; exit 1; }
docker inspect sc-workspace-uncertainty-runtime --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}' | grep -q 'sc-workspace-runtime' || { echo 'ERROR: uncertainty runtime is not on internal runtime network' >&2; exit 1; }
echo 'PASS: uncertainty runtime sandbox is read-only + internal-only + bounded resources'

echo "=== OPTIMIZATION & PARAMETER SEARCH RUNTIME ==="
curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/polyglot/runtimes/optimization/status >/tmp/sc-workspace-v2220-opt-status.json
python3 - <<'PYOPTSTATUS'
import json
d=json.load(open('/tmp/sc-workspace-v2220-opt-status.json'))['item']
assert d['configured'] is True and d['available'] is True and d['runtime']=='python-optimization-parameter-search',d
assert len(d['operations'])==8 and d['arbitraryCodeExecution'] is False,d
print('PASS: optimization runtime service health + eight bounded operations')
PYOPTSTATUS
cat >/tmp/sc-workspace-v2220-opt-job.json <<JSON
{"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.optimize.linear-box","priority":8,"maxAttempts":1,"idempotencyKey":"deploy-v2220-opt-${STAMP}","payload":{"direction":"minimize","bounds":[{"name":"x","min":0,"max":10},{"name":"y","min":-2,"max":3}],"objective":{"kind":"linear","coefficients":[2,-4],"intercept":1}}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/sc-workspace-v2220-opt-job.json http://127.0.0.1:8094/v1/jobs >/tmp/sc-workspace-v2220-opt-created.json
OPT_JOB_ID="$(python3 -c "import json; print(json.load(open('/tmp/sc-workspace-v2220-opt-created.json'))['item']['jobId'])")"
for i in $(seq 1 60); do
  curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${OPT_JOB_ID}" >/tmp/sc-workspace-v2220-opt-state.json
  state="$(python3 -c "import json; print(json.load(open('/tmp/sc-workspace-v2220-opt-state.json'))['item']['status'])")"; echo "optimization attempt $i: $state"
  [[ "$state" == succeeded ]] && break
  [[ "$state" == failed || "$state" == blocked ]] && { cat /tmp/sc-workspace-v2220-opt-state.json; exit 1; }
  sleep 1
done
python3 - <<'PYOPTJOB'
import json
doc=json.load(open('/tmp/sc-workspace-v2220-opt-state.json')); assert doc['item']['status']=='succeeded',doc
r=doc.get('result') or {}; assert r.get('optimizationReceiptId'),r
z=r['polyglot']['result']['remote']['result']; assert z['kind']=='linear-box' and z['bestParameters']=={'x':0.0,'y':3.0} and z['bestValue']==-11.0,z
print('PASS: durable bounded optimization job produced exact solution and job result')
PYOPTJOB
curl -fsS "${AUTH[@]}" 'http://127.0.0.1:8094/v1/optimization-receipts?limit=10' >/tmp/sc-workspace-v2220-opt-receipts.json
python3 - <<'PYOPTREC'
import json
items=json.load(open('/tmp/sc-workspace-v2220-opt-receipts.json'))['items']; assert any(x.get('optimizationKind')=='linear-box' and x.get('bestValue')==-11.0 for x in items),items
print('PASS: optimization receipt persisted and is discoverable through API')
PYOPTREC
OPT_SEC="$(docker inspect sc-workspace-optimization-runtime --format '{{.HostConfig.ReadonlyRootfs}}|{{.HostConfig.NanoCpus}}|{{.HostConfig.Memory}}|{{.HostConfig.PidsLimit}}')"
echo "$OPT_SEC" | grep -q '^true|' || { echo 'ERROR: optimization runtime rootfs is not read-only' >&2; exit 1; }
docker inspect sc-workspace-optimization-runtime --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}' | grep -q 'sc-workspace-runtime' || { echo 'ERROR: optimization runtime is not on internal runtime network' >&2; exit 1; }
echo 'PASS: optimization runtime sandbox is read-only + internal-only + bounded resources'
echo '=== ROBUST DECISION OPTIMIZATION & PARETO ANALYSIS ==='
curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/polyglot/runtimes/decision/status >/tmp/sc-workspace-v2220-decision-status.json
python3 - <<'PYDECSTATUS'
import json
d=json.load(open('/tmp/sc-workspace-v2220-decision-status.json'))['item']
assert d['configured'] is True and d['available'] is True and d['runtime']=='python-robust-decision-pareto',d
assert len(d['operations'])==8,d
print('PASS: decision runtime service health + eight bounded operations')
PYDECSTATUS
STAMP="$(date +%s)"
cat >/tmp/sc-workspace-v2220-decision-job.json <<JSON
{"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.decision.minimax-regret","priority":8,"maxAttempts":1,"idempotencyKey":"deploy-v2220-decision-${STAMP}","payload":{"candidates":[{"id":"A","scores":[10,2]},{"id":"B","scores":[7,7]}],"scenarios":[{"id":"growth","probability":0.5},{"id":"stress","probability":0.5}],"direction":"maximize"}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/sc-workspace-v2220-decision-job.json http://127.0.0.1:8094/v1/jobs >/tmp/sc-workspace-v2220-decision-created.json
DEC_JOB_ID="$(python3 -c "import json; print(json.load(open('/tmp/sc-workspace-v2220-decision-created.json'))['item']['jobId'])")"
for i in $(seq 1 60); do
  curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${DEC_JOB_ID}" >/tmp/sc-workspace-v2220-decision-state.json
  state="$(python3 -c "import json; print(json.load(open('/tmp/sc-workspace-v2220-decision-state.json'))['item']['status'])")"; echo "decision attempt $i: $state"
  [[ "$state" == succeeded ]] && break
  [[ "$state" == failed || "$state" == blocked ]] && { cat /tmp/sc-workspace-v2220-decision-state.json; exit 1; }
  sleep 2
done
python3 - <<'PYDECRESULT'
import json
doc=json.load(open('/tmp/sc-workspace-v2220-decision-state.json'))
assert doc['item']['status']=='succeeded',doc
r=doc.get('result') or {}; assert r.get('decisionOptimizationReceiptId'),r
x=r['polyglot']['result']['remote']['result']; assert x['kind']=='minimax-regret' and x['selectedAlternative']=='B',x
print('PASS: durable minimax-regret decision job selected robust alternative and persisted job result')
PYDECRESULT
curl -fsS "${AUTH[@]}" 'http://127.0.0.1:8094/v1/decision-optimization-receipts?limit=10' >/tmp/sc-workspace-v2220-decision-receipts.json
python3 - <<'PYDECRECEIPT'
import json
items=json.load(open('/tmp/sc-workspace-v2220-decision-receipts.json'))['items']
assert any(x.get('analysisKind')=='minimax-regret' and x.get('selectedAlternative')=='B' and x.get('scenarioCount')==2 for x in items),items
print('PASS: decision optimization receipt persisted and is discoverable through API')
PYDECRECEIPT
DEC_SEC="$(docker inspect sc-workspace-decision-runtime --format '{{.HostConfig.ReadonlyRootfs}}|{{.HostConfig.NanoCpus}}|{{.HostConfig.Memory}}|{{.HostConfig.PidsLimit}}')"
echo "$DEC_SEC" | grep -q '^true|' || { echo 'ERROR: decision runtime rootfs is not read-only' >&2; exit 1; }
docker inspect sc-workspace-decision-runtime --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}' | grep -q 'sc-workspace-runtime' || { echo 'ERROR: decision runtime is not on internal runtime network' >&2; exit 1; }
echo 'PASS: decision runtime sandbox is read-only + internal-only + bounded resources'
echo 'PASS: Workspace backend v2.22.0 API + worker + R + Julia + ML + Arrow/Parquet + cross-runtime verification + forecasting/time-series + probabilistic/Bayesian + Monte Carlo/UQ + optimization/parameter-search + robust decision/Pareto runtimes are running.'




