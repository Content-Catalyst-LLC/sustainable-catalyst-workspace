#!/usr/bin/env bash
set -euo pipefail

ZIP_PATH="${1:-/tmp/sustainable-catalyst-workspace-backend-v2.9.0.zip}"
BASE="/opt/sustainable-catalyst"
NEW="$BASE/sustainable-catalyst-workspace-backend-v2.9.0"

[[ -f "$ZIP_PATH" ]] || { echo "ERROR: backend ZIP not found: $ZIP_PATH" >&2; exit 1; }
ENV_SOURCE=""
for candidate in \
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
docker ps --format '{{.Names}}' | grep -qx sc-postgres || { echo "ERROR: sc-postgres is not running." >&2; exit 1; }
docker volume inspect sc-workspace-data >/dev/null 2>&1 || docker volume create sc-workspace-data >/dev/null

echo "=== WORKSPACE BACKEND v2.9.0 UPGRADE ==="
echo "Credential source: $(dirname "$ENV_SOURCE")"
rm -rf "$NEW"
unzip -q "$ZIP_PATH" -d "$BASE"
cp "$ENV_SOURCE" "$NEW/.env"
chmod 600 "$NEW/.env"
cd "$NEW"
cp docker-compose.example.yml docker-compose.yml

grep -q '^SC_WORKSPACE_MAX_REPRODUCTION_EXECUTION_PLANS_PER_ACCOUNT=' .env || echo 'SC_WORKSPACE_MAX_REPRODUCTION_EXECUTION_PLANS_PER_ACCOUNT=1000' >> .env
grep -q '^SC_WORKSPACE_MAX_RUNTIME_HANDOFF_RECEIPTS_PER_ACCOUNT=' .env || echo 'SC_WORKSPACE_MAX_RUNTIME_HANDOFF_RECEIPTS_PER_ACCOUNT=2000' >> .env
grep -q '^SC_WORKSPACE_MAX_EXECUTION_POLICIES_PER_ACCOUNT=' .env || echo 'SC_WORKSPACE_MAX_EXECUTION_POLICIES_PER_ACCOUNT=250' >> .env
grep -q '^SC_WORKSPACE_MAX_EXECUTION_POLICY_DECISIONS_PER_ACCOUNT=' .env || echo 'SC_WORKSPACE_MAX_EXECUTION_POLICY_DECISIONS_PER_ACCOUNT=5000' >> .env
grep -q '^SC_WORKSPACE_MAX_RUNTIME_EXECUTION_ATTESTATIONS_PER_ACCOUNT=' .env || echo 'SC_WORKSPACE_MAX_RUNTIME_EXECUTION_ATTESTATIONS_PER_ACCOUNT=5000' >> .env
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
  migrations/009_runtime_enforcement_telemetry_attestations.sql
do
  echo "Applying ${migration}"
  docker exec -i sc-postgres psql -U "$PG_ADMIN_USER" -d sc_workspace -v ON_ERROR_STOP=1 < "$migration" >/dev/null
  echo "PASS: ${migration}"
done

echo "=== VERIFY v2.8 POLICY REGISTRY PRIVILEGES ==="
docker exec -i sc-postgres psql -U "$PG_ADMIN_USER" -d sc_workspace -v ON_ERROR_STOP=1 -tAc \
  "SELECT count(*) FROM information_schema.role_table_grants WHERE grantee='sc_workspace' AND table_name IN ('workspace_execution_policy_heads','workspace_execution_policy_revisions','workspace_execution_policy_decisions') AND privilege_type='INSERT';" \
  | grep -q '^3$' || { echo 'ERROR: sc_workspace v2.8 policy-registry INSERT privileges are incomplete.' >&2; exit 1; }
docker exec -i sc-postgres psql -U "$PG_ADMIN_USER" -d sc_workspace -v ON_ERROR_STOP=1 -tAc \
  "SELECT count(*) FROM information_schema.columns WHERE table_name IN ('workspace_runtime_adapter_heads','workspace_runtime_adapter_revisions') AND column_name='trust_level';" \
  | grep -q '^2$' || { echo 'ERROR: runtime adapter trust_level migration is incomplete.' >&2; exit 1; }
echo "PASS: v2.8 policy registry privileges + adapter trust migration"

echo "=== VERIFY v2.9 RUNTIME ATTESTATION REGISTRY ==="
docker exec -i sc-postgres psql -U "$PG_ADMIN_USER" -d sc_workspace -v ON_ERROR_STOP=1 -tAc \
  "SELECT count(*) FROM information_schema.role_table_grants WHERE grantee='sc_workspace' AND table_name='workspace_runtime_execution_attestations' AND privilege_type='INSERT';" \
  | grep -q '^1$' || { echo 'ERROR: sc_workspace runtime-attestation INSERT privilege is missing.' >&2; exit 1; }
echo "PASS: v2.9 runtime attestation registry + privileges"

docker rm -f sc-workspace-worker 2>/dev/null || true
docker rm -f sc-workspace-backend 2>/dev/null || true

echo "=== BUILD + START v2.9.0 API AND WORKER ==="
docker compose --env-file .env -f docker-compose.yml up -d --build

for i in $(seq 1 30); do
  code="$(curl -sS -o /tmp/sc-workspace-v290-health.json -w '%{http_code}' http://127.0.0.1:8094/health 2>/dev/null || true)"
  echo "health attempt $i: HTTP ${code:-000}"
  [[ "$code" == "200" ]] && break
  sleep 2
done
python3 -m json.tool /tmp/sc-workspace-v290-health.json
python3 - <<'PY'
import json
d=json.load(open('/tmp/sc-workspace-v290-health.json'))
assert d.get('ok') is True and d.get('version')=='2.9.0'
for key in ('reproductionExecutionPlans','controlledRuntimeHandoffs','humanAuthorizedDispatch','executionPolicyRegistry','resourceBudgets','runtimeSandboxing','policyRequiredForControlledHandoffs','adapterTrustLevels','runtimeEnforcementTelemetry','budgetAccounting','executionAttestations','dedicatedRuntimeAttestationCredential'):
    assert d.get(key) is True, key
assert d.get('automaticReproductionExecution') is False
assert d.get('clientSuppliedRuntimeUrlsAllowed') is False
assert d.get('arbitraryCodeExecution') is False
PY

curl -fsS http://127.0.0.1:8094/ready | python3 -m json.tool
set -a; . ./.env; set +a
AUTH=( -H "Authorization: Bearer ${SC_WORKSPACE_SERVICE_TOKEN}" -H "X-SC-User-ID: 999999999999" )
RUNTIME_ATTESTATION_TOKEN="$(awk -F= '$1=="SC_WORKSPACE_RUNTIME_ATTESTATION_TOKEN"{print $2}' .env | tail -1)"
[[ -n "$RUNTIME_ATTESTATION_TOKEN" ]] || { echo "ERROR: runtime attestation token missing." >&2; exit 1; }

curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/capabilities >/tmp/sc-workspace-v290-capabilities.json
python3 - <<'PY'
import json
d=json.load(open('/tmp/sc-workspace-v290-capabilities.json'))
for key in ('reproductionExecutionPlans','controlledRuntimeHandoffs','humanAuthorizedDispatch','frozenExecutionEnvelope','executionPolicyRegistry','executionPolicyDecisions','resourceBudgets','runtimeSandboxing','policyRequiredForControlledHandoffs','adapterTrustLevels','runtimeEnforcementTelemetry','budgetAccounting','executionAttestations'):
    assert d.get(key) is True, key
for key in ('automaticReproductionExecution','clientSuppliedRuntimeUrlsAllowed','clientSuppliedRuntimeCredentialsAllowed','hostFilesystemAccessAllowed','dockerSocketAccessAllowed','privilegedExecutionAllowed','arbitraryCodeExecution','browserAttestationSubmissionAllowed'):
    assert d.get(key) is False, key
assert d.get('runtimeAttestationAuth')=='dedicated-server-token'
print('PASS: v2.9 runtime-enforcement telemetry/attestation capabilities')
PY

for i in $(seq 1 20); do
  curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/worker/status >/tmp/sc-workspace-v290-worker.json
  python3 - <<'PY' && break || true
import json
d=json.load(open('/tmp/sc-workspace-v290-worker.json'))
raise SystemExit(0 if any(x.get('version')=='2.9.0' and x.get('status') in ('idle','running') for x in d.get('items',[])) else 1)
PY
  sleep 2
done

STAMP="$(date +%s)"
ENV_ID="deploy-v290-env-${STAMP}"; ADAPTER_ID="deploy-v290-python-${STAMP}"
DATASET_ID="deploy-v290-dataset-${STAMP}"; MODEL_ID="deploy-v290-model-${STAMP}"; PARAM_ID="deploy-v290-params-${STAMP}"
RUN1="deploy-v290-original-${STAMP}"; RUN2="deploy-v290-reproduction-${STAMP}"

cat >/tmp/v290-env.json <<JSON
{"schema":"sc-workspace-execution-environment/1.0","environmentId":"${ENV_ID}","name":"v2.8 smoke environment","runtime":{"language":"python","version":"3.12"},"dependencies":{"manager":"pip","manifest":"requirements.txt"},"container":{"image":"python:3.12-slim"},"system":{"os":"linux","architecture":"x86_64"},"randomSeeds":{"python":42},"expectedRevision":0}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/v290-env.json http://127.0.0.1:8094/v1/execution-environments >/dev/null

cat >/tmp/v290-adapter.json <<JSON
{"schema":"sc-workspace-runtime-adapter/1.0","adapterId":"${ADAPTER_ID}","name":"Python 3.12 controlled adapter","runtimeFamily":"python","runtimeVersion":"3.12","adapterType":"metadata","trustLevel":"bounded","dependencyManagers":["pip"],"container":{"image":"python:3.12-slim"},"capabilities":["workspace.echo"],"configuration":{"strictContainerIdentity":true},"expectedRevision":0}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/v290-adapter.json http://127.0.0.1:8094/v1/runtime-adapters >/dev/null

POLICY_ID="deploy-v290-policy-${STAMP}"
cat >/tmp/v290-policy.json <<JSON
{"schema":"sc-workspace-execution-policy/1.0","policyId":"${POLICY_ID}","name":"v2.8 bounded deployment policy","allowedTargetProducts":["workspace"],"allowedOperations":["workspace.echo"],"minimumAdapterTrust":"bounded","resourceLimits":{"cpuCores":1.0,"memoryMb":512,"wallSeconds":60,"outputBytes":1048576,"pids":32,"tempStorageMb":128},"sandboxMode":"metadata-gate","networkMode":"none","readOnlyRootFilesystem":true,"noNewPrivileges":true,"dropAllCapabilities":true,"requirePinnedContainer":false,"expectedRevision":0}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/v290-policy.json http://127.0.0.1:8094/v1/execution-policies >/tmp/v290-policy-created.json
python3 - <<'PY2'
import json
d=json.load(open('/tmp/v290-policy-created.json'))['item']
assert d['revision']==1 and len(d['fingerprint'])==64
assert d['minimumAdapterTrust']=='bounded'
assert d['sandbox']['allowPrivileged'] is False
assert d['sandbox']['allowHostFilesystem'] is False
assert d['sandbox']['allowDockerSocket'] is False
print('PASS: revisioned bounded execution policy created')
PY2

cat >/tmp/v290-dataset.json <<JSON
{"schema":"sc-workspace-dataset-record/1.0","datasetId":"${DATASET_ID}","name":"v2.8 smoke dataset","datasetType":"table","sourceKind":"generated","expectedRevision":0}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/v290-dataset.json http://127.0.0.1:8094/v1/datasets >/dev/null
cat >/tmp/v290-model.json <<JSON
{"schema":"sc-workspace-model-record/1.0","modelId":"${MODEL_ID}","name":"v2.8 smoke model","modelKind":"custom","executionTarget":"workspace","executionOperation":"workspace.echo","expectedRevision":0}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/v290-model.json http://127.0.0.1:8094/v1/models >/dev/null
cat >/tmp/v290-params.json <<JSON
{"schema":"sc-workspace-parameter-set/1.0","parameterSetId":"${PARAM_ID}","modelId":"${MODEL_ID}","name":"v2.8 smoke params","parameters":{"value":42},"expectedRevision":0}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/v290-params.json http://127.0.0.1:8094/v1/parameter-sets >/dev/null

create_run () {
  local RID="$1" KEY="$2"
  cat >/tmp/v290-run.json <<JSON
{"schema":"sc-workspace-execution-run/1.0","runId":"${RID}","name":"v2.8 policy-governed reproduction smoke","datasetRefs":[{"datasetId":"${DATASET_ID}"}],"modelRef":{"modelId":"${MODEL_ID}"},"parameterSetRef":{"parameterSetId":"${PARAM_ID}"},"environmentRef":{"environmentId":"${ENV_ID}","revision":1},"runtimeAdapterRef":{"adapterId":"${ADAPTER_ID}","revision":1},"idempotencyKey":"${KEY}-run"}
JSON
  curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/v290-run.json http://127.0.0.1:8094/v1/runs >/tmp/v290-run-created.json
}

queue_job_and_wait () {
  local RID="$1" KEY="$2"
  cat >/tmp/v290-job.json <<JSON
{"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.echo","executionRunId":"${RID}","priority":9,"maxAttempts":1,"idempotencyKey":"${KEY}-job","payload":{"value":42,"version":"2.9.0"}}
JSON
  curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/v290-job.json http://127.0.0.1:8094/v1/jobs >/tmp/v290-job-created.json
  JOB_ID="$(python3 -c "import json; print(json.load(open('/tmp/v290-job-created.json'))['item']['jobId'])")"
  wait_job "$JOB_ID"
}

wait_job () {
  local JOB_ID="$1" STATUS=""
  for i in $(seq 1 30); do
    curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/jobs/${JOB_ID} >/tmp/v290-job-status.json
    STATUS="$(python3 -c "import json; print(json.load(open('/tmp/v290-job-status.json'))['item']['status'])")"
    [[ "$STATUS" == "succeeded" ]] && break
    [[ "$STATUS" =~ ^(failed|blocked|cancelled)$ ]] && break
    sleep 1
  done
  [[ "$STATUS" == "succeeded" ]] || { echo "ERROR: smoke job ${JOB_ID} ended ${STATUS}" >&2; exit 1; }
}

add_output () {
  local RID="$1"
  cat >/tmp/v290-output.json <<JSON
{"schema":"sc-workspace-execution-run-output/1.0","outputId":"primary","role":"result","label":"deterministic smoke output","mediaType":"application/json","sha256":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","bytes":42}
JSON
  curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/v290-output.json http://127.0.0.1:8094/v1/runs/${RID}/outputs >/dev/null
}

create_run "$RUN1" "deploy-v290-original-${STAMP}"
queue_job_and_wait "$RUN1" "deploy-v290-original-${STAMP}"
add_output "$RUN1"

cat >/tmp/v290-repro-plan.json <<JSON
{"schema":"sc-workspace-reproduction-plan/1.0","originalRunId":"${RUN1}","runtimeAdapterRef":{"adapterId":"${ADAPTER_ID}","revision":1},"notes":"v2.8 policy-governed handoff smoke"}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/v290-repro-plan.json http://127.0.0.1:8094/v1/reproduction-plans >/tmp/v290-repro-plan-created.json
REPRO_PLAN_ID="$(python3 -c "import json; print(json.load(open('/tmp/v290-repro-plan-created.json'))['item']['planId'])")"

create_run "$RUN2" "deploy-v290-reproduction-${STAMP}"

cat >/tmp/v290-overbudget-plan.json <<JSON
{"schema":"sc-workspace-reproduction-execution-plan/1.0","reproductionPlanId":"${REPRO_PLAN_ID}","reproductionRunId":"${RUN2}","executionPolicyRef":{"policyId":"${POLICY_ID}","revision":1},"resourceBudget":{"cpuCores":1.0,"memoryMb":1024,"wallSeconds":60,"outputBytes":1048576,"pids":32,"tempStorageMb":128},"priority":9,"maxAttempts":1,"payload":{"value":42,"version":"2.9.0"},"notes":"over-budget policy smoke"}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/v290-overbudget-plan.json http://127.0.0.1:8094/v1/reproduction-execution-plans >/tmp/v290-overbudget-plan-created.json
python3 - <<'PY2'
import json
d=json.load(open('/tmp/v290-overbudget-plan-created.json'))['item']
assert d['status']=='blocked', d
pd=d['readiness']['policyDecision']
assert pd['eligible'] is False and pd['classification']=='blocked'
assert any(x['check']=='resource-memoryMb' and x['status']=='fail' for x in pd['checks'])
print('PASS: over-budget execution plan blocked by policy')
PY2

cat >/tmp/v290-exec-plan.json <<JSON
{"schema":"sc-workspace-reproduction-execution-plan/1.0","reproductionPlanId":"${REPRO_PLAN_ID}","reproductionRunId":"${RUN2}","executionPolicyRef":{"policyId":"${POLICY_ID}","revision":1},"resourceBudget":{"cpuCores":1.0,"memoryMb":512,"wallSeconds":60,"outputBytes":1048576,"pids":32,"tempStorageMb":128},"priority":9,"maxAttempts":1,"payload":{"value":42,"version":"2.9.0"},"notes":"policy-governed human-gated deployment smoke"}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/v290-exec-plan.json http://127.0.0.1:8094/v1/reproduction-execution-plans >/tmp/v290-exec-plan-created.json
EXEC_PLAN_ID="$(python3 -c "import json; print(json.load(open('/tmp/v290-exec-plan-created.json'))['item']['executionPlanId'])")"
python3 - <<'PY'
import json
d=json.load(open('/tmp/v290-exec-plan-created.json'))['item']
assert d['status']=='ready', d['readiness']
assert d['readiness']['ready'] is True
assert d['policy']['humanAuthorizationRequired'] is True
assert d['policy']['automaticDispatch'] is False
assert d['policy']['clientSuppliedRouteUrlAllowed'] is False
assert d['policy']['arbitraryCodeExecution'] is False
assert d['policy']['executionEligible'] is True
assert d['policy']['resourceBudget']['memoryMb']==512
assert d['policy']['sandbox']['allowPrivileged'] is False
assert d['readiness']['policyDecision']['classification']=='eligible'
assert not d['jobRequest'].get('routeUrl')
print('PASS: policy-eligible frozen execution plan ready; no automatic dispatch')
PY

cat >/tmp/v290-handoff.json <<JSON
{"schema":"sc-workspace-controlled-runtime-handoff/1.0","humanAuthorized":true,"reason":"deployment-smoke-human-authorization"}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/v290-handoff.json http://127.0.0.1:8094/v1/reproduction-execution-plans/${EXEC_PLAN_ID}/handoff >/tmp/v290-handoff-created.json
HANDOFF_JOB_ID="$(python3 -c "import json; print(json.load(open('/tmp/v290-handoff-created.json'))['item']['jobId'])")"
python3 - <<'PY'
import json
d=json.load(open('/tmp/v290-handoff-created.json'))['item']
assert d['details']['humanAuthorized'] is True
assert d['details']['automaticDispatch'] is False
assert d['details']['serverConfiguredRouteOnly'] is True
assert d['details']['clientSuppliedRouteUrlAllowed'] is False
assert d['details']['arbitraryCodeExecution'] is False
assert d['details']['executionPolicyEligible'] is True
assert len(d['details']['executionPolicyDecisionFingerprint'])==64
assert d['details']['resourceBudget']['memoryMb']==512
assert d['details']['sandbox']['allowPrivileged'] is False
assert len(d['fingerprint'])==64
print('PASS: human-authorized policy-governed runtime handoff receipt')
PY

wait_job "$HANDOFF_JOB_ID"
add_output "$RUN2"

cat >/tmp/v290-verify.json <<JSON
{"schema":"sc-workspace-reproduction-verification/1.0","originalRunId":"${RUN1}","reproductionRunId":"${RUN2}"}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/v290-verify.json http://127.0.0.1:8094/v1/reproduction-verifications >/tmp/v290-verify-created.json
python3 - <<'PY'
import json
d=json.load(open('/tmp/v290-verify-created.json'))['item']
assert d['classification']=='exact', d
assert all(d[k] is True for k in ('exactInputs','exactEnvironment','exactRuntimeAdapter','exactOutputs'))
print('PASS: controlled handoff reproduced exact run provenance and output digest')
PY


HANDOFF_RECEIPT_ID="$(python3 -c "import json; print(json.load(open('/tmp/v290-handoff-created.json'))['item']['receiptId'])")"
cat >/tmp/v290-attestation.json <<JSON
{"schema":"sc-workspace-runtime-execution-attestation/1.0","source":"specialist-runtime","observedUsage":{"cpuCoreSeconds":2.5,"peakMemoryMb":128,"wallSeconds":3.0,"outputBytes":42,"pidsPeak":4,"tempStorageMbPeak":8},"sandboxAttestation":{"mode":"metadata-gate","networkMode":"server-routed-only","readOnlyRootFilesystem":true,"noNewPrivileges":true,"dropAllCapabilities":true,"hostFilesystemAccess":false,"dockerSocketAccess":false,"privilegedExecution":false,"pinnedContainer":false,"attestedBy":"workspace-v2.9-deploy-smoke","evidenceDigest":"cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"},"notes":"v2.9 deployment attestation smoke"}
JSON
curl -fsS "${AUTH[@]}" -H "X-SC-Runtime-Attestation-Token: ${RUNTIME_ATTESTATION_TOKEN}" -H 'Content-Type: application/json' --data-binary @/tmp/v290-attestation.json http://127.0.0.1:8094/v1/runtime-handoff-receipts/${HANDOFF_RECEIPT_ID}/attest >/tmp/v290-attestation-created.json
python3 - <<'PYATTEST'
import json
d=json.load(open('/tmp/v290-attestation-created.json'))['item']
assert d['classification']=='compliant', d
assert d['executionSucceeded'] is True
assert d['budgetCompliant'] is True
assert d['sandboxCompliant'] is True
assert d['budgetAccounting']['peakMemoryMb']['observed']==128
assert d['budgetAccounting']['peakMemoryMb']['headroom']==384.0
assert len(d['policyDecisionFingerprint'])==64
assert len(d['fingerprint'])==64
print('PASS: compliant runtime execution attestation with budget accounting')
PYATTEST

curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/runtime-execution-attestations >/tmp/v290-attestation-index.json
python3 - <<'PYINDEX'
import json
d=json.load(open('/tmp/v290-attestation-index.json'))
assert d['browserSubmissionAllowed'] is False
assert any(x['classification']=='compliant' for x in d['items'])
print('PASS: runtime attestation registry readable; browser submission disabled')
PYINDEX

echo "=== CONTAINERS ==="
docker ps --filter name=sc-workspace --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
echo "PASS: Workspace backend v2.9.0 API + worker + runtime enforcement telemetry + budget accounting + execution attestations are running."
