#!/usr/bin/env bash
set -Eeuo pipefail
PACKAGE="${1:-/tmp/sustainable-catalyst-workspace-backend-v3.29.0.zip}"
BASE="/opt/sustainable-catalyst"
OLD="$BASE/sustainable-catalyst-workspace-backend-v3.28.0"
NEW="$BASE/sustainable-catalyst-workspace-backend-v3.29.0"
SWITCHED=0
fail(){ echo "ERROR: $*" >&2; exit 1; }
rollback(){ local code=$?; if [[ "$SWITCHED" == 1 ]]; then echo "=== v3.29.0 verification failed; restoring v3.28.0 ===" >&2; docker rm -f sc-workspace-backend sc-workspace-worker sc-workspace-neural-runtime >/dev/null 2>&1 || true; if [[ -d "$OLD" ]]; then cd "$OLD"; [[ -f docker-compose.yml ]] || cp docker-compose.example.yml docker-compose.yml; docker compose --env-file .env -f docker-compose.yml up -d --no-deps --no-build sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker || true; fi; fi; exit "$code"; }
trap rollback ERR
[[ -f "$PACKAGE" ]] || fail "backend package not found: $PACKAGE"
[[ -d "$OLD" && -f "$OLD/.env" ]] || fail "Workspace v3.28.0 production baseline not found at $OLD"
TMP="$(mktemp -d)"; cleanup(){ rm -rf "$TMP"; }; trap cleanup EXIT
unzip -q "$PACKAGE" -d "$TMP/package"
[[ -f "$TMP/package/app/config.py" && -f "$TMP/package/neural-runtime/service.py" && -f "$TMP/package/docker-compose.example.yml" ]] || fail "malformed v3.29.0 backend package"
grep -q 'service_version: str = "3.29.0"' "$TMP/package/app/config.py" || fail "v3.29.0 backend version marker missing"
grep -q 'SERVICE_VERSION = "3.29.0"' "$TMP/package/neural-runtime/service.py" || fail "v3.29.0 neural version marker missing"
for op in workspace.neural.device-inventory workspace.neural.device-plan workspace.neural.device-verify workspace.neural.accelerator-smoke; do grep -q "$op" "$TMP/package/neural-runtime/service.py" || fail "device orchestration operation missing: $op"; done
grep -q 'SC_WORKSPACE_NEURAL_ACCELERATOR_ENABLED' "$TMP/package/docker-compose.example.yml" || fail "accelerator policy configuration missing"
grep -q '^torch==2.10.0$' "$TMP/package/neural-runtime/requirements.txt" || fail "PyTorch pin missing"
grep -q '^numpy==2.2.6$' "$TMP/package/neural-runtime/requirements.txt" || fail "NumPy pin missing"
rm -rf "$NEW"; mkdir -p "$NEW"; cp -a "$TMP/package/." "$NEW/"; cp "$OLD/.env" "$NEW/.env"
cd "$NEW"; cp docker-compose.example.yml docker-compose.yml
# Base production deployment stays CPU-safe unless an operator explicitly changes policy later.
if grep -q '^SC_WORKSPACE_NEURAL_ACCELERATOR_ENABLED=' .env; then sed -i 's/^SC_WORKSPACE_NEURAL_ACCELERATOR_ENABLED=.*/SC_WORKSPACE_NEURAL_ACCELERATOR_ENABLED=false/' .env; else echo 'SC_WORKSPACE_NEURAL_ACCELERATOR_ENABLED=false' >> .env; fi
if grep -q '^SC_WORKSPACE_NEURAL_ALLOWED_DEVICES=' .env; then sed -i 's/^SC_WORKSPACE_NEURAL_ALLOWED_DEVICES=.*/SC_WORKSPACE_NEURAL_ALLOWED_DEVICES=cpu/' .env; else echo 'SC_WORKSPACE_NEURAL_ALLOWED_DEVICES=cpu' >> .env; fi
python3 -m compileall -q app neural-runtime

echo "=== BUILD WORKSPACE v3.29.0 ==="
docker compose --env-file .env -f docker-compose.yml build sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker

echo "=== PRE-SWITCH HARDENED DEVICE ORCHESTRATION CERTIFICATION ==="
docker compose --env-file .env -f docker-compose.yml run --rm -T --no-deps --entrypoint python sc-workspace-neural-runtime - <<'PYCODE'
from fastapi import HTTPException
import service
h=service.health(); assert h['version']=='3.29.0' and len(h['operations'])==39,h
assert h['devicePolicy']=='governed-explicit-device-orchestration' and h['availableDevices']==['cpu'],h
assert h['acceleratorPolicyEnabled'] is False,h
inv=service._device_inventory({})['deviceInventory']; assert inv['devices'][0]['device']=='cpu',inv
plan=service._device_plan({'deviceRequest':'cpu'})['devicePlan']; assert plan['selectedDevice']=='cpu' and len(plan['planFingerprint'])==64,plan
service._device_verify({'devicePlan':plan})
auto=service._device_plan({'deviceRequest':{'preference':'auto','allowFallback':True}})['devicePlan']; assert auto['selectedDevice']=='cpu' and auto['fallbackReason'],auto
smoke=service._CURRENT_DEVICE.set('cpu')
try:
    x=service._accelerator_smoke({}); assert x['acceleratorUsed'] is False and x['output']==[[1.0,2.0],[3.0,4.0]],x
finally: service._CURRENT_DEVICE.reset(smoke)
try:
    service._device_plan({'deviceRequest':{'preference':'accelerator','strict':True,'allowFallback':False}})
    raise AssertionError('strict unavailable accelerator unexpectedly accepted')
except HTTPException as exc: assert exc.status_code==409,exc
print('NEURAL_V32900_PRESWITCH_ACCELERATOR_DEVICE_ORCHESTRATION=PASS')
PYCODE

echo "=== SWITCH TO v3.29.0 ==="
docker rm -f sc-workspace-backend sc-workspace-worker sc-workspace-neural-runtime >/dev/null 2>&1 || true
docker compose --env-file .env -f docker-compose.yml up -d --no-deps sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker
SWITCHED=1
for i in $(seq 1 60); do code="$(curl -sS -o /tmp/scw32900-health.json -w '%{http_code}' http://127.0.0.1:8094/health 2>/dev/null || true)"; echo "backend health attempt $i: HTTP $code"; [[ "$code" == 200 ]] && break; sleep 2; done
python3 - <<'PYCODE'
import json
x=json.load(open('/tmp/scw32900-health.json')); assert x['ok'] is True and x['version']=='3.29.0',x
assert x.get('neuralRuntimeBoundedOperations')==39,x
assert x.get('neuralAcceleratorDeviceOrchestrationRuntime') is True,x
assert x.get('neuralRuntimeDevicePolicy')=='governed-explicit-device-orchestration',x
print('WORKSPACE_V32900_HEALTH=PASS')
PYCODE

echo "=== DIRECT NEURAL HEALTH ==="
docker exec -i sc-workspace-neural-runtime python - <<'PYCODE'
import json,urllib.request
x=json.load(urllib.request.urlopen('http://127.0.0.1:8101/health',timeout=5))
assert x['version']=='3.29.0' and len(x['operations'])==39,x
assert x['deviceOrchestrationEnabled'] is True and x['availableDevices']==['cpu'],x
assert x['acceleratorPolicyEnabled'] is False and x['runtimeIdentity']=='scworkspace',x
print('NEURAL_V32900_DIRECT_HEALTH=PASS engineVersion='+x['engineVersion'])
PYCODE
SERVICE_TOKEN="$(awk -F= '$1=="SC_WORKSPACE_SERVICE_TOKEN"{sub($1"=","");print;exit}' .env)"; [[ -n "$SERVICE_TOKEN" ]] || fail "SC_WORKSPACE_SERVICE_TOKEN blank"
AUTH=(-H "Authorization: Bearer $SERVICE_TOKEN" -H 'X-SC-User-ID: 1')
wait_job(){ local id="$1" out="$2" label="$3"; for i in $(seq 1 45); do curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${id}" >"$out"; state="$(python3 -c "import json;print(json.load(open('$out'))['item']['status'])")"; echo "$label attempt $i: $state"; [[ "$state" == succeeded ]] && return 0; [[ "$state" =~ ^(failed|blocked|cancelled)$ ]] && { cat "$out"; return 1; }; sleep 2; done; return 1; }

echo "=== END-TO-END DEVICE SMOKE JOB ==="
STAMP="$(date +%s)"
cat >/tmp/scw32900-device-job.json <<JSON
{"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.neural.accelerator-smoke","priority":8,"maxAttempts":1,"idempotencyKey":"deploy-v32900-device-${STAMP}","payload":{"deviceRequest":"cpu","left":[[1,2],[3,4]],"right":[[1,0],[0,1]]}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/scw32900-device-job.json http://127.0.0.1:8094/v1/jobs >/tmp/scw32900-device-created.json
JOB_ID="$(python3 -c "import json;print(json.load(open('/tmp/scw32900-device-created.json'))['item']['jobId'])")"
wait_job "$JOB_ID" /tmp/scw32900-device-state.json "device smoke"
python3 - <<'PYCODE'
import json
x=json.load(open('/tmp/scw32900-device-state.json')); item=x.get('item') or {}; jr=x.get('result') or {}; remote=jr['polyglot']['result']['remote']; nr=remote['result']; plan=remote['devicePlan']
assert item.get('status')=='succeeded',item
assert remote.get('device')=='cpu' and plan.get('schema')=='sc-workspace-neural-device-plan/1.0',remote
assert len(plan.get('planFingerprint',''))==64 and nr.get('acceleratorUsed') is False,nr
assert nr.get('output')==[[1.0,2.0],[3.0,4.0]],nr
assert jr.get('receiptId'),jr
open('/tmp/scw32900-device-receipt-id.txt','w').write(jr['receiptId'])
print('NEURAL_DEVICE_SMOKE_JOB=PASS jobId='+item['jobId'])
PYCODE
RID="$(cat /tmp/scw32900-device-receipt-id.txt)"
curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/polyglot/receipts/${RID}" >/tmp/scw32900-device-receipt.json
python3 - <<'PYCODE'
import json
x=json.load(open('/tmp/scw32900-device-receipt.json')); d=(x.get('item') or {}).get('details') or {}
assert d.get('neuralDeviceOrchestration') is True,d
assert d.get('selectedDevice')=='cpu' and d.get('devicePlanSchema')=='sc-workspace-neural-device-plan/1.0',d
assert len(d.get('devicePlanFingerprint') or '')==64,d
assert d.get('deviceAcceleratorSelected') is False,d
print('NEURAL_DEVICE_RECEIPT_LINEAGE=PASS')
PYCODE

echo "=== OPENAPI / RUNTIME REGISTRY ==="
docker exec -i sc-workspace-backend python3 - <<'PYCODE'
from app.main import app
from app.client_contracts import TYPED_ENDPOINTS,profile
from app.polyglot import RUNTIME_BY_LANGUAGE
x=profile(app.openapi()); assert x['workspaceVersion']=='3.29.0' and x['typedEndpointCount']==291 and not x['missingOpenApiOperations'],x
n=RUNTIME_BY_LANGUAGE['neural']; assert len(n.operations)==39,n
for op in ['workspace.neural.device-inventory','workspace.neural.device-plan','workspace.neural.device-verify','workspace.neural.accelerator-smoke']: assert op in n.operations,(op,n)
print('WORKSPACE_V32900_OPENAPI_RUNTIME_REGISTRY=PASS typed_endpoints=%d'%len(TYPED_ENDPOINTS))
PYCODE

echo "=== CONTAINER HARDENING ==="
python3 - <<'PYCODE'
import json,subprocess
d=json.loads(subprocess.check_output(['docker','inspect','sc-workspace-neural-runtime']))[0]; h=d['HostConfig']; c=d['Config']
assert h['ReadonlyRootfs'] is True and c.get('User')=='65532:65532',d
assert 'ALL' in (h.get('CapDrop') or []) and 'no-new-privileges:true' in (h.get('SecurityOpt') or []),d
print('NEURAL_RUNTIME_HARDENING=PASS')
PYCODE

echo "PASS: Workspace v3.29.0 backend deployed; governed device orchestration, CPU-safe fallback, execution receipt lineage, runtime registry, and hardening verified"
trap - ERR
