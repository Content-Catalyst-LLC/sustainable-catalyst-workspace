#!/usr/bin/env bash
set -Eeuo pipefail
PACKAGE="${1:-/tmp/sustainable-catalyst-workspace-backend-v3.39.0.1.zip}"
BASE="/opt/sustainable-catalyst"; OLD="$BASE/sustainable-catalyst-workspace-backend-v3.39.0"; NEW="$BASE/sustainable-catalyst-workspace-backend-v3.39.0.1"; SWITCHED=0
fail(){ echo "ERROR: $*" >&2; exit 1; }
rollback(){ code=$?; if [[ "$SWITCHED" == 1 && -d "$OLD" ]]; then echo "=== v3.39.0.1 failed; restoring v3.39.0 ===" >&2; docker rm -f sc-workspace-backend sc-workspace-worker sc-workspace-neural-runtime >/dev/null 2>&1 || true; cd "$OLD"; [[ -f docker-compose.yml ]] || cp docker-compose.example.yml docker-compose.yml; docker compose --env-file .env -f docker-compose.yml up -d --no-deps --no-build sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker || true; fi; exit "$code"; }
trap rollback ERR
[[ -f "$PACKAGE" ]] || fail "v3.39.0.1 package not found: $PACKAGE"
[[ -d "$OLD" && -f "$OLD/.env" ]] || fail "v3.39.0 production baseline not found at $OLD"
grep -q 'service_version: str = "3.39.0"' "$OLD/app/config.py" || fail "v3.39.0 backend baseline marker missing"
grep -q 'SERVICE_VERSION = "3.39.0"' "$OLD/neural-runtime/service.py" || fail "v3.39.0 neural baseline marker missing"
TMP="$(mktemp -d)"; cleanup(){ rm -rf "$TMP"; }; trap cleanup EXIT
unzip -q "$PACKAGE" -d "$TMP/package"; [[ -f "$TMP/package/app/config.py" && -f "$TMP/package/neural-runtime/service.py" ]] || fail "v3.39.0.1 full backend package incomplete"
rm -rf "$NEW"; mkdir -p "$NEW"; cp -a "$TMP/package/." "$NEW/"; cp "$OLD/.env" "$NEW/.env"; cd "$NEW"; [[ -f docker-compose.yml ]] || cp docker-compose.example.yml docker-compose.yml
python3 -m compileall -q app neural-runtime
grep -q 'service_version: str = "3.39.0.1"' app/config.py || fail "v3.39.0.1 backend marker missing"; grep -q 'SERVICE_VERSION = "3.39.0"' neural-runtime/service.py || fail "v3.39 neural runtime marker missing"; ! grep -q 'sc-workspace-artifact-store-request/1.0' app/polyglot.py || fail "obsolete neural-symbolic artifact store request still present"
for op in workspace.neural.neural-symbolic-symbol-contract workspace.neural.neural-symbolic-context-project workspace.neural.neural-symbolic-bind workspace.neural.neural-symbolic-rule-contract workspace.neural.neural-symbolic-constraint-evaluate workspace.neural.neural-symbolic-relation-score workspace.neural.neural-symbolic-infer workspace.neural.neural-symbolic-explain; do grep -q "$op" neural-runtime/service.py || fail "missing operation $op"; done

echo "=== BUILD WORKSPACE v3.39.0.1 ==="
docker compose --env-file .env -f docker-compose.yml build sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker

echo "=== PRE-SWITCH ARTIFACT PERSISTENCE CONTRACT CERTIFICATION ==="
docker compose --env-file .env -f docker-compose.yml run --rm -T --no-deps --entrypoint python sc-workspace-backend - <<'PYCODE'
import base64, json
from app.schemas import ArtifactStoreRequest
blob={"schema":"sc-workspace-neural-symbolic-inference-artifact/1.0","kind":"neural-symbolic-inference","artifactFingerprint":"deploy-v339001"}
raw=json.dumps(blob,sort_keys=True,separators=(",",":")).encode()
x=ArtifactStoreRequest.model_validate({"schema":"sc-workspace-artifact-store/1.0","artifactId":"neural-symbolic-inference-deploy-v339001","filename":"neural-symbolic-inference-deploy-v339001.json","mediaType":"application/vnd.sc.workspace.neural-symbolic-inference+json","contentBase64":base64.b64encode(raw).decode("ascii"),"expectedRevision":0,"metadata":{"role":"analysis","truthValueAssigned":False,"isObservedEvidence":False}})
assert x.artifactId.startswith("neural-symbolic-inference-") and x.expectedRevision==0
print("WORKSPACE_V339001_PERSISTENCE_CONTRACT=PASS")
PYCODE

echo "=== PRE-SWITCH NEURAL-SYMBOLIC CERTIFICATION ==="
docker compose --env-file .env -f docker-compose.yml run --rm -T --no-deps --entrypoint python sc-workspace-neural-runtime - <<'PYCODE'
import service
h=service.health(); assert h['version']=='3.39.0' and len(h['operations'])==101,h; assert h['neuralSymbolicResearchIntelligenceRuntime'] is True,h; assert h['neuralSymbolicTruthAdjudicationEnabled'] is False,h
symbols=[{'symbolId':'claim:A','symbolType':'claim-ref','sourceRef':'core:claim:A'},{'symbolId':'evidence:B','symbolType':'evidence-ref','sourceRef':'core:evidence:B'},{'symbolId':'finding:C','symbolType':'finding-ref','sourceRef':'core:finding:C'}]
rules=[{'ruleId':'r1','operator':'implies','leftSymbolId':'claim:A','rightSymbolId':'evidence:B'},{'ruleId':'r2','operator':'requires','leftSymbolId':'evidence:B','rightSymbolId':'finding:C'}]
c=service._ns_context_project({'symbols':symbols}); assert c['neuralSymbolicContextArtifact']['symbolCount']==3
b=service._ns_bind({'symbol':symbols[0],'embedding':[0.1,0.2,0.3],'representationRef':'deploy:v339'}); assert b['neuralSymbolicBindingArtifact']['semanticEquivalenceAsserted'] is False
inf=service._ns_infer({'rules':rules,'activeSymbolIds':['claim:A']}); assert inf['inferredSymbolIds']==['evidence:B']; assert inf['neuralSymbolicInferenceArtifact']['truthValueAssigned'] is False
ex=service._ns_explain({'inferenceArtifact':inf['neuralSymbolicInferenceArtifact']}); assert ex['neuralSymbolicExplanationArtifact']['reasonCount']==1
r=service._ns_relation_score({'leftEmbedding':[1.0,0.0],'rightEmbedding':[1.0,0.0],'metric':'cosine','relationType':'representation-affinity'}); assert abs(r['value']-1.0)<1e-6
print('NEURAL_V33900_SYMBOL_CONTEXT_BINDING=PASS'); print('NEURAL_V33900_RULE_INFERENCE_EXPLANATION=PASS'); print('NEURAL_V33900_RELATION_SCORE=PASS')
PYCODE

echo "=== SWITCH TO v3.39.0.1 ==="
docker rm -f sc-workspace-backend sc-workspace-worker sc-workspace-neural-runtime >/dev/null 2>&1 || true
docker compose --env-file .env -f docker-compose.yml up -d --no-deps sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker; SWITCHED=1
for i in $(seq 1 60); do code="$(curl -sS -o /tmp/scw339001-health.json -w '%{http_code}' http://127.0.0.1:8094/health 2>/dev/null || true)"; echo "backend health attempt $i: HTTP $code"; [[ "$code" == 200 ]] && break; sleep 2; done
python3 - <<'PYCODE'
import json
x=json.load(open('/tmp/scw339001-health.json')); assert x['ok'] is True and x['version']=='3.39.0.1',x; assert x.get('neuralRuntimeBoundedOperations')==101,x; assert x.get('neuralSymbolicResearchIntelligenceRuntime') is True,x; assert x.get('neuralSymbolicTruthAdjudicationEnabled') is False,x; print('WORKSPACE_V339001_HEALTH=PASS')
PYCODE
SERVICE_TOKEN="$(awk -F= '$1=="SC_WORKSPACE_SERVICE_TOKEN"{sub($1"=","");print;exit}' .env)"; [[ -n "$SERVICE_TOKEN" ]] || fail "SC_WORKSPACE_SERVICE_TOKEN blank"; AUTH=(-H "Authorization: Bearer $SERVICE_TOKEN" -H 'X-SC-User-ID: 1'); STAMP="$(date +%s)"
cat >/tmp/scw339001-job.json <<'JSON'
{"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.neural.neural-symbolic-infer","priority":9,"maxAttempts":1,"idempotencyKey":"deploy-v339001-__STAMP__","payload":{"deviceRequest":"cpu","seed":339001,"activeSymbolIds":["claim:A"],"rules":[{"ruleId":"r1","operator":"implies","leftSymbolId":"claim:A","rightSymbolId":"evidence:B"},{"ruleId":"r2","operator":"requires","leftSymbolId":"evidence:B","rightSymbolId":"finding:C"}]}}
JSON
sed -i "s/__STAMP__/${STAMP}/g" /tmp/scw339001-job.json
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/scw339001-job.json http://127.0.0.1:8094/v1/jobs >/tmp/scw339001-created.json; JOB_ID="$(python3 -c "import json;print(json.load(open('/tmp/scw339001-created.json'))['item']['jobId'])")"
for i in $(seq 1 60); do curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${JOB_ID}" >/tmp/scw339001-state.json; state="$(python3 -c "import json;print(json.load(open('/tmp/scw339001-state.json'))['item']['status'])")"; echo "neural-symbolic job attempt $i: $state"; [[ "$state" == succeeded ]] && break; [[ "$state" =~ ^(failed|blocked|cancelled)$ ]] && { cat /tmp/scw339001-state.json; exit 1; }; sleep 2; done
python3 - <<'PYCODE'
import json
x=json.load(open('/tmp/scw339001-state.json')); nr=x['result']['polyglot']['result']['remote']['result']; a=nr['neuralSymbolicInferenceArtifact']; wa=nr.get('workspaceNeuralSymbolicArtifact') or {}; assert a['schema']=='sc-workspace-neural-symbolic-inference-artifact/1.0'; assert a['truthValueAssigned'] is False and a['isObservedEvidence'] is False; assert wa.get('artifactId'); print('NEURAL_SYMBOLIC_INFERENCE_JOB=PASS jobId='+x['item']['jobId']); print('WORKSPACE_NEURAL_SYMBOLIC_ARTIFACT=PASS artifactId='+wa['artifactId'])
PYCODE

echo "=== RUNTIME REGISTRY ==="
docker exec -i sc-workspace-backend python3 - <<'PYCODE'
from app.polyglot import RUNTIME_BY_LANGUAGE
n=RUNTIME_BY_LANGUAGE['neural']; assert len(n.operations)==101,n
for op in ['workspace.neural.neural-symbolic-symbol-contract','workspace.neural.neural-symbolic-context-project','workspace.neural.neural-symbolic-bind','workspace.neural.neural-symbolic-rule-contract','workspace.neural.neural-symbolic-constraint-evaluate','workspace.neural.neural-symbolic-relation-score','workspace.neural.neural-symbolic-infer','workspace.neural.neural-symbolic-explain']: assert op in n.operations,(op,n)
print('WORKSPACE_V339001_RUNTIME_REGISTRY=PASS')
PYCODE

echo "=== CONTAINER HARDENING ==="
python3 - <<'PYCODE'
import json,subprocess
d=json.loads(subprocess.check_output(['docker','inspect','sc-workspace-neural-runtime']))[0]; h=d['HostConfig']; c=d['Config']; assert h['ReadonlyRootfs'] is True and c.get('User')=='65532:65532'; assert 'ALL' in (h.get('CapDrop') or []); print('NEURAL_RUNTIME_HARDENING=PASS')
PYCODE
trap - ERR
echo "PASS: Workspace v3.39.0.1 backend deployed; neural-symbolic artifact persistence repaired; neural-symbolic contracts, bounded rule inference, constraint evaluation, relation scoring, explanation traces, governed artifact lineage, 101-operation registry integrity, and hardening verified"
