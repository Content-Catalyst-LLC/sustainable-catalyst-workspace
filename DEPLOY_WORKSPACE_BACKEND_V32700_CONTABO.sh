#!/usr/bin/env bash
set -Eeuo pipefail
PACKAGE="${1:-/tmp/sustainable-catalyst-workspace-backend-v3.27.0.zip}"
BASE="/opt/sustainable-catalyst"
OLD="$BASE/sustainable-catalyst-workspace-backend-v3.26.0"
NEW="$BASE/sustainable-catalyst-workspace-backend-v3.27.0"
SWITCHED=0
fail(){ echo "ERROR: $*" >&2; exit 1; }
rollback(){
  local code=$?
  if [[ "$SWITCHED" == 1 ]]; then
    echo "=== v3.27.0 verification failed; restoring v3.26.0 ===" >&2
    docker rm -f sc-workspace-backend sc-workspace-worker sc-workspace-neural-runtime >/dev/null 2>&1 || true
    if [[ -d "$OLD" ]]; then
      cd "$OLD"
      [[ -f docker-compose.yml ]] || cp docker-compose.example.yml docker-compose.yml
      docker compose --env-file .env -f docker-compose.yml up -d --no-deps --no-build \
        sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker || true
    fi
  fi
  exit "$code"
}
trap rollback ERR
[[ -f "$PACKAGE" ]] || fail "backend package not found: $PACKAGE"
[[ -d "$OLD" && -f "$OLD/.env" ]] || fail "Workspace v3.26.0 production baseline not found at $OLD"
TMP="$(mktemp -d)"; cleanup(){ rm -rf "$TMP"; }; trap cleanup EXIT
unzip -q "$PACKAGE" -d "$TMP/package"
[[ -f "$TMP/package/app/config.py" && -f "$TMP/package/neural-runtime/service.py" && -f "$TMP/package/docker-compose.example.yml" ]] || fail "malformed v3.27.0 backend package"
grep -q 'service_version: str = "3.27.0"' "$TMP/package/app/config.py" || fail "v3.27.0 backend version marker missing"
grep -q 'SERVICE_VERSION = "3.27.0"' "$TMP/package/neural-runtime/service.py" || fail "v3.27.0 neural version marker missing"
for op in workspace.neural.infer-regression workspace.neural.infer-binary workspace.neural.infer-multiclass workspace.neural.prediction-inspect; do
  grep -q "$op" "$TMP/package/neural-runtime/service.py" || fail "inference operation missing: $op"
done
grep -q 'PREDICTION_ARTIFACT_SCHEMA = "sc-workspace-neural-prediction-artifact/1.0"' "$TMP/package/neural-runtime/service.py" || fail "prediction artifact schema missing"
grep -q 'application/vnd.sc.workspace.neural-prediction+json' "$TMP/package/app/polyglot.py" || fail "Workspace prediction artifact persistence missing"
grep -q 'neuralInferencePredictionProvenance' "$TMP/package/app/polyglot.py" || fail "prediction receipt provenance missing"
grep -q '^numpy==2.2.6$' "$TMP/package/neural-runtime/requirements.txt" || fail "NumPy pin missing"
grep -q '^torch==2.10.0$' "$TMP/package/neural-runtime/requirements.txt" || fail "PyTorch pin missing"
rm -rf "$NEW"; mkdir -p "$NEW"; cp -a "$TMP/package/." "$NEW/"; cp "$OLD/.env" "$NEW/.env"
cd "$NEW"; cp docker-compose.example.yml docker-compose.yml
python3 -m compileall -q app neural-runtime

echo "=== BUILD WORKSPACE v3.27.0 ==="
docker compose --env-file .env -f docker-compose.yml build sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker

echo "=== PRE-SWITCH HARDENED INFERENCE / PREDICTION PROVENANCE CERTIFICATION ==="
docker compose --env-file .env -f docker-compose.yml run --rm --no-deps --entrypoint python sc-workspace-neural-runtime - <<'PYCODE'
from copy import deepcopy
from fastapi import HTTPException
import service
h=service.health()
assert h['version']=='3.27.0' and len(h['operations'])==31,h
assert h['neuralInferencePredictionProvenanceEnabled'] is True,h
assert h['predictionArtifactSchema']=='sc-workspace-neural-prediction-artifact/1.0',h
assert h['inferenceTargetsAccepted'] is False,h
assert h['runtimeIdentity']=='scworkspace' and h['runtimeHome']=='/tmp',h
lin={'schema':'sc-workspace-neural-model-spec/1.0','modelType':'linear','weights':[[2.0,-1.0]],'bias':[0.5],'activation':'identity'}
r=service._infer_regression({'modelSpec':lin,'features':[[3.0,1.0]],'rowIds':['r1']})
assert abs(r['predictions'][0]['outputs'][0]-5.5)<1e-6,r
assert r['predictionArtifact']['uncertaintySemantics']['status']=='not-estimated',r
assert r['predictionArtifact']['evidenceBoundary']['isObservedEvidence'] is False,r
binary={'schema':'sc-workspace-neural-model-spec/1.0','modelType':'linear','weights':[[1.0]],'bias':[0.0],'activation':'identity'}
b=service._infer_binary({'modelSpec':binary,'features':[[0.0],[2.0]],'rowIds':['zero','two'],'threshold':0.6})
assert b['predictions'][0]['predictedClass']==0 and b['predictions'][1]['predictedClass']==1,b
multi={'schema':'sc-workspace-neural-model-spec/1.0','modelType':'linear','weights':[[2.0,0.0],[0.0,2.0],[-1.0,-1.0]],'bias':[0.0,0.0,0.0],'activation':'identity'}
m=service._infer_multiclass({'modelSpec':multi,'features':[[2.0,0.0],[0.0,2.0]],'rowIds':['a','b']})
assert [x['predictedClass'] for x in m['predictions']]==[0,1],m
art=m['predictionArtifact']; ins=service._prediction_inspect({'predictionArtifact':art})
assert ins['predictionArtifactFingerprint']==art['artifactFingerprint'],ins
bad=deepcopy(art); bad['predictions'][0]['predictedClass']=2
try:
    service._prediction_inspect({'predictionArtifact':bad})
    raise AssertionError('tampered prediction artifact was accepted')
except HTTPException as exc:
    assert exc.status_code==400 and 'fingerprint verification failed' in str(exc.detail),exc
try:
    service._infer_regression({'modelSpec':lin,'features':[[1.0,1.0]],'targets':[[1.0]]})
    raise AssertionError('inference target boundary was not enforced')
except HTTPException as exc:
    assert exc.status_code==400 and 'do not accept targets' in str(exc.detail),exc
print('NEURAL_V32700_PRESWITCH_INFERENCE_PREDICTION_PROVENANCE=PASS')
PYCODE

echo "=== SWITCH TO v3.27.0 ==="
docker rm -f sc-workspace-backend sc-workspace-worker sc-workspace-neural-runtime >/dev/null 2>&1 || true
docker compose --env-file .env -f docker-compose.yml up -d --no-deps sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker
SWITCHED=1
for i in $(seq 1 60); do
  code="$(curl -sS -o /tmp/scw32700-health.json -w '%{http_code}' http://127.0.0.1:8094/health 2>/dev/null || true)"
  echo "backend health attempt $i: HTTP $code"
  [[ "$code" == 200 ]] && break
  sleep 2
done
python3 - <<'PYCODE'
import json
x=json.load(open('/tmp/scw32700-health.json'))
assert x['ok'] is True and x['version']=='3.27.0',x
assert x.get('neuralRuntimeBoundedOperations')==31,x
assert x.get('neuralInferencePredictionProvenanceRuntime') is True,x
assert x.get('neuralInferenceTargetsAccepted') is False,x
assert x.get('neuralEmbeddingRepresentationRuntime') is True,x
assert x.get('neuralExplainabilityRuntime') is True,x
assert x.get('neuralEvaluationCalibrationUncertaintyRuntime') is True,x
assert x.get('neuralTrainingResumeEnabled') is True,x
print('WORKSPACE_V32700_HEALTH=PASS')
PYCODE

echo "=== DIRECT NEURAL HEALTH ==="
docker exec sc-workspace-neural-runtime python - <<'PYCODE'
import json,urllib.request
x=json.load(urllib.request.urlopen('http://127.0.0.1:8101/health',timeout=5))
assert x['version']=='3.27.0' and len(x['operations'])==31,x
assert x['neuralInferencePredictionProvenanceEnabled'] is True and x['inferenceTargetsAccepted'] is False,x
assert x['acceleratorExecutionEnabled'] is False,x
assert x['runtimeIdentity']=='scworkspace' and x['torchInductorCacheDir']=='/tmp/torchinductor',x
print('NEURAL_V32700_DIRECT_HEALTH=PASS engineVersion='+x['engineVersion'])
PYCODE
SERVICE_TOKEN="$(awk -F= '$1=="SC_WORKSPACE_SERVICE_TOKEN"{sub($1"=","");print;exit}' .env)"
[[ -n "$SERVICE_TOKEN" ]] || fail "SC_WORKSPACE_SERVICE_TOKEN blank"
AUTH=(-H "Authorization: Bearer $SERVICE_TOKEN" -H 'X-SC-User-ID: 1')

echo "=== END-TO-END GOVERNED BINARY INFERENCE JOB ==="
STAMP="$(date +%s)"
cat >/tmp/scw32700-inference-job.json <<JSON
{"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.neural.infer-binary","priority":8,"maxAttempts":1,"idempotencyKey":"deploy-v32700-inference-${STAMP}","payload":{"modelSpec":{"schema":"sc-workspace-neural-model-spec/1.0","modelType":"linear","weights":[[1.0]],"bias":[0.0],"activation":"identity"},"features":[[0.0],[2.0]],"rowIds":["zero","two"],"threshold":0.6}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/scw32700-inference-job.json http://127.0.0.1:8094/v1/jobs >/tmp/scw32700-inference-created.json
JOB_ID="$(python3 -c "import json;print(json.load(open('/tmp/scw32700-inference-created.json'))['item']['jobId'])")"
for i in $(seq 1 45); do
  curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${JOB_ID}" >/tmp/scw32700-inference-state.json
  state="$(python3 -c "import json;print(json.load(open('/tmp/scw32700-inference-state.json'))['item']['status'])")"
  echo "inference job attempt $i: $state"
  [[ "$state" == succeeded ]] && break
  [[ "$state" =~ ^(failed|blocked|cancelled)$ ]] && { cat /tmp/scw32700-inference-state.json; false; }
  sleep 2
done
python3 - <<'PYCODE'
import json
x=json.load(open('/tmp/scw32700-inference-state.json')); item=x.get('item') or {}; jr=x.get('result') or {}; nr=jr['polyglot']['result']['remote']['result']
pa=nr.get('predictionArtifact') or {}; wa=nr.get('workspacePredictionArtifact') or {}; preds=nr.get('predictions') or []
assert item.get('status')=='succeeded',item
assert pa.get('schema')=='sc-workspace-neural-prediction-artifact/1.0' and pa.get('task')=='binary-classification',pa
assert [p.get('predictedClass') for p in preds]==[0,1],preds
assert pa.get('evidenceBoundary',{}).get('isObservedEvidence') is False and pa.get('evidenceBoundary',{}).get('targetsAccepted') is False,pa
assert pa.get('predictionPolicy',{}).get('calibrationStatus')=='not-assessed',pa
assert wa.get('artifactId') and wa.get('sha256') and jr.get('receiptId'),(wa,jr)
open('/tmp/scw32700-prediction-artifact-id.txt','w').write(wa['artifactId'])
open('/tmp/scw32700-prediction-fingerprint.txt','w').write(pa['artifactFingerprint'])
open('/tmp/scw32700-prediction-receipt-id.txt','w').write(jr['receiptId'])
open('/tmp/scw32700-prediction-doc.json','w').write(json.dumps(pa,separators=(',',':')))
print('NEURAL_INFERENCE_JOB=PASS jobId='+item['jobId'])
PYCODE
ARTIFACT_ID="$(cat /tmp/scw32700-prediction-artifact-id.txt)"
curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/artifacts/${ARTIFACT_ID}" >/tmp/scw32700-prediction-artifact.json
python3 - <<'PYCODE'
import base64,json
x=json.load(open('/tmp/scw32700-prediction-artifact.json')); item=x.get('item') or {}; doc=json.loads(base64.b64decode(x['contentBase64'])); expected=open('/tmp/scw32700-prediction-fingerprint.txt').read().strip()
assert item.get('mediaType')=='application/vnd.sc.workspace.neural-prediction+json',item
assert doc.get('artifactFingerprint')==expected and doc.get('schema')=='sc-workspace-neural-prediction-artifact/1.0',doc
assert doc.get('evidenceBoundary',{}).get('isObservedEvidence') is False,doc
print('NEURAL_PREDICTION_WORKSPACE_ARTIFACT=PASS artifactId='+item['artifactId'])
PYCODE
RECEIPT_ID="$(cat /tmp/scw32700-prediction-receipt-id.txt)"
curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/polyglot/receipts/${RECEIPT_ID}" >/tmp/scw32700-prediction-receipt.json
python3 - <<'PYCODE'
import json
x=json.load(open('/tmp/scw32700-prediction-receipt.json')); d=(x.get('item') or {}).get('details') or {}
assert d.get('neuralInferencePredictionProvenance') is True,d
assert d.get('predictionArtifactSchema')=='sc-workspace-neural-prediction-artifact/1.0',d
assert d.get('workspacePredictionArtifactId') and d.get('inferenceDatasetFingerprint'),d
assert d.get('isObservedEvidence') is False and d.get('isEvaluation') is False and d.get('targetsAccepted') is False,d
print('NEURAL_PREDICTION_RECEIPT_LINEAGE=PASS')
PYCODE

echo "=== END-TO-END PREDICTION INSPECTION JOB ==="
python3 - <<'PYCODE'
import json,time
art=json.load(open('/tmp/scw32700-prediction-doc.json'))
req={"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.neural.prediction-inspect","priority":8,"maxAttempts":1,"idempotencyKey":"deploy-v32700-inspect-%d"%int(time.time()),"payload":{"predictionArtifact":art}}
json.dump(req,open('/tmp/scw32700-inspect-job.json','w'),separators=(',',':'))
PYCODE
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/scw32700-inspect-job.json http://127.0.0.1:8094/v1/jobs >/tmp/scw32700-inspect-created.json
IJOB_ID="$(python3 -c "import json;print(json.load(open('/tmp/scw32700-inspect-created.json'))['item']['jobId'])")"
for i in $(seq 1 45); do
  curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${IJOB_ID}" >/tmp/scw32700-inspect-state.json
  state="$(python3 -c "import json;print(json.load(open('/tmp/scw32700-inspect-state.json'))['item']['status'])")"
  echo "prediction inspect attempt $i: $state"
  [[ "$state" == succeeded ]] && break
  [[ "$state" =~ ^(failed|blocked|cancelled)$ ]] && { cat /tmp/scw32700-inspect-state.json; false; }
  sleep 2
done
python3 - <<'PYCODE'
import json
x=json.load(open('/tmp/scw32700-inspect-state.json')); item=x.get('item') or {}; jr=x.get('result') or {}; nr=jr['polyglot']['result']['remote']['result']; expected=open('/tmp/scw32700-prediction-fingerprint.txt').read().strip()
assert item.get('status')=='succeeded',item
assert nr.get('kind')=='neural-prediction-inspection' and nr.get('predictionArtifactFingerprint')==expected,nr
assert nr.get('summary',{}).get('evidenceBoundary',{}).get('isObservedEvidence') is False,nr
print('NEURAL_PREDICTION_INSPECT_JOB=PASS jobId='+item['jobId'])
PYCODE

echo "=== OPENAPI / RUNTIME REGISTRY ==="
docker exec -i sc-workspace-backend python3 - <<'PYCODE'
from app.main import app
from app.client_contracts import TYPED_ENDPOINTS,profile
from app.polyglot import RUNTIME_BY_LANGUAGE
x=profile(app.openapi())
assert x['workspaceVersion']=='3.27.0' and x['typedEndpointCount']==291 and not x['missingOpenApiOperations'],x
n=RUNTIME_BY_LANGUAGE['neural']; assert len(n.operations)==31,n
for op in ['workspace.neural.infer-regression','workspace.neural.infer-binary','workspace.neural.infer-multiclass','workspace.neural.prediction-inspect']:
    assert op in n.operations,(op,n)
assert RUNTIME_BY_LANGUAGE['ml'].runtime=='python-sklearn-predictive'
print('WORKSPACE_V32700_OPENAPI_RUNTIME_REGISTRY=PASS typed_endpoints=%d'%len(TYPED_ENDPOINTS))
PYCODE

echo "=== CONTAINER HARDENING ==="
python3 - <<'PYCODE'
import json,subprocess
d=json.loads(subprocess.check_output(['docker','inspect','sc-workspace-neural-runtime']))[0]; h=d['HostConfig']; c=d['Config']
assert h['ReadonlyRootfs'] is True and c.get('User')=='65532:65532',d
assert 'ALL' in (h.get('CapDrop') or []) and 'no-new-privileges:true' in (h.get('SecurityOpt') or []),d
print('NEURAL_RUNTIME_HARDENING=PASS')
PYCODE

echo "PASS: Workspace v3.27.0 backend deployed; governed neural inference, persisted predictions, prediction inspection, receipt provenance, evidence boundaries, and hardening verified"
trap - ERR
