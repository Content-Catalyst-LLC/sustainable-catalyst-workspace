#!/usr/bin/env bash
set -Eeuo pipefail
PACKAGE="${1:-/tmp/sustainable-catalyst-workspace-backend-v3.40.0.zip}"; BASE="/opt/sustainable-catalyst"; SOURCE="$BASE/sustainable-catalyst-workspace-backend-v3.39.0.1"; ROLLBACK="$SOURCE"; NEW="$BASE/sustainable-catalyst-workspace-backend-v3.40.0"; SWITCHED=0
fail(){ echo "ERROR: $*" >&2; exit 1; }
rollback(){ code=$?; if [[ "$SWITCHED" == 1 && -d "$ROLLBACK" ]]; then echo '=== v3.40.0 failed; restoring v3.39.0.1 ===' >&2; docker rm -f sc-workspace-backend sc-workspace-worker sc-workspace-neural-runtime >/dev/null 2>&1 || true; cd "$ROLLBACK"; [[ -f docker-compose.yml ]] || cp docker-compose.example.yml docker-compose.yml; docker compose --env-file .env -f docker-compose.yml up -d --no-deps --no-build sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker || true; fi; exit "$code"; }
trap rollback ERR
[[ -f "$PACKAGE" ]] || fail "package not found: $PACKAGE"; [[ -d "$SOURCE" && -f "$SOURCE/.env" ]] || fail "v3.39.0.1 production baseline not found at $SOURCE"; grep -q 'service_version: str = "3.39.0.1"' "$SOURCE/app/config.py" || fail 'v3.39.0.1 baseline marker missing'
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT; unzip -q "$PACKAGE" -d "$TMP/package"; rm -rf "$NEW"; mkdir -p "$NEW"; cp -a "$TMP/package/." "$NEW/"; cp "$SOURCE/.env" "$NEW/.env"; cd "$NEW"; [[ -f docker-compose.yml ]] || cp docker-compose.example.yml docker-compose.yml
python3 -m compileall -q app neural-runtime; grep -q 'service_version: str = "3.40.0"' app/config.py || fail 'v3.40.0 backend marker missing'; grep -q 'SERVICE_VERSION = "3.40.0"' neural-runtime/service.py || fail 'v3.40.0 neural marker missing'
echo '=== BUILD WORKSPACE v3.40.0 ==='; docker compose --env-file .env -f docker-compose.yml build sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker

echo '=== PRE-SWITCH RESEARCH PACKAGE CERTIFICATION ==='
docker compose --env-file .env -f docker-compose.yml run --rm -T --no-deps --entrypoint python sc-workspace-neural-runtime - <<'PYCODE'
import importlib.util
spec=importlib.util.spec_from_file_location('svc','/app/service.py'); s=importlib.util.module_from_spec(spec); spec.loader.exec_module(s)
c=[
 {'componentId':'dataset','artifactId':'dataset-a','role':'dataset','schema':'sc-workspace-neural-dataset-manifest/1.0','sha256':'1'*64,'bytes':1024,'operation':'workspace.neural.dataset-manifest','requiredForReproduction':True,'dependsOn':[]},
 {'componentId':'model','artifactId':'model-a','role':'model-package','schema':'sc-workspace-neural-model-package/1.0','sha256':'2'*64,'bytes':2048,'operation':'workspace.neural.package-create','requiredForReproduction':True,'dependsOn':['dataset']},
 {'componentId':'eval','artifactId':'eval-a','role':'evaluation','schema':'sc-workspace-neural-evaluation-artifact/1.0','sha256':'3'*64,'bytes':512,'operation':'workspace.neural.evaluate-regression','requiredForReproduction':False,'dependsOn':['model']},]
p=s._research_package_create({'components':c,'title':'deploy-v34000','seed':3400})['deepLearningResearchPackage']; assert s._research_package_verify({'researchPackage':p})['valid'] is True; assert s._research_package_reproduction_verify({'researchPackage':p,'observedComponents':c})['classification']=='exact'; assert len(s.OPERATIONS)==109
print('NEURAL_V34000_RESEARCH_PACKAGE=PASS')
print('NEURAL_V34000_REPRODUCTION_VERIFY=PASS')
print('NEURAL_V34000_REGISTRY=PASS')
PYCODE

echo '=== SWITCH TO v3.40.0 ==='; docker rm -f sc-workspace-backend sc-workspace-worker sc-workspace-neural-runtime >/dev/null 2>&1 || true; docker compose --env-file .env -f docker-compose.yml up -d --no-deps sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker; SWITCHED=1
for i in $(seq 1 60); do code="$(curl -sS -o /tmp/scw34000-health.json -w '%{http_code}' http://127.0.0.1:8094/health 2>/dev/null || true)"; echo "backend health attempt $i: HTTP $code"; [[ "$code" == 200 ]] && break; sleep 2; done
python3 - <<'PYCODE'
import json
x=json.load(open('/tmp/scw34000-health.json')); assert x['ok'] is True and x['version']=='3.40.0',x; assert x.get('neuralRuntimeBoundedOperations')==109,x; assert x.get('reproducibleDeepLearningResearchPackagesRuntime') is True,x; print('WORKSPACE_V34000_HEALTH=PASS')
PYCODE
SERVICE_TOKEN="$(awk -F= '$1=="SC_WORKSPACE_SERVICE_TOKEN"{sub($1"=","");print;exit}' .env)"; [[ -n "$SERVICE_TOKEN" ]] || fail 'SC_WORKSPACE_SERVICE_TOKEN blank'; AUTH=(-H "Authorization: Bearer $SERVICE_TOKEN" -H 'X-SC-User-ID: 1'); STAMP="$(date +%s)"
cat >/tmp/scw34000-job.json <<'JSON'
{"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.neural.research-package-create","priority":9,"maxAttempts":1,"idempotencyKey":"deploy-v34000-__STAMP__","payload":{"deviceRequest":"cpu","seed":3400,"title":"Production certification package","components":[{"componentId":"dataset","artifactId":"dataset-prod","role":"dataset","schema":"sc-workspace-neural-dataset-manifest/1.0","sha256":"1111111111111111111111111111111111111111111111111111111111111111","bytes":1024,"operation":"workspace.neural.dataset-manifest","requiredForReproduction":true,"dependsOn":[]},{"componentId":"model","artifactId":"model-prod","role":"model-package","schema":"sc-workspace-neural-model-package/1.0","sha256":"2222222222222222222222222222222222222222222222222222222222222222","bytes":2048,"operation":"workspace.neural.package-create","requiredForReproduction":true,"dependsOn":["dataset"]}]}}
JSON
sed -i "s/__STAMP__/${STAMP}/g" /tmp/scw34000-job.json; curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/scw34000-job.json http://127.0.0.1:8094/v1/jobs >/tmp/scw34000-created.json; JOB_ID="$(python3 -c "import json;print(json.load(open('/tmp/scw34000-created.json'))['item']['jobId'])")"
for i in $(seq 1 60); do curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${JOB_ID}" >/tmp/scw34000-state.json; state="$(python3 -c "import json;print(json.load(open('/tmp/scw34000-state.json'))['item']['status'])")"; echo "research package job attempt $i: $state"; [[ "$state" == succeeded ]] && break; [[ "$state" =~ ^(failed|blocked|cancelled)$ ]] && { cat /tmp/scw34000-state.json; exit 1; }; sleep 2; done
python3 - <<'PYCODE'
import json
x=json.load(open('/tmp/scw34000-state.json')); assert x['item']['status']=='succeeded',x; nr=x['result']['polyglot']['result']['remote']['result']; pkg=nr['deepLearningResearchPackage']; wa=nr.get('workspaceDeepLearningResearchArtifact') or {}; assert pkg['packageId'].startswith('dlrp_') and pkg['evidenceBoundary']['isObservedEvidence'] is False; assert wa.get('artifactId') and wa.get('sha256'); print('DEEP_LEARNING_RESEARCH_PACKAGE_JOB=PASS jobId='+x['item']['jobId']); print('WORKSPACE_DEEP_LEARNING_RESEARCH_ARTIFACT=PASS artifactId='+wa['artifactId'])
PYCODE

echo '=== RUNTIME REGISTRY ==='; docker exec -i sc-workspace-backend python3 - <<'PYCODE'
from app.polyglot import RUNTIME_BY_LANGUAGE
n=RUNTIME_BY_LANGUAGE['neural']; assert len(n.operations)==109,n; print('WORKSPACE_V34000_RUNTIME_REGISTRY=PASS')
PYCODE

echo '=== CONTAINER HARDENING ==='; python3 - <<'PYCODE'
import json,subprocess
d=json.loads(subprocess.check_output(['docker','inspect','sc-workspace-neural-runtime']))[0]; assert d['HostConfig']['ReadonlyRootfs'] is True; assert d['Config'].get('User')=='65532:65532'; assert 'ALL' in (d['HostConfig'].get('CapDrop') or []); print('NEURAL_RUNTIME_HARDENING=PASS')
PYCODE
trap - ERR; echo 'PASS: Workspace v3.40.0 backend deployed; reproducible deep learning research packages, 109-operation registry integrity, artifact lineage, reproduction verification, and hardening verified'
