#!/usr/bin/env bash
set -Eeuo pipefail
PACKAGE="${1:-/tmp/sustainable-catalyst-workspace-backend-v3.33.0-upgrade.zip}"
BASE="/opt/sustainable-catalyst"
OLD="$BASE/sustainable-catalyst-workspace-backend-v3.32.0"
NEW="$BASE/sustainable-catalyst-workspace-backend-v3.33.0"
SWITCHED=0

fail(){ echo "ERROR: $*" >&2; exit 1; }
rollback(){
  local code=$?
  if [[ "$SWITCHED" == 1 ]]; then
    echo "=== v3.33.0 verification failed; restoring v3.32.0 ===" >&2
    docker rm -f sc-workspace-backend sc-workspace-worker sc-workspace-neural-runtime >/dev/null 2>&1 || true
    if [[ -d "$OLD" ]]; then
      cd "$OLD"
      [[ -f docker-compose.yml ]] || cp docker-compose.example.yml docker-compose.yml
      docker compose --env-file .env -f docker-compose.yml up -d --no-deps --no-build sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker || true
    fi
  fi
  exit "$code"
}
trap rollback ERR

[[ -f "$PACKAGE" ]] || fail "v3.33.0 package not found: $PACKAGE"
[[ -d "$OLD" && -f "$OLD/.env" ]] || fail "Workspace v3.32.0 production baseline not found at $OLD"
grep -q 'service_version: str = "3.32.0"' "$OLD/app/config.py" || fail "v3.32.0 backend baseline marker missing"
grep -q 'SERVICE_VERSION = "3.32.0"' "$OLD/neural-runtime/service.py" || fail "v3.32.0 neural baseline marker missing"
for op in workspace.neural.certification-plan workspace.neural.certification-execute workspace.neural.certification-verify workspace.neural.certification-report; do
  grep -q "$op" "$OLD/neural-runtime/service.py" || fail "v3.32.0 production certification operation missing: $op"
done

TMP="$(mktemp -d)"; cleanup(){ rm -rf "$TMP"; }; trap cleanup EXIT
unzip -q "$PACKAGE" -d "$TMP/package"
rm -rf "$NEW"

if [[ -f "$TMP/package/app/config.py" && -f "$TMP/package/neural-runtime/service.py" ]]; then
  echo "=== INSTALL FULL v3.33.0 BACKEND PACKAGE ==="
  mkdir -p "$NEW"; cp -a "$TMP/package/." "$NEW/"
else
  echo "=== APPLY v3.33.0 UPGRADE TO VERIFIED v3.32.0 BACKEND ==="
  [[ -f "$TMP/package/APPLY_WORKSPACE_V33300.py" ]] || fail "upgrade package missing APPLY_WORKSPACE_V33300.py"
  [[ -d "$TMP/package/payload/backend" ]] || fail "upgrade package missing payload/backend"
  cp -a "$OLD" "$NEW"
  python3 "$TMP/package/APPLY_WORKSPACE_V33300.py" "$NEW" --payload "$TMP/package/payload"
fi
cp "$OLD/.env" "$NEW/.env"
cd "$NEW"
[[ -f docker-compose.yml ]] || cp docker-compose.example.yml docker-compose.yml

grep -q 'service_version: str = "3.33.0"' app/config.py || fail "v3.33.0 backend version marker missing"
grep -q 'SERVICE_VERSION = "3.33.0"' neural-runtime/service.py || fail "v3.33.0 neural runtime version marker missing"
for op in workspace.neural.graph-tensor-contract workspace.neural.graph-dataset-project workspace.neural.gnn-model-summary workspace.neural.gnn-forward workspace.neural.gnn-infer; do
  grep -q "$op" neural-runtime/service.py || fail "v3.33.0 GNN operation missing: $op"
done
python3 -m compileall -q app neural-runtime
[[ -f tests/test_neural_gnn_runtime_foundation_v33300.py ]] || fail "v3.33.0 GNN test payload missing"

echo "=== BUILD WORKSPACE v3.33.0 ==="
docker compose --env-file .env -f docker-compose.yml build sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker

echo "=== PRE-SWITCH GNN RUNTIME CERTIFICATION ==="
docker compose --env-file .env -f docker-compose.yml run --rm -T --no-deps --entrypoint python sc-workspace-neural-runtime - <<'PYCODE'
import service
from fastapi import HTTPException
h=service.health()
assert h['version']=='3.33.0',h
assert len(h['operations'])==57,h
assert h['graphNeuralNetworkRuntimeFoundation'] is True,h
assert h['gnnAdapters']==['gcn','graphsage-mean'],h
assert h['gnnTrainingEnabled'] is False,h
assert h['gnnExternalGraphReadEnabled'] is False,h
for op in ['workspace.neural.certification-plan','workspace.neural.certification-execute','workspace.neural.certification-verify','workspace.neural.certification-report']:
    assert op in h['operations'],(op,h)
assert h.get('productionCertificationEnabled') is True,h
assert h.get('clientSuppliedRemoteWorkerUrlsAllowed') is False,h

base={'seed':333,'nodeFeatures':[[1.0,0.0],[0.0,1.0],[1.0,1.0]],'nodeIds':['a','b','c'],'edges':[[0,1],[1,2]],'directed':False}
contract=service._graph_tensor_contract(dict(base))['graphTensorContract']
assert contract['nodeCount']==3 and contract['edgeCount']==2 and len(contract['artifactFingerprint'])==64,contract
projection=service._graph_dataset_project({'graphDataset':{'sourceFingerprint':'deploy-source','nodes':[{'id':'a','features':[1.0,0.0]},{'id':'b','features':[0.0,1.0]}],'edges':[{'source':'a','target':'b'}],'directed':True}})['graphProjectionArtifact']
assert projection['edges']==[[0,1]] and projection['inferredEdges'] is False and projection['inferredFeatures'] is False,projection

gcn={'schema':service.GNN_MODEL_SPEC_SCHEMA,'adapter':'gcn','inputFeatures':2,'outputFeatures':2,'activation':'relu','weights':[[1.0,0.5],[0.25,1.0]],'bias':[0.0,0.0],'addSelfLoops':True}
p=dict(base); p['modelSpec']=gcn
f=service._gnn_forward(p)
assert len(f['nodeEmbeddings'])==3 and len(f['nodeEmbeddings'][0])==2,f
assert f['gnnExecutionArtifact']['schema']==service.GNN_EXECUTION_ARTIFACT_SCHEMA,f

sage={'schema':service.GNN_MODEL_SPEC_SCHEMA,'adapter':'graphsage-mean','inputFeatures':2,'outputFeatures':1,'activation':'identity','weights':[[0.3],[0.2],[0.4],[0.1]],'bias':[0.0],'addSelfLoops':False}
p2=dict(base); p2['modelSpec']=sage; p2['task']='node-regression'
i=service._gnn_infer(p2)
assert len(i['predictions'])==3 and i['gnnPredictionArtifact']['isObservedEvidence'] is False,i
bad=dict(base); bad['edges']=[[0,99]]
try:
    service._graph_tensor_contract(bad); raise AssertionError('invalid edge accepted')
except HTTPException as exc:
    assert exc.status_code==400
bad_spec=dict(gcn); bad_spec['torchModuleBase64']='forbidden'
try:
    service._gnn_model_summary({'modelSpec':bad_spec}); raise AssertionError('serialized module accepted')
except HTTPException as exc:
    assert exc.status_code==400
print('NEURAL_V33300_GRAPH_TENSOR_CONTRACT=PASS')
print('NEURAL_V33300_GRAPH_DATASET_PROJECTION=PASS')
print('NEURAL_V33300_GCN_FORWARD=PASS')
print('NEURAL_V33300_GRAPHSAGE_INFERENCE=PASS')
print('NEURAL_V33300_SECURITY_BOUNDARY=PASS')
PYCODE

echo "=== SWITCH TO v3.33.0 ==="
docker rm -f sc-workspace-backend sc-workspace-worker sc-workspace-neural-runtime >/dev/null 2>&1 || true
docker compose --env-file .env -f docker-compose.yml up -d --no-deps sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker
SWITCHED=1
for i in $(seq 1 60); do
  code="$(curl -sS -o /tmp/scw33300-health.json -w '%{http_code}' http://127.0.0.1:8094/health 2>/dev/null || true)"
  echo "backend health attempt $i: HTTP $code"
  [[ "$code" == 200 ]] && break
  sleep 2
done
python3 - <<'PYCODE'
import json
x=json.load(open('/tmp/scw33300-health.json'))
assert x['ok'] is True and x['version']=='3.33.0',x
assert x.get('neuralRuntimeBoundedOperations')==57,x
assert x.get('graphNeuralNetworkRuntimeFoundation') is True,x
assert x.get('neuralGnnTrainingEnabled') is False,x
print('WORKSPACE_V33300_HEALTH=PASS')
PYCODE

echo "=== DIRECT NEURAL HEALTH ==="
docker exec -i sc-workspace-neural-runtime python - <<'PYCODE'
import json,urllib.request
x=json.load(urllib.request.urlopen('http://127.0.0.1:8101/health',timeout=5))
assert x['version']=='3.33.0' and len(x['operations'])==57,x
assert x['graphNeuralNetworkRuntimeFoundation'] is True,x
assert x['graphTensorContractSchema']=='sc-workspace-neural-graph-tensor-contract/1.0',x
assert x['gnnModelSpecSchema']=='sc-workspace-neural-gnn-model-spec/1.0',x
assert x['clientSuppliedRemoteWorkerUrlsAllowed'] is False,x
print('NEURAL_V33300_DIRECT_HEALTH=PASS engineVersion='+x['engineVersion'])
PYCODE

SERVICE_TOKEN="$(awk -F= '$1=="SC_WORKSPACE_SERVICE_TOKEN"{sub($1"=","");print;exit}' .env)"
[[ -n "$SERVICE_TOKEN" ]] || fail "SC_WORKSPACE_SERVICE_TOKEN blank"
AUTH=(-H "Authorization: Bearer $SERVICE_TOKEN" -H 'X-SC-User-ID: 1')
wait_job(){
  local id="$1" out="$2" label="$3"
  for i in $(seq 1 60); do
    curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${id}" >"$out"
    state="$(python3 -c "import json;print(json.load(open('$out'))['item']['status'])")"
    echo "$label attempt $i: $state"
    [[ "$state" == succeeded ]] && return 0
    [[ "$state" =~ ^(failed|blocked|cancelled)$ ]] && { cat "$out"; return 1; }
    sleep 2
  done
  return 1
}

echo "=== END-TO-END GNN FORWARD JOB ==="
STAMP="$(date +%s)"
cat >/tmp/scw33300-gnn-job.json <<JSON
{"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.neural.gnn-forward","priority":9,"maxAttempts":1,"idempotencyKey":"deploy-v33300-gnn-${STAMP}","payload":{"deviceRequest":"cpu","seed":333,"nodeFeatures":[[1.0,0.0],[0.0,1.0],[1.0,1.0]],"nodeIds":["a","b","c"],"edges":[[0,1],[1,2]],"directed":false,"modelSpec":{"schema":"sc-workspace-neural-gnn-model-spec/1.0","adapter":"gcn","inputFeatures":2,"outputFeatures":2,"activation":"relu","weights":[[1.0,0.5],[0.25,1.0]],"bias":[0.0,0.0],"addSelfLoops":true}}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/scw33300-gnn-job.json http://127.0.0.1:8094/v1/jobs >/tmp/scw33300-gnn-created.json
JOB_ID="$(python3 -c "import json;print(json.load(open('/tmp/scw33300-gnn-created.json'))['item']['jobId'])")"
wait_job "$JOB_ID" /tmp/scw33300-gnn-state.json "GNN forward"
python3 - <<'PYCODE'
import json
x=json.load(open('/tmp/scw33300-gnn-state.json')); item=x.get('item') or {}; jr=x.get('result') or {}; nr=jr['polyglot']['result']['remote']['result']
assert item.get('status')=='succeeded',item
art=nr.get('gnnExecutionArtifact') or {}; wa=nr.get('workspaceGnnArtifact') or {}
assert art.get('schema')=='sc-workspace-neural-gnn-execution-artifact/1.0',art
assert art.get('adapter')=='gcn' and art.get('isObservedEvidence') is False,art
assert wa.get('artifactId') and wa.get('mediaType')=='application/vnd.sc.workspace.neural-gnn-execution+json',wa
open('/tmp/scw33300-gnn-artifact-id.txt','w').write(wa['artifactId'])
open('/tmp/scw33300-gnn-receipt-id.txt','w').write(jr['receiptId'])
print('NEURAL_GNN_FORWARD_JOB=PASS jobId='+item['jobId'])
PYCODE
AID="$(cat /tmp/scw33300-gnn-artifact-id.txt)"; RID="$(cat /tmp/scw33300-gnn-receipt-id.txt)"
curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/artifacts/${AID}" >/tmp/scw33300-gnn-artifact.json
python3 - <<'PYCODE'
import base64,json
x=json.load(open('/tmp/scw33300-gnn-artifact.json')); item=x.get('item') or {}
assert item.get('mediaType')=='application/vnd.sc.workspace.neural-gnn-execution+json',item
art=json.loads(base64.b64decode(x['contentBase64']))
assert art['schema']=='sc-workspace-neural-gnn-execution-artifact/1.0' and len(art['artifactFingerprint'])==64,art
print('NEURAL_GNN_WORKSPACE_ARTIFACT=PASS')
PYCODE
curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/polyglot/receipts/${RID}" >/tmp/scw33300-gnn-receipt.json
python3 - <<'PYCODE'
import json
x=json.load(open('/tmp/scw33300-gnn-receipt.json')); d=(x.get('item') or {}).get('details') or {}
assert d.get('graphNeuralNetworkRuntimeFoundation') is True,d
assert d.get('gnnArtifactSchema')=='sc-workspace-neural-gnn-execution-artifact/1.0',d
assert d.get('workspaceGnnArtifactId'),d
assert d.get('isObservedEvidence') is False,d
print('NEURAL_GNN_RECEIPT_LINEAGE=PASS')
PYCODE

echo "=== OPENAPI / RUNTIME REGISTRY ==="
docker exec -i sc-workspace-backend python3 - <<'PYCODE'
from app.main import app
from app.client_contracts import TYPED_ENDPOINTS,profile
from app.polyglot import RUNTIME_BY_LANGUAGE
x=profile(app.openapi())
assert x['workspaceVersion']=='3.33.0' and x['typedEndpointCount']==291 and not x['missingOpenApiOperations'],x
n=RUNTIME_BY_LANGUAGE['neural']
assert len(n.operations)==57,n
for op in ['workspace.neural.graph-tensor-contract','workspace.neural.graph-dataset-project','workspace.neural.gnn-model-summary','workspace.neural.gnn-forward','workspace.neural.gnn-infer']:
    assert op in n.operations,(op,n)
print('WORKSPACE_V33300_OPENAPI_RUNTIME_REGISTRY=PASS typed_endpoints=%d'%len(TYPED_ENDPOINTS))
PYCODE

echo "=== CONTAINER HARDENING ==="
python3 - <<'PYCODE'
import json,subprocess
d=json.loads(subprocess.check_output(['docker','inspect','sc-workspace-neural-runtime']))[0]; h=d['HostConfig']; c=d['Config']
assert h['ReadonlyRootfs'] is True and c.get('User')=='65532:65532',d
assert 'ALL' in (h.get('CapDrop') or []) and 'no-new-privileges:true' in (h.get('SecurityOpt') or []),d
print('NEURAL_RUNTIME_HARDENING=PASS')
PYCODE

echo "PASS: Workspace v3.33.0 backend deployed; graph tensor contracts, explicit graph projection, GCN/GraphSAGE execution, GNN artifact persistence, receipt lineage, v3.32 certification continuity, registry integrity, and hardening verified"
trap - ERR
