#!/usr/bin/env bash
set -Eeuo pipefail
PACKAGE="${1:-/tmp/sustainable-catalyst-workspace-backend-v3.28.0.zip}"
BASE="/opt/sustainable-catalyst"
OLD="$BASE/sustainable-catalyst-workspace-backend-v3.27.0"
NEW="$BASE/sustainable-catalyst-workspace-backend-v3.28.0"
SWITCHED=0
fail(){ echo "ERROR: $*" >&2; exit 1; }
rollback(){
  local code=$?
  if [[ "$SWITCHED" == 1 ]]; then
    echo "=== v3.28.0 verification failed; restoring v3.27.0 ===" >&2
    docker rm -f sc-workspace-backend sc-workspace-worker sc-workspace-neural-runtime >/dev/null 2>&1 || true
    if [[ -d "$OLD" ]]; then
      cd "$OLD"; [[ -f docker-compose.yml ]] || cp docker-compose.example.yml docker-compose.yml
      docker compose --env-file .env -f docker-compose.yml up -d --no-deps --no-build sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker || true
    fi
  fi
  exit "$code"
}
trap rollback ERR
[[ -f "$PACKAGE" ]] || fail "backend package not found: $PACKAGE"
[[ -d "$OLD" && -f "$OLD/.env" ]] || fail "Workspace v3.27.0 production baseline not found at $OLD"
TMP="$(mktemp -d)"; cleanup(){ rm -rf "$TMP"; }; trap cleanup EXIT
unzip -q "$PACKAGE" -d "$TMP/package"
[[ -f "$TMP/package/app/config.py" && -f "$TMP/package/neural-runtime/service.py" && -f "$TMP/package/docker-compose.example.yml" ]] || fail "malformed v3.28.0 backend package"
grep -q 'service_version: str = "3.28.0"' "$TMP/package/app/config.py" || fail "v3.28.0 backend version marker missing"
grep -q 'SERVICE_VERSION = "3.28.0"' "$TMP/package/neural-runtime/service.py" || fail "v3.28.0 neural version marker missing"
for op in workspace.neural.package-create workspace.neural.package-verify workspace.neural.package-inspect workspace.neural.package-infer; do
  grep -q "$op" "$TMP/package/neural-runtime/service.py" || fail "model package operation missing: $op"
done
grep -q 'MODEL_PACKAGE_SCHEMA = "sc-workspace-neural-model-package/1.0"' "$TMP/package/neural-runtime/service.py" || fail "model package schema missing"
grep -q 'application/vnd.sc.workspace.neural-model-package+json' "$TMP/package/app/polyglot.py" || fail "Workspace model package persistence missing"
grep -q '^numpy==2.2.6$' "$TMP/package/neural-runtime/requirements.txt" || fail "NumPy pin missing"
grep -q '^torch==2.10.0$' "$TMP/package/neural-runtime/requirements.txt" || fail "PyTorch pin missing"
rm -rf "$NEW"; mkdir -p "$NEW"; cp -a "$TMP/package/." "$NEW/"; cp "$OLD/.env" "$NEW/.env"
cd "$NEW"; cp docker-compose.example.yml docker-compose.yml
python3 -m compileall -q app neural-runtime

echo "=== BUILD WORKSPACE v3.28.0 ==="
docker compose --env-file .env -f docker-compose.yml build sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker

echo "=== PRE-SWITCH HARDENED REPRODUCIBLE MODEL PACKAGE CERTIFICATION ==="
docker compose --env-file .env -f docker-compose.yml run --rm --no-deps --entrypoint python sc-workspace-neural-runtime - <<'PYCODE'
from copy import deepcopy
from fastapi import HTTPException
import service
h=service.health()
assert h['version']=='3.28.0' and len(h['operations'])==35,h
assert h['reproducibleModelPackagesEnabled'] is True,h
assert h['modelPackageSchema']=='sc-workspace-neural-model-package/1.0',h
assert h['modelPackageDependencyPins']=={'torch':'2.10.0','numpy':'2.2.6'},h
assert h['runtimeIdentity']=='scworkspace' and h['runtimeHome']=='/tmp',h
model={'schema':'sc-workspace-neural-model-spec/1.0','modelType':'linear','weights':[[1.0]],'bias':[0.0],'activation':'identity'}
created=service._model_package_create({'modelSpec':model,'task':'binary-classification','featureNames':['signal'],'threshold':0.6})
pkg=created['modelPackage']
assert pkg['portable'] is True and pkg['manifest']['containsArbitraryCode'] is False,pkg
ver=service._model_package_verify({'modelPackage':pkg}); assert ver['valid'] is True and ver['compatible'] is True,ver
ins=service._model_package_inspect({'modelPackage':pkg}); assert ins['inputFeatures']==1 and ins['featureNames']==['signal'],ins
pred=service._model_package_infer({'modelPackage':pkg,'features':[[0.0],[2.0]],'rowIds':['zero','two']})
assert [x['predictedClass'] for x in pred['predictions']]==[0,1],pred
pa=pred['predictionArtifact']; assert pa['sourceModelPackageFingerprint']==pkg['artifactFingerprint'],pa
service._prediction_inspect({'predictionArtifact':pa})
bad=deepcopy(pkg); bad['modelSpec']['weights'][0][0]=9.0
try:
    service._model_package_verify({'modelPackage':bad})
    raise AssertionError('tampered model package accepted')
except HTTPException as exc:
    assert exc.status_code==400 and 'fingerprint verification failed' in str(exc.detail),exc
try:
    service._model_package_infer({'modelPackage':pkg,'features':[[1.0]],'targets':[[1.0]]})
    raise AssertionError('packaged inference target boundary not enforced')
except HTTPException as exc:
    assert exc.status_code==400 and 'does not accept targets' in str(exc.detail),exc
print('NEURAL_V32800_PRESWITCH_REPRODUCIBLE_MODEL_PACKAGES=PASS')
PYCODE

echo "=== SWITCH TO v3.28.0 ==="
docker rm -f sc-workspace-backend sc-workspace-worker sc-workspace-neural-runtime >/dev/null 2>&1 || true
docker compose --env-file .env -f docker-compose.yml up -d --no-deps sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker
SWITCHED=1
for i in $(seq 1 60); do
  code="$(curl -sS -o /tmp/scw32800-health.json -w '%{http_code}' http://127.0.0.1:8094/health 2>/dev/null || true)"
  echo "backend health attempt $i: HTTP $code"; [[ "$code" == 200 ]] && break; sleep 2
done
python3 - <<'PYCODE'
import json
x=json.load(open('/tmp/scw32800-health.json'))
assert x['ok'] is True and x['version']=='3.28.0',x
assert x.get('neuralRuntimeBoundedOperations')==35,x
assert x.get('neuralReproducibleModelPackagesRuntime') is True,x
assert x.get('neuralModelPackageWorkspaceArtifactPersistence') is True,x
assert x.get('neuralInferencePredictionProvenanceRuntime') is True,x
print('WORKSPACE_V32800_HEALTH=PASS')
PYCODE

echo "=== DIRECT NEURAL HEALTH ==="
docker exec sc-workspace-neural-runtime python - <<'PYCODE'
import json,urllib.request
x=json.load(urllib.request.urlopen('http://127.0.0.1:8101/health',timeout=5))
assert x['version']=='3.28.0' and len(x['operations'])==35,x
assert x['reproducibleModelPackagesEnabled'] is True,x
assert x['modelPackageArbitraryCodeAllowed'] is False and x['modelPackageSerializedPyTorchAllowed'] is False,x
assert x['acceleratorExecutionEnabled'] is False,x
assert x['runtimeIdentity']=='scworkspace' and x['torchInductorCacheDir']=='/tmp/torchinductor',x
print('NEURAL_V32800_DIRECT_HEALTH=PASS engineVersion='+x['engineVersion'])
PYCODE
SERVICE_TOKEN="$(awk -F= '$1=="SC_WORKSPACE_SERVICE_TOKEN"{sub($1"=","");print;exit}' .env)"
[[ -n "$SERVICE_TOKEN" ]] || fail "SC_WORKSPACE_SERVICE_TOKEN blank"
AUTH=(-H "Authorization: Bearer $SERVICE_TOKEN" -H 'X-SC-User-ID: 1')

wait_job(){
  local id="$1" out="$2" label="$3"
  for i in $(seq 1 45); do
    curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${id}" >"$out"
    state="$(python3 -c "import json;print(json.load(open('$out'))['item']['status'])")"
    echo "$label attempt $i: $state"
    [[ "$state" == succeeded ]] && return 0
    [[ "$state" =~ ^(failed|blocked|cancelled)$ ]] && { cat "$out"; return 1; }
    sleep 2
  done
  return 1
}

echo "=== END-TO-END MODEL PACKAGE CREATION ==="
STAMP="$(date +%s)"
cat >/tmp/scw32800-package-job.json <<JSON
{"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.neural.package-create","priority":8,"maxAttempts":1,"idempotencyKey":"deploy-v32800-package-${STAMP}","payload":{"modelSpec":{"schema":"sc-workspace-neural-model-spec/1.0","modelType":"linear","weights":[[1.0]],"bias":[0.0],"activation":"identity"},"task":"binary-classification","featureNames":["signal"],"threshold":0.6}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/scw32800-package-job.json http://127.0.0.1:8094/v1/jobs >/tmp/scw32800-package-created.json
PJOB_ID="$(python3 -c "import json;print(json.load(open('/tmp/scw32800-package-created.json'))['item']['jobId'])")"
wait_job "$PJOB_ID" /tmp/scw32800-package-state.json "package job"
python3 - <<'PYCODE'
import json
x=json.load(open('/tmp/scw32800-package-state.json')); item=x.get('item') or {}; jr=x.get('result') or {}; nr=jr['polyglot']['result']['remote']['result']
pkg=nr.get('modelPackage') or {}; wa=nr.get('workspaceModelPackageArtifact') or {}
assert item.get('status')=='succeeded',item
assert pkg.get('schema')=='sc-workspace-neural-model-package/1.0' and pkg.get('portable') is True,pkg
assert pkg.get('manifest',{}).get('containsArbitraryCode') is False,pkg
assert wa.get('artifactId') and wa.get('sha256') and jr.get('receiptId'),(wa,jr)
open('/tmp/scw32800-package-artifact-id.txt','w').write(wa['artifactId'])
open('/tmp/scw32800-package-fingerprint.txt','w').write(pkg['artifactFingerprint'])
open('/tmp/scw32800-package-receipt-id.txt','w').write(jr['receiptId'])
open('/tmp/scw32800-package-doc.json','w').write(json.dumps(pkg,separators=(',',':')))
print('NEURAL_MODEL_PACKAGE_JOB=PASS jobId='+item['jobId'])
PYCODE
PACKAGE_ARTIFACT_ID="$(cat /tmp/scw32800-package-artifact-id.txt)"
curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/artifacts/${PACKAGE_ARTIFACT_ID}" >/tmp/scw32800-package-artifact.json
python3 - <<'PYCODE'
import base64,json
x=json.load(open('/tmp/scw32800-package-artifact.json')); item=x.get('item') or {}; doc=json.loads(base64.b64decode(x['contentBase64'])); expected=open('/tmp/scw32800-package-fingerprint.txt').read().strip()
assert item.get('mediaType')=='application/vnd.sc.workspace.neural-model-package+json',item
assert doc.get('artifactFingerprint')==expected and doc.get('schema')=='sc-workspace-neural-model-package/1.0',doc
print('NEURAL_MODEL_PACKAGE_WORKSPACE_ARTIFACT=PASS artifactId='+item['artifactId'])
PYCODE
PACKAGE_RECEIPT_ID="$(cat /tmp/scw32800-package-receipt-id.txt)"
curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/polyglot/receipts/${PACKAGE_RECEIPT_ID}" >/tmp/scw32800-package-receipt.json
python3 - <<'PYCODE'
import json
x=json.load(open('/tmp/scw32800-package-receipt.json')); d=(x.get('item') or {}).get('details') or {}
assert d.get('neuralReproducibleModelPackage') is True,d
assert d.get('modelPackageSchema')=='sc-workspace-neural-model-package/1.0',d
assert d.get('workspaceModelPackageArtifactId') and d.get('runtimeContractFingerprint') and d.get('inferenceContractFingerprint'),d
assert d.get('containsArbitraryCode') is False,d
print('NEURAL_MODEL_PACKAGE_RECEIPT_LINEAGE=PASS')
PYCODE

echo "=== END-TO-END PACKAGED INFERENCE ==="
python3 - <<'PYCODE'
import json,time
pkg=json.load(open('/tmp/scw32800-package-doc.json'))
req={"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.neural.package-infer","priority":8,"maxAttempts":1,"idempotencyKey":"deploy-v32800-package-infer-%d"%int(time.time()),"payload":{"modelPackage":pkg,"features":[[0.0],[2.0]],"rowIds":["zero","two"]}}
json.dump(req,open('/tmp/scw32800-package-infer-job.json','w'),separators=(',',':'))
PYCODE
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/scw32800-package-infer-job.json http://127.0.0.1:8094/v1/jobs >/tmp/scw32800-package-infer-created.json
IJOB_ID="$(python3 -c "import json;print(json.load(open('/tmp/scw32800-package-infer-created.json'))['item']['jobId'])")"
wait_job "$IJOB_ID" /tmp/scw32800-package-infer-state.json "package inference"
python3 - <<'PYCODE'
import json
x=json.load(open('/tmp/scw32800-package-infer-state.json')); item=x.get('item') or {}; jr=x.get('result') or {}; nr=jr['polyglot']['result']['remote']['result']; pa=nr.get('predictionArtifact') or {}; wa=nr.get('workspacePredictionArtifact') or {}; expected=open('/tmp/scw32800-package-fingerprint.txt').read().strip()
assert item.get('status')=='succeeded',item
assert [p.get('predictedClass') for p in nr.get('predictions',[])]==[0,1],nr
assert pa.get('sourceModelPackageFingerprint')==expected,pa
assert wa.get('artifactId') and wa.get('sha256') and jr.get('receiptId'),(wa,jr)
assert pa.get('evidenceBoundary',{}).get('isObservedEvidence') is False,pa
open('/tmp/scw32800-package-infer-receipt-id.txt','w').write(jr['receiptId'])
print('NEURAL_PACKAGED_INFERENCE_JOB=PASS jobId='+item['jobId'])
PYCODE
INFER_RECEIPT_ID="$(cat /tmp/scw32800-package-infer-receipt-id.txt)"
curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/polyglot/receipts/${INFER_RECEIPT_ID}" >/tmp/scw32800-package-infer-receipt.json
python3 - <<'PYCODE'
import json
x=json.load(open('/tmp/scw32800-package-infer-receipt.json')); d=(x.get('item') or {}).get('details') or {}; expected=open('/tmp/scw32800-package-fingerprint.txt').read().strip()
assert d.get('neuralInferencePredictionProvenance') is True and d.get('packagedInference') is True,d
assert d.get('sourceModelPackageFingerprint')==expected,d
assert d.get('workspacePredictionArtifactId'),d
print('NEURAL_PACKAGED_INFERENCE_RECEIPT_LINEAGE=PASS')
PYCODE

echo "=== OPENAPI / RUNTIME REGISTRY ==="
docker exec -i sc-workspace-backend python3 - <<'PYCODE'
from app.main import app
from app.client_contracts import TYPED_ENDPOINTS,profile
from app.polyglot import RUNTIME_BY_LANGUAGE
x=profile(app.openapi())
assert x['workspaceVersion']=='3.28.0' and x['typedEndpointCount']==291 and not x['missingOpenApiOperations'],x
n=RUNTIME_BY_LANGUAGE['neural']; assert len(n.operations)==35,n
for op in ['workspace.neural.package-create','workspace.neural.package-verify','workspace.neural.package-inspect','workspace.neural.package-infer']:
    assert op in n.operations,(op,n)
assert RUNTIME_BY_LANGUAGE['ml'].runtime=='python-sklearn-predictive'
print('WORKSPACE_V32800_OPENAPI_RUNTIME_REGISTRY=PASS typed_endpoints=%d'%len(TYPED_ENDPOINTS))
PYCODE

echo "=== CONTAINER HARDENING ==="
python3 - <<'PYCODE'
import json,subprocess
d=json.loads(subprocess.check_output(['docker','inspect','sc-workspace-neural-runtime']))[0]; h=d['HostConfig']; c=d['Config']
assert h['ReadonlyRootfs'] is True and c.get('User')=='65532:65532',d
assert 'ALL' in (h.get('CapDrop') or []) and 'no-new-privileges:true' in (h.get('SecurityOpt') or []),d
print('NEURAL_RUNTIME_HARDENING=PASS')
PYCODE

echo "PASS: Workspace v3.28.0 backend deployed; reproducible neural model packages, persisted package artifacts, packaged inference, receipt lineage, and hardening verified"
trap - ERR
