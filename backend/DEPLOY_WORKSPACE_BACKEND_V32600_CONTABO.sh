#!/usr/bin/env bash
set -Eeuo pipefail
PACKAGE="${1:-/tmp/sustainable-catalyst-workspace-backend-v3.26.0.zip}"
BASE="/opt/sustainable-catalyst"
OLD="$BASE/sustainable-catalyst-workspace-backend-v3.25.0"
NEW="$BASE/sustainable-catalyst-workspace-backend-v3.26.0"
SWITCHED=0
fail(){ echo "ERROR: $*" >&2; exit 1; }
rollback(){
  local code=$?
  if [[ "$SWITCHED" == 1 ]]; then
    echo "=== v3.26.0 verification failed; restoring v3.25.0 ===" >&2
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
[[ -d "$OLD" && -f "$OLD/.env" ]] || fail "Workspace v3.25.0 production baseline not found at $OLD"
TMP="$(mktemp -d)"; cleanup(){ rm -rf "$TMP"; }; trap cleanup EXIT
unzip -q "$PACKAGE" -d "$TMP/package"
[[ -f "$TMP/package/app/config.py" && -f "$TMP/package/neural-runtime/service.py" && -f "$TMP/package/docker-compose.example.yml" ]] || fail "malformed v3.26.0 backend package"
grep -q 'service_version: str = "3.26.0"' "$TMP/package/app/config.py" || fail "v3.26.0 backend version marker missing"
grep -q 'SERVICE_VERSION = "3.26.0"' "$TMP/package/neural-runtime/service.py" || fail "v3.26.0 neural version marker missing"
for op in workspace.neural.embedding-generate workspace.neural.representation-summary workspace.neural.embedding-similarity workspace.neural.embedding-neighbors; do
  grep -q "$op" "$TMP/package/neural-runtime/service.py" || fail "embedding/representation operation missing: $op"
done
grep -q 'EMBEDDING_ARTIFACT_SCHEMA = "sc-workspace-neural-embedding-artifact/1.0"' "$TMP/package/neural-runtime/service.py" || fail "embedding artifact schema missing"
grep -q 'REPRESENTATION_ANALYSIS_ARTIFACT_SCHEMA = "sc-workspace-neural-representation-analysis-artifact/1.0"' "$TMP/package/neural-runtime/service.py" || fail "representation analysis artifact schema missing"
grep -q 'application/vnd.sc.workspace.neural-embedding+json' "$TMP/package/app/polyglot.py" || fail "Workspace embedding artifact persistence missing"
grep -q 'application/vnd.sc.workspace.neural-representation+json' "$TMP/package/app/polyglot.py" || fail "Workspace representation artifact persistence missing"
grep -q '^numpy==2.2.6$' "$TMP/package/neural-runtime/requirements.txt" || fail "NumPy pin missing"
grep -q '^torch==2.10.0$' "$TMP/package/neural-runtime/requirements.txt" || fail "PyTorch pin missing"
rm -rf "$NEW"; mkdir -p "$NEW"; cp -a "$TMP/package/." "$NEW/"; cp "$OLD/.env" "$NEW/.env"
cd "$NEW"; cp docker-compose.example.yml docker-compose.yml
python3 -m compileall -q app neural-runtime

echo "=== BUILD WORKSPACE v3.26.0 ==="
docker compose --env-file .env -f docker-compose.yml build sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker

echo "=== PRE-SWITCH HARDENED EMBEDDING / REPRESENTATION CERTIFICATION ==="
docker compose --env-file .env -f docker-compose.yml run --rm --no-deps --entrypoint python sc-workspace-neural-runtime - <<'PYCODE'
import service
h=service.health()
assert h['version']=='3.26.0',h
assert len(h['operations'])==27,h
assert h['embeddingRepresentationRuntimeEnabled'] is True,h
assert h['embeddingArtifactSchema']=='sc-workspace-neural-embedding-artifact/1.0',h
assert h['representationAnalysisArtifactSchema']=='sc-workspace-neural-representation-analysis-artifact/1.0',h
assert h['runtimeIdentity']=='scworkspace' and h['runtimeHome']=='/tmp',h
model={'schema':'sc-workspace-neural-model-spec/1.0','modelType':'mlp','layers':[
 {'weights':[[1.0,0.0],[0.0,1.0]],'bias':[0.0,0.0],'activation':'relu'},
 {'weights':[[1.0,1.0]],'bias':[0.0],'activation':'identity'}]}
e=service._embedding_generate({'modelSpec':model,'features':[[1.0,2.0],[-1.0,3.0]],'representation':'penultimate','rowIds':['r1','r2']})
assert e['vectors']==[[1.0,2.0],[0.0,3.0]],e
art=e['embeddingArtifact']
assert art['schema']=='sc-workspace-neural-embedding-artifact/1.0' and len(art['artifactFingerprint'])==64,art
sm=service._representation_summary({'embeddingArtifact':art})
assert sm['summary']['centroid']==[0.5,2.5],sm
si=service._embedding_similarity({'embeddingArtifact':art,'metric':'cosine','pairs':[[0,1]]})
assert 0.89 < si['pairs'][0]['similarity'] < 0.90,si
nn=service._embedding_neighbors({'embeddingArtifact':art,'metric':'cosine','queryIndices':[0],'k':1})
assert nn['queries'][0]['neighbors'][0]['rowId']=='r2',nn
print('NEURAL_V32600_PRESWITCH_EMBEDDING_REPRESENTATION=PASS')
PYCODE

echo "=== SWITCH TO v3.26.0 ==="
docker rm -f sc-workspace-backend sc-workspace-worker sc-workspace-neural-runtime >/dev/null 2>&1 || true
docker compose --env-file .env -f docker-compose.yml up -d --no-deps sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker
SWITCHED=1
for i in $(seq 1 60); do
  code="$(curl -sS -o /tmp/scw32600-health.json -w '%{http_code}' http://127.0.0.1:8094/health 2>/dev/null || true)"
  echo "backend health attempt $i: HTTP $code"
  [[ "$code" == 200 ]] && break
  sleep 2
done
python3 - <<'PYCODE'
import json
x=json.load(open('/tmp/scw32600-health.json'))
assert x['ok'] is True and x['version']=='3.26.0',x
assert x.get('neuralRuntimeBoundedOperations')==27,x
assert x.get('neuralEmbeddingRepresentationRuntime') is True,x
assert x.get('neuralExplainabilityRuntime') is True,x
assert x.get('neuralEvaluationCalibrationUncertaintyRuntime') is True,x
assert x.get('neuralTrainingResumeEnabled') is True,x
print('WORKSPACE_V32600_HEALTH=PASS')
PYCODE

echo "=== DIRECT NEURAL HEALTH ==="
docker exec sc-workspace-neural-runtime python - <<'PYCODE'
import json,urllib.request
x=json.load(urllib.request.urlopen('http://127.0.0.1:8101/health',timeout=5))
assert x['version']=='3.26.0' and len(x['operations'])==27,x
assert x['embeddingRepresentationRuntimeEnabled'] is True and x['acceleratorExecutionEnabled'] is False,x
assert x['runtimeIdentity']=='scworkspace' and x['torchInductorCacheDir']=='/tmp/torchinductor',x
print('NEURAL_V32600_DIRECT_HEALTH=PASS engineVersion='+x['engineVersion'])
PYCODE
SERVICE_TOKEN="$(awk -F= '$1=="SC_WORKSPACE_SERVICE_TOKEN"{sub($1"=","");print;exit}' .env)"
[[ -n "$SERVICE_TOKEN" ]] || fail "SC_WORKSPACE_SERVICE_TOKEN blank"
AUTH=(-H "Authorization: Bearer $SERVICE_TOKEN" -H 'X-SC-User-ID: 1')

echo "=== END-TO-END EMBEDDING ARTIFACT JOB ==="
STAMP="$(date +%s)"
cat >/tmp/scw32600-embedding-job.json <<JSON
{"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.neural.embedding-generate","priority":8,"maxAttempts":1,"idempotencyKey":"deploy-v32600-embedding-${STAMP}","payload":{"modelSpec":{"schema":"sc-workspace-neural-model-spec/1.0","modelType":"mlp","layers":[{"weights":[[1.0,0.0],[0.0,1.0]],"bias":[0.0,0.0],"activation":"relu"},{"weights":[[1.0,1.0]],"bias":[0.0],"activation":"identity"}]},"features":[[1.0,2.0],[0.9,2.1],[-1.0,3.0]],"representation":"penultimate","rowIds":["a","b","c"],"normalization":"l2"}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/scw32600-embedding-job.json http://127.0.0.1:8094/v1/jobs >/tmp/scw32600-embedding-created.json
JOB_ID="$(python3 -c "import json;print(json.load(open('/tmp/scw32600-embedding-created.json'))['item']['jobId'])")"
for i in $(seq 1 45); do
  curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${JOB_ID}" >/tmp/scw32600-embedding-state.json
  state="$(python3 -c "import json;print(json.load(open('/tmp/scw32600-embedding-state.json'))['item']['status'])")"
  echo "embedding job attempt $i: $state"
  [[ "$state" == succeeded ]] && break
  [[ "$state" =~ ^(failed|blocked|cancelled)$ ]] && { cat /tmp/scw32600-embedding-state.json; false; }
  sleep 2
done
python3 - <<'PYCODE'
import json
x=json.load(open('/tmp/scw32600-embedding-state.json')); item=x.get('item') or {}; jr=x.get('result') or {}; nr=jr['polyglot']['result']['remote']['result']
ea=nr.get('embeddingArtifact') or {}; wa=nr.get('workspaceRepresentationArtifact') or {}
assert item.get('status')=='succeeded',item
assert ea.get('schema')=='sc-workspace-neural-embedding-artifact/1.0' and ea.get('rows')==3 and ea.get('dimensions')==2,ea
assert ea.get('normalization')=='l2' and ea.get('rowIds')==['a','b','c'],ea
assert wa.get('artifactId') and wa.get('sha256') and jr.get('receiptId'),(wa,jr)
open('/tmp/scw32600-embedding-artifact-id.txt','w').write(wa['artifactId'])
open('/tmp/scw32600-embedding-fingerprint.txt','w').write(ea['artifactFingerprint'])
open('/tmp/scw32600-embedding-receipt-id.txt','w').write(jr['receiptId'])
open('/tmp/scw32600-embedding-doc.json','w').write(json.dumps(ea,separators=(',',':')))
print('NEURAL_EMBEDDING_JOB=PASS jobId='+item['jobId'])
PYCODE
ARTIFACT_ID="$(cat /tmp/scw32600-embedding-artifact-id.txt)"
curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/artifacts/${ARTIFACT_ID}" >/tmp/scw32600-embedding-artifact.json
python3 - <<'PYCODE'
import base64,json
x=json.load(open('/tmp/scw32600-embedding-artifact.json')); item=x.get('item') or {}; doc=json.loads(base64.b64decode(x['contentBase64'])); expected=open('/tmp/scw32600-embedding-fingerprint.txt').read().strip()
assert item.get('mediaType')=='application/vnd.sc.workspace.neural-embedding+json',item
assert doc.get('artifactFingerprint')==expected and doc.get('schema')=='sc-workspace-neural-embedding-artifact/1.0',doc
print('NEURAL_EMBEDDING_WORKSPACE_ARTIFACT=PASS artifactId='+item['artifactId'])
PYCODE
RECEIPT_ID="$(cat /tmp/scw32600-embedding-receipt-id.txt)"
curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/polyglot/receipts/${RECEIPT_ID}" >/tmp/scw32600-embedding-receipt.json
python3 - <<'PYCODE'
import json
x=json.load(open('/tmp/scw32600-embedding-receipt.json')); d=(x.get('item') or {}).get('details') or {}
assert d.get('neuralEmbeddingRepresentation') is True,d
assert d.get('representationArtifactSchema')=='sc-workspace-neural-embedding-artifact/1.0',d
assert d.get('workspaceRepresentationArtifactId') and d.get('representationDatasetFingerprint'),d
print('NEURAL_EMBEDDING_RECEIPT_LINEAGE=PASS')
PYCODE

echo "=== END-TO-END NEAREST-NEIGHBOR REPRESENTATION JOB ==="
python3 - <<'PYCODE'
import json,time
art=json.load(open('/tmp/scw32600-embedding-doc.json'))
req={"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.neural.embedding-neighbors","priority":8,"maxAttempts":1,"idempotencyKey":"deploy-v32600-neighbors-%d"%int(time.time()),"payload":{"embeddingArtifact":art,"metric":"cosine","queryIndices":[0],"k":2}}
json.dump(req,open('/tmp/scw32600-neighbor-job.json','w'),separators=(',',':'))
PYCODE
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/scw32600-neighbor-job.json http://127.0.0.1:8094/v1/jobs >/tmp/scw32600-neighbor-created.json
NJOB_ID="$(python3 -c "import json;print(json.load(open('/tmp/scw32600-neighbor-created.json'))['item']['jobId'])")"
for i in $(seq 1 45); do
  curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${NJOB_ID}" >/tmp/scw32600-neighbor-state.json
  state="$(python3 -c "import json;print(json.load(open('/tmp/scw32600-neighbor-state.json'))['item']['status'])")"
  echo "neighbor job attempt $i: $state"
  [[ "$state" == succeeded ]] && break
  [[ "$state" =~ ^(failed|blocked|cancelled)$ ]] && { cat /tmp/scw32600-neighbor-state.json; false; }
  sleep 2
done
python3 - <<'PYCODE'
import json
x=json.load(open('/tmp/scw32600-neighbor-state.json')); item=x.get('item') or {}; jr=x.get('result') or {}; nr=jr['polyglot']['result']['remote']['result']
ra=nr.get('representationArtifact') or {}; wa=nr.get('workspaceRepresentationArtifact') or {}
assert item.get('status')=='succeeded',item
assert ra.get('schema')=='sc-workspace-neural-representation-analysis-artifact/1.0' and ra.get('analysisType')=='nearest-neighbors',ra
assert nr['queries'][0]['neighbors'][0]['rowId']=='b',nr
assert wa.get('artifactId') and wa.get('sha256') and jr.get('receiptId'),(wa,jr)
open('/tmp/scw32600-representation-artifact-id.txt','w').write(wa['artifactId'])
open('/tmp/scw32600-representation-fingerprint.txt','w').write(ra['artifactFingerprint'])
open('/tmp/scw32600-representation-receipt-id.txt','w').write(jr['receiptId'])
print('NEURAL_NEIGHBOR_JOB=PASS jobId='+item['jobId'])
PYCODE
RARTIFACT_ID="$(cat /tmp/scw32600-representation-artifact-id.txt)"
curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/artifacts/${RARTIFACT_ID}" >/tmp/scw32600-representation-artifact.json
python3 - <<'PYCODE'
import base64,json
x=json.load(open('/tmp/scw32600-representation-artifact.json')); item=x.get('item') or {}; doc=json.loads(base64.b64decode(x['contentBase64'])); expected=open('/tmp/scw32600-representation-fingerprint.txt').read().strip()
assert item.get('mediaType')=='application/vnd.sc.workspace.neural-representation+json',item
assert doc.get('artifactFingerprint')==expected and doc.get('analysisType')=='nearest-neighbors',doc
print('NEURAL_REPRESENTATION_WORKSPACE_ARTIFACT=PASS artifactId='+item['artifactId'])
PYCODE
RRECEIPT_ID="$(cat /tmp/scw32600-representation-receipt-id.txt)"
curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/polyglot/receipts/${RRECEIPT_ID}" >/tmp/scw32600-representation-receipt.json
python3 - <<'PYCODE'
import json
x=json.load(open('/tmp/scw32600-representation-receipt.json')); d=(x.get('item') or {}).get('details') or {}
assert d.get('neuralEmbeddingRepresentation') is True,d
assert d.get('representationArtifactSchema')=='sc-workspace-neural-representation-analysis-artifact/1.0',d
assert d.get('sourceEmbeddingArtifactFingerprint') and d.get('workspaceRepresentationArtifactId'),d
assert d.get('representationAnalysisType')=='nearest-neighbors',d
print('NEURAL_REPRESENTATION_RECEIPT_LINEAGE=PASS')
PYCODE

echo "=== OPENAPI / RUNTIME REGISTRY ==="
docker exec -i sc-workspace-backend python3 - <<'PYCODE'
from app.main import app
from app.client_contracts import TYPED_ENDPOINTS,profile
from app.polyglot import RUNTIME_BY_LANGUAGE
x=profile(app.openapi())
assert x['workspaceVersion']=='3.26.0' and x['typedEndpointCount']==291 and not x['missingOpenApiOperations'],x
n=RUNTIME_BY_LANGUAGE['neural']; assert len(n.operations)==27,n
for op in ['workspace.neural.embedding-generate','workspace.neural.representation-summary','workspace.neural.embedding-similarity','workspace.neural.embedding-neighbors']:
    assert op in n.operations,(op,n)
assert RUNTIME_BY_LANGUAGE['ml'].runtime=='python-sklearn-predictive'
print('WORKSPACE_V32600_OPENAPI_RUNTIME_REGISTRY=PASS typed_endpoints=%d'%len(TYPED_ENDPOINTS))
PYCODE

echo "=== CONTAINER HARDENING ==="
python3 - <<'PYCODE'
import json,subprocess
d=json.loads(subprocess.check_output(['docker','inspect','sc-workspace-neural-runtime']))[0]; h=d['HostConfig']; c=d['Config']
assert h['ReadonlyRootfs'] is True and c.get('User')=='65532:65532',d
assert 'ALL' in (h.get('CapDrop') or []) and 'no-new-privileges:true' in (h.get('SecurityOpt') or []),d
print('NEURAL_RUNTIME_HARDENING=PASS')
PYCODE

echo "PASS: Workspace v3.26.0 backend deployed; governed neural embeddings, representation analysis, artifact persistence, receipt lineage, and hardening verified"
trap - ERR
