#!/usr/bin/env bash
set -Eeuo pipefail
PACKAGE="${1:-/tmp/sustainable-catalyst-workspace-backend-v3.22.0.zip}"
BASE="/opt/sustainable-catalyst"
OLD="$BASE/sustainable-catalyst-workspace-backend-v3.21.0"
NEW="$BASE/sustainable-catalyst-workspace-backend-v3.22.0"
SWITCHED=0
fail(){ echo "ERROR: $*" >&2; exit 1; }
rollback(){ local code=$?; if [[ "$SWITCHED" == 1 ]]; then echo "=== v3.22.0 failed; restoring v3.21.0 ===" >&2; docker rm -f sc-workspace-backend sc-workspace-worker sc-workspace-neural-runtime >/dev/null 2>&1 || true; if [[ -d "$OLD" ]]; then cd "$OLD"; [[ -f docker-compose.yml ]] || cp docker-compose.example.yml docker-compose.yml; docker compose --env-file .env -f docker-compose.yml up -d --no-deps sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker || true; fi; fi; exit "$code"; }
trap rollback ERR
[[ -f "$PACKAGE" ]] || fail "backend package not found: $PACKAGE"
[[ -d "$OLD" && -f "$OLD/.env" ]] || fail "Workspace v3.21.0 backend baseline not found at $OLD"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
unzip -q "$PACKAGE" -d "$TMP/package"
[[ -f "$TMP/package/app/config.py" && -f "$TMP/package/neural-runtime/service.py" && -f "$TMP/package/docker-compose.example.yml" ]] || fail "malformed v3.22.0 backend package"
rm -rf "$NEW"; mkdir -p "$NEW"; cp -a "$TMP/package/." "$NEW/"; cp "$OLD/.env" "$NEW/.env"
cd "$NEW"; cp docker-compose.example.yml docker-compose.yml
python3 -m compileall -q app neural-runtime

echo "=== BUILD WORKSPACE v3.22.0 ==="
docker compose --env-file .env -f docker-compose.yml build sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker

echo "=== SWITCH TO v3.22.0 ==="
docker rm -f sc-workspace-backend sc-workspace-worker sc-workspace-neural-runtime >/dev/null 2>&1 || true
docker compose --env-file .env -f docker-compose.yml up -d --no-deps sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker
SWITCHED=1
for i in $(seq 1 60); do code="$(curl -sS -o /tmp/scw32200-health.json -w '%{http_code}' http://127.0.0.1:8094/health 2>/dev/null || true)"; echo "backend health attempt $i: HTTP $code"; [[ "$code" == 200 ]] && break; sleep 2; done
python3 - <<'PY'
import json
d=json.load(open('/tmp/scw32200-health.json'))
assert d['ok'] is True and d['version']=='3.22.0',d
assert d.get('neuralRuntimeBoundedOperations')==11,d
assert d.get('neuralRuntimeTrainingEnabled') is True,d
assert d.get('neuralTrainingJobRuntime') is True,d
assert d.get('neuralTrainingCheckpointPersistenceEnabled') is False,d
assert d.get('neuralTrainingResumeEnabled') is False,d
assert d.get('neuralTensorDatasetTransformationInterchange') is True,d
print('WORKSPACE_V32200_HEALTH=PASS')
PY

echo "=== DIRECT NEURAL HEALTH ==="
docker exec sc-workspace-neural-runtime python - <<'PY'
import json,urllib.request
x=json.load(urllib.request.urlopen('http://127.0.0.1:8101/health',timeout=5))
assert x['version']=='3.22.0' and len(x['operations'])==11,x
assert x['trainingEnabled'] is True and x['checkpointPersistenceEnabled'] is False,x
assert x['resumeTrainingEnabled'] is False and x['acceleratorExecutionEnabled'] is False,x
print('NEURAL_V32200_DIRECT_HEALTH=PASS engineVersion='+x['engineVersion'])
PY
SERVICE_TOKEN="$(awk -F= '$1=="SC_WORKSPACE_SERVICE_TOKEN"{sub($1"=","");print;exit}' .env)"; [[ -n "$SERVICE_TOKEN" ]] || fail "SC_WORKSPACE_SERVICE_TOKEN blank"
AUTH=(-H "Authorization: Bearer $SERVICE_TOKEN" -H 'X-SC-User-ID: 1')

echo "=== NEURAL TRAINING JOB SMOKE TEST ==="
STAMP="$(date +%s)"
cat >/tmp/scw32200-job.json <<JSON
{"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.neural.train-linear","priority":8,"maxAttempts":1,"idempotencyKey":"deploy-v32200-train-${STAMP}","payload":{"seed":17,"features":[[0.0],[1.0],[2.0],[3.0],[4.0],[5.0]],"targets":[[1.0],[3.0],[5.0],[7.0],[9.0],[11.0]],"trainingSpec":{"schema":"sc-workspace-neural-training-spec/1.0","modelType":"linear","task":"regression","inputFeatures":1,"outputFeatures":1,"epochs":30,"batchSize":3,"shuffle":true,"optimizer":{"name":"adam","learningRate":0.05,"weightDecay":0.0}}}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/scw32200-job.json http://127.0.0.1:8094/v1/jobs >/tmp/scw32200-created.json
JOB_ID="$(python3 -c "import json;print(json.load(open('/tmp/scw32200-created.json'))['item']['jobId'])")"
for i in $(seq 1 45); do curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${JOB_ID}" >/tmp/scw32200-state.json; state="$(python3 -c "import json;print(json.load(open('/tmp/scw32200-state.json'))['item']['status'])")"; echo "neural training job attempt $i: $state"; [[ "$state" == succeeded ]] && break; [[ "$state" =~ ^(failed|blocked|cancelled)$ ]] && { cat /tmp/scw32200-state.json; false; }; sleep 2; done
python3 - <<'PY'
import json
x=json.load(open('/tmp/scw32200-state.json'))['item']; assert x['status']=='succeeded',x
r=x.get('result') or {}; p=r.get('polyglot') or {}; outer=p.get('result') or {}; remote=outer.get('remote') or {}; nr=remote.get('result') or {}; run=nr.get('trainingRun') or {}
assert run.get('schema')=='sc-workspace-neural-training-run/1.0',run
assert run.get('completedEpochs')==30,run
assert run.get('checkpointCreated') is False,run
assert nr.get('trainedModelSpecFingerprint'),nr
print('NEURAL_TRAINING_JOB=PASS jobId='+x['jobId']+' loss='+str((run.get('trainingMetrics') or {}).get('loss')))
PY

echo "=== OPENAPI / RUNTIME REGISTRY ==="
docker exec -i sc-workspace-backend python3 - <<'PY'
from app.main import app
from app.client_contracts import TYPED_ENDPOINTS,profile
from app.polyglot import RUNTIME_BY_LANGUAGE
x=profile(app.openapi()); assert x['workspaceVersion']=='3.22.0' and x['typedEndpointCount']==291 and not x['missingOpenApiOperations'],x
n=RUNTIME_BY_LANGUAGE['neural']; assert len(n.operations)==11 and 'workspace.neural.train-linear' in n.operations and 'workspace.neural.train-mlp' in n.operations,n
assert RUNTIME_BY_LANGUAGE['ml'].runtime=='python-sklearn-predictive'
print('WORKSPACE_V32200_OPENAPI_RUNTIME_REGISTRY=PASS typed_endpoints=%d'%len(TYPED_ENDPOINTS))
PY

echo "=== CONTAINER HARDENING ==="
python3 - <<'PY'
import json,subprocess
d=json.loads(subprocess.check_output(['docker','inspect','sc-workspace-neural-runtime']))[0]; h=d['HostConfig']; c=d['Config']
assert h['ReadonlyRootfs'] is True and c.get('User')=='65532:65532',d
assert 'ALL' in (h.get('CapDrop') or []) and 'no-new-privileges:true' in (h.get('SecurityOpt') or []),d
print('NEURAL_RUNTIME_HARDENING=PASS')
PY

echo "PASS: Workspace v3.22.0 backend deployed and bounded neural training job runtime verified"
trap - ERR
