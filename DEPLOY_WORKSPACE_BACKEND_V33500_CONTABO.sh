#!/usr/bin/env bash
set -Eeuo pipefail
PACKAGE="${1:-/tmp/sustainable-catalyst-workspace-backend-v3.35.0.zip}"
BASE="/opt/sustainable-catalyst"
OLD="$BASE/sustainable-catalyst-workspace-backend-v3.34.0"
NEW="$BASE/sustainable-catalyst-workspace-backend-v3.35.0"
SWITCHED=0
fail(){ echo "ERROR: $*" >&2; exit 1; }
rollback(){ code=$?; if [[ "$SWITCHED" == 1 && -d "$OLD" ]]; then echo "=== v3.35.0 failed; restoring v3.34.0 ===" >&2; docker rm -f sc-workspace-backend sc-workspace-worker sc-workspace-neural-runtime >/dev/null 2>&1 || true; cd "$OLD"; [[ -f docker-compose.yml ]] || cp docker-compose.example.yml docker-compose.yml; docker compose --env-file .env -f docker-compose.yml up -d --no-deps --no-build sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker || true; fi; exit "$code"; }
trap rollback ERR
[[ -f "$PACKAGE" ]] || fail "v3.35.0 package not found: $PACKAGE"
[[ -d "$OLD" && -f "$OLD/.env" ]] || fail "v3.34.0 production baseline not found at $OLD"
grep -q 'service_version: str = "3.34.0"' "$OLD/app/config.py" || fail "v3.34.0 backend baseline marker missing"
grep -q 'SERVICE_VERSION = "3.34.0"' "$OLD/neural-runtime/service.py" || fail "v3.34.0 neural baseline marker missing"
TMP="$(mktemp -d)"; cleanup(){ rm -rf "$TMP"; }; trap cleanup EXIT
unzip -q "$PACKAGE" -d "$TMP/package"
[[ -f "$TMP/package/app/config.py" && -f "$TMP/package/neural-runtime/service.py" ]] || fail "v3.35.0 full backend package is incomplete"
rm -rf "$NEW"; mkdir -p "$NEW"; cp -a "$TMP/package/." "$NEW/"; cp "$OLD/.env" "$NEW/.env"
cd "$NEW"; [[ -f docker-compose.yml ]] || cp docker-compose.example.yml docker-compose.yml
python3 -m compileall -q app neural-runtime
grep -q 'service_version: str = "3.35.0"' app/config.py || fail "v3.35.0 backend marker missing"
grep -q 'SERVICE_VERSION = "3.35.0"' neural-runtime/service.py || fail "v3.35.0 neural marker missing"
for op in workspace.neural.gnn-evaluate workspace.neural.gnn-calibration-report workspace.neural.gnn-explain-gradient workspace.neural.gnn-explain-occlusion workspace.neural.gnn-embedding-extract workspace.neural.gnn-embedding-similarity workspace.neural.gnn-embedding-neighbors; do grep -q "$op" neural-runtime/service.py || fail "missing operation $op"; done

echo "=== BUILD WORKSPACE v3.35.0 ==="
docker compose --env-file .env -f docker-compose.yml build sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker

echo "=== PRE-SWITCH GNN ANALYSIS CERTIFICATION ==="
docker compose --env-file .env -f docker-compose.yml run --rm -T --no-deps --entrypoint python sc-workspace-neural-runtime - <<'PYCODE'
import service
h=service.health(); assert h['version']=='3.35.0' and len(h['operations'])==69,h; assert h['gnnEvaluationExplainabilityEmbeddingsEnabled'] is True,h
model={'schema':service.GNN_MODEL_SPEC_SCHEMA,'adapter':'gcn','inputFeatures':2,'outputFeatures':2,'activation':'identity','weights':[[0.6,0.15],[0.15,0.6]],'bias':[0.0,0.0],'addSelfLoops':True}
g={'nodeFeatures':[[1.,0.],[0.,1.],[1.,1.],[.2,.8]],'nodeIds':['a','b','c','d'],'edges':[[0,1],[1,2],[2,3]],'directed':False,'modelSpec':model}
p=dict(g); p.update({'task':'node-multiclass-classification','labels':[0,1,0,1]}); e=service._gnn_evaluate(p); assert e['gnnEvaluationArtifact']['schema']==service.GNN_EVALUATION_ARTIFACT_SCHEMA
c=dict(p); c['bins']=4; cal=service._gnn_calibration_report(c); assert cal['gnnCalibrationArtifact']['schema']==service.GNN_CALIBRATION_ARTIFACT_SCHEMA
x=dict(g); x.update({'targetNodeIndex':2,'targetOutputIndex':1}); ex=service._gnn_explain_gradient(x); assert ex['gnnExplainabilityArtifact']['isObservedEvidence'] is False
em=service._gnn_embedding_extract(g); assert len(em['nodeEmbeddings'])==4 and len(em['graphEmbedding'])==2
si=dict(g); si.update({'metric':'cosine','pairs':[[0,1],[0,2]]}); assert len(service._gnn_embedding_similarity(si)['results'])==2
nn=dict(g); nn.update({'metric':'cosine','queryNodeIndices':[0],'topK':2}); assert len(service._gnn_embedding_neighbors(nn)['results'][0]['neighbors'])==2
print('NEURAL_V33500_GNN_EVALUATION=PASS'); print('NEURAL_V33500_GNN_EXPLAINABILITY=PASS'); print('NEURAL_V33500_GNN_EMBEDDINGS=PASS')
PYCODE

echo "=== SWITCH TO v3.35.0 ==="
docker rm -f sc-workspace-backend sc-workspace-worker sc-workspace-neural-runtime >/dev/null 2>&1 || true
docker compose --env-file .env -f docker-compose.yml up -d --no-deps sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker
SWITCHED=1
for i in $(seq 1 60); do code="$(curl -sS -o /tmp/scw33500-health.json -w '%{http_code}' http://127.0.0.1:8094/health 2>/dev/null || true)"; echo "backend health attempt $i: HTTP $code"; [[ "$code" == 200 ]] && break; sleep 2; done
python3 - <<'PYCODE'
import json
x=json.load(open('/tmp/scw33500-health.json')); assert x['ok'] is True and x['version']=='3.35.0',x; assert x.get('neuralRuntimeBoundedOperations')==69,x; assert x.get('neuralGnnEvaluationExplainabilityEmbeddings') is True,x; print('WORKSPACE_V33500_HEALTH=PASS')
PYCODE
SERVICE_TOKEN="$(awk -F= '$1=="SC_WORKSPACE_SERVICE_TOKEN"{sub($1"=","");print;exit}' .env)"; [[ -n "$SERVICE_TOKEN" ]] || fail "SC_WORKSPACE_SERVICE_TOKEN blank"
AUTH=(-H "Authorization: Bearer $SERVICE_TOKEN" -H 'X-SC-User-ID: 1')
STAMP="$(date +%s)"
cat >/tmp/scw33500-job.json <<JSON
{"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.neural.gnn-evaluate","priority":9,"maxAttempts":1,"idempotencyKey":"deploy-v33500-${STAMP}","payload":{"deviceRequest":"cpu","seed":335,"task":"node-binary-classification","nodeFeatures":[[1,0],[0,1],[1,1],[0.2,0.8]],"nodeIds":["a","b","c","d"],"edges":[[0,1],[1,2],[2,3]],"directed":false,"labels":[0,1,1,0],"modelSpec":{"schema":"sc-workspace-neural-gnn-model-spec/1.0","adapter":"gcn","inputFeatures":2,"outputFeatures":1,"activation":"identity","weights":[[0.6],[0.2]],"bias":[0],"addSelfLoops":true}}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/scw33500-job.json http://127.0.0.1:8094/v1/jobs >/tmp/scw33500-created.json
JOB_ID="$(python3 -c "import json;print(json.load(open('/tmp/scw33500-created.json'))['item']['jobId'])")"
for i in $(seq 1 60); do curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${JOB_ID}" >/tmp/scw33500-state.json; state="$(python3 -c "import json;print(json.load(open('/tmp/scw33500-state.json'))['item']['status'])")"; echo "GNN evaluation attempt $i: $state"; [[ "$state" == succeeded ]] && break; [[ "$state" =~ ^(failed|blocked|cancelled)$ ]] && { cat /tmp/scw33500-state.json; exit 1; }; sleep 2; done
python3 - <<'PYCODE'
import json
x=json.load(open('/tmp/scw33500-state.json')); nr=x['result']['polyglot']['result']['remote']['result']; a=nr['gnnEvaluationArtifact']; wa=nr.get('workspaceGnnArtifact') or {}; assert a['schema']=='sc-workspace-neural-gnn-evaluation-artifact/1.0'; assert wa.get('artifactId'); print('NEURAL_GNN_EVALUATION_JOB=PASS jobId='+x['item']['jobId']); print('NEURAL_GNN_EVALUATION_ARTIFACT=PASS artifactId='+wa['artifactId'])
PYCODE

echo "=== RUNTIME REGISTRY ==="
docker exec -i sc-workspace-backend python3 - <<'PYCODE'
from app.polyglot import RUNTIME_BY_LANGUAGE
n=RUNTIME_BY_LANGUAGE['neural']; assert len(n.operations)==69,n
for op in ['workspace.neural.gnn-evaluate','workspace.neural.gnn-calibration-report','workspace.neural.gnn-explain-gradient','workspace.neural.gnn-explain-occlusion','workspace.neural.gnn-embedding-extract','workspace.neural.gnn-embedding-similarity','workspace.neural.gnn-embedding-neighbors']: assert op in n.operations,(op,n)
print('WORKSPACE_V33500_RUNTIME_REGISTRY=PASS')
PYCODE

echo "=== CONTAINER HARDENING ==="
python3 - <<'PYCODE'
import json,subprocess
d=json.loads(subprocess.check_output(['docker','inspect','sc-workspace-neural-runtime']))[0]; h=d['HostConfig']; c=d['Config']; assert h['ReadonlyRootfs'] is True and c.get('User')=='65532:65532'; assert 'ALL' in (h.get('CapDrop') or []); print('NEURAL_RUNTIME_HARDENING=PASS')
PYCODE
trap - ERR
echo "PASS: Workspace v3.35.0 backend deployed; GNN evaluation, calibration, explainability, graph embeddings, governed artifact lineage, 69-operation registry integrity, and hardening verified"
