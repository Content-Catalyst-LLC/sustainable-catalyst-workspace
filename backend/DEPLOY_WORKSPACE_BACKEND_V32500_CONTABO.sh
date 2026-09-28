#!/usr/bin/env bash
set -Eeuo pipefail
PACKAGE="${1:-/tmp/sustainable-catalyst-workspace-backend-v3.25.0.zip}"
BASE="/opt/sustainable-catalyst"
OLD="$BASE/sustainable-catalyst-workspace-backend-v3.24.0"
NEW="$BASE/sustainable-catalyst-workspace-backend-v3.25.0"
SWITCHED=0
fail(){ echo "ERROR: $*" >&2; exit 1; }
rollback(){
  local code=$?
  if [[ "$SWITCHED" == 1 ]]; then
    echo "=== v3.25.0 verification failed; restoring v3.24.0 ===" >&2
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
[[ -d "$OLD" && -f "$OLD/.env" ]] || fail "Workspace v3.24.0 production baseline not found at $OLD"
TMP="$(mktemp -d)"; cleanup(){ rm -rf "$TMP"; }; trap cleanup EXIT
unzip -q "$PACKAGE" -d "$TMP/package"
[[ -f "$TMP/package/app/config.py" && -f "$TMP/package/neural-runtime/service.py" && -f "$TMP/package/docker-compose.example.yml" ]] || fail "malformed v3.25.0 backend package"
grep -q 'service_version: str = "3.25.0"' "$TMP/package/app/config.py" || fail "v3.25.0 backend version marker missing"
grep -q 'SERVICE_VERSION = "3.25.0"' "$TMP/package/neural-runtime/service.py" || fail "v3.25.0 neural version marker missing"
for op in workspace.neural.explain-gradient workspace.neural.explain-integrated-gradients workspace.neural.explain-occlusion workspace.neural.explain-global-sensitivity; do
  grep -q "$op" "$TMP/package/neural-runtime/service.py" || fail "explainability operation missing: $op"
done
grep -q 'EXPLAINABILITY_ARTIFACT_SCHEMA = "sc-workspace-neural-explainability-artifact/1.0"' "$TMP/package/neural-runtime/service.py" || fail "explainability artifact schema missing"
grep -q 'application/vnd.sc.workspace.neural-explainability+json' "$TMP/package/app/polyglot.py" || fail "Workspace explainability artifact persistence missing"
grep -q '^numpy==2.2.6$' "$TMP/package/neural-runtime/requirements.txt" || fail "NumPy pin missing"
grep -q '^torch==2.10.0$' "$TMP/package/neural-runtime/requirements.txt" || fail "PyTorch pin missing"
rm -rf "$NEW"; mkdir -p "$NEW"; cp -a "$TMP/package/." "$NEW/"; cp "$OLD/.env" "$NEW/.env"
cd "$NEW"; cp docker-compose.example.yml docker-compose.yml
python3 -m compileall -q app neural-runtime

echo "=== BUILD WORKSPACE v3.25.0 ==="
docker compose --env-file .env -f docker-compose.yml build sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker

echo "=== PRE-SWITCH HARDENED NEURAL EXPLAINABILITY CERTIFICATION ==="
docker compose --env-file .env -f docker-compose.yml run --rm --no-deps --entrypoint python sc-workspace-neural-runtime - <<'PY'
import service
h=service.health()
assert h['version']=='3.25.0',h
assert len(h['operations'])==23,h
assert h['explainabilityRuntimeEnabled'] is True,h
assert h['explainabilityArtifactSchema']=='sc-workspace-neural-explainability-artifact/1.0',h
assert h['runtimeIdentity']=='scworkspace' and h['runtimeHome']=='/tmp',h
model={'schema':'sc-workspace-neural-model-spec/1.0','modelType':'linear','weights':[[2.0,3.0]],'bias':[1.0],'activation':'identity'}
base={'modelSpec':model,'features':[[1.0,2.0]],'task':'regression','featureNames':['a','b']}
g=service._explain_gradient(base)
assert g['attributions']==[[2.0,3.0]],g
ig=service._explain_integrated_gradients({**base,'steps':32})
a=ig['attributions'][0]
assert abs(a[0]-2.0)<1e-6 and abs(a[1]-6.0)<1e-6,ig
assert abs(ig['completenessDelta'][0])<1e-5,ig
oc=service._explain_occlusion(base)
assert oc['explainabilityArtifact']['schema']=='sc-workspace-neural-explainability-artifact/1.0',oc
sens=service._explain_global_sensitivity({**base,'features':[[1.0,2.0],[3.0,4.0]]})
assert sens['sensitivity'][0]['featureName']=='b',sens
print('NEURAL_V32500_PRESWITCH_EXPLAINABILITY=PASS')
PY

echo "=== SWITCH TO v3.25.0 ==="
docker rm -f sc-workspace-backend sc-workspace-worker sc-workspace-neural-runtime >/dev/null 2>&1 || true
docker compose --env-file .env -f docker-compose.yml up -d --no-deps sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker
SWITCHED=1
for i in $(seq 1 60); do
  code="$(curl -sS -o /tmp/scw32500-health.json -w '%{http_code}' http://127.0.0.1:8094/health 2>/dev/null || true)"
  echo "backend health attempt $i: HTTP $code"
  [[ "$code" == 200 ]] && break
  sleep 2
done
python3 - <<'PY'
import json
x=json.load(open('/tmp/scw32500-health.json'))
assert x['ok'] is True and x['version']=='3.25.0',x
assert x.get('neuralRuntimeBoundedOperations')==23,x
assert x.get('neuralExplainabilityRuntime') is True,x
assert x.get('neuralEvaluationCalibrationUncertaintyRuntime') is True,x
assert x.get('neuralTrainingResumeEnabled') is True,x
print('WORKSPACE_V32500_HEALTH=PASS')
PY

echo "=== DIRECT NEURAL HEALTH ==="
docker exec sc-workspace-neural-runtime python - <<'PY'
import json,urllib.request
x=json.load(urllib.request.urlopen('http://127.0.0.1:8101/health',timeout=5))
assert x['version']=='3.25.0' and len(x['operations'])==23,x
assert x['explainabilityRuntimeEnabled'] is True and x['acceleratorExecutionEnabled'] is False,x
assert x['runtimeIdentity']=='scworkspace' and x['torchInductorCacheDir']=='/tmp/torchinductor',x
print('NEURAL_V32500_DIRECT_HEALTH=PASS engineVersion='+x['engineVersion'])
PY
SERVICE_TOKEN="$(awk -F= '$1=="SC_WORKSPACE_SERVICE_TOKEN"{sub($1"=","");print;exit}' .env)"
[[ -n "$SERVICE_TOKEN" ]] || fail "SC_WORKSPACE_SERVICE_TOKEN blank"
AUTH=(-H "Authorization: Bearer $SERVICE_TOKEN" -H 'X-SC-User-ID: 1')

echo "=== END-TO-END INTEGRATED-GRADIENTS ARTIFACT JOB ==="
STAMP="$(date +%s)"
cat >/tmp/scw32500-explain-job.json <<JSON
{"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.neural.explain-integrated-gradients","priority":8,"maxAttempts":1,"idempotencyKey":"deploy-v32500-explain-${STAMP}","payload":{"modelSpec":{"schema":"sc-workspace-neural-model-spec/1.0","modelType":"linear","weights":[[2.0,3.0]],"bias":[1.0],"activation":"identity"},"features":[[1.0,2.0]],"task":"regression","featureNames":["a","b"],"steps":32}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/scw32500-explain-job.json http://127.0.0.1:8094/v1/jobs >/tmp/scw32500-explain-created.json
JOB_ID="$(python3 -c "import json;print(json.load(open('/tmp/scw32500-explain-created.json'))['item']['jobId'])")"
for i in $(seq 1 45); do
  curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${JOB_ID}" >/tmp/scw32500-explain-state.json
  state="$(python3 -c "import json;print(json.load(open('/tmp/scw32500-explain-state.json'))['item']['status'])")"
  echo "explainability job attempt $i: $state"
  [[ "$state" == succeeded ]] && break
  [[ "$state" =~ ^(failed|blocked|cancelled)$ ]] && { cat /tmp/scw32500-explain-state.json; false; }
  sleep 2
done
python3 - <<'PY'
import json
x=json.load(open('/tmp/scw32500-explain-state.json'))
item=x.get('item') or {}; jr=x.get('result') or {}; nr=jr['polyglot']['result']['remote']['result']
ea=nr.get('explainabilityArtifact') or {}; wa=nr.get('workspaceAnalysisArtifact') or {}
assert item.get('status')=='succeeded',item
a=nr['attributions'][0]
assert abs(a[0]-2.0)<1e-6 and abs(a[1]-6.0)<1e-6,nr
assert ea.get('schema')=='sc-workspace-neural-explainability-artifact/1.0' and ea.get('method')=='integrated-gradients',ea
assert wa.get('artifactId') and wa.get('sha256') and jr.get('receiptId'),(wa,jr)
open('/tmp/scw32500-analysis-artifact-id.txt','w').write(wa['artifactId'])
open('/tmp/scw32500-analysis-fingerprint.txt','w').write(ea['artifactFingerprint'])
open('/tmp/scw32500-receipt-id.txt','w').write(jr['receiptId'])
print('NEURAL_EXPLAINABILITY_JOB=PASS jobId='+item['jobId'])
PY
ARTIFACT_ID="$(cat /tmp/scw32500-analysis-artifact-id.txt)"
curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/artifacts/${ARTIFACT_ID}" >/tmp/scw32500-analysis-artifact.json
python3 - <<'PY'
import base64,json
x=json.load(open('/tmp/scw32500-analysis-artifact.json'))
item=x.get('item') or {}; doc=json.loads(base64.b64decode(x['contentBase64'])); expected=open('/tmp/scw32500-analysis-fingerprint.txt').read().strip()
assert item.get('mediaType')=='application/vnd.sc.workspace.neural-explainability+json',item
assert doc.get('artifactFingerprint')==expected and doc.get('method')=='integrated-gradients',doc
print('NEURAL_EXPLAINABILITY_WORKSPACE_ARTIFACT=PASS artifactId='+item['artifactId'])
PY
RECEIPT_ID="$(cat /tmp/scw32500-receipt-id.txt)"
curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/polyglot/receipts/${RECEIPT_ID}" >/tmp/scw32500-receipt.json
python3 - <<'PY'
import json
x=json.load(open('/tmp/scw32500-receipt.json'))
d=(x.get('item') or {}).get('details') or {}
assert d.get('neuralExplainability') is True,d
assert d.get('explainabilityMethod')=='integrated-gradients',d
assert d.get('workspaceAnalysisArtifactId') and d.get('explanationDatasetFingerprint'),d
print('NEURAL_EXPLAINABILITY_RECEIPT_LINEAGE=PASS')
PY

echo "=== OPENAPI / RUNTIME REGISTRY ==="
docker exec -i sc-workspace-backend python3 - <<'PY'
from app.main import app
from app.client_contracts import TYPED_ENDPOINTS,profile
from app.polyglot import RUNTIME_BY_LANGUAGE
x=profile(app.openapi())
assert x['workspaceVersion']=='3.25.0' and x['typedEndpointCount']==291 and not x['missingOpenApiOperations'],x
n=RUNTIME_BY_LANGUAGE['neural']; assert len(n.operations)==23,n
for op in ['workspace.neural.explain-gradient','workspace.neural.explain-integrated-gradients','workspace.neural.explain-occlusion','workspace.neural.explain-global-sensitivity']:
    assert op in n.operations,(op,n)
assert RUNTIME_BY_LANGUAGE['ml'].runtime=='python-sklearn-predictive'
print('WORKSPACE_V32500_OPENAPI_RUNTIME_REGISTRY=PASS typed_endpoints=%d'%len(TYPED_ENDPOINTS))
PY

echo "=== CONTAINER HARDENING ==="
python3 - <<'PY'
import json,subprocess
d=json.loads(subprocess.check_output(['docker','inspect','sc-workspace-neural-runtime']))[0]; h=d['HostConfig']; c=d['Config']
assert h['ReadonlyRootfs'] is True and c.get('User')=='65532:65532',d
assert 'ALL' in (h.get('CapDrop') or []) and 'no-new-privileges:true' in (h.get('SecurityOpt') or []),d
print('NEURAL_RUNTIME_HARDENING=PASS')
PY

echo "PASS: Workspace v3.25.0 backend deployed; governed neural explainability compute, artifact persistence, receipt lineage, and hardening verified"
trap - ERR
