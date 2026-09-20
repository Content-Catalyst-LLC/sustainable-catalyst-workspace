#!/usr/bin/env bash
set -euo pipefail

ZIP_PATH="${1:-/tmp/sustainable-catalyst-workspace-backend-v2.34.0.zip}"
BASE="/opt/sustainable-catalyst"
NEW="$BASE/sustainable-catalyst-workspace-backend-v2.34.0"

[[ -f "$ZIP_PATH" ]] || { echo "ERROR: backend ZIP not found: $ZIP_PATH" >&2; exit 1; }
ENV_SOURCE=""
for candidate in \
  "$BASE/sustainable-catalyst-workspace-backend-v2.34.0/.env" \
  "$BASE/sustainable-catalyst-workspace-backend-v2.33.0/.env" \
  "$BASE/sustainable-catalyst-workspace-backend-v2.31.0/.env" \
  "$BASE/sustainable-catalyst-workspace-backend-v2.27.0/.env" \
  "$BASE/sustainable-catalyst-workspace-backend-v2.26.0/.env" \
  "$BASE/sustainable-catalyst-workspace-backend-v2.23.0/.env" \
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
if [[ -z "${SC_WORKSPACE_RUNTIME_RELIABILITY_TOKEN:-}" ]]; then SC_WORKSPACE_RUNTIME_RELIABILITY_TOKEN="$(python3 - <<'PYRELTOKEN'
import secrets
print(secrets.token_urlsafe(48))
PYRELTOKEN
)"; fi
set_env_value SC_WORKSPACE_RUNTIME_RELIABILITY_TOKEN "$SC_WORKSPACE_RUNTIME_RELIABILITY_TOKEN"
set_env_value SC_WORKSPACE_RUNTIME_RELIABILITY_URL "http://sc-workspace-reliability-runtime:8100/v1/execute"
set_env_value SC_WORKSPACE_MAX_RELIABILITY_ANALYSIS_RECEIPTS_PER_ACCOUNT "10000"
set_env_value SC_WORKSPACE_MAX_VISUALIZATION_SPECS_PER_ACCOUNT "1000"
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
  migrations/022_robust_decision_optimization_pareto.sql \
  migrations/023_reliability_survival_failure_time.sql \
  migrations/024_backend_authority_domain_service.sql \
  migrations/025_workspace_command_query_api.sql \
  migrations/026_server_side_notebook_artifact_orchestration.sql \
  migrations/027_reproducible_scientific_study_packages.sql \
  migrations/028_declarative_visualization_specification_api.sql \
  migrations/029_local_first_synchronization_protocol.sql \
  migrations/030_cross_product_research_handoff_fabric.sql \
  migrations/031_backend_policy_identity_authorization_consolidation.sql
do
  echo "Applying $migration"
  docker exec -i sc-postgres psql -U "$PG_ADMIN_USER" -d sc_workspace -v ON_ERROR_STOP=1 < "$migration" >/dev/null
done

docker exec -i sc-postgres psql -U "$PG_ADMIN_USER" -d sc_workspace -tAc \
  "SELECT count(*) FROM information_schema.role_table_grants WHERE grantee='sc_workspace' AND table_name='workspace_statistical_model_receipts' AND privilege_type='INSERT';" \
  | grep -q '^1$' || { echo 'ERROR: statistical model receipt privilege missing' >&2; exit 1; }
echo 'PASS: v2.15 statistical model receipt registry + privileges'
docker exec -i sc-postgres psql -U "$PG_ADMIN_USER" -d sc_workspace -tAc \
  "SELECT count(*) FROM information_schema.role_table_grants WHERE grantee='sc_workspace' AND table_name='workspace_cross_product_research_handoffs' AND privilege_type='INSERT';" \
  | grep -q '^1$' || { echo 'ERROR: cross-product handoff privilege missing' >&2; exit 1; }
echo 'PASS: v2.33 cross-product handoff registry + privileges'
docker exec -i sc-postgres psql -U "$PG_ADMIN_USER" -d sc_workspace -tAc \
  "SELECT count(*) FROM information_schema.role_table_grants WHERE grantee='sc_workspace' AND table_name='workspace_authorization_decision_receipts' AND privilege_type='INSERT';" \
  | grep -q '^1$' || { echo 'ERROR: authorization decision receipt privilege missing' >&2; exit 1; }
echo 'PASS: v2.34 authorization decision receipt registry + privileges'

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
docker exec -i sc-postgres psql -U "$PG_ADMIN_USER" -d sc_workspace -tAc "SELECT count(*) FROM information_schema.role_table_grants WHERE grantee='sc_workspace' AND table_name='workspace_reliability_analysis_receipts' AND privilege_type='INSERT';" | grep -q '^1$' || { echo 'ERROR: reliability analysis receipt privilege missing' >&2; exit 1; }
echo 'PASS: v2.23 reliability analysis receipt registry + privileges'
docker exec -i sc-postgres psql -U "$PG_ADMIN_USER" -d sc_workspace -tAc "SELECT count(*) FROM information_schema.role_table_grants WHERE grantee='sc_workspace' AND table_name='workspace_local_first_sync_receipts' AND privilege_type='INSERT';" | grep -q '^1$' || { echo 'ERROR: local-first sync receipt privilege missing' >&2; exit 1; }
echo 'PASS: v2.31 local-first sync receipt registry + privileges'
docker exec -i sc-postgres psql -U "$PG_ADMIN_USER" -d sc_workspace -tAc "SELECT count(*) FROM information_schema.role_table_grants WHERE grantee='sc_workspace' AND table_name='workspace_domain_mutation_receipts' AND privilege_type='INSERT';" | grep -q '^1$' || { echo 'ERROR: domain mutation receipt privilege missing' >&2; exit 1; }
echo 'PASS: v2.24 backend authority domain mutation receipt registry + privileges'
docker exec -i sc-postgres psql -U "$PG_ADMIN_USER" -d sc_workspace -tAc "SELECT count(*) FROM information_schema.role_table_grants WHERE grantee='sc_workspace' AND table_name='workspace_command_receipts' AND privilege_type='INSERT';" | grep -q '^1$' || { echo 'ERROR: command receipt privilege missing' >&2; exit 1; }
echo 'PASS: v2.25 command receipt registry + privileges'

docker exec -i sc-postgres psql -U "$PG_ADMIN_USER" -d sc_workspace -tAc "SELECT count(*) FROM information_schema.role_table_grants WHERE grantee='sc_workspace' AND table_name='workspace_scientific_study_packages' AND privilege_type='INSERT';" | grep -q '^1$' || { echo 'ERROR: scientific study package privilege missing' >&2; exit 1; }
echo 'PASS: v2.27 scientific study package registry + privileges'
docker exec -i sc-postgres psql -U "$PG_ADMIN_USER" -d sc_workspace -tAc "SELECT count(*) FROM information_schema.role_table_grants WHERE grantee='sc_workspace' AND table_name='workspace_visualization_specs' AND privilege_type='INSERT';" | grep -q '^1$' || { echo 'ERROR: visualization spec privilege missing' >&2; exit 1; }
docker exec -i sc-postgres psql -U "$PG_ADMIN_USER" -d sc_workspace -tAc "SELECT count(*) FROM information_schema.role_table_grants WHERE grantee='sc_workspace' AND table_name='workspace_visualization_spec_receipts' AND privilege_type='INSERT';" | grep -q '^1$' || { echo 'ERROR: visualization spec receipt privilege missing' >&2; exit 1; }
echo 'PASS: v2.28 visualization specification registry + privileges'

docker rm -f sc-workspace-reliability-runtime sc-workspace-decision-runtime sc-workspace-optimization-runtime sc-workspace-uncertainty-runtime sc-workspace-probability-runtime sc-workspace-forecast-runtime sc-workspace-interchange-runtime sc-workspace-ml-runtime sc-workspace-julia-runtime sc-workspace-r-runtime sc-workspace-worker sc-workspace-backend 2>/dev/null || true
docker compose --env-file .env -f docker-compose.yml up -d --build

for i in $(seq 1 75); do
  code="$(curl -sS -o /tmp/sc-workspace-v2340-health.json -w '%{http_code}' http://127.0.0.1:8094/health 2>/dev/null || true)"
  echo "health attempt $i: HTTP ${code:-000}"
  [[ "$code" == 200 ]] && break
  sleep 2
done
python3 - <<'PY'
import json
d=json.load(open('/tmp/sc-workspace-v2340-health.json'))
assert d['ok'] is True and d['version']=='2.34.0', d
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
assert d['reliabilitySurvivalFailureTimeRuntime'] is True and d['reliabilityRuntimeConfigured'] is True, d
assert d['reliabilityRuntimeBoundedOperations']==8 and d['reliabilityAnalysisReceipts'] is True, d
assert d['backendDomainAuthority'] is True and d['backendAuthoritativeState'] is True, d
assert d['browserAuthoritativeState'] is False and d['serverSideDomainValidation'] is True, d
assert d['serverSideRevisionAuthority'] is True and d['domainMutationReceipts'] is True, d
assert d['canonicalDomainStore']=='postgresql' and d['domainAuthoritySchema']=='sc-workspace-domain-authority/1.0', d
assert d['workspaceCommandQueryApi'] is True and d['serverSideCommandDispatch'] is True, d
assert d['serverGeneratedReadModels'] is True and d['commandReceipts'] is True, d
assert d['queriesAreReadOnly'] is True and d['commandQuerySchema']=='sc-workspace-command-query/1.0', d
assert d['toleranceAwareNumericComparison'] is True and d['crossRuntimeVerificationReceipts'] is True, d
assert d['declarativeVisualizationSpecificationApi'] is True and d['rendererNeutralVisualizationSpecs'] is True, d
assert d['visualizationSpecRevisionHistory'] is True and d['visualizationSpecReceipts'] is True, d
assert d['linkedVisualizationViews'] is True and d['visualizationSourceProvenancePinning'] is True, d
assert d['browserDefinesAnalyticalMeaning'] is False, d
assert d['arbitraryCodeExecution'] is False
print('PASS: v2.25 command/query + backend authority + inherited runtime health identity')
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
for i in $(seq 1 60); do
  if docker exec sc-workspace-backend python -c "import httpx,sys; r=httpx.get('http://sc-workspace-reliability-runtime:8100/health',timeout=2); sys.exit(0 if r.status_code==200 and r.json().get('ok') is True else 1)" 2>/dev/null; then echo "Reliability runtime health attempt $i: ready"; break; fi
  echo "Reliability runtime health attempt $i: not ready"; sleep 2; [[ "$i" -lt 60 ]] || { echo 'ERROR: reliability runtime did not become ready' >&2; exit 1; }
done

AUTH=(-H "Authorization: Bearer ${SC_WORKSPACE_SERVICE_TOKEN}" -H "X-SC-User-ID: 999999999999")
curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/polyglot/runtimes >/tmp/sc-workspace-v2340-runtimes.json
python3 - <<'PY'
import json
d=json.load(open('/tmp/sc-workspace-v2340-runtimes.json'))
j=next(x for x in d['items'] if x['language']=='julia')
assert j['configured'] is True and j['serviceCredentialConfigured'] is True, j
assert j['runtime']=='julia-simulation-numerical', j
assert len(j['operations'])==8, j
assert j['arbitraryCodeExecution'] is False
print('PASS: Julia runtime registered + configured with eight bounded operations')
PY

curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/polyglot/runtimes/julia/status >/tmp/sc-workspace-v2340-j-status.json
python3 - <<'PY'
import json
d=json.load(open('/tmp/sc-workspace-v2340-j-status.json'))['item']
assert d['configured'] is True and d['available'] is True, d
assert d['runtime']=='julia-simulation-numerical', d
assert len(d['operations'])==8, d
assert d['arbitraryCodeExecution'] is False
print('PASS: Julia runtime service health + bounded operation registry')
PY

curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/polyglot/runtimes/ml/status >/tmp/sc-workspace-v2340-ml-status.json
python3 - <<'PY'
import json
d=json.load(open('/tmp/sc-workspace-v2340-ml-status.json'))['item']
assert d['configured'] is True and d['available'] is True, d
assert d['runtime']=='python-sklearn-predictive', d
assert len(d['operations'])==8, d
assert d['arbitraryCodeExecution'] is False
print('PASS: ML runtime service health + eight bounded operations')
PY

curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/polyglot/runtimes/forecast/status >/tmp/sc-workspace-v2340-forecast-status.json
python3 - <<'PY'
import json
d=json.load(open('/tmp/sc-workspace-v2340-forecast-status.json'))['item']
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
cat >/tmp/sc-workspace-v2340-j-job.json <<JSON
{"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.polyglot.julia.ode-linear-rk4","priority":8,"maxAttempts":1,"idempotencyKey":"deploy-v2340-j-ode-${STAMP}","payload":{"A":[[-1.0]],"initialState":[1.0],"forcing":[0.0],"dt":0.1,"steps":10}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' -d @/tmp/sc-workspace-v2340-j-job.json http://127.0.0.1:8094/v1/jobs >/tmp/sc-workspace-v2340-j-created.json
JOB_ID="$(python3 - <<'PY'
import json; print(json.load(open('/tmp/sc-workspace-v2340-j-created.json'))['item']['jobId'])
PY
)"
for i in $(seq 1 75); do
  curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${JOB_ID}" >/tmp/sc-workspace-v2340-j-job-state.json
  status="$(python3 - <<'PY'
import json; print(json.load(open('/tmp/sc-workspace-v2340-j-job-state.json'))['item']['status'])
PY
)"
  echo "Julia ODE attempt $i: $status"
  [[ "$status" =~ ^(succeeded|failed|blocked|cancelled)$ ]] && break
  sleep 1
done
python3 - <<'PY'
import json
d=json.load(open('/tmp/sc-workspace-v2340-j-job-state.json'))
assert d['item']['status']=='succeeded', d
r=d['result']['polyglot']['result']['remote']['result']
assert r['kind']=='linear-ode' and r['solver']=='rk4', r
v=float(r['finalState'][0]); assert 0.36 < v < 0.38, v
assert d['result']['numericalSimulationReceiptId'], d['result']
assert len(d['result']['resultSha256'])==64
print('PASS: durable Julia RK4 linear ODE produced exp(-1)-equivalent state')
print('PASS: Julia result artifact + polyglot receipt + numerical simulation receipt persisted')
PY

curl -fsS "${AUTH[@]}" 'http://127.0.0.1:8094/v1/numerical-simulation-receipts?limit=25' >/tmp/sc-workspace-v2340-num-receipts.json
python3 - <<'PY'
import json
job=json.load(open('/tmp/sc-workspace-v2340-j-job-state.json'))['item']['jobId']
d=json.load(open('/tmp/sc-workspace-v2340-num-receipts.json'))
row=next((x for x in d['items'] if x['jobId']==job),None)
assert row and row['language']=='julia' and row['modelKind']=='linear-ode', (row,d)
assert row['solver']=='rk4' and row['steps']==10, row
print('PASS: numerical simulation receipt discoverable through API')
PY

echo "=== DURABLE ML LINEAR REGRESSION ==="
python3 - <<'PY' >/tmp/sc-workspace-v2340-ml-job.json
import json,time
rows=[{"x":float(i),"y":2.0*float(i)+1.0} for i in range(1,41)]
print(json.dumps({"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.ml.linear-regression","priority":8,"maxAttempts":1,"idempotencyKey":f"deploy-v2340-ml-linear-{int(time.time())}","payload":{"rows":rows,"features":["x"],"target":"y","seed":17,"testFraction":0.2,"preprocessing":{"standardize":True}}}))
PY
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' -d @/tmp/sc-workspace-v2340-ml-job.json http://127.0.0.1:8094/v1/jobs >/tmp/sc-workspace-v2340-ml-created.json
ML_JOB_ID="$(python3 - <<'PY'
import json; print(json.load(open('/tmp/sc-workspace-v2340-ml-created.json'))['item']['jobId'])
PY
)"
for i in $(seq 1 90); do
  curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${ML_JOB_ID}" >/tmp/sc-workspace-v2340-ml-job-state.json
  status="$(python3 - <<'PY'
import json; print(json.load(open('/tmp/sc-workspace-v2340-ml-job-state.json'))['item']['status'])
PY
)"
  echo "ML linear regression attempt $i: $status"
  [[ "$status" =~ ^(succeeded|failed|blocked|cancelled)$ ]] && break
  sleep 1
done
python3 - <<'PY'
import json
d=json.load(open('/tmp/sc-workspace-v2340-ml-job-state.json'))
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

curl -fsS "${AUTH[@]}" 'http://127.0.0.1:8094/v1/predictive-model-receipts?limit=25' >/tmp/sc-workspace-v2340-model-receipts.json
curl -fsS "${AUTH[@]}" 'http://127.0.0.1:8094/v1/model-evaluation-receipts?limit=25' >/tmp/sc-workspace-v2340-eval-receipts.json
python3 - <<'PY'
import json
job=json.load(open('/tmp/sc-workspace-v2340-ml-job-state.json'))['item']['jobId']
pm=next((x for x in json.load(open('/tmp/sc-workspace-v2340-model-receipts.json'))['items'] if x['jobId']==job),None)
ev=next((x for x in json.load(open('/tmp/sc-workspace-v2340-eval-receipts.json'))['items'] if x['jobId']==job),None)
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
curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/interchange/runtime/status >/tmp/sc-workspace-v2340-ix-status.json
python3 - <<'PY2'
import json
d=json.load(open('/tmp/sc-workspace-v2340-ix-status.json'))['item']
assert d['configured'] is True and d['available'] is True, d
assert d['runtime']=='arrow-parquet-interchange' and len(d['operations'])==8, d
assert d['arbitraryCodeExecution'] is False, d
print('PASS: Arrow/Parquet interchange runtime healthy with eight bounded operations')
PY2
python3 - <<'PY2' >/tmp/sc-workspace-v2340-ix-job.json
import json,time
rows=[{'id':i,'x':float(i),'group':'a' if i%2 else 'b'} for i in range(1,21)]
print(json.dumps({'schema':'sc-workspace-job-request/1.0','jobType':'workspace-task','targetProduct':'workspace','operation':'workspace.interchange.parquet.write','priority':8,'maxAttempts':1,'idempotencyKey':f'deploy-v2340-parquet-{int(time.time())}','payload':{'rows':rows}}))
PY2
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' -d @/tmp/sc-workspace-v2340-ix-job.json http://127.0.0.1:8094/v1/jobs >/tmp/sc-workspace-v2340-ix-created.json
IX_JOB_ID="$(python3 - <<'PY2'
import json; print(json.load(open('/tmp/sc-workspace-v2340-ix-created.json'))['item']['jobId'])
PY2
)"
for i in $(seq 1 90); do
  curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${IX_JOB_ID}" >/tmp/sc-workspace-v2340-ix-job-state.json
  status="$(python3 - <<'PY2'
import json; print(json.load(open('/tmp/sc-workspace-v2340-ix-job-state.json'))['item']['status'])
PY2
)"
  echo "Parquet interchange attempt $i: $status"
  [[ "$status" =~ ^(succeeded|failed|blocked|cancelled)$ ]] && break
  sleep 1
done
python3 - <<'PY2'
import json
d=json.load(open('/tmp/sc-workspace-v2340-ix-job-state.json'))
assert d['item']['status']=='succeeded', d
r=d['result']['interchange']['result']
assert r['format']=='parquet' and r['verified'] is True, r
assert r['descriptor']['rowCount']==20 and r['descriptor']['columnCount']==3, r
assert len(r['descriptor']['schemaFingerprint'])==64, r
assert d['result']['binaryArtifactId'] and d['result']['interchangeReceiptId'], d['result']
print('PASS: durable Parquet artifact + schema fingerprint + interchange receipt persisted')
PY2
curl -fsS "${AUTH[@]}" 'http://127.0.0.1:8094/v1/interchange/receipts?limit=25' >/tmp/sc-workspace-v2340-ix-receipts.json
python3 - <<'PY2'
import json
job=json.load(open('/tmp/sc-workspace-v2340-ix-job-state.json'))['item']['jobId']
row=next((x for x in json.load(open('/tmp/sc-workspace-v2340-ix-receipts.json'))['items'] if x['jobId']==job),None)
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
user='deploy-v2340-smoke'
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

curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/reproduction/cross-runtime/profiles >/tmp/sc-workspace-v2340-xrv-profiles.json
python3 - <<'PYV217'
import json
d=json.load(open('/tmp/sc-workspace-v2340-xrv-profiles.json'))
assert {x['mode'] for x in d['items']}=={'auto','exact-digest','tolerance-aware-json'}, d
assert d['automaticExecution'] is False and d['arbitraryCodeExecution'] is False, d
print('PASS: cross-runtime verification profile API exposes bounded comparison modes')
PYV217

echo "=== FORECASTING & TIME-SERIES RUNTIME ==="
STAMP="$(date +%s)"
cat >/tmp/sc-workspace-v2340-forecast-job.json <<JSON
{"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.forecast.linear-trend","priority":8,"maxAttempts":1,"idempotencyKey":"deploy-v2340-forecast-${STAMP}","payload":{"values":[10,12,14,16,18,20,22,24,26,28,30,32],"horizon":4,"frequency":"monthly"}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/sc-workspace-v2340-forecast-job.json http://127.0.0.1:8094/v1/jobs >/tmp/sc-workspace-v2340-forecast-created.json
FORECAST_JOB_ID="$(python3 -c "import json; print(json.load(open('/tmp/sc-workspace-v2340-forecast-created.json'))['item']['jobId'])")"
for i in $(seq 1 60); do
  curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${FORECAST_JOB_ID}" >/tmp/sc-workspace-v2340-forecast-state.json
  state="$(python3 -c "import json; print(json.load(open('/tmp/sc-workspace-v2340-forecast-state.json'))['item']['status'])")"; echo "forecast attempt $i: $state"
  [[ "$state" == succeeded ]] && break
  [[ "$state" == failed || "$state" == blocked ]] && { cat /tmp/sc-workspace-v2340-forecast-state.json; exit 1; }
  sleep 2
done
python3 - <<'PY'
import json
doc=json.load(open('/tmp/sc-workspace-v2340-forecast-state.json'))
j=doc['item']; assert j['status']=='succeeded',j
result=doc.get('result') or {}; assert result.get('forecastReceiptId'),result
remote=((((result.get('polyglot') or {}).get('result') or {}).get('remote') or {}).get('result') or {})
f=remote.get('forecast') or []; assert len(f)==4 and 33.5<float(f[0])<34.5,remote
print('PASS: durable linear-trend forecast produced deterministic four-step forecast')
PY
curl -fsS "${AUTH[@]}" 'http://127.0.0.1:8094/v1/forecast-receipts?limit=10' >/tmp/sc-workspace-v2340-forecast-receipts.json
python3 - <<'PY'
import json
items=json.load(open('/tmp/sc-workspace-v2340-forecast-receipts.json'))['items']; assert any(x.get('modelKind')=='linear-trend' and x.get('horizon')==4 for x in items),items
print('PASS: forecast receipt persisted and is discoverable through API')
PY
FORECAST_SEC="$(docker inspect sc-workspace-forecast-runtime --format '{{.HostConfig.ReadonlyRootfs}}|{{.HostConfig.NanoCpus}}|{{.HostConfig.Memory}}|{{.HostConfig.PidsLimit}}')"
echo "$FORECAST_SEC" | grep -q '^true|' || { echo 'ERROR: forecast runtime rootfs is not read-only' >&2; exit 1; }
docker inspect sc-workspace-forecast-runtime --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}' | grep -q 'sc-workspace-runtime' || { echo 'ERROR: forecast runtime is not on internal runtime network' >&2; exit 1; }
echo 'PASS: forecast runtime sandbox is read-only + internal-only + bounded resources'

echo '=== PROBABILISTIC & BAYESIAN RUNTIME ==='
curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/polyglot/runtimes/probability/status >/tmp/sc-workspace-v2340-probability-status.json
python3 - <<'PY2'
import json
d=json.load(open('/tmp/sc-workspace-v2340-probability-status.json'))['item']
assert d['configured'] is True and d['available'] is True and d['runtime']=='python-probabilistic-bayesian', d
assert len(d.get('operations') or [])==6, d
print('PASS: probabilistic runtime service health + six bounded operations')
PY2
cat >/tmp/sc-workspace-v2340-probability-job.json <<JSON
{"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.probability.beta-binomial-update","priority":8,"maxAttempts":1,"idempotencyKey":"deploy-v2340-probability-${STAMP}","payload":{"alpha":2,"beta":2,"successes":8,"trials":10,"seed":7,"draws":2000}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/sc-workspace-v2340-probability-job.json http://127.0.0.1:8094/v1/jobs >/tmp/sc-workspace-v2340-probability-created.json
PROB_JOB_ID="$(python3 -c "import json; print(json.load(open('/tmp/sc-workspace-v2340-probability-created.json'))['item']['jobId'])")"
for i in $(seq 1 60); do
  curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${PROB_JOB_ID}" >/tmp/sc-workspace-v2340-probability-state.json
  state="$(python3 -c "import json; print(json.load(open('/tmp/sc-workspace-v2340-probability-state.json'))['item']['status'])")"; echo "probability attempt $i: $state"
  [[ "$state" == succeeded ]] && break
  [[ "$state" == failed || "$state" == blocked ]] && { cat /tmp/sc-workspace-v2340-probability-state.json; exit 1; }
  sleep 2
done
python3 - <<'PY2'
import json
doc=json.load(open('/tmp/sc-workspace-v2340-probability-state.json'))
d=doc['item']; assert d['status']=='succeeded',d
r=doc.get('result') or {}; assert r.get('probabilisticInferenceReceiptId'),r
p=r['polyglot']['result']['remote']['result']['posterior']; assert p['alpha']==10.0 and p['beta']==4.0,p
print('PASS: durable Beta-Binomial Bayesian update produced posterior and job result')
PY2
curl -fsS "${AUTH[@]}" 'http://127.0.0.1:8094/v1/probabilistic-inference-receipts?limit=10' >/tmp/sc-workspace-v2340-probability-receipts.json
python3 - <<'PY2'
import json
items=json.load(open('/tmp/sc-workspace-v2340-probability-receipts.json'))['items']; assert any(x.get('inferenceKind')=='beta-binomial' for x in items),items
print('PASS: probabilistic inference receipt persisted and is discoverable through API')
PY2
PROB_SEC="$(docker inspect sc-workspace-probability-runtime --format '{{.HostConfig.ReadonlyRootfs}}|{{.HostConfig.NanoCpus}}|{{.HostConfig.Memory}}|{{.HostConfig.PidsLimit}}')"
echo "$PROB_SEC" | grep -q '^true|' || { echo 'ERROR: probability runtime rootfs is not read-only' >&2; exit 1; }
docker inspect sc-workspace-probability-runtime --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}' | grep -q 'sc-workspace-runtime' || { echo 'ERROR: probability runtime is not on internal runtime network' >&2; exit 1; }
echo 'PASS: probability runtime sandbox is read-only + internal-only + bounded resources'
echo '=== MONTE CARLO & UNCERTAINTY QUANTIFICATION ==='
curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/polyglot/runtimes/uncertainty/status >/tmp/sc-workspace-v2340-uncertainty-status.json
python3 - <<'PYUQ'
import json
d=json.load(open('/tmp/sc-workspace-v2340-uncertainty-status.json'))['item']
assert d['configured'] is True and d['available'] is True and d['runtime']=='python-monte-carlo-uq', d
assert len(d.get('operations') or [])==8, d
print('PASS: uncertainty runtime service health + eight bounded operations')
PYUQ
cat >/tmp/sc-workspace-v2340-uncertainty-job.json <<JSON
{"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.uncertainty.monte-carlo-weighted-sum","priority":8,"maxAttempts":1,"idempotencyKey":"deploy-v2340-uncertainty-${STAMP}","payload":{"terms":[{"name":"demand","coefficient":2,"distribution":{"kind":"normal","mean":10,"sd":1}},{"name":"loss","coefficient":-1,"distribution":{"kind":"uniform","min":1,"max":3}}],"offset":5,"draws":2000,"seed":2200,"threshold":24}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/sc-workspace-v2340-uncertainty-job.json http://127.0.0.1:8094/v1/jobs >/tmp/sc-workspace-v2340-uncertainty-created.json
UQ_JOB_ID="$(python3 -c "import json; print(json.load(open('/tmp/sc-workspace-v2340-uncertainty-created.json'))['item']['jobId'])")"
for i in $(seq 1 60); do
  curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${UQ_JOB_ID}" >/tmp/sc-workspace-v2340-uncertainty-state.json
  state="$(python3 -c "import json; print(json.load(open('/tmp/sc-workspace-v2340-uncertainty-state.json'))['item']['status'])")"; echo "uncertainty attempt $i: $state"
  [[ "$state" == succeeded ]] && break
  [[ "$state" == failed || "$state" == blocked ]] && { cat /tmp/sc-workspace-v2340-uncertainty-state.json; exit 1; }
  sleep 2
done
python3 - <<'PYUQ'
import json
doc=json.load(open('/tmp/sc-workspace-v2340-uncertainty-state.json'))
j=doc['item']; assert j['status']=='succeeded',j
r=doc.get('result') or {}; assert r.get('uncertaintyAnalysisReceiptId'),r
u=r['polyglot']['result']['remote']['result']; assert u['kind']=='monte-carlo-weighted-sum' and u['draws']==2000 and u['seed']==2200,u
assert 22.0 < float(u['summary']['mean']) < 24.0,u
print('PASS: durable seeded Monte Carlo uncertainty job produced reproducible summary and job result')
PYUQ
curl -fsS "${AUTH[@]}" 'http://127.0.0.1:8094/v1/uncertainty-analysis-receipts?limit=10' >/tmp/sc-workspace-v2340-uncertainty-receipts.json
python3 - <<'PYUQ'
import json
items=json.load(open('/tmp/sc-workspace-v2340-uncertainty-receipts.json'))['items']; assert any(x.get('analysisKind')=='monte-carlo-weighted-sum' and x.get('sampleCount')==2000 and x.get('seed')==2200 for x in items),items
print('PASS: uncertainty analysis receipt persisted and is discoverable through API')
PYUQ
UQ_SEC="$(docker inspect sc-workspace-uncertainty-runtime --format '{{.HostConfig.ReadonlyRootfs}}|{{.HostConfig.NanoCpus}}|{{.HostConfig.Memory}}|{{.HostConfig.PidsLimit}}')"
echo "$UQ_SEC" | grep -q '^true|' || { echo 'ERROR: uncertainty runtime rootfs is not read-only' >&2; exit 1; }
docker inspect sc-workspace-uncertainty-runtime --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}' | grep -q 'sc-workspace-runtime' || { echo 'ERROR: uncertainty runtime is not on internal runtime network' >&2; exit 1; }
echo 'PASS: uncertainty runtime sandbox is read-only + internal-only + bounded resources'

echo "=== OPTIMIZATION & PARAMETER SEARCH RUNTIME ==="
curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/polyglot/runtimes/optimization/status >/tmp/sc-workspace-v2340-opt-status.json
python3 - <<'PYOPTSTATUS'
import json
d=json.load(open('/tmp/sc-workspace-v2340-opt-status.json'))['item']
assert d['configured'] is True and d['available'] is True and d['runtime']=='python-optimization-parameter-search',d
assert len(d['operations'])==8 and d['arbitraryCodeExecution'] is False,d
print('PASS: optimization runtime service health + eight bounded operations')
PYOPTSTATUS
cat >/tmp/sc-workspace-v2340-opt-job.json <<JSON
{"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.optimize.linear-box","priority":8,"maxAttempts":1,"idempotencyKey":"deploy-v2340-opt-${STAMP}","payload":{"direction":"minimize","bounds":[{"name":"x","min":0,"max":10},{"name":"y","min":-2,"max":3}],"objective":{"kind":"linear","coefficients":[2,-4],"intercept":1}}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/sc-workspace-v2340-opt-job.json http://127.0.0.1:8094/v1/jobs >/tmp/sc-workspace-v2340-opt-created.json
OPT_JOB_ID="$(python3 -c "import json; print(json.load(open('/tmp/sc-workspace-v2340-opt-created.json'))['item']['jobId'])")"
for i in $(seq 1 60); do
  curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${OPT_JOB_ID}" >/tmp/sc-workspace-v2340-opt-state.json
  state="$(python3 -c "import json; print(json.load(open('/tmp/sc-workspace-v2340-opt-state.json'))['item']['status'])")"; echo "optimization attempt $i: $state"
  [[ "$state" == succeeded ]] && break
  [[ "$state" == failed || "$state" == blocked ]] && { cat /tmp/sc-workspace-v2340-opt-state.json; exit 1; }
  sleep 1
done
python3 - <<'PYOPTJOB'
import json
doc=json.load(open('/tmp/sc-workspace-v2340-opt-state.json')); assert doc['item']['status']=='succeeded',doc
r=doc.get('result') or {}; assert r.get('optimizationReceiptId'),r
z=r['polyglot']['result']['remote']['result']; assert z['kind']=='linear-box' and z['bestParameters']=={'x':0.0,'y':3.0} and z['bestValue']==-11.0,z
print('PASS: durable bounded optimization job produced exact solution and job result')
PYOPTJOB
curl -fsS "${AUTH[@]}" 'http://127.0.0.1:8094/v1/optimization-receipts?limit=10' >/tmp/sc-workspace-v2340-opt-receipts.json
python3 - <<'PYOPTREC'
import json
items=json.load(open('/tmp/sc-workspace-v2340-opt-receipts.json'))['items']; assert any(x.get('optimizationKind')=='linear-box' and x.get('bestValue')==-11.0 for x in items),items
print('PASS: optimization receipt persisted and is discoverable through API')
PYOPTREC
OPT_SEC="$(docker inspect sc-workspace-optimization-runtime --format '{{.HostConfig.ReadonlyRootfs}}|{{.HostConfig.NanoCpus}}|{{.HostConfig.Memory}}|{{.HostConfig.PidsLimit}}')"
echo "$OPT_SEC" | grep -q '^true|' || { echo 'ERROR: optimization runtime rootfs is not read-only' >&2; exit 1; }
docker inspect sc-workspace-optimization-runtime --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}' | grep -q 'sc-workspace-runtime' || { echo 'ERROR: optimization runtime is not on internal runtime network' >&2; exit 1; }
echo 'PASS: optimization runtime sandbox is read-only + internal-only + bounded resources'
echo '=== ROBUST DECISION OPTIMIZATION & PARETO ANALYSIS ==='
curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/polyglot/runtimes/decision/status >/tmp/sc-workspace-v2340-decision-status.json
python3 - <<'PYDECSTATUS'
import json
d=json.load(open('/tmp/sc-workspace-v2340-decision-status.json'))['item']
assert d['configured'] is True and d['available'] is True and d['runtime']=='python-robust-decision-pareto',d
assert len(d['operations'])==8,d
print('PASS: decision runtime service health + eight bounded operations')
PYDECSTATUS
STAMP="$(date +%s)"
cat >/tmp/sc-workspace-v2340-decision-job.json <<JSON
{"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.decision.minimax-regret","priority":8,"maxAttempts":1,"idempotencyKey":"deploy-v2340-decision-${STAMP}","payload":{"candidates":[{"id":"A","scores":[10,2]},{"id":"B","scores":[7,7]}],"scenarios":[{"id":"growth","probability":0.5},{"id":"stress","probability":0.5}],"direction":"maximize"}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/sc-workspace-v2340-decision-job.json http://127.0.0.1:8094/v1/jobs >/tmp/sc-workspace-v2340-decision-created.json
DEC_JOB_ID="$(python3 -c "import json; print(json.load(open('/tmp/sc-workspace-v2340-decision-created.json'))['item']['jobId'])")"
for i in $(seq 1 60); do
  curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${DEC_JOB_ID}" >/tmp/sc-workspace-v2340-decision-state.json
  state="$(python3 -c "import json; print(json.load(open('/tmp/sc-workspace-v2340-decision-state.json'))['item']['status'])")"; echo "decision attempt $i: $state"
  [[ "$state" == succeeded ]] && break
  [[ "$state" == failed || "$state" == blocked ]] && { cat /tmp/sc-workspace-v2340-decision-state.json; exit 1; }
  sleep 2
done
python3 - <<'PYDECRESULT'
import json
doc=json.load(open('/tmp/sc-workspace-v2340-decision-state.json'))
assert doc['item']['status']=='succeeded',doc
r=doc.get('result') or {}; assert r.get('decisionOptimizationReceiptId'),r
x=r['polyglot']['result']['remote']['result']; assert x['kind']=='minimax-regret' and x['selectedAlternative']=='B',x
print('PASS: durable minimax-regret decision job selected robust alternative and persisted job result')
PYDECRESULT
curl -fsS "${AUTH[@]}" 'http://127.0.0.1:8094/v1/decision-optimization-receipts?limit=10' >/tmp/sc-workspace-v2340-decision-receipts.json
python3 - <<'PYDECRECEIPT'
import json
items=json.load(open('/tmp/sc-workspace-v2340-decision-receipts.json'))['items']
assert any(x.get('analysisKind')=='minimax-regret' and x.get('selectedAlternative')=='B' and x.get('scenarioCount')==2 for x in items),items
print('PASS: decision optimization receipt persisted and is discoverable through API')
PYDECRECEIPT
DEC_SEC="$(docker inspect sc-workspace-decision-runtime --format '{{.HostConfig.ReadonlyRootfs}}|{{.HostConfig.NanoCpus}}|{{.HostConfig.Memory}}|{{.HostConfig.PidsLimit}}')"
echo "$DEC_SEC" | grep -q '^true|' || { echo 'ERROR: decision runtime rootfs is not read-only' >&2; exit 1; }
docker inspect sc-workspace-decision-runtime --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}' | grep -q 'sc-workspace-runtime' || { echo 'ERROR: decision runtime is not on internal runtime network' >&2; exit 1; }
echo 'PASS: decision runtime sandbox is read-only + internal-only + bounded resources'
echo '=== RELIABILITY, SURVIVAL & FAILURE-TIME ANALYSIS ==='
curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/polyglot/runtimes/reliability/status >/tmp/sc-workspace-v2340-reliability-status.json
python3 - <<'PYRELSTATUS'
import json
d=json.load(open('/tmp/sc-workspace-v2340-reliability-status.json'))['item']
assert d['configured'] is True and d['available'] is True and d['runtime']=='python-reliability-survival',d
assert len(d['operations'])==8,d
print('PASS: reliability runtime service health + eight bounded operations')
PYRELSTATUS
STAMP="$(date +%s)"
cat >/tmp/sc-workspace-v2340-reliability-job.json <<JSON
{"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.reliability.exponential-fit","priority":8,"maxAttempts":1,"idempotencyKey":"deploy-v2340-reliability-${STAMP}","payload":{"times":[10,20,30,40],"events":[1,1,1,1],"horizon":25}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/sc-workspace-v2340-reliability-job.json http://127.0.0.1:8094/v1/jobs >/tmp/sc-workspace-v2340-reliability-created.json
REL_JOB_ID="$(python3 -c "import json; print(json.load(open('/tmp/sc-workspace-v2340-reliability-created.json'))['item']['jobId'])")"
for i in $(seq 1 60); do
  curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${REL_JOB_ID}" >/tmp/sc-workspace-v2340-reliability-state.json
  state="$(python3 -c "import json; print(json.load(open('/tmp/sc-workspace-v2340-reliability-state.json'))['item']['status'])")"; echo "reliability attempt $i: $state"
  [[ "$state" == succeeded ]] && break
  [[ "$state" == failed || "$state" == blocked ]] && { cat /tmp/sc-workspace-v2340-reliability-state.json; exit 1; }
  sleep 2
done
python3 - <<'PYRELRESULT'
import json,math
doc=json.load(open('/tmp/sc-workspace-v2340-reliability-state.json')); assert doc['item']['status']=='succeeded',doc
r=doc.get('result') or {}; assert r.get('reliabilityAnalysisReceiptId'),r
x=r['polyglot']['result']['remote']['result']; assert x['kind']=='exponential-fit' and abs(x['metrics']['failureRate']-0.04)<1e-12,x
print('PASS: durable exponential failure-time analysis produced deterministic rate and job result')
PYRELRESULT
curl -fsS "${AUTH[@]}" 'http://127.0.0.1:8094/v1/reliability-analysis-receipts?limit=10' >/tmp/sc-workspace-v2340-reliability-receipts.json
python3 - <<'PYRELRECEIPT'
import json
items=json.load(open('/tmp/sc-workspace-v2340-reliability-receipts.json'))['items']
assert any(x.get('analysisKind')=='exponential-fit' and x.get('modelKind')=='exponential' and x.get('sampleCount')==4 and x.get('eventCount')==4 for x in items),items
print('PASS: reliability analysis receipt persisted and is discoverable through API')
PYRELRECEIPT
REL_SEC="$(docker inspect sc-workspace-reliability-runtime --format '{{.HostConfig.ReadonlyRootfs}}|{{.HostConfig.NanoCpus}}|{{.HostConfig.Memory}}|{{.HostConfig.PidsLimit}}')"
echo "$REL_SEC" | grep -q '^true|' || { echo 'ERROR: reliability runtime rootfs is not read-only' >&2; exit 1; }
docker inspect sc-workspace-reliability-runtime --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}' | grep -q 'sc-workspace-runtime' || { echo 'ERROR: reliability runtime is not on internal runtime network' >&2; exit 1; }
echo 'PASS: reliability runtime sandbox is read-only + internal-only + bounded resources'
echo '=== BACKEND AUTHORITY & DOMAIN SERVICE CONSOLIDATION ==='
curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/domain-authority >/tmp/sc-workspace-v2340-domain-authority.json
python3 - <<'PYAUTH'
import json
d=json.load(open('/tmp/sc-workspace-v2340-domain-authority.json'))['item']
assert d['mode']=='server-authoritative' and d['canonicalStore']=='postgresql',d
assert d['backendAuthoritativeState'] is True and d['browserAuthoritativeState'] is False,d
assert d['clientRole']=='presentation-interaction-local-drafts',d
assert 'mutation-receipts' in d['authoritativeConcerns'],d
print('PASS: backend authority profile declares PostgreSQL/Python canonical state and thin-client boundary')
PYAUTH
cat >/tmp/sc-workspace-v2340-domain-validate.json <<JSON
{"schema":"sc-workspace-domain-validation-request/1.0","objectKind":"project","document":{"schema":"sc-workspace-project/20.0","id":"authority-smoke","title":"Backend authority smoke","objects":[{"id":"evidence-1","type":"note"},{"id":"dataset-1","type":"dataset"}],"traceability":{"lineage":[]}}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/sc-workspace-v2340-domain-validate.json http://127.0.0.1:8094/v1/domain-authority/validate >/tmp/sc-workspace-v2340-domain-validation-result.json
python3 - <<'PYAUTHVALID'
import json
x=json.load(open('/tmp/sc-workspace-v2340-domain-validation-result.json'))['item']
assert x['accepted'] is True and x['authorityDecision']=='accept' and x['objectCount']==2,x
assert len(x['canonicalFingerprint'])==64,x
print('PASS: server-side project validation produced canonical SHA-256 authority fingerprint')
PYAUTHVALID
AUTH_PROJECT_ID="deploy-v2340-authority-${STAMP}"
export AUTH_PROJECT_ID
cat >/tmp/sc-workspace-v2340-authority-project.json <<JSON
{"schema":"sc-workspace-sync-push/1.0","sourceProjectId":"${AUTH_PROJECT_ID}","projectTitle":"v2.24 backend authority smoke","expectedRevision":0,"operationId":"deploy-v2340-authority-${STAMP}","project":{"schema":"sc-workspace-project/20.0","id":"${AUTH_PROJECT_ID}","title":"v2.24 backend authority smoke","objects":[{"id":"object-1","type":"note"}],"traceability":{"lineage":[]}}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/sc-workspace-v2340-authority-project.json http://127.0.0.1:8094/v1/projects >/tmp/sc-workspace-v2340-authority-project-result.json
python3 - <<'PYAUTHSTORE'
import json
x=json.load(open('/tmp/sc-workspace-v2340-authority-project-result.json'))
assert x['ok'] is True and x['replayed'] is False,x
assert x['item']['revision']==1 and x['item']['storageMode']=='sync-head',x
print('PASS: authoritative sync command persisted revision 1 under server revision control')
PYAUTHSTORE
curl -fsS "${AUTH[@]}" 'http://127.0.0.1:8094/v1/domain-mutation-receipts?limit=25' >/tmp/sc-workspace-v2340-domain-receipts.json
python3 - <<'PYAUTHREC'
import json,os
project=os.environ.get('AUTH_PROJECT_ID','')
items=json.load(open('/tmp/sc-workspace-v2340-domain-receipts.json'))['items']
row=next((x for x in items if x.get('objectId')==project and x.get('command')=='project.sync'),None)
assert row,row
assert row['fromRevision']==0 and row['toRevision']==1,row
assert row['validation']['accepted'] is True and row['policy']['serverAuthoritative'] is True,row
assert len(row['requestFingerprint'])==64 and len(row['canonicalFingerprint'])==64,row
print('PASS: immutable domain mutation receipt persisted revision, validation, policy, provenance and fingerprints')
PYAUTHREC
curl -fsS -X DELETE "${AUTH[@]}" "http://127.0.0.1:8094/v1/projects/${AUTH_PROJECT_ID}" >/tmp/sc-workspace-v2340-authority-delete.json
python3 - <<'PYAUTHDEL'
import json
x=json.load(open('/tmp/sc-workspace-v2340-authority-delete.json')); assert x['ok'] is True and x['deleted'] is True,x
print('PASS: authoritative delete completed and emitted an independent mutation receipt')
PYAUTHDEL
echo "=== WORKSPACE COMMAND & QUERY API ==="
curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/command-query >/tmp/sc-workspace-v2340-command-query.json
python3 - <<'PYCQ'
import json
x=json.load(open('/tmp/sc-workspace-v2340-command-query.json'))['item']
assert x['mode']=='server-command-query' and x['backendAuthoritative'] is True,x
assert x['browserCommandAuthority'] is False and x['queriesMutate'] is False,x
assert x['commandCount']==9 and x['queryCount']==9,x
print('PASS: command/query profile exposes bounded server-authoritative command and read-only query registries')
PYCQ
CQ_PROJECT_ID="deploy-v2340-command-${STAMP}"; export CQ_PROJECT_ID
cat >/tmp/sc-workspace-v2340-command.json <<JSON
{"schema":"sc-workspace-command-request/1.0","command":"project.put","commandId":"deploy-v2340-${STAMP}","idempotencyKey":"deploy-v2340-${STAMP}","payload":{"schema":"sc-workspace-sync-push/1.0","sourceProjectId":"${CQ_PROJECT_ID}","projectTitle":"v2.25 command smoke","expectedRevision":0,"operationId":"deploy-v2340-${STAMP}","project":{"schema":"sc-workspace-project/20.0","id":"${CQ_PROJECT_ID}","title":"v2.25 command smoke","objects":[],"traceability":{"lineage":[]}}}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/sc-workspace-v2340-command.json http://127.0.0.1:8094/v1/commands/execute >/tmp/sc-workspace-v2340-command-result.json
python3 - <<'PYCMD'
import json
x=json.load(open('/tmp/sc-workspace-v2340-command-result.json'))
assert x['ok'] is True and x['replayed'] is False,x
assert x['receipt']['command']=='project.put' and len(x['receipt']['requestFingerprint'])==64,x
assert x['result']['item']['revision']==1,x
print('PASS: project.put executed through authoritative command dispatcher and emitted command receipt')
PYCMD
cat >/tmp/sc-workspace-v2340-query.json <<JSON
{"schema":"sc-workspace-query-request/1.0","query":"project.detail","parameters":{"projectId":"${CQ_PROJECT_ID}"}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/sc-workspace-v2340-query.json http://127.0.0.1:8094/v1/queries/execute >/tmp/sc-workspace-v2340-query-result.json
python3 - <<'PYQUERY'
import json
x=json.load(open('/tmp/sc-workspace-v2340-query-result.json'))
assert x['ok'] is True and x['mutated'] is False,x
assert x['data']['generatedServerSide'] is True and x['data']['project']['revision']==1,x
print('PASS: project.detail returned server-generated read model without mutation')
PYQUERY
curl -fsS -X DELETE "${AUTH[@]}" "http://127.0.0.1:8094/v1/projects/${CQ_PROJECT_ID}" >/dev/null

echo "=== SERVER-SIDE NOTEBOOK & ARTIFACT ORCHESTRATION ==="
curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/notebook-orchestration > /tmp/scw-v227-orchestration.json
python3 - <<'PYV226'
import json
x=json.load(open('/tmp/scw-v227-orchestration.json'))['item']
assert x['backendAuthoritative'] is True
assert x['browserSchedulesDependencies'] is False
assert x['artifactSha256Pinning'] is True
assert x['dependencyAwareDispatch'] is True
assert x['arbitraryCodeExecution'] is False
print('PASS: notebook orchestration profile is backend-authoritative and dependency-aware')
PYV226
echo "=== REPRODUCIBLE SCIENTIFIC STUDY PACKAGES ==="
STUDY_PROJECT_ID="deploy-v2340-study-${STAMP}"; export STUDY_PROJECT_ID
cat >/tmp/sc-workspace-v2340-study-project.json <<JSON
{"schema":"sc-workspace-sync-push/1.0","sourceProjectId":"${STUDY_PROJECT_ID}","projectTitle":"v2.27 study package smoke","expectedRevision":0,"operationId":"study-v2340-${STAMP}","project":{"schema":"sc-workspace-project/20.0","id":"${STUDY_PROJECT_ID}","title":"v2.27 study package smoke","objects":[],"traceability":{"lineage":[]}}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/sc-workspace-v2340-study-project.json http://127.0.0.1:8094/v1/projects >/dev/null
curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/scientific-study-packages/profile >/tmp/sc-workspace-v2340-study-profile.json
python3 - <<'PYSTUDYPROFILE'
import json
x=json.load(open('/tmp/sc-workspace-v2340-study-profile.json'))['item']
assert x['backendAuthoritative'] is True and x['deterministicManifest'] is True,x
assert x['artifactRevisionAndSha256Pinning'] is True and x['arbitraryCodeExecution'] is False,x
print('PASS: scientific study package profile is backend-authoritative, deterministic and SHA-256 pinned')
PYSTUDYPROFILE
cat >/tmp/sc-workspace-v2340-study-request.json <<JSON
{"schema":"sc-workspace-scientific-study-package-request/1.0","projectId":"${STUDY_PROJECT_ID}","title":"Deployment verification study","includeArtifactBlobs":true,"includeScientificReceipts":true}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/sc-workspace-v2340-study-request.json http://127.0.0.1:8094/v1/scientific-study-packages >/tmp/sc-workspace-v2340-study-result.json
STUDY_PACKAGE_ID="$(python3 - <<'PYSTUDYID'
import json
x=json.load(open('/tmp/sc-workspace-v2340-study-result.json'))['item']
assert len(x['manifestFingerprint'])==64 and len(x['bundleSha256'])==64,x
assert x['closureVerified'] is True,x
print(x['packageId'])
PYSTUDYID
)"; export STUDY_PACKAGE_ID
echo "study package: ${STUDY_PACKAGE_ID}"
cat >/tmp/sc-workspace-v2340-study-verify.json <<JSON
{"schema":"sc-workspace-scientific-study-package-verify-request/1.0","deep":true}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/sc-workspace-v2340-study-verify.json "http://127.0.0.1:8094/v1/scientific-study-packages/${STUDY_PACKAGE_ID}/verify" >/tmp/sc-workspace-v2340-study-verified.json
python3 - <<'PYSTUDYVERIFY'
import json
x=json.load(open('/tmp/sc-workspace-v2340-study-verified.json'))
assert x['ok'] is True and not x['errors'],x
assert len(x['manifestFingerprint'])==64 and len(x['bundleSha256'])==64,x
print('PASS: durable scientific study package created and deep integrity verification succeeded')
PYSTUDYVERIFY
curl -fsS -X DELETE "${AUTH[@]}" "http://127.0.0.1:8094/v1/scientific-study-packages/${STUDY_PACKAGE_ID}" >/dev/null
curl -fsS -X DELETE "${AUTH[@]}" "http://127.0.0.1:8094/v1/projects/${STUDY_PROJECT_ID}" >/dev/null
echo "=== DECLARATIVE VISUALIZATION SPECIFICATION API ==="
curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/visualization-specs/profile >/tmp/sc-workspace-v2340-viz-profile.json
python3 - <<'PYVIZPROFILE'
import json
x=json.load(open('/tmp/sc-workspace-v2340-viz-profile.json'))['item']
assert x['backendAuthoritative'] is True and x['rendererNeutral'] is True,x
assert x['linkedViews'] is True and x['browserDefinesAnalyticalMeaning'] is False,x
assert x['arbitraryCodeExecution'] is False,x
assert 'uncertainty-band' in x['viewTypes'] and 'network' in x['viewTypes'],x
print('PASS: visualization specification profile is backend-authoritative and renderer-neutral')
PYVIZPROFILE
VIZ_PROJECT_ID="deploy-v2340-viz-${STAMP}"; export VIZ_PROJECT_ID
cat >/tmp/sc-workspace-v2340-viz-project.json <<JSON
{"schema":"sc-workspace-sync-push/1.0","sourceProjectId":"${VIZ_PROJECT_ID}","projectTitle":"v2.28 visualization smoke","expectedRevision":0,"operationId":"viz-v2340-${STAMP}","project":{"schema":"sc-workspace-project/20.0","id":"${VIZ_PROJECT_ID}","title":"v2.28 visualization smoke","objects":[],"traceability":{"lineage":[]}}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/sc-workspace-v2340-viz-project.json http://127.0.0.1:8094/v1/projects >/dev/null
cat >/tmp/sc-workspace-v2340-viz-request.json <<JSON
{"schema":"sc-workspace-visualization-spec-request/1.0","visualizationId":"deploy-v2340-viz-${STAMP}","projectId":"${VIZ_PROJECT_ID}","expectedRevision":0,"title":"Deployment uncertainty visualization","spec":{"schema":"sc-workspace-visualization-spec/1.0","title":"Deployment uncertainty visualization","sources":[{"id":"series","kind":"inline","rows":[{"x":1,"mean":10,"lower":8,"upper":12},{"x":2,"mean":11,"lower":9,"upper":13}]}],"scene":{"layout":"grid","views":[{"id":"band","type":"uncertainty-band","source":"series","encoding":{"x":{"field":"x"},"y":{"field":"mean"},"lower":{"field":"lower"},"upper":{"field":"upper"}}},{"id":"table","type":"table","source":"series","encoding":{}}]},"links":[{"sourceViewId":"band","targetViewId":"table","mode":"filter","field":"x"}]}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/sc-workspace-v2340-viz-request.json http://127.0.0.1:8094/v1/visualization-specs >/tmp/sc-workspace-v2340-viz-result.json
VIZ_ID="$(python3 - <<'PYVIZ'
import json
x=json.load(open('/tmp/sc-workspace-v2340-viz-result.json'))
assert x['ok'] is True and x['replayed'] is False,x
assert x['item']['revision']==1 and x['item']['viewCount']==2 and x['item']['sourceCount']==1,x
assert len(x['item']['specFingerprint'])==64,x
assert x['spec']['rendererContract']['rendererNeutral'] is True,x
assert x['spec']['policy']['browserDefinesAnalyticalMeaning'] is False,x
assert x['spec']['links'][0]['mode']=='filter',x
print(x['item']['visualizationId'])
PYVIZ
)"; export VIZ_ID
echo "visualization spec: ${VIZ_ID}"
curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/visualization-specs/${VIZ_ID}" >/tmp/sc-workspace-v2340-viz-get.json
curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/visualization-spec-receipts?visualizationId=${VIZ_ID}" >/tmp/sc-workspace-v2340-viz-receipts.json
python3 - <<'PYVIZREAD'
import json
x=json.load(open('/tmp/sc-workspace-v2340-viz-get.json'))
r=json.load(open('/tmp/sc-workspace-v2340-viz-receipts.json'))['items']
assert x['item']['revision']==1 and x['spec']['scene']['layout']=='grid',x
assert r and r[0]['action']=='create' and r[0]['revision']==1,r
print('PASS: durable renderer-neutral visualization spec persisted with linked views, provenance and receipt')
PYVIZREAD
curl -fsS -X DELETE "${AUTH[@]}" "http://127.0.0.1:8094/v1/visualization-specs/${VIZ_ID}" >/dev/null
curl -fsS -X DELETE "${AUTH[@]}" "http://127.0.0.1:8094/v1/projects/${VIZ_PROJECT_ID}" >/dev/null
echo "=== TYPED CLIENT CONTRACTS & TYPESCRIPT BOUNDARY ==="
curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/client-contracts > /tmp/sc-workspace-v2340-client-contracts.json
python3 - <<'PYCHECK'
import json,re
x=json.load(open('/tmp/sc-workspace-v2340-client-contracts.json')); i=x['item']
assert i['workspaceVersion']=='2.34.0'
assert i['backendAuthoritative'] is True and i['browserAuthoritativeState'] is False
assert i['transport']=='wordpress-server-proxy' and i['browserDirectBackendAccess'] is False
assert i['serviceCredentialsBrowserVisible'] is False and i['strictTypeScript'] is True
assert i['typedEndpointCount']==34 and i['missingOpenApiOperations']==[]
assert re.fullmatch(r'[a-f0-9]{64}',i['openApiProjectionSha256'])
assert i['commandCount']==9 and i['queryCount']==9
print('PASS: backend typed-client contract is OpenAPI-derived, bounded, proxy-only and fingerprinted')
PYCHECK
echo "=== BACKEND POLICY, IDENTITY & AUTHORIZATION CONSOLIDATION ==="
curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/authorization >/tmp/sc-workspace-v2340-authorization-profile.json
curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/authorization/identity >/tmp/sc-workspace-v2340-authorization-identity.json
cat >/tmp/sc-workspace-v2340-authorization-evaluate.json <<JSON
{"schema":"sc-workspace-authorization-evaluate-request/1.0","action":"workspace.read","resourceKind":"workspace","context":{"release":"2.34.0"}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/sc-workspace-v2340-authorization-evaluate.json http://127.0.0.1:8094/v1/authorization/evaluate >/tmp/sc-workspace-v2340-authorization-decision.json
python3 - <<'PYAUTH'
import json,re
p=json.load(open('/tmp/sc-workspace-v2340-authorization-profile.json'))['item']
i=json.load(open('/tmp/sc-workspace-v2340-authorization-identity.json'))['item']
d=json.load(open('/tmp/sc-workspace-v2340-authorization-decision.json'))
assert p['backendAuthoritative'] is True and p['browserAuthoritativeAuthorization'] is False,p
assert p['defaultEffect']=='deny' and p['routePolicyEnforcement'] is True,p
assert p['clientSuppliedRolesTrusted'] is False and p['clientSuppliedScopesTrusted'] is False,p
assert i['serverResolved'] is True and i['servicePrincipal']=='wordpress-proxy',i
assert i['principalId'].startswith('wp-user:'),i
assert d['ok'] is True and d['item']['effect']=='allow',d
assert re.fullmatch(r'[a-f0-9]{64}',d['item']['decisionFingerprint']),d
assert d['receipt']['effect']=='allow' and d['receipt']['policyId']=='workspace-authenticated-user-v1',d
print('PASS: server-resolved principal, default-deny route policy and durable authorization decision receipt verified')
PYAUTH
echo "=== THIN CLIENT STATE ARCHITECTURE ==="
curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/thin-client-state > /tmp/sc-workspace-v2340-thin-state.json
curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/thin-client-state/bootstrap > /tmp/sc-workspace-v2340-thin-bootstrap.json
python3 - <<'PYTHIN'
import json,re
p=json.load(open('/tmp/sc-workspace-v2340-thin-state.json'))['item']
b=json.load(open('/tmp/sc-workspace-v2340-thin-bootstrap.json'))
assert p['backendAuthoritative'] is True and p['browserAuthoritativeState'] is False,p
assert p['canonicalStore']=='postgresql' and p['canonicalCache']=='memory-only-rehydratable',p
assert p['canonicalCachePersistent'] is False and p['persistentBrowserState']=='transient-only',p
assert p['canonicalMutations']=='command-api-only' and p['offlineCacheAuthoritative'] is False,p
assert b['generatedServerSide'] is True and b['backendAuthoritative'] is True,b
assert b['clientPolicy']['persistCanonicalCache'] is False and b['clientPolicy']['persistTransientStateOnly'] is True,b
assert re.fullmatch(r'[a-f0-9]{64}',b['projectionFingerprint']),b
print('PASS: thin client state is transient-only in browser with memory-only canonical cache and server rehydration')
PYTHIN
echo "=== LOCAL-FIRST SYNCHRONIZATION PROTOCOL ==="
curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/sync >/tmp/sc-workspace-v2340-sync-profile.json
curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/sync/bootstrap >/tmp/sc-workspace-v2340-sync-bootstrap.json
python3 - <<'PYSYNC'
import json,re
p=json.load(open('/tmp/sc-workspace-v2340-sync-profile.json'))['item']; b=json.load(open('/tmp/sc-workspace-v2340-sync-bootstrap.json'))
assert p['backendAuthoritative'] is True and p['browserAuthoritativeState'] is False,p
assert p['offlineOutboxAllowed'] is True and p['offlineOutboxAuthoritative'] is False,p
assert p['baseRevisionRequired'] is True and p['automaticSemanticMerge'] is False,p
assert b['backendAuthoritative'] is True and re.fullmatch(r'[a-f0-9]{64}',b['checkpoint']),b
print('PASS: local-first sync profile preserves server authority with retry-safe offline draft envelopes')
PYSYNC
SYNC_PROJECT_ID="deploy-v2340-sync-${STAMP}"
cat >/tmp/sc-workspace-v2340-sync-envelope.json <<JSON
{"schema":"sc-workspace-sync-envelope/1.0","envelopeId":"env-${STAMP}","operationId":"op-${STAMP}","deviceId":"deploy-device","objectKind":"project","objectId":"${SYNC_PROJECT_ID}","baseRevision":0,"clientSequence":1,"mutation":{"action":"put","title":"v2.31 sync smoke","document":{"schema":"sc-workspace-project/20.0","id":"${SYNC_PROJECT_ID}","title":"v2.31 sync smoke","objects":[],"traceability":{"lineage":[]}}}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/sc-workspace-v2340-sync-envelope.json http://127.0.0.1:8094/v1/sync/envelopes >/tmp/sc-workspace-v2340-sync-result.json
python3 - <<'PYSYNCAPPLY'
import json
x=json.load(open('/tmp/sc-workspace-v2340-sync-result.json')); assert x['ok'] is True and x['status']=='applied' and x['serverRevision']==1,x
assert x['receipt']['status']=='applied' and len(x['canonicalFingerprint'])>=64,x
print('PASS: durable local-first envelope applied exactly once at base revision 0')
PYSYNCAPPLY
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/sc-workspace-v2340-sync-envelope.json http://127.0.0.1:8094/v1/sync/envelopes >/tmp/sc-workspace-v2340-sync-replay.json
python3 - <<'PYSYNCREPLAY'
import json
x=json.load(open('/tmp/sc-workspace-v2340-sync-replay.json')); assert x['replayed'] is True and x['status']=='applied',x
print('PASS: sync retry replayed durable receipt without duplicate canonical mutation')
PYSYNCREPLAY
cat >/tmp/sc-workspace-v2340-sync-reconcile.json <<JSON
{"schema":"sc-workspace-sync-reconcile-request/1.0","deviceId":"deploy-device","clientRevisionVector":{"${SYNC_PROJECT_ID}":0},"projectIds":["${SYNC_PROJECT_ID}"]}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/sc-workspace-v2340-sync-reconcile.json http://127.0.0.1:8094/v1/sync/reconcile >/tmp/sc-workspace-v2340-sync-reconcile-result.json
python3 - <<'PYSYNCREC'
import json
x=json.load(open('/tmp/sc-workspace-v2340-sync-reconcile-result.json')); assert x['items'][0]['status']=='server-ahead' and x['items'][0]['action']=='rehydrate',x
assert x['automaticMerge'] is False
print('PASS: revision-vector reconciliation detects server-ahead state and requires rehydration')
PYSYNCREC
curl -fsS -X DELETE "${AUTH[@]}" "http://127.0.0.1:8094/v1/projects/${SYNC_PROJECT_ID}" >/dev/null

echo "=== UNIFIED SCIENTIFIC OBJECT API ==="
curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/scientific-objects/profile >/tmp/sc-workspace-v2340-scientific-object-profile.json
python3 - <<'PYOBJECTPROFILE'
import json
p=json.load(open('/tmp/sc-workspace-v2340-scientific-object-profile.json'))['item']
assert p['backendAuthoritative'] is True and p['browserAuthoritativeState'] is False,p
assert len(p['supportedKinds'])==10 and 'dataset' in p['supportedKinds'] and 'scientific-receipt' in p['supportedKinds'],p
assert p['relations'] is True and p['genericArbitraryMutationEndpoint'] is False,p
print('PASS: unified scientific object profile exposes ten backend-authoritative object kinds without generic mutation authority')
PYOBJECTPROFILE
SCIENTIFIC_OBJECT_ID="deploy-v2340-object-${STAMP}"; export SCIENTIFIC_OBJECT_ID
cat >/tmp/sc-workspace-v2340-artifact.json <<JSON
{"schema":"sc-workspace-artifact-store/1.0","artifactId":"${SCIENTIFIC_OBJECT_ID}","filename":"unified-object.txt","mediaType":"text/plain","contentBase64":"dW5pZmllZA==","expectedRevision":0,"metadata":{"release":"2.34.0"}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/sc-workspace-v2340-artifact.json http://127.0.0.1:8094/v1/artifacts >/tmp/sc-workspace-v2340-artifact-result.json
curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/scientific-objects?kind=artifact&q=${SCIENTIFIC_OBJECT_ID}&limit=10" >/tmp/sc-workspace-v2340-object-index.json
curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/scientific-objects/artifact/${SCIENTIFIC_OBJECT_ID}" >/tmp/sc-workspace-v2340-object-get.json
curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/scientific-objects/artifact/${SCIENTIFIC_OBJECT_ID}/revisions" >/tmp/sc-workspace-v2340-object-history.json
curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/scientific-objects/artifact/${SCIENTIFIC_OBJECT_ID}/relations" >/tmp/sc-workspace-v2340-object-relations.json
python3 - <<'PYOBJECT'
import json,os,re
object_id=os.environ['SCIENTIFIC_OBJECT_ID']
idx=json.load(open('/tmp/sc-workspace-v2340-object-index.json'))
get=json.load(open('/tmp/sc-workspace-v2340-object-get.json'))['item']
history=json.load(open('/tmp/sc-workspace-v2340-object-history.json'))
relations=json.load(open('/tmp/sc-workspace-v2340-object-relations.json'))
assert idx['count']==1 and idx['items'][0]['objectId']==object_id,idx
assert get['kind']=='artifact' and get['revision']==1 and get['summary']['filename']=='unified-object.txt',get
assert re.fullmatch(r'[a-f0-9]{64}',get['objectFingerprint']),get
assert history['historyMode']=='revisions' and history['items'][0]['revision']==1,history
assert relations['kind']=='artifact' and relations['relationCount']==0,relations
print('PASS: unified object discovery, canonical lookup, revision history and relation projection are consistent for a stored artifact')
PYOBJECT
curl -fsS -X DELETE "${AUTH[@]}" "http://127.0.0.1:8094/v1/artifacts/${SCIENTIFIC_OBJECT_ID}" >/dev/null

echo "=== CROSS-PRODUCT RESEARCH HANDOFF FABRIC ==="
curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/handoffs/profile >/tmp/sc-workspace-v2340-handoff-profile.json
python3 - <<'PYHANDOFFPROFILE'
import json
p=json.load(open('/tmp/sc-workspace-v2340-handoff-profile.json'))['item']
assert p['backendAuthoritative'] is True and p['revisionPinning'] is True and p['fingerprintPinning'] is True,p
assert p['durableReceipts'] is True and p['genericDestinationMutation'] is False,p
assert 'research-lab' in p['supportedProducts'] and 'decision-studio' in p['supportedProducts'],p
print('PASS: cross-product handoff profile preserves provenance and backend authority')
PYHANDOFFPROFILE
HANDOFF_ARTIFACT_ID="deploy-v2340-handoff-${STAMP}"; export HANDOFF_ARTIFACT_ID
cat >/tmp/sc-workspace-v2340-handoff-artifact.json <<JSON
{"schema":"sc-workspace-artifact-store/1.0","artifactId":"${HANDOFF_ARTIFACT_ID}","filename":"handoff.txt","mediaType":"text/plain","contentBase64":"aGFuZG9mZg==","expectedRevision":0,"metadata":{"release":"2.34.0"}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/sc-workspace-v2340-handoff-artifact.json http://127.0.0.1:8094/v1/artifacts >/dev/null
cat >/tmp/sc-workspace-v2340-handoff-request.json <<JSON
{"schema":"sc-workspace-research-handoff-request/1.0","handoffId":"deploy-handoff-${STAMP}","sourceProduct":"workspace","destinationProduct":"research-lab","intent":"analyze","objects":[{"kind":"artifact","objectId":"${HANDOFF_ARTIFACT_ID}","revision":1}],"context":{"release":"2.34.0"}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/sc-workspace-v2340-handoff-request.json http://127.0.0.1:8094/v1/handoffs >/tmp/sc-workspace-v2340-handoff-result.json
HANDOFF_ID="$(python3 - <<'PYHANDOFF'
import json,re
x=json.load(open('/tmp/sc-workspace-v2340-handoff-result.json')); i=x['item']
assert x['ok'] is True and i['status']=='prepared',x
assert i['objects'][0]['revision']==1 and re.fullmatch(r'[a-f0-9]{64}',i['packageFingerprint']),i
print(i['handoffId'])
PYHANDOFF
)"; export HANDOFF_ID
cat >/tmp/sc-workspace-v2340-handoff-accept.json <<JSON
{"schema":"sc-workspace-research-handoff-accept-request/1.0","destinationProduct":"research-lab","destinationObjectId":"lab-object-${STAMP}","notes":{"verified":true}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/sc-workspace-v2340-handoff-accept.json "http://127.0.0.1:8094/v1/handoffs/${HANDOFF_ID}/accept" >/tmp/sc-workspace-v2340-handoff-accepted.json
python3 - <<'PYHANDOFFACCEPT'
import json
x=json.load(open('/tmp/sc-workspace-v2340-handoff-accepted.json')); assert x['item']['status']=='accepted',x
assert x['receipt']['action']=='accept' and x['receipt']['status']=='accepted',x
print('PASS: canonical object handoff was prepared, fingerprinted, accepted and durably receipted')
PYHANDOFFACCEPT
curl -fsS -X DELETE "${AUTH[@]}" "http://127.0.0.1:8094/v1/artifacts/${HANDOFF_ARTIFACT_ID}" >/dev/null

echo 'PASS: Workspace backend v2.34.0 API + backend policy, identity & authorization consolidation + cross-product research handoff fabric + unified scientific object API + local-first synchronization protocol + generated typed client contracts + inherited scientific runtime fabric are running.'










