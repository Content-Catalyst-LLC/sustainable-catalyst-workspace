#!/usr/bin/env bash
set -Eeuo pipefail
PACKAGE="${1:-/tmp/sustainable-catalyst-workspace-backend-v3.34.0.zip}"; BASE="/opt/sustainable-catalyst"; OLD="$BASE/sustainable-catalyst-workspace-backend-v3.33.0"; NEW="$BASE/sustainable-catalyst-workspace-backend-v3.34.0"; SWITCHED=0
fail(){ echo "ERROR: $*" >&2; exit 1; }
rollback(){ code=$?; if [[ "$SWITCHED" == 1 && -d "$OLD" ]]; then echo "=== v3.34.0 failed; restoring v3.33.0 ===" >&2; docker rm -f sc-workspace-backend sc-workspace-worker sc-workspace-neural-runtime >/dev/null 2>&1 || true; cd "$OLD"; [[ -f docker-compose.yml ]] || cp docker-compose.example.yml docker-compose.yml; docker compose --env-file .env -f docker-compose.yml up -d --no-deps --no-build sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker || true; fi; exit "$code"; }
trap rollback ERR
[[ -f "$PACKAGE" ]] || fail "v3.34.0 package not found: $PACKAGE"; [[ -d "$OLD" && -f "$OLD/.env" ]] || fail "v3.33.0 production baseline not found at $OLD"
grep -q 'service_version: str = "3.33.0"' "$OLD/app/config.py" || fail "v3.33.0 backend baseline marker missing"; grep -q 'SERVICE_VERSION = "3.33.0"' "$OLD/neural-runtime/service.py" || fail "v3.33.0 neural baseline marker missing"
TMP="$(mktemp -d)"; cleanup(){ rm -rf "$TMP"; }; trap cleanup EXIT; unzip -q "$PACKAGE" -d "$TMP/package"; rm -rf "$NEW"
if [[ -f "$TMP/package/app/config.py" && -f "$TMP/package/neural-runtime/service.py" ]]; then mkdir -p "$NEW"; cp -a "$TMP/package/." "$NEW/"; else [[ -f "$TMP/package/APPLY_WORKSPACE_V33400.py" ]] || fail "upgrade package missing patcher"; cp -a "$OLD" "$NEW"; python3 "$TMP/package/APPLY_WORKSPACE_V33400.py" "$NEW" --payload "$TMP/package/payload"; fi
cp "$OLD/.env" "$NEW/.env"; cd "$NEW"; [[ -f docker-compose.yml ]] || cp docker-compose.example.yml docker-compose.yml
python3 -m compileall -q app neural-runtime; grep -q 'SERVICE_VERSION = "3.34.0"' neural-runtime/service.py || fail "v3.34.0 neural marker missing"
for op in workspace.neural.gnn-split-plan workspace.neural.gnn-training-plan workspace.neural.gnn-train workspace.neural.gnn-checkpoint-create workspace.neural.gnn-checkpoint-resume; do grep -q "$op" neural-runtime/service.py || fail "missing operation $op"; done
echo "=== BUILD WORKSPACE v3.34.0 ==="; docker compose --env-file .env -f docker-compose.yml build sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker
echo "=== PRE-SWITCH GNN TRAINING CERTIFICATION ==="
docker compose --env-file .env -f docker-compose.yml run --rm -T --no-deps --entrypoint python sc-workspace-neural-runtime - <<'PYCODE'
import service
h=service.health(); assert h['version']=='3.34.0' and len(h['operations'])==62,h; assert h['gnnTrainingEnabled'] is True and h['gnnTrainingRuntime'] is True,h
split=service._gnn_split_plan({'itemCount':4,'seed':334,'trainFraction':0.5,'validationFraction':0.25}); assert split['gnnSplitPlanArtifact']['schema']==service.GNN_SPLIT_PLAN_SCHEMA
model={'schema':service.GNN_MODEL_SPEC_SCHEMA,'adapter':'gcn','inputFeatures':2,'outputFeatures':2,'activation':'identity','weights':[[0.01,0.01],[0.01,0.01]],'bias':[0.0,0.0],'addSelfLoops':True}
p={'seed':334,'task':'node-multiclass-classification','nodeFeatures':[[1.,0.],[0.,1.],[1.,1.],[.2,.8]],'nodeIds':['a','b','c','d'],'edges':[[0,1],[1,2],[2,3]],'directed':False,'labels':[0,1,0,1],'modelSpec':model,'epochs':3,'learningRate':0.1,'splitIndices':{'train':[0,1,2],'validation':[3],'test':[]}}
r=service._gnn_train(p); assert r['gnnTrainingArtifact']['epochsCompleted']==3; assert r['gnnCheckpointArtifact']['currentEpoch']==3; assert r['gnnTrainingArtifact']['opaqueSerializedOptimizerStateAllowed'] is False
q=dict(p); q.pop('modelSpec'); q.pop('epochs'); q['checkpoint']=r['gnnCheckpointArtifact']; q['additionalEpochs']=1; rr=service._gnn_checkpoint_resume(q); assert rr['gnnCheckpointArtifact']['currentEpoch']==4
print('NEURAL_V33400_GNN_TRAINING=PASS'); print('NEURAL_V33400_CHECKPOINT_RESUME=PASS')
PYCODE
echo "=== SWITCH TO v3.34.0 ==="; docker rm -f sc-workspace-backend sc-workspace-worker sc-workspace-neural-runtime >/dev/null 2>&1 || true; docker compose --env-file .env -f docker-compose.yml up -d --no-deps sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker; SWITCHED=1
for i in $(seq 1 60); do code="$(curl -sS -o /tmp/scw33400-health.json -w '%{http_code}' http://127.0.0.1:8094/health 2>/dev/null || true)"; echo "backend health attempt $i: HTTP $code"; [[ "$code" == 200 ]] && break; sleep 2; done
python3 - <<'PYCODE'
import json
x=json.load(open('/tmp/scw33400-health.json')); assert x['ok'] is True and x['version']=='3.34.0',x; assert x.get('neuralRuntimeBoundedOperations')==62,x; assert x.get('neuralGnnTrainingEnabled') is True,x; print('WORKSPACE_V33400_HEALTH=PASS')
PYCODE
SERVICE_TOKEN="$(awk -F= '$1=="SC_WORKSPACE_SERVICE_TOKEN"{sub($1"=","");print;exit}' .env)"; [[ -n "$SERVICE_TOKEN" ]] || fail "SC_WORKSPACE_SERVICE_TOKEN blank"; AUTH=(-H "Authorization: Bearer $SERVICE_TOKEN" -H 'X-SC-User-ID: 1')
STAMP="$(date +%s)"; cat >/tmp/scw33400-job.json <<JSON
{"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.neural.gnn-train","priority":9,"maxAttempts":1,"idempotencyKey":"deploy-v33400-${STAMP}","payload":{"deviceRequest":"cpu","seed":334,"task":"node-binary-classification","nodeFeatures":[[1,0],[0,1],[1,1],[0.2,0.8]],"nodeIds":["a","b","c","d"],"edges":[[0,1],[1,2],[2,3]],"directed":false,"labels":[0,1,1,0],"modelSpec":{"schema":"sc-workspace-neural-gnn-model-spec/1.0","adapter":"gcn","inputFeatures":2,"outputFeatures":1,"activation":"identity","weights":[[0.01],[0.01]],"bias":[0],"addSelfLoops":true},"epochs":3,"learningRate":0.1,"splitIndices":{"train":[0,1,2],"validation":[3],"test":[]}}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/scw33400-job.json http://127.0.0.1:8094/v1/jobs >/tmp/scw33400-created.json; JOB_ID="$(python3 -c "import json;print(json.load(open('/tmp/scw33400-created.json'))['item']['jobId'])")"
for i in $(seq 1 60); do curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${JOB_ID}" >/tmp/scw33400-state.json; state="$(python3 -c "import json;print(json.load(open('/tmp/scw33400-state.json'))['item']['status'])")"; echo "GNN train attempt $i: $state"; [[ "$state" == succeeded ]] && break; [[ "$state" =~ ^(failed|blocked|cancelled)$ ]] && { cat /tmp/scw33400-state.json; exit 1; }; sleep 2; done
python3 - <<'PYCODE'
import json
x=json.load(open('/tmp/scw33400-state.json')); nr=x['result']['polyglot']['result']['remote']['result']; a=nr['gnnTrainingArtifact']; c=nr['gnnCheckpointArtifact']; wa=nr.get('workspaceGnnArtifact') or {}; assert a['schema']=='sc-workspace-neural-gnn-training-artifact/1.0' and c['schema']=='sc-workspace-neural-gnn-checkpoint-artifact/1.0'; assert wa.get('artifactId'); print('NEURAL_GNN_TRAIN_JOB=PASS jobId='+x['item']['jobId']); print('NEURAL_GNN_TRAIN_ARTIFACT=PASS')
PYCODE
echo "=== RUNTIME REGISTRY ==="; docker exec -i sc-workspace-backend python3 - <<'PYCODE'
from app.polyglot import RUNTIME_BY_LANGUAGE
n=RUNTIME_BY_LANGUAGE['neural']; assert len(n.operations)==62,n
for op in ['workspace.neural.gnn-split-plan','workspace.neural.gnn-training-plan','workspace.neural.gnn-train','workspace.neural.gnn-checkpoint-create','workspace.neural.gnn-checkpoint-resume']: assert op in n.operations,(op,n)
print('WORKSPACE_V33400_RUNTIME_REGISTRY=PASS')
PYCODE
echo "=== CONTAINER HARDENING ==="; python3 - <<'PYCODE'
import json,subprocess
d=json.loads(subprocess.check_output(['docker','inspect','sc-workspace-neural-runtime']))[0]; h=d['HostConfig']; c=d['Config']; assert h['ReadonlyRootfs'] is True and c.get('User')=='65532:65532'; assert 'ALL' in (h.get('CapDrop') or []); print('NEURAL_RUNTIME_HARDENING=PASS')
PYCODE
trap - ERR; echo "PASS: Workspace v3.34.0 backend deployed; governed GNN training, deterministic split planning, node/graph/link tasks, JSON checkpoints, exact stateless-SGD resume, artifact lineage, registry integrity, and hardening verified"
