#!/usr/bin/env bash
set -Eeuo pipefail
PACKAGE="${1:-/tmp/sustainable-catalyst-workspace-backend-v3.23.0.zip}"
BASE="/opt/sustainable-catalyst"
OLD="$BASE/sustainable-catalyst-workspace-backend-v3.22.0.2"
NEW="$BASE/sustainable-catalyst-workspace-backend-v3.23.0"
SWITCHED=0
fail(){ echo "ERROR: $*" >&2; exit 1; }
rollback(){
  local code=$?
  if [[ "$SWITCHED" == 1 ]]; then
    echo "=== v3.23.0 verification failed; restoring v3.22.0.2 ===" >&2
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
[[ -d "$OLD" && -f "$OLD/.env" ]] || fail "Workspace v3.22.0.2 production baseline not found at $OLD"
TMP="$(mktemp -d)"; cleanup(){ rm -rf "$TMP"; }; trap cleanup EXIT
unzip -q "$PACKAGE" -d "$TMP/package"
[[ -f "$TMP/package/app/config.py" && -f "$TMP/package/neural-runtime/service.py" && -f "$TMP/package/neural-runtime/requirements.txt" && -f "$TMP/package/docker-compose.example.yml" ]] || fail "malformed v3.23.0 backend package"
grep -q 'service_version: str = "3.23.0"' "$TMP/package/app/config.py" || fail "v3.23.0 backend version marker missing"
grep -q 'SERVICE_VERSION = "3.23.0"' "$TMP/package/neural-runtime/service.py" || fail "v3.23.0 neural version marker missing"
grep -q 'workspace.neural.resume-linear' "$TMP/package/neural-runtime/service.py" || fail "resume-linear operation missing"
grep -q 'CHECKPOINT_SCHEMA = "sc-workspace-neural-checkpoint-artifact/1.0"' "$TMP/package/neural-runtime/service.py" || fail "checkpoint schema missing"
grep -q 'application/vnd.sc.workspace.neural-checkpoint+json' "$TMP/package/app/polyglot.py" || fail "Workspace checkpoint artifact persistence missing"
grep -q '^numpy==2.2.6$' "$TMP/package/neural-runtime/requirements.txt" || fail "NumPy pin missing"
grep -q '^torch==2.10.0$' "$TMP/package/neural-runtime/requirements.txt" || fail "PyTorch pin missing"
rm -rf "$NEW"; mkdir -p "$NEW"; cp -a "$TMP/package/." "$NEW/"; cp "$OLD/.env" "$NEW/.env"
cd "$NEW"; cp docker-compose.example.yml docker-compose.yml
python3 -m compileall -q app neural-runtime

echo "=== BUILD WORKSPACE v3.23.0 ==="
docker compose --env-file .env -f docker-compose.yml build sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker

echo "=== PRE-SWITCH HARDENED CHECKPOINT/RESUME CERTIFICATION ==="
docker compose --env-file .env -f docker-compose.yml run --rm --no-deps --entrypoint python sc-workspace-neural-runtime - <<'PY'
import service
h=service.health()
assert h['version']=='3.23.0',h
assert len(h['operations'])==14,h
assert h['checkpointPersistenceEnabled'] is True,h
assert h['resumeTrainingEnabled'] is True,h
assert h['checkpointArtifactSchema']=='sc-workspace-neural-checkpoint-artifact/1.0',h
assert h['checkpointResumePolicy']=='same-dataset-only',h
assert h['runtimeIdentity']=='scworkspace' and h['runtimeHome']=='/tmp',h
base={
 'seed':17,
 'features':[[0.0],[1.0],[2.0],[3.0],[4.0],[5.0]],
 'targets':[[1.0],[3.0],[5.0],[7.0],[9.0],[11.0]],
}
def spec(epochs):
 return {'schema':'sc-workspace-neural-training-spec/1.0','modelType':'linear','task':'regression','inputFeatures':1,'outputFeatures':1,'epochs':epochs,'batchSize':3,'shuffle':True,'optimizer':{'name':'adam','learningRate':0.05,'weightDecay':0.0}}
first=service._train({**base,'trainingSpec':spec(5)},expected_model_type='linear')
ck=first['checkpointArtifact']
assert first['trainingRun']['checkpointCreated'] is True,first
assert ck['completedEpochs']==5 and ck['lineageDepth']==0 and ck['parentCheckpointFingerprint'] is None,ck
inspection=service._checkpoint_inspect({'checkpointArtifact':ck})
assert inspection['stateBundleVerified'] is True,inspection
resumed=service._train({**base,'trainingSpec':spec(3),'checkpointArtifact':ck},expected_model_type='linear',resume=True)
child=resumed['checkpointArtifact']; run=resumed['trainingRun']
assert run['startingEpoch']==5 and run['completedEpochs']==3 and run['cumulativeEpochs']==8,run
assert child['parentCheckpointFingerprint']==ck['artifactFingerprint'] and child['lineageDepth']==1,child
continuous=service._train({**base,'trainingSpec':spec(8)},expected_model_type='linear')
assert resumed['trainedModelSpecFingerprint']==continuous['trainedModelSpecFingerprint'],(resumed,continuous)
print('NEURAL_V32300_PRESWITCH_CHECKPOINT_RESUME=PASS parent='+ck['artifactFingerprint'][:12]+' child='+child['artifactFingerprint'][:12])
PY

echo "=== SWITCH TO v3.23.0 ==="
docker rm -f sc-workspace-backend sc-workspace-worker sc-workspace-neural-runtime >/dev/null 2>&1 || true
docker compose --env-file .env -f docker-compose.yml up -d --no-deps sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker
SWITCHED=1
for i in $(seq 1 60); do
  code="$(curl -sS -o /tmp/scw32300-health.json -w '%{http_code}' http://127.0.0.1:8094/health 2>/dev/null || true)"
  echo "backend health attempt $i: HTTP $code"
  [[ "$code" == 200 ]] && break
  sleep 2
done
python3 - <<'PY'
import json
x=json.load(open('/tmp/scw32300-health.json'))
assert x['ok'] is True and x['version']=='3.23.0',x
assert x.get('neuralRuntimeBoundedOperations')==14,x
assert x.get('neuralRuntimeTrainingEnabled') is True,x
assert x.get('neuralTrainingCheckpointPersistenceEnabled') is True,x
assert x.get('neuralTrainingResumeEnabled') is True,x
assert x.get('neuralCheckpointWorkspaceArtifactPersistence') is True,x
assert x.get('neuralCheckpointResumePolicy')=='same-dataset-only',x
print('WORKSPACE_V32300_HEALTH=PASS')
PY

echo "=== DIRECT NEURAL HEALTH ==="
docker exec sc-workspace-neural-runtime python - <<'PY'
import json,urllib.request
x=json.load(urllib.request.urlopen('http://127.0.0.1:8101/health',timeout=5))
assert x['version']=='3.23.0' and len(x['operations'])==14,x
assert x['trainingEnabled'] is True and x['checkpointPersistenceEnabled'] is True,x
assert x['resumeTrainingEnabled'] is True and x['acceleratorExecutionEnabled'] is False,x
assert x['checkpointArtifactSchema']=='sc-workspace-neural-checkpoint-artifact/1.0',x
assert x['checkpointStateSchema']=='sc-workspace-neural-checkpoint-state/1.0',x
assert x['checkpointResumePolicy']=='same-dataset-only',x
assert x.get('runtimeIdentity')=='scworkspace' and x.get('torchInductorCacheDir')=='/tmp/torchinductor',x
print('NEURAL_V32300_DIRECT_HEALTH=PASS engineVersion='+x['engineVersion'])
PY
SERVICE_TOKEN="$(awk -F= '$1=="SC_WORKSPACE_SERVICE_TOKEN"{sub($1"=","");print;exit}' .env)"; [[ -n "$SERVICE_TOKEN" ]] || fail "SC_WORKSPACE_SERVICE_TOKEN blank"
AUTH=(-H "Authorization: Bearer $SERVICE_TOKEN" -H 'X-SC-User-ID: 1')

echo "=== END-TO-END CHECKPOINT CREATION JOB ==="
STAMP="$(date +%s)"
cat >/tmp/scw32300-train-job.json <<JSON
{"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.neural.train-linear","priority":8,"maxAttempts":1,"idempotencyKey":"deploy-v32300-train-${STAMP}","payload":{"seed":17,"features":[[0.0],[1.0],[2.0],[3.0],[4.0],[5.0]],"targets":[[1.0],[3.0],[5.0],[7.0],[9.0],[11.0]],"trainingSpec":{"schema":"sc-workspace-neural-training-spec/1.0","modelType":"linear","task":"regression","inputFeatures":1,"outputFeatures":1,"epochs":5,"batchSize":3,"shuffle":true,"optimizer":{"name":"adam","learningRate":0.05,"weightDecay":0.0}}}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/scw32300-train-job.json http://127.0.0.1:8094/v1/jobs >/tmp/scw32300-train-created.json
TRAIN_JOB_ID="$(python3 -c "import json;print(json.load(open('/tmp/scw32300-train-created.json'))['item']['jobId'])")"
for i in $(seq 1 45); do
  curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${TRAIN_JOB_ID}" >/tmp/scw32300-train-state.json
  state="$(python3 -c "import json;print(json.load(open('/tmp/scw32300-train-state.json'))['item']['status'])")"
  echo "checkpoint training job attempt $i: $state"
  [[ "$state" == succeeded ]] && break
  [[ "$state" =~ ^(failed|blocked|cancelled)$ ]] && { cat /tmp/scw32300-train-state.json; false; }
  sleep 2
done
python3 - <<'PY'
import json
x=json.load(open('/tmp/scw32300-train-state.json')); item=x.get('item') or {}; jr=x.get('result') or {}
assert item.get('status')=='succeeded',item
p=jr.get('polyglot') or {}; remote=((p.get('result') or {}).get('remote') or {}); nr=remote.get('result') or {}; run=nr.get('trainingRun') or {}; ck=nr.get('checkpointArtifact') or {}; wa=nr.get('workspaceCheckpointArtifact') or {}
assert run.get('completedEpochs')==5 and run.get('checkpointCreated') is True,run
assert ck.get('schema')=='sc-workspace-neural-checkpoint-artifact/1.0' and ck.get('lineageDepth')==0,ck
assert ck.get('parentCheckpointFingerprint') is None,ck
assert wa.get('artifactId') and wa.get('sha256'),wa
assert jr.get('receiptId'),jr
open('/tmp/scw32300-parent-fingerprint.txt','w').write(ck['artifactFingerprint'])
open('/tmp/scw32300-parent-artifact-id.txt','w').write(wa['artifactId'])
open('/tmp/scw32300-train-receipt-id.txt','w').write(jr['receiptId'])
print('NEURAL_CHECKPOINT_CREATION_JOB=PASS jobId='+item['jobId']+' checkpointId='+ck['checkpointId'])
PY
PARENT_ARTIFACT_ID="$(cat /tmp/scw32300-parent-artifact-id.txt)"
curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/artifacts/${PARENT_ARTIFACT_ID}" >/tmp/scw32300-parent-artifact.json
python3 - <<'PY'
import base64,json
x=json.load(open('/tmp/scw32300-parent-artifact.json')); item=x.get('item') or {}; raw=base64.b64decode(x['contentBase64']); ck=json.loads(raw)
expected=open('/tmp/scw32300-parent-fingerprint.txt').read().strip()
assert item.get('mediaType')=='application/vnd.sc.workspace.neural-checkpoint+json',item
assert ck.get('artifactFingerprint')==expected,ck
assert ck.get('completedEpochs')==5 and ck.get('lineageDepth')==0,ck
print('NEURAL_CHECKPOINT_WORKSPACE_ARTIFACT=PASS artifactId='+item['artifactId'])
PY
TRAIN_RECEIPT_ID="$(cat /tmp/scw32300-train-receipt-id.txt)"
curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/polyglot/receipts/${TRAIN_RECEIPT_ID}" >/tmp/scw32300-train-receipt.json
python3 - <<'PY'
import json
x=json.load(open('/tmp/scw32300-train-receipt.json')); d=(x.get('item') or {}).get('details') or {}
assert d.get('checkpointPersistenceEnabled') is True,d
assert d.get('resumeTrainingEnabled') is True,d
assert d.get('workspaceCheckpointArtifactId'),d
assert d.get('checkpointLineageDepth')==0,d
assert d.get('resumed') is False,d
print('NEURAL_CHECKPOINT_RECEIPT_LINEAGE=PASS')
PY

echo "=== END-TO-END RESUME JOB ==="
python3 - <<'PY'
import json,time
x=json.load(open('/tmp/scw32300-train-state.json')); jr=x['result']; nr=jr['polyglot']['result']['remote']['result']; ck=nr['checkpointArtifact']
req={
 'schema':'sc-workspace-job-request/1.0','jobType':'workspace-task','targetProduct':'workspace',
 'operation':'workspace.neural.resume-linear','priority':8,'maxAttempts':1,
 'idempotencyKey':'deploy-v32300-resume-'+str(int(time.time())),
 'payload':{
  'seed':17,'features':[[0.0],[1.0],[2.0],[3.0],[4.0],[5.0]],'targets':[[1.0],[3.0],[5.0],[7.0],[9.0],[11.0]],
  'trainingSpec':{'schema':'sc-workspace-neural-training-spec/1.0','modelType':'linear','task':'regression','inputFeatures':1,'outputFeatures':1,'epochs':3,'batchSize':3,'shuffle':True,'optimizer':{'name':'adam','learningRate':0.05,'weightDecay':0.0}},
  'checkpointArtifact':ck,
 }
}
json.dump(req,open('/tmp/scw32300-resume-job.json','w'),separators=(',',':'))
PY
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/scw32300-resume-job.json http://127.0.0.1:8094/v1/jobs >/tmp/scw32300-resume-created.json
RESUME_JOB_ID="$(python3 -c "import json;print(json.load(open('/tmp/scw32300-resume-created.json'))['item']['jobId'])")"
for i in $(seq 1 45); do
  curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${RESUME_JOB_ID}" >/tmp/scw32300-resume-state.json
  state="$(python3 -c "import json;print(json.load(open('/tmp/scw32300-resume-state.json'))['item']['status'])")"
  echo "resume job attempt $i: $state"
  [[ "$state" == succeeded ]] && break
  [[ "$state" =~ ^(failed|blocked|cancelled)$ ]] && { cat /tmp/scw32300-resume-state.json; false; }
  sleep 2
done
python3 - <<'PY'
import json
parent=open('/tmp/scw32300-parent-fingerprint.txt').read().strip()
x=json.load(open('/tmp/scw32300-resume-state.json')); item=x.get('item') or {}; jr=x.get('result') or {}; nr=jr['polyglot']['result']['remote']['result']; run=nr.get('trainingRun') or {}; ck=nr.get('checkpointArtifact') or {}; wa=nr.get('workspaceCheckpointArtifact') or {}
assert item.get('status')=='succeeded',item
assert run.get('resumed') is True and run.get('startingEpoch')==5 and run.get('completedEpochs')==3 and run.get('cumulativeEpochs')==8,run
assert run.get('resumedFromCheckpointFingerprint')==parent,run
assert ck.get('parentCheckpointFingerprint')==parent and ck.get('lineageDepth')==1 and ck.get('completedEpochs')==8,ck
assert wa.get('artifactId') and jr.get('receiptId'),(wa,jr)
open('/tmp/scw32300-child-artifact-id.txt','w').write(wa['artifactId'])
open('/tmp/scw32300-resume-receipt-id.txt','w').write(jr['receiptId'])
print('NEURAL_RESUME_JOB=PASS jobId='+item['jobId']+' childCheckpoint='+ck['checkpointId'])
PY
CHILD_ARTIFACT_ID="$(cat /tmp/scw32300-child-artifact-id.txt)"
curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/artifacts/${CHILD_ARTIFACT_ID}" >/tmp/scw32300-child-artifact.json
python3 - <<'PY'
import base64,json
parent=open('/tmp/scw32300-parent-fingerprint.txt').read().strip()
x=json.load(open('/tmp/scw32300-child-artifact.json')); ck=json.loads(base64.b64decode(x['contentBase64']))
assert ck.get('parentCheckpointFingerprint')==parent and ck.get('lineageDepth')==1 and ck.get('completedEpochs')==8,ck
print('NEURAL_CHILD_CHECKPOINT_ARTIFACT_LINEAGE=PASS artifactId='+(x.get('item') or {}).get('artifactId',''))
PY
RESUME_RECEIPT_ID="$(cat /tmp/scw32300-resume-receipt-id.txt)"
curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/polyglot/receipts/${RESUME_RECEIPT_ID}" >/tmp/scw32300-resume-receipt.json
python3 - <<'PY'
import json
parent=open('/tmp/scw32300-parent-fingerprint.txt').read().strip()
x=json.load(open('/tmp/scw32300-resume-receipt.json')); d=(x.get('item') or {}).get('details') or {}
assert d.get('checkpointPersistenceEnabled') is True and d.get('resumeTrainingEnabled') is True,d
assert d.get('resumed') is True and d.get('resumedFromCheckpointFingerprint')==parent,d
assert d.get('startingEpoch')==5 and d.get('cumulativeEpochs')==8 and d.get('checkpointLineageDepth')==1,d
assert d.get('workspaceCheckpointArtifactId'),d
print('NEURAL_RESUME_RECEIPT_LINEAGE=PASS')
PY

echo "=== OPENAPI / RUNTIME REGISTRY ==="
docker exec -i sc-workspace-backend python3 - <<'PY'
from app.main import app
from app.client_contracts import TYPED_ENDPOINTS,profile
from app.polyglot import RUNTIME_BY_LANGUAGE
x=profile(app.openapi()); assert x['workspaceVersion']=='3.23.0' and x['typedEndpointCount']==291 and not x['missingOpenApiOperations'],x
n=RUNTIME_BY_LANGUAGE['neural']; assert len(n.operations)==14,n
for op in ['workspace.neural.checkpoint-inspect','workspace.neural.resume-linear','workspace.neural.resume-mlp']:
 assert op in n.operations,(op,n)
assert RUNTIME_BY_LANGUAGE['ml'].runtime=='python-sklearn-predictive'
print('WORKSPACE_V32300_OPENAPI_RUNTIME_REGISTRY=PASS typed_endpoints=%d'%len(TYPED_ENDPOINTS))
PY

echo "=== CONTAINER HARDENING ==="
python3 - <<'PY'
import json,subprocess
d=json.loads(subprocess.check_output(['docker','inspect','sc-workspace-neural-runtime']))[0]; h=d['HostConfig']; c=d['Config']
assert h['ReadonlyRootfs'] is True and c.get('User')=='65532:65532',d
assert 'ALL' in (h.get('CapDrop') or []) and 'no-new-privileges:true' in (h.get('SecurityOpt') or []),d
print('NEURAL_RUNTIME_HARDENING=PASS')
PY

echo "PASS: Workspace v3.23.0 backend deployed; checkpoint persistence, deterministic resume, Workspace artifact storage, and neural lineage verified"
trap - ERR
