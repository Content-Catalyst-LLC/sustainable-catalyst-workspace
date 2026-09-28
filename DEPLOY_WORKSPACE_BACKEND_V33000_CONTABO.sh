#!/usr/bin/env bash
set -Eeuo pipefail
PACKAGE="${1:-/tmp/sustainable-catalyst-workspace-backend-v3.30.0.zip}"
BASE="/opt/sustainable-catalyst"
OLD="$BASE/sustainable-catalyst-workspace-backend-v3.29.0"
NEW="$BASE/sustainable-catalyst-workspace-backend-v3.30.0"
SWITCHED=0
fail(){ echo "ERROR: $*" >&2; exit 1; }
rollback(){ local code=$?; if [[ "$SWITCHED" == 1 ]]; then echo "=== v3.30.0 verification failed; restoring v3.29.0 ===" >&2; docker rm -f sc-workspace-backend sc-workspace-worker sc-workspace-neural-runtime >/dev/null 2>&1 || true; if [[ -d "$OLD" ]]; then cd "$OLD"; [[ -f docker-compose.yml ]] || cp docker-compose.example.yml docker-compose.yml; docker compose --env-file .env -f docker-compose.yml up -d --no-deps --no-build sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker || true; fi; fi; exit "$code"; }
trap rollback ERR
[[ -f "$PACKAGE" ]] || fail "backend package not found: $PACKAGE"
[[ -d "$OLD" && -f "$OLD/.env" ]] || fail "Workspace v3.29.0 production baseline not found at $OLD"
TMP="$(mktemp -d)"; cleanup(){ rm -rf "$TMP"; }; trap cleanup EXIT
unzip -q "$PACKAGE" -d "$TMP/package"
[[ -f "$TMP/package/app/config.py" && -f "$TMP/package/neural-runtime/service.py" ]] || fail "malformed v3.30.0 backend package"
grep -q 'service_version: str = "3.30.0"' "$TMP/package/app/config.py" || fail "v3.30.0 backend version marker missing"
grep -q 'SERVICE_VERSION = "3.30.0"' "$TMP/package/neural-runtime/service.py" || fail "v3.30.0 neural version marker missing"
for op in workspace.neural.trial-plan workspace.neural.trial-execute workspace.neural.batch-execute workspace.neural.hyperparameter-grid workspace.neural.hyperparameter-random; do grep -q "$op" "$TMP/package/neural-runtime/service.py" || fail "v3.30 operation missing: $op"; done
rm -rf "$NEW"; mkdir -p "$NEW"; cp -a "$TMP/package/." "$NEW/"; cp "$OLD/.env" "$NEW/.env"
cd "$NEW"; cp docker-compose.example.yml docker-compose.yml
python3 -m compileall -q app neural-runtime

echo "=== BUILD WORKSPACE v3.30.0 ==="
docker compose --env-file .env -f docker-compose.yml build sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker

echo "=== PRE-SWITCH HARDENED BATCH/TRIAL CERTIFICATION ==="
docker compose --env-file .env -f docker-compose.yml run --rm -T --no-deps --entrypoint python sc-workspace-neural-runtime - <<'PYCODE'
import service
h=service.health(); assert h['version']=='3.30.0' and len(h['operations'])==44,h
payload={
 'trainingSpec':{'schema':'sc-workspace-neural-training-spec/1.0','modelType':'linear','task':'regression','inputFeatures':1,'outputFeatures':1,'optimizer':{'name':'sgd','learningRate':0.05,'weightDecay':0.0},'epochs':1,'batchSize':4,'shuffle':False},
 'features':[[0.0],[1.0],[2.0],[3.0]],'targets':[[1.0],[3.0],[5.0],[7.0]],
 'validationFeatures':[[4.0],[5.0]],'validationTargets':[[9.0],[11.0]],
 'objective':{'dataset':'validation','metric':'loss','direction':'minimize'},'seed':31,'deviceRequest':'cpu',
 'parameterGrid':{'optimizer.learningRate':[0.01,0.05]}
}
tok=service._CURRENT_DEVICE.set('cpu')
try:
    x=service._hyperparameter_grid(payload); a=x['searchArtifact']
finally: service._CURRENT_DEVICE.reset(tok)
assert a['schema']=='sc-workspace-neural-hyperparameter-search-artifact/1.0' and a['trialCount']==2,a
assert a['bestTrialId']==a['ranking'][0]['trialId'] and len(a['artifactFingerprint'])==64,a
assert 'checkpointArtifact' not in a['trials'][0],a['trials'][0]
print('NEURAL_V33000_PRESWITCH_BATCH_TRIAL_HYPERPARAMETER=PASS')
PYCODE

echo "=== SWITCH TO v3.30.0 ==="
docker rm -f sc-workspace-backend sc-workspace-worker sc-workspace-neural-runtime >/dev/null 2>&1 || true
docker compose --env-file .env -f docker-compose.yml up -d --no-deps sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker
SWITCHED=1
for i in $(seq 1 60); do code="$(curl -sS -o /tmp/scw33000-health.json -w '%{http_code}' http://127.0.0.1:8094/health 2>/dev/null || true)"; echo "backend health attempt $i: HTTP $code"; [[ "$code" == 200 ]] && break; sleep 2; done
python3 - <<'PYCODE'
import json
x=json.load(open('/tmp/scw33000-health.json')); assert x['ok'] is True and x['version']=='3.30.0',x
assert x.get('neuralRuntimeBoundedOperations')==44,x
assert x.get('neuralBatchTrialHyperparameterExecutionRuntime') is True,x
print('WORKSPACE_V33000_HEALTH=PASS')
PYCODE

echo "=== DIRECT NEURAL HEALTH ==="
docker exec -i sc-workspace-neural-runtime python - <<'PYCODE'
import json,urllib.request
x=json.load(urllib.request.urlopen('http://127.0.0.1:8101/health',timeout=5))
assert x['version']=='3.30.0' and len(x['operations'])==44,x
assert x['batchTrialHyperparameterExecutionEnabled'] is True,x
print('NEURAL_V33000_DIRECT_HEALTH=PASS engineVersion='+x['engineVersion'])
PYCODE
SERVICE_TOKEN="$(awk -F= '$1=="SC_WORKSPACE_SERVICE_TOKEN"{sub($1"=","");print;exit}' .env)"; [[ -n "$SERVICE_TOKEN" ]] || fail "SC_WORKSPACE_SERVICE_TOKEN blank"
AUTH=(-H "Authorization: Bearer $SERVICE_TOKEN" -H 'X-SC-User-ID: 1')
wait_job(){ local id="$1" out="$2" label="$3"; for i in $(seq 1 60); do curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${id}" >"$out"; state="$(python3 -c "import json;print(json.load(open('$out'))['item']['status'])")"; echo "$label attempt $i: $state"; [[ "$state" == succeeded ]] && return 0; [[ "$state" =~ ^(failed|blocked|cancelled)$ ]] && { cat "$out"; return 1; }; sleep 2; done; return 1; }

echo "=== END-TO-END HYPERPARAMETER GRID JOB ==="
STAMP="$(date +%s)"
cat >/tmp/scw33000-search-job.json <<JSON
{"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.neural.hyperparameter-grid","priority":8,"maxAttempts":1,"idempotencyKey":"deploy-v33000-search-${STAMP}","payload":{"deviceRequest":"cpu","trainingSpec":{"schema":"sc-workspace-neural-training-spec/1.0","modelType":"linear","task":"regression","inputFeatures":1,"outputFeatures":1,"optimizer":{"name":"sgd","learningRate":0.05,"weightDecay":0.0},"epochs":1,"batchSize":4,"shuffle":false},"features":[[0.0],[1.0],[2.0],[3.0]],"targets":[[1.0],[3.0],[5.0],[7.0]],"validationFeatures":[[4.0],[5.0]],"validationTargets":[[9.0],[11.0]],"objective":{"dataset":"validation","metric":"loss","direction":"minimize"},"seed":31,"parameterGrid":{"optimizer.learningRate":[0.01,0.05]}}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/scw33000-search-job.json http://127.0.0.1:8094/v1/jobs >/tmp/scw33000-search-created.json
JOB_ID="$(python3 -c "import json;print(json.load(open('/tmp/scw33000-search-created.json'))['item']['jobId'])")"
wait_job "$JOB_ID" /tmp/scw33000-search-state.json "hyperparameter grid"
python3 - <<'PYCODE'
import json
x=json.load(open('/tmp/scw33000-search-state.json')); item=x.get('item') or {}; jr=x.get('result') or {}; nr=jr['polyglot']['result']['remote']['result']; a=nr.get('searchArtifact') or {}; wa=nr.get('workspaceTrialSearchArtifact') or {}
assert item.get('status')=='succeeded',item
assert a.get('schema')=='sc-workspace-neural-hyperparameter-search-artifact/1.0' and a.get('trialCount')==2,a
assert a.get('bestTrialId') and len(a.get('artifactFingerprint',''))==64,a
assert wa.get('artifactId') and wa.get('mediaType')=='application/vnd.sc.workspace.neural-hyperparameter-search+json',wa
open('/tmp/scw33000-artifact-id.txt','w').write(wa['artifactId']); open('/tmp/scw33000-receipt-id.txt','w').write(jr['receiptId'])
print('NEURAL_HYPERPARAMETER_GRID_JOB=PASS jobId='+item['jobId'])
PYCODE
AID="$(cat /tmp/scw33000-artifact-id.txt)"; RID="$(cat /tmp/scw33000-receipt-id.txt)"
curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/artifacts/${AID}" >/tmp/scw33000-search-artifact.json
python3 - <<'PYCODE'
import base64,json
x=json.load(open('/tmp/scw33000-search-artifact.json')); item=x.get('item') or {}
assert item.get('mediaType')=='application/vnd.sc.workspace.neural-hyperparameter-search+json',item
raw=base64.b64decode(item['contentBase64']); a=json.loads(raw)
assert a['schema']=='sc-workspace-neural-hyperparameter-search-artifact/1.0' and a['trialCount']==2,a
print('NEURAL_HYPERPARAMETER_SEARCH_WORKSPACE_ARTIFACT=PASS')
PYCODE
curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/polyglot/receipts/${RID}" >/tmp/scw33000-search-receipt.json
python3 - <<'PYCODE'
import json
x=json.load(open('/tmp/scw33000-search-receipt.json')); d=(x.get('item') or {}).get('details') or {}
assert d.get('neuralBatchTrialHyperparameterExecution') is True,d
assert d.get('trialCount')==2 and d.get('bestTrialId'),d
assert d.get('workspaceTrialSearchArtifactId') and d.get('searchSpaceFingerprint'),d
assert d.get('selectedDevice')=='cpu',d
print('NEURAL_HYPERPARAMETER_SEARCH_RECEIPT_LINEAGE=PASS')
PYCODE

echo "=== OPENAPI / RUNTIME REGISTRY ==="
docker exec -i sc-workspace-backend python3 - <<'PYCODE'
from app.main import app
from app.client_contracts import TYPED_ENDPOINTS,profile
from app.polyglot import RUNTIME_BY_LANGUAGE
x=profile(app.openapi()); assert x['workspaceVersion']=='3.30.0' and x['typedEndpointCount']==291 and not x['missingOpenApiOperations'],x
n=RUNTIME_BY_LANGUAGE['neural']; assert len(n.operations)==44,n
for op in ['workspace.neural.trial-plan','workspace.neural.trial-execute','workspace.neural.batch-execute','workspace.neural.hyperparameter-grid','workspace.neural.hyperparameter-random']: assert op in n.operations,(op,n)
print('WORKSPACE_V33000_OPENAPI_RUNTIME_REGISTRY=PASS typed_endpoints=%d'%len(TYPED_ENDPOINTS))
PYCODE

echo "=== CONTAINER HARDENING ==="
python3 - <<'PYCODE'
import json,subprocess
d=json.loads(subprocess.check_output(['docker','inspect','sc-workspace-neural-runtime']))[0]; h=d['HostConfig']; c=d['Config']
assert h['ReadonlyRootfs'] is True and c.get('User')=='65532:65532',d
assert 'ALL' in (h.get('CapDrop') or []) and 'no-new-privileges:true' in (h.get('SecurityOpt') or []),d
print('NEURAL_RUNTIME_HARDENING=PASS')
PYCODE

echo "PASS: Workspace v3.30.0 backend deployed; bounded neural trials, batch execution, deterministic hyperparameter search, governed artifact persistence, receipt lineage, and hardening verified"
trap - ERR
