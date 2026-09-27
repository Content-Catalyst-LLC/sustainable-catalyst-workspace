#!/usr/bin/env bash
set -Eeuo pipefail

PACKAGE="${1:-/tmp/sustainable-catalyst-workspace-backend-v3.20.0.zip}"
BASE="/opt/sustainable-catalyst"
OLD="$BASE/sustainable-catalyst-workspace-backend-v3.19.0"
NEW="$BASE/sustainable-catalyst-workspace-backend-v3.20.0"
SWITCHED=0

fail(){ echo "ERROR: $*" >&2; exit 1; }

rollback(){
  local code=$?
  if [[ "$SWITCHED" == "1" ]]; then
    echo "=== v3.20.0 validation failed; restoring v3.19.0 backend/worker ===" >&2
    docker rm -f sc-workspace-backend sc-workspace-worker sc-workspace-neural-runtime >/dev/null 2>&1 || true
    if [[ -d "$OLD" ]]; then
      cd "$OLD"
      [[ -f docker-compose.yml ]] || { [[ -f docker-compose.example.yml ]] && cp docker-compose.example.yml docker-compose.yml; }
      docker compose --env-file .env -f docker-compose.yml up -d --no-deps sc-workspace-backend sc-workspace-worker || true
    fi
  fi
  exit "$code"
}
trap rollback ERR

[[ -f "$PACKAGE" ]] || fail "backend package not found: $PACKAGE"
[[ -d "$OLD" ]] || fail "verified Workspace v3.19.0 backend directory not found: $OLD"
[[ -f "$OLD/.env" ]] || fail "v3.19.0 .env not found: $OLD/.env"
[[ -f "$OLD/app/config.py" ]] || fail "v3.19.0 backend app is incomplete"

echo "=== STAGE WORKSPACE v3.20.0 ==="
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
unzip -q "$PACKAGE" -d "$TMP/package"
[[ -f "$TMP/package/app/config.py" ]] || fail "malformed v3.20.0 backend package: app/config.py missing"
[[ -f "$TMP/package/neural-runtime/service.py" ]] || fail "malformed v3.20.0 backend package: neural runtime missing"
[[ -f "$TMP/package/docker-compose.example.yml" ]] || fail "malformed v3.20.0 backend package: compose file missing"

rm -rf "$NEW"
mkdir -p "$NEW"
cp -a "$TMP/package/." "$NEW/"
cp "$OLD/.env" "$NEW/.env"
cd "$NEW"
cp docker-compose.example.yml docker-compose.yml

python3 - <<'PY'
from pathlib import Path
import secrets
p=Path('.env')
lines=p.read_text().splitlines()
key='SC_WORKSPACE_RUNTIME_NEURAL_TOKEN'
value=''
for line in lines:
    if line.startswith(key+'='):
        value=line.split('=',1)[1].strip()
        break
if not value:
    token=secrets.token_hex(32)
    found=False
    out=[]
    for line in lines:
        if line.startswith(key+'='):
            out.append(f'{key}={token}'); found=True
        else:
            out.append(line)
    if not found: out.append(f'{key}={token}')
    p.write_text('\n'.join(out)+'\n')
    print('NEURAL_RUNTIME_TOKEN=GENERATED')
else:
    print('NEURAL_RUNTIME_TOKEN=PRESERVED')
PY

python3 -m compileall -q app neural-runtime

echo "=== BUILD v3.20.0 BACKEND / WORKER / NEURAL RUNTIME ==="
docker compose --env-file .env -f docker-compose.yml build \
  sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker

echo "=== SWITCH TO v3.20.0 ==="
docker rm -f sc-workspace-backend sc-workspace-worker sc-workspace-neural-runtime >/dev/null 2>&1 || true
docker compose --env-file .env -f docker-compose.yml up -d --no-deps \
  sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker
SWITCHED=1

for i in $(seq 1 40); do
  code="$(curl -sS -o /tmp/scw32000-health.json -w '%{http_code}' http://127.0.0.1:8094/health 2>/dev/null || true)"
  echo "backend health attempt $i: HTTP $code"
  [[ "$code" == "200" ]] && break
  sleep 2
done

echo "=== BACKEND HEALTH ==="
python3 - <<'PY'
import json
p='/tmp/scw32000-health.json'
d=json.load(open(p))
assert d['ok'] is True, d
assert d['version']=='3.20.0', d
assert d.get('neuralPyTorchRuntimeFoundation') is True, d
assert d.get('neuralRuntimeConfigured') is True, d
assert d.get('neuralRuntimeBoundedOperations')==4, d
assert d.get('neuralRuntimeTrainingEnabled') is False, d
assert d.get('neuralRuntimeDeclarativeModelSpecsOnly') is True, d
assert d.get('mlRuntimeBoundedOperations')==8, d
print('WORKSPACE_V32000_HEALTH=PASS')
PY

SERVICE_TOKEN="$(awk -F= '$1=="SC_WORKSPACE_SERVICE_TOKEN"{sub($1"=",""); print; exit}' .env)"
[[ -n "$SERVICE_TOKEN" ]] || fail "SC_WORKSPACE_SERVICE_TOKEN is blank"
AUTH=(-H "Authorization: Bearer $SERVICE_TOKEN" -H 'X-SC-User-ID: 1')

echo "=== DIRECT NEURAL RUNTIME HEALTH ==="
docker exec sc-workspace-neural-runtime python - <<'PY'
import json, urllib.request
body=json.load(urllib.request.urlopen('http://127.0.0.1:8101/health',timeout=5))
assert body['ok'] is True, body
assert body['version']=='3.20.0', body
assert body['runtime']=='python-pytorch-neural', body
assert body['devicePolicy']=='cpu-only-foundation', body
assert body['trainingEnabled'] is False, body
assert len(body['operations'])==4, body
print('NEURAL_RUNTIME_DIRECT_HEALTH=PASS engineVersion='+body['engineVersion'])
PY

echo "=== WORKSPACE NEURAL STATUS ROUTE ==="
curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/polyglot/runtimes/neural/status >/tmp/scw32000-neural-status.json
python3 - <<'PY'
import json
d=json.load(open('/tmp/scw32000-neural-status.json'))['item']
assert d['language']=='neural', d
assert d['configured'] is True, d
assert d['available'] is True, d
assert d['runtime']=='python-pytorch-neural', d
assert len(d['operations'])==4, d
assert d['arbitraryCodeExecution'] is False, d
print('WORKSPACE_NEURAL_STATUS=PASS')
PY

echo "=== BOUNDED NEURAL JOB SMOKE TEST ==="
STAMP="$(date +%s)"
cat >/tmp/scw32000-neural-job.json <<JSON
{"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.neural.linear-forward","priority":8,"maxAttempts":1,"idempotencyKey":"deploy-v32000-neural-${STAMP}","payload":{"seed":7,"inputs":[[1.0,2.0],[3.0,4.0]],"modelSpec":{"schema":"sc-workspace-neural-model-spec/1.0","modelType":"linear","weights":[[2.0,-1.0],[0.5,0.5]],"bias":[1.0,-1.0],"activation":"identity"}}}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/scw32000-neural-job.json \
  http://127.0.0.1:8094/v1/jobs >/tmp/scw32000-neural-created.json
JOB_ID="$(python3 -c "import json; print(json.load(open('/tmp/scw32000-neural-created.json'))['item']['jobId'])")"
for i in $(seq 1 30); do
  curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${JOB_ID}" >/tmp/scw32000-neural-job-state.json
  state="$(python3 -c "import json; print(json.load(open('/tmp/scw32000-neural-job-state.json'))['item']['status'])")"
  echo "neural job attempt $i: $state"
  [[ "$state" == "succeeded" ]] && break
  [[ "$state" == "failed" || "$state" == "blocked" || "$state" == "cancelled" ]] && { cat /tmp/scw32000-neural-job-state.json; false; }
  sleep 2
done
python3 - <<'PY'
import json
d=json.load(open('/tmp/scw32000-neural-job-state.json'))['item']
assert d['status']=='succeeded', d
print('NEURAL_JOB=PASS jobId='+d['jobId'])
PY

echo "=== POLYGLOT RECEIPT PERSISTENCE ==="
curl -fsS "${AUTH[@]}" 'http://127.0.0.1:8094/v1/polyglot/receipts?limit=50' >/tmp/scw32000-receipts.json
python3 - "$JOB_ID" <<'PY'
import json,sys
job=sys.argv[1]
items=json.load(open('/tmp/scw32000-receipts.json'))['items']
row=next((x for x in items if x.get('jobId')==job),None)
assert row, items[:5]
assert row['language']=='neural', row
assert row['runtime']=='python-pytorch-neural', row
assert row['operation']=='workspace.neural.linear-forward', row
print('NEURAL_RECEIPT=PASS receiptId='+row['receiptId'])
PY

echo "=== OPENAPI / TYPED CLIENT ==="
docker exec -i sc-workspace-backend python3 - <<'PY'
from app.main import app
from app.client_contracts import TYPED_ENDPOINTS, profile
x=profile(app.openapi())
assert x['workspaceVersion']=='3.20.0', x
assert x['typedEndpointCount']==291, x
assert not x['missingOpenApiOperations'], x
assert TYPED_ENDPOINTS['neuralRuntimeStatus']['path']=='/v1/polyglot/runtimes/neural/status'
print('WORKSPACE_V32000_OPENAPI=PASS typed_endpoints=%d' % len(TYPED_ENDPOINTS))
PY

echo "=== CLASSICAL ML SEPARATION ==="
docker exec -i sc-workspace-backend python3 - <<'PY'
from app.polyglot import RUNTIME_BY_LANGUAGE
assert RUNTIME_BY_LANGUAGE['ml'].runtime=='python-sklearn-predictive'
assert RUNTIME_BY_LANGUAGE['neural'].runtime=='python-pytorch-neural'
assert set(RUNTIME_BY_LANGUAGE['ml'].operations).isdisjoint(set(RUNTIME_BY_LANGUAGE['neural'].operations))
print('CLASSICAL_ML_NEURAL_SEPARATION=PASS')
PY

echo "=== CONTAINER HARDENING ==="
python3 - <<'PY'
import json,subprocess
raw=subprocess.check_output(['docker','inspect','sc-workspace-neural-runtime'])
d=json.loads(raw)[0]
h=d['HostConfig']; c=d['Config']
assert h['ReadonlyRootfs'] is True, h
assert c.get('User')=='65532:65532', c
assert 'ALL' in (h.get('CapDrop') or []), h
assert any(x=='no-new-privileges:true' for x in (h.get('SecurityOpt') or [])), h
print('NEURAL_RUNTIME_HARDENING=PASS')
PY

echo "PASS: Workspace v3.20.0 backend deployed and neural PyTorch runtime verified"
trap - ERR
exit 0
