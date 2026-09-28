#!/usr/bin/env bash
set -Eeuo pipefail
PACKAGE="${1:-/tmp/sustainable-catalyst-workspace-backend-v3.32.0.zip}"
BASE="/opt/sustainable-catalyst"
OLD="$BASE/sustainable-catalyst-workspace-backend-v3.31.0"
NEW="$BASE/sustainable-catalyst-workspace-backend-v3.32.0"
SWITCHED=0
fail(){ echo "ERROR: $*" >&2; exit 1; }
rollback(){ local code=$?; if [[ "$SWITCHED" == 1 ]]; then echo "=== v3.32.0 verification failed; restoring v3.31.0 ===" >&2; docker rm -f sc-workspace-backend sc-workspace-worker sc-workspace-neural-runtime >/dev/null 2>&1 || true; if [[ -d "$OLD" ]]; then cd "$OLD"; [[ -f docker-compose.yml ]] || cp docker-compose.example.yml docker-compose.yml; docker compose --env-file .env -f docker-compose.yml up -d --no-deps --no-build sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker || true; fi; fi; exit "$code"; }
trap rollback ERR
[[ -f "$PACKAGE" ]] || fail "backend package not found: $PACKAGE"
[[ -d "$OLD" && -f "$OLD/.env" ]] || fail "Workspace v3.31.0 production baseline not found at $OLD; deploy and verify v3.31.0 before v3.32.0"
TMP="$(mktemp -d)"; cleanup(){ rm -rf "$TMP"; }; trap cleanup EXIT
unzip -q "$PACKAGE" -d "$TMP/package"
[[ -f "$TMP/package/app/config.py" && -f "$TMP/package/neural-runtime/service.py" ]] || fail "malformed v3.32.0 backend package"
grep -q 'service_version: str = "3.32.0"' "$TMP/package/app/config.py" || fail "v3.32.0 backend version marker missing"
grep -q 'SERVICE_VERSION = "3.32.0"' "$TMP/package/neural-runtime/service.py" || fail "v3.32.0 neural version marker missing"
for op in workspace.neural.certification-plan workspace.neural.certification-execute workspace.neural.certification-verify workspace.neural.certification-report; do grep -q "$op" "$TMP/package/neural-runtime/service.py" || fail "v3.32 certification operation missing: $op"; done
rm -rf "$NEW"; mkdir -p "$NEW"; cp -a "$TMP/package/." "$NEW/"; cp "$OLD/.env" "$NEW/.env"
cd "$NEW"; cp docker-compose.example.yml docker-compose.yml
python3 -m compileall -q app neural-runtime

echo "=== BUILD WORKSPACE v3.32.0 ==="
docker compose --env-file .env -f docker-compose.yml build sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker

echo "=== PRE-SWITCH NEURAL RUNTIME PRODUCTION CERTIFICATION ==="
docker compose --env-file .env -f docker-compose.yml run --rm -T --no-deps --entrypoint python sc-workspace-neural-runtime - <<'PYCODE'
import copy
import service
from fastapi import HTTPException
h=service.health(); assert h['version']=='3.32.0' and len(h['operations'])==52,h
assert h['productionCertificationEnabled'] is True,h
assert h['productionCertificationProfile']=='workspace-neural-production/1.0',h
cert=service._certification_execute({}); art=cert['certificationArtifact']
assert cert['allRequiredPassed'] is True and art['productionStatus']=='certified',art
assert art['requiredCheckCount']==9 and art['passedRequiredCheckCount']==9,art
assert art['remoteGpuTransportStatus'] in {'not-exercised-no-worker-attached','ready-worker-registered'},art
assert service._certification_verify({'certificationArtifact':art})['valid'] is True
report=service._certification_report({'certificationArtifact':art})['certificationReport']
assert report['productionStatus']=='certified' and report['requiredChecksPassed']==9,report

# Representative cross-release capability smoke: training/checkpoint/evaluation/explanation/embedding/package/inference/search.
tok=service._CURRENT_DEVICE.set('cpu')
try:
    t={
      'seed':32,'features':[[0.0],[1.0],[2.0],[3.0]],'targets':[[1.0],[3.0],[5.0],[7.0]],
      'trainingSpec':{'schema':'sc-workspace-neural-training-spec/1.0','modelType':'linear','task':'regression','inputFeatures':1,'outputFeatures':1,'epochs':2,'batchSize':2,'shuffle':False,'optimizer':{'name':'sgd','learningRate':0.05,'weightDecay':0.0}}
    }
    tr=service._train(t,expected_model_type='linear',resume=False)
    cp=tr['checkpointArtifact']; assert cp['schema']=='sc-workspace-neural-checkpoint-artifact/1.0'
    ci=service._checkpoint_inspect({'checkpointArtifact':cp}); assert ci['valid'] is True
    ev=service._evaluate_regression({'modelSpec':tr['trainedModelSpec'],'checkpointArtifact':cp,'features':[[0.0],[1.0]],'targets':[[1.0],[3.0]]}); assert ev['evaluationArtifact']['schema']=='sc-workspace-neural-evaluation-artifact/1.0'
    ex=service._explain_integrated_gradients({'modelSpec':tr['trainedModelSpec'],'checkpointArtifact':cp,'features':[[1.0]],'task':'regression','steps':8}); assert ex['explainabilityArtifact']['schema']=='sc-workspace-neural-explainability-artifact/1.0'
    em=service._embedding_generate({'modelSpec':tr['trainedModelSpec'],'checkpointArtifact':cp,'features':[[1.0],[2.0]],'representation':'output','rowIds':['a','b']}); assert em['embeddingArtifact']['schema']=='sc-workspace-neural-embedding-artifact/1.0'
    pkg=service._model_package_create({'modelSpec':tr['trainedModelSpec'],'checkpointArtifact':cp,'task':'regression','featureNames':['x']})['modelPackage']
    assert service._model_package_verify({'modelPackage':pkg})['valid'] is True
    inf=service._model_package_infer({'modelPackage':pkg,'features':[[1.5]],'rowIds':['future']}); assert inf['predictionArtifact']['schema']=='sc-workspace-neural-prediction-artifact/1.0'
    hp={
      'trainingSpec':{'schema':'sc-workspace-neural-training-spec/1.0','modelType':'linear','task':'regression','inputFeatures':1,'outputFeatures':1,'optimizer':{'name':'sgd','learningRate':0.05,'weightDecay':0.0},'epochs':1,'batchSize':4,'shuffle':False},
      'features':[[0.0],[1.0],[2.0],[3.0]],'targets':[[1.0],[3.0],[5.0],[7.0]],'validationFeatures':[[4.0],[5.0]],'validationTargets':[[9.0],[11.0]],
      'objective':{'dataset':'validation','metric':'loss','direction':'minimize'},'seed':32,'deviceRequest':'cpu','parameterGrid':{'optimizer.learningRate':[0.01,0.05]}
    }
    search=service._hyperparameter_grid(hp)['searchArtifact']; assert search['trialCount']==2 and len(search['artifactFingerprint'])==64
finally:
    service._CURRENT_DEVICE.reset(tok)

# Broker protocol remains locally certifiable without pretending a physical GPU worker was exercised.
service.REMOTE_BROKER_ENABLED=True
service.REMOTE_SHARED_SECRET='deploy-v33200-broker-cert-secret'
service.REMOTE_WORKERS_JSON='[{"workerId":"gpu-cert-1","url":"https://gpu.invalid","device":"cuda:0","enabled":true,"tags":["cert"]}]'
payload={'remoteOperation':'workspace.neural.infer-regression','remotePayload':{'modelSpec':{'schema':'sc-workspace-neural-model-spec/1.0','modelType':'linear','weights':[[2.0]],'bias':[1.0],'activation':'identity'},'features':[[3.0]],'rowIds':['r1'],'seed':32}}
plan=service._remote_dispatch_plan(payload)['dispatchPlan']; assert plan['workerId']=='gpu-cert-1' and len(plan['planFingerprint'])==64,plan
base={'schema':service.REMOTE_EXECUTION_RECEIPT_SCHEMA,'dispatchId':'ngd_cert','workerId':'gpu-cert-1','operation':'workspace.neural.infer-regression','payloadFingerprint':plan['payloadFingerprint'],'dispatchPlanFingerprint':plan['planFingerprint'],'resultFingerprint':'a'*64,'selectedDevice':'cuda:0','devicePlanFingerprint':'b'*64,'runtimeVersion':'3.32.0','engineVersion':service.torch.__version__,'startedAt':1,'finishedAt':2}
fp=service._canonical_sha256(base); sigbase=dict(base); sigbase['receiptFingerprint']=fp
receipt=dict(sigbase); receipt['signature']=service._remote_hmac(sigbase)
assert service._validate_remote_receipt(receipt)['receiptFingerprint']==fp
bad=copy.deepcopy(receipt); bad['workerId']='tampered'
try:
    service._validate_remote_receipt(bad); raise AssertionError('tampered receipt accepted')
except HTTPException as exc:
    assert exc.status_code==400
print('NEURAL_V33200_PRESWITCH_PRODUCTION_CERTIFICATION=PASS')
print('NEURAL_V33200_CROSS_CAPABILITY_SMOKE=PASS')
print('NEURAL_V33200_REMOTE_BROKER_PROTOCOL=PASS')
PYCODE

echo "=== SWITCH TO v3.32.0 ==="
docker rm -f sc-workspace-backend sc-workspace-worker sc-workspace-neural-runtime >/dev/null 2>&1 || true
docker compose --env-file .env -f docker-compose.yml up -d --no-deps sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker
SWITCHED=1
for i in $(seq 1 60); do code="$(curl -sS -o /tmp/scw33200-health.json -w '%{http_code}' http://127.0.0.1:8094/health 2>/dev/null || true)"; echo "backend health attempt $i: HTTP $code"; [[ "$code" == 200 ]] && break; sleep 2; done
python3 - <<'PYCODE'
import json
x=json.load(open('/tmp/scw33200-health.json')); assert x['ok'] is True and x['version']=='3.32.0',x
assert x.get('neuralRuntimeBoundedOperations')==52,x
assert x.get('neuralRuntimeProductionCertification') is True,x
assert x.get('neuralProductionCertificationProfile')=='workspace-neural-production/1.0',x
assert x.get('neuralProductionCertificationWorkspaceArtifactPersistence') is True,x
print('WORKSPACE_V33200_HEALTH=PASS')
PYCODE

echo "=== DIRECT NEURAL HEALTH ==="
docker exec -i sc-workspace-neural-runtime python - <<'PYCODE'
import json,urllib.request
x=json.load(urllib.request.urlopen('http://127.0.0.1:8101/health',timeout=5))
assert x['version']=='3.32.0' and len(x['operations'])==52,x
assert x['productionCertificationEnabled'] is True,x
assert x['productionCertificationArtifactSchema']=='sc-workspace-neural-production-certification-artifact/1.0',x
assert x['clientSuppliedRemoteWorkerUrlsAllowed'] is False,x
print('NEURAL_V33200_DIRECT_HEALTH=PASS engineVersion='+x['engineVersion'])
PYCODE
SERVICE_TOKEN="$(awk -F= '$1=="SC_WORKSPACE_SERVICE_TOKEN"{sub($1"=","");print;exit}' .env)"; [[ -n "$SERVICE_TOKEN" ]] || fail "SC_WORKSPACE_SERVICE_TOKEN blank"
AUTH=(-H "Authorization: Bearer $SERVICE_TOKEN" -H 'X-SC-User-ID: 1')
wait_job(){ local id="$1" out="$2" label="$3"; for i in $(seq 1 60); do curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${id}" >"$out"; state="$(python3 -c "import json;print(json.load(open('$out'))['item']['status'])")"; echo "$label attempt $i: $state"; [[ "$state" == succeeded ]] && return 0; [[ "$state" =~ ^(failed|blocked|cancelled)$ ]] && { cat "$out"; return 1; }; sleep 2; done; return 1; }

echo "=== END-TO-END PRODUCTION CERTIFICATION JOB ==="
STAMP="$(date +%s)"
cat >/tmp/scw33200-cert-job.json <<JSON
{"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.neural.certification-execute","priority":9,"maxAttempts":1,"idempotencyKey":"deploy-v33200-cert-${STAMP}","payload":{"deviceRequest":"cpu"}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/scw33200-cert-job.json http://127.0.0.1:8094/v1/jobs >/tmp/scw33200-cert-created.json
JOB_ID="$(python3 -c "import json;print(json.load(open('/tmp/scw33200-cert-created.json'))['item']['jobId'])")"
wait_job "$JOB_ID" /tmp/scw33200-cert-state.json "production certification"
python3 - <<'PYCODE'
import json
x=json.load(open('/tmp/scw33200-cert-state.json')); item=x.get('item') or {}; jr=x.get('result') or {}; nr=jr['polyglot']['result']['remote']['result']; a=nr.get('certificationArtifact') or {}; wa=nr.get('workspaceProductionCertificationArtifact') or {}
assert item.get('status')=='succeeded',item
assert a.get('schema')=='sc-workspace-neural-production-certification-artifact/1.0' and a.get('productionStatus')=='certified',a
assert a.get('requiredCheckCount')==9 and a.get('passedRequiredCheckCount')==9,a
assert wa.get('artifactId') and wa.get('mediaType')=='application/vnd.sc.workspace.neural-production-certification+json',wa
open('/tmp/scw33200-artifact-id.txt','w').write(wa['artifactId']); open('/tmp/scw33200-receipt-id.txt','w').write(jr['receiptId'])
print('NEURAL_PRODUCTION_CERTIFICATION_JOB=PASS jobId='+item['jobId'])
PYCODE
AID="$(cat /tmp/scw33200-artifact-id.txt)"; RID="$(cat /tmp/scw33200-receipt-id.txt)"
curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/artifacts/${AID}" >/tmp/scw33200-cert-artifact.json
python3 - <<'PYCODE'
import base64,json
x=json.load(open('/tmp/scw33200-cert-artifact.json')); item=x.get('item') or {}
assert item.get('mediaType')=='application/vnd.sc.workspace.neural-production-certification+json',item
raw=base64.b64decode(x['contentBase64']); a=json.loads(raw)
assert a['schema']=='sc-workspace-neural-production-certification-artifact/1.0' and a['productionStatus']=='certified',a
assert len(a['artifactFingerprint'])==64 and a['certificationId'].startswith('nrc_'),a
open('/tmp/scw33200-cert-artifact-body.json','w').write(json.dumps(a,separators=(',',':')))
print('NEURAL_PRODUCTION_CERTIFICATION_WORKSPACE_ARTIFACT=PASS')
PYCODE
curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/polyglot/receipts/${RID}" >/tmp/scw33200-cert-receipt.json
python3 - <<'PYCODE'
import json
x=json.load(open('/tmp/scw33200-cert-receipt.json')); d=(x.get('item') or {}).get('details') or {}
assert d.get('neuralRuntimeProductionCertification') is True,d
assert d.get('productionCertificationStatus')=='certified',d
assert d.get('productionCertificationRequiredChecksPassed')==9,d
assert d.get('workspaceProductionCertificationArtifactId'),d
print('NEURAL_PRODUCTION_CERTIFICATION_RECEIPT_LINEAGE=PASS')
PYCODE

python3 - <<'PYCODE'
import json
art=json.load(open('/tmp/scw33200-cert-artifact-body.json'))
base={"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.neural.certification-verify","priority":9,"maxAttempts":1,"idempotencyKey":"deploy-v33200-verify","payload":{"deviceRequest":"cpu","certificationArtifact":art}}
open('/tmp/scw33200-verify-job.json','w').write(json.dumps(base,separators=(',',':')))
base['operation']='workspace.neural.certification-report'; base['idempotencyKey']='deploy-v33200-report'; open('/tmp/scw33200-report-job.json','w').write(json.dumps(base,separators=(',',':')))
PYCODE
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/scw33200-verify-job.json http://127.0.0.1:8094/v1/jobs >/tmp/scw33200-verify-created.json
VERIFY_ID="$(python3 -c "import json;print(json.load(open('/tmp/scw33200-verify-created.json'))['item']['jobId'])")"; wait_job "$VERIFY_ID" /tmp/scw33200-verify-state.json "certification verify"
python3 - <<'PYCODE'
import json
x=json.load(open('/tmp/scw33200-verify-state.json')); nr=x['result']['polyglot']['result']['remote']['result']; assert nr.get('valid') is True and nr.get('productionStatus')=='certified',nr
print('NEURAL_PRODUCTION_CERTIFICATION_VERIFY_JOB=PASS')
PYCODE
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/scw33200-report-job.json http://127.0.0.1:8094/v1/jobs >/tmp/scw33200-report-created.json
REPORT_ID="$(python3 -c "import json;print(json.load(open('/tmp/scw33200-report-created.json'))['item']['jobId'])")"; wait_job "$REPORT_ID" /tmp/scw33200-report-state.json "certification report"
python3 - <<'PYCODE'
import json
x=json.load(open('/tmp/scw33200-report-state.json')); nr=x['result']['polyglot']['result']['remote']['result']; rep=nr.get('certificationReport') or {}
assert rep.get('productionStatus')=='certified' and rep.get('requiredChecksPassed')==9 and rep.get('failedRequiredChecks')==[],rep
print('NEURAL_PRODUCTION_CERTIFICATION_REPORT_JOB=PASS')
PYCODE

echo "=== OPENAPI / RUNTIME REGISTRY ==="
docker exec -i sc-workspace-backend python3 - <<'PYCODE'
from app.main import app
from app.client_contracts import TYPED_ENDPOINTS,profile
from app.polyglot import RUNTIME_BY_LANGUAGE
x=profile(app.openapi()); assert x['workspaceVersion']=='3.32.0' and x['typedEndpointCount']==291 and not x['missingOpenApiOperations'],x
n=RUNTIME_BY_LANGUAGE['neural']; assert len(n.operations)==52,n
for op in ['workspace.neural.certification-plan','workspace.neural.certification-execute','workspace.neural.certification-verify','workspace.neural.certification-report']: assert op in n.operations,(op,n)
print('WORKSPACE_V33200_OPENAPI_RUNTIME_REGISTRY=PASS typed_endpoints=%d'%len(TYPED_ENDPOINTS))
PYCODE

echo "=== CONTAINER HARDENING ==="
python3 - <<'PYCODE'
import json,subprocess
d=json.loads(subprocess.check_output(['docker','inspect','sc-workspace-neural-runtime']))[0]; h=d['HostConfig']; c=d['Config']
assert h['ReadonlyRootfs'] is True and c.get('User')=='65532:65532',d
assert 'ALL' in (h.get('CapDrop') or []) and 'no-new-privileges:true' in (h.get('SecurityOpt') or []),d
print('NEURAL_RUNTIME_HARDENING=PASS')
PYCODE

echo "PASS: Workspace v3.32.0 backend deployed; neural runtime production certification, cross-capability assurance, governed certification artifact persistence, receipt lineage, registry integrity, and hardening verified"
trap - ERR
