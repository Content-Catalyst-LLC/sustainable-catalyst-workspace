#!/usr/bin/env bash
set -Eeuo pipefail
PACKAGE="${1:-/tmp/sustainable-catalyst-workspace-backend-v3.31.0.zip}"
BASE="/opt/sustainable-catalyst"
OLD="$BASE/sustainable-catalyst-workspace-backend-v3.30.0"
NEW="$BASE/sustainable-catalyst-workspace-backend-v3.31.0"
SWITCHED=0
fail(){ echo "ERROR: $*" >&2; exit 1; }
rollback(){ local code=$?; if [[ "$SWITCHED" == 1 ]]; then echo "=== v3.31.0 verification failed; restoring v3.30.0 ===" >&2; docker rm -f sc-workspace-backend sc-workspace-worker sc-workspace-neural-runtime >/dev/null 2>&1 || true; if [[ -d "$OLD" ]]; then cd "$OLD"; [[ -f docker-compose.yml ]] || cp docker-compose.example.yml docker-compose.yml; docker compose --env-file .env -f docker-compose.yml up -d --no-deps --no-build sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker || true; fi; fi; exit "$code"; }
trap rollback ERR
[[ -f "$PACKAGE" ]] || fail "backend package not found: $PACKAGE"
[[ -d "$OLD" && -f "$OLD/.env" ]] || fail "Workspace v3.30.0 production baseline not found at $OLD; finish the corrected v3.30 deployment before v3.31"
TMP="$(mktemp -d)"; cleanup(){ rm -rf "$TMP"; }; trap cleanup EXIT
unzip -q "$PACKAGE" -d "$TMP/package"
[[ -f "$TMP/package/app/config.py" && -f "$TMP/package/neural-runtime/service.py" ]] || fail "malformed v3.31.0 backend package"
grep -q 'service_version: str = "3.31.0"' "$TMP/package/app/config.py" || fail "v3.31.0 backend version marker missing"
grep -q 'SERVICE_VERSION = "3.31.0"' "$TMP/package/neural-runtime/service.py" || fail "v3.31.0 neural version marker missing"
for op in workspace.neural.remote-worker-inventory workspace.neural.remote-dispatch-plan workspace.neural.remote-execute workspace.neural.remote-receipt-verify; do grep -q "$op" "$TMP/package/neural-runtime/service.py" || fail "v3.31 operation missing: $op"; done
rm -rf "$NEW"; mkdir -p "$NEW"; cp -a "$TMP/package/." "$NEW/"; cp "$OLD/.env" "$NEW/.env"
cd "$NEW"; cp docker-compose.example.yml docker-compose.yml
python3 -m compileall -q app neural-runtime

echo "=== BUILD WORKSPACE v3.31.0 ==="
docker compose --env-file .env -f docker-compose.yml build sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker

echo "=== PRE-SWITCH HARDENED REMOTE GPU BROKER CERTIFICATION ==="
docker compose --env-file .env -f docker-compose.yml run --rm -T --no-deps --entrypoint python sc-workspace-neural-runtime - <<'PYCODE'
import copy
import service
from fastapi import HTTPException
h=service.health(); assert h['version']=='3.31.0' and len(h['operations'])==48,h
assert h['remoteGpuExecutionBrokerEnabled'] is False,h
assert h['clientSuppliedRemoteWorkerUrlsAllowed'] is False,h
service.REMOTE_BROKER_ENABLED=True
service.REMOTE_SHARED_SECRET='deploy-v33100-hmac-test-secret'
service.REMOTE_WORKERS_JSON='[{"workerId":"gpu-cert-1","url":"https://gpu.invalid","device":"cuda:0","enabled":true,"tags":["cert"]}]'
payload={'remoteOperation':'workspace.neural.infer-regression','remotePayload':{'modelSpec':{'schema':'sc-workspace-neural-model-spec/1.0','modelType':'linear','weights':[[2.0]],'bias':[1.0],'activation':'identity'},'features':[[3.0]],'rowIds':['r1'],'seed':31}}
plan=service._remote_dispatch_plan(payload)['dispatchPlan']
assert plan['workerId']=='gpu-cert-1' and plan['selectedDevice']=='cuda:0' and len(plan['planFingerprint'])==64,plan
base={'schema':service.REMOTE_EXECUTION_RECEIPT_SCHEMA,'dispatchId':'ngd_cert','workerId':'gpu-cert-1','operation':'workspace.neural.infer-regression','payloadFingerprint':plan['payloadFingerprint'],'dispatchPlanFingerprint':plan['planFingerprint'],'resultFingerprint':'a'*64,'selectedDevice':'cuda:0','devicePlanFingerprint':'b'*64,'runtimeVersion':'3.31.0','engineVersion':'2.10.0','startedAt':1,'finishedAt':2}
fp=service._canonical_sha256(base); sigbase=dict(base); sigbase['receiptFingerprint']=fp
receipt=dict(sigbase); receipt['signature']=service._remote_hmac(sigbase)
assert service._validate_remote_receipt(receipt)['receiptFingerprint']==fp
bad=copy.deepcopy(receipt); bad['workerId']='tampered'
try:
    service._validate_remote_receipt(bad); raise AssertionError('tampered receipt accepted')
except HTTPException as exc:
    assert exc.status_code==400
try:
    service._remote_dispatch_plan({'remoteOperation':'workspace.neural.remote-execute','remotePayload':{}}); raise AssertionError('recursive broker dispatch accepted')
except HTTPException as exc:
    assert exc.status_code==400
print('NEURAL_V33100_PRESWITCH_REMOTE_GPU_BROKER=PASS')
PYCODE

echo "=== SWITCH TO v3.31.0 ==="
docker rm -f sc-workspace-backend sc-workspace-worker sc-workspace-neural-runtime >/dev/null 2>&1 || true
docker compose --env-file .env -f docker-compose.yml up -d --no-deps sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker
SWITCHED=1
for i in $(seq 1 60); do code="$(curl -sS -o /tmp/scw33100-health.json -w '%{http_code}' http://127.0.0.1:8094/health 2>/dev/null || true)"; echo "backend health attempt $i: HTTP $code"; [[ "$code" == 200 ]] && break; sleep 2; done
python3 - <<'PYCODE'
import json
x=json.load(open('/tmp/scw33100-health.json')); assert x['ok'] is True and x['version']=='3.31.0',x
assert x.get('neuralRuntimeBoundedOperations')==48,x
assert x.get('neuralRemoteGpuExecutionBroker') is True,x
assert x.get('neuralRemoteGpuBrokerDefaultEnabled') is False,x
assert x.get('neuralClientSuppliedRemoteWorkerUrlsAllowed') is False,x
print('WORKSPACE_V33100_HEALTH=PASS')
PYCODE

echo "=== DIRECT NEURAL HEALTH ==="
docker exec -i sc-workspace-neural-runtime python - <<'PYCODE'
import json,urllib.request
x=json.load(urllib.request.urlopen('http://127.0.0.1:8101/health',timeout=5))
assert x['version']=='3.31.0' and len(x['operations'])==48,x
assert x['remoteGpuExecutionBrokerEnabled'] is False,x
assert x['remoteGpuWorkerMode'] is False,x
assert x['clientSuppliedRemoteWorkerUrlsAllowed'] is False,x
print('NEURAL_V33100_DIRECT_HEALTH=PASS engineVersion='+x['engineVersion'])
PYCODE
SERVICE_TOKEN="$(awk -F= '$1=="SC_WORKSPACE_SERVICE_TOKEN"{sub($1"=","");print;exit}' .env)"; [[ -n "$SERVICE_TOKEN" ]] || fail "SC_WORKSPACE_SERVICE_TOKEN blank"
AUTH=(-H "Authorization: Bearer $SERVICE_TOKEN" -H 'X-SC-User-ID: 1')
wait_job(){ local id="$1" out="$2" label="$3"; for i in $(seq 1 60); do curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${id}" >"$out"; state="$(python3 -c "import json;print(json.load(open('$out'))['item']['status'])")"; echo "$label attempt $i: $state"; [[ "$state" == succeeded ]] && return 0; [[ "$state" =~ ^(failed|blocked|cancelled)$ ]] && { cat "$out"; return 1; }; sleep 2; done; return 1; }

echo "=== END-TO-END REMOTE WORKER INVENTORY JOB ==="
STAMP="$(date +%s)"
cat >/tmp/scw33100-inventory-job.json <<JSON
{"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.neural.remote-worker-inventory","priority":8,"maxAttempts":1,"idempotencyKey":"deploy-v33100-inventory-${STAMP}","payload":{}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/scw33100-inventory-job.json http://127.0.0.1:8094/v1/jobs >/tmp/scw33100-inventory-created.json
JOB_ID="$(python3 -c "import json;print(json.load(open('/tmp/scw33100-inventory-created.json'))['item']['jobId'])")"
wait_job "$JOB_ID" /tmp/scw33100-inventory-state.json "remote worker inventory"
python3 - <<'PYCODE'
import json
x=json.load(open('/tmp/scw33100-inventory-state.json')); item=x.get('item') or {}; jr=x.get('result') or {}; nr=jr['polyglot']['result']['remote']['result']; inv=nr.get('remoteWorkerInventory') or {}
assert item.get('status')=='succeeded',item
assert inv.get('schema')=='sc-workspace-neural-remote-worker-inventory/1.0',inv
assert inv.get('brokerEnabled') is False and inv.get('workerCount')==0,inv
assert inv.get('clientSuppliedWorkerUrlsAllowed') is False,inv
open('/tmp/scw33100-receipt-id.txt','w').write(jr['receiptId'])
print('NEURAL_REMOTE_WORKER_INVENTORY_JOB=PASS jobId='+item['jobId'])
PYCODE
RID="$(cat /tmp/scw33100-receipt-id.txt)"
curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/polyglot/receipts/${RID}" >/tmp/scw33100-inventory-receipt.json
python3 - <<'PYCODE'
import json
x=json.load(open('/tmp/scw33100-inventory-receipt.json')); d=(x.get('item') or {}).get('details') or {}
assert d.get('neuralRemoteGpuExecutionBroker') is True,d
assert d.get('clientSuppliedRemoteWorkerUrlsAllowed') is False,d
print('NEURAL_REMOTE_BROKER_RECEIPT_LINEAGE=PASS')
PYCODE

echo "=== OPENAPI / RUNTIME REGISTRY ==="
docker exec -i sc-workspace-backend python3 - <<'PYCODE'
from app.main import app
from app.client_contracts import TYPED_ENDPOINTS,profile
from app.polyglot import RUNTIME_BY_LANGUAGE
x=profile(app.openapi()); assert x['workspaceVersion']=='3.31.0' and x['typedEndpointCount']==291 and not x['missingOpenApiOperations'],x
n=RUNTIME_BY_LANGUAGE['neural']; assert len(n.operations)==48,n
for op in ['workspace.neural.remote-worker-inventory','workspace.neural.remote-dispatch-plan','workspace.neural.remote-execute','workspace.neural.remote-receipt-verify']: assert op in n.operations,(op,n)
print('WORKSPACE_V33100_OPENAPI_RUNTIME_REGISTRY=PASS typed_endpoints=%d'%len(TYPED_ENDPOINTS))
PYCODE

echo "=== CONTAINER HARDENING ==="
python3 - <<'PYCODE'
import json,subprocess
d=json.loads(subprocess.check_output(['docker','inspect','sc-workspace-neural-runtime']))[0]; h=d['HostConfig']; c=d['Config']
assert h['ReadonlyRootfs'] is True and c.get('User')=='65532:65532',d
assert 'ALL' in (h.get('CapDrop') or []) and 'no-new-privileges:true' in (h.get('SecurityOpt') or []),d
print('NEURAL_RUNTIME_HARDENING=PASS')
PYCODE

echo "PASS: Workspace v3.31.0 backend deployed; remote GPU broker contracts, operator-only worker registry, signed dispatch/receipt provenance, Workspace receipt lineage, runtime registry, and hardening verified"
trap - ERR
