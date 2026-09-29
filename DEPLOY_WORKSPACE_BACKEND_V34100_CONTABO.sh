#!/usr/bin/env bash
set -Eeuo pipefail
PACKAGE="${1:-/tmp/sustainable-catalyst-workspace-backend-v3.41.0.zip}"; BASE="/opt/sustainable-catalyst"; SOURCE="$BASE/sustainable-catalyst-workspace-backend-v3.40.0"; ROLLBACK="$SOURCE"; NEW="$BASE/sustainable-catalyst-workspace-backend-v3.41.0"; SWITCHED=0
fail(){ echo "ERROR: $*" >&2; exit 1; }
rollback(){ code=$?; if [[ "$SWITCHED" == 1 && -d "$ROLLBACK" ]]; then echo '=== v3.41.0 failed; restoring v3.40.0 ===' >&2; docker rm -f sc-workspace-backend sc-workspace-worker sc-workspace-neural-runtime >/dev/null 2>&1 || true; cd "$ROLLBACK"; [[ -f docker-compose.yml ]] || cp docker-compose.example.yml docker-compose.yml; docker compose --env-file .env -f docker-compose.yml up -d --no-deps --no-build sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker || true; fi; exit "$code"; }
trap rollback ERR
[[ -f "$PACKAGE" ]] || fail "package not found: $PACKAGE"; [[ -d "$SOURCE" && -f "$SOURCE/.env" ]] || fail "v3.40.0 production baseline not found at $SOURCE"; grep -q 'service_version: str = "3.40.0"' "$SOURCE/app/config.py" || fail 'v3.40.0 baseline marker missing'
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT; unzip -q "$PACKAGE" -d "$TMP/package"; rm -rf "$NEW"; mkdir -p "$NEW"; cp -a "$TMP/package/." "$NEW/"; cp "$SOURCE/.env" "$NEW/.env"; cd "$NEW"; [[ -f docker-compose.yml ]] || cp docker-compose.example.yml docker-compose.yml
python3 -m compileall -q app neural-runtime; grep -q 'service_version: str = "3.41.0"' app/config.py || fail 'v3.41.0 backend marker missing'; grep -q 'SERVICE_VERSION = "3.41.0"' neural-runtime/service.py || fail 'v3.41.0 neural marker missing'
echo '=== BUILD WORKSPACE v3.41.0 ==='; docker compose --env-file .env -f docker-compose.yml build sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker

echo '=== PRE-SWITCH DISTRIBUTED WORKER FABRIC CERTIFICATION ==='
docker compose --env-file .env -f docker-compose.yml run --rm -T --no-deps --entrypoint python sc-workspace-neural-runtime - <<'PYCODE'
import importlib.util
spec=importlib.util.spec_from_file_location('svc','/app/service.py'); s=importlib.util.module_from_spec(spec); spec.loader.exec_module(s)
workers=[
 {'workerId':'cpu-a','capabilities':['cpu','training','inference','research-package'],'devices':['cpu'],'maxConcurrentTasks':2,'memoryMiB':8192,'labels':{'zone':'a'}},
 {'workerId':'cpu-b','capabilities':['cpu','training','inference','research-package'],'devices':['cpu'],'maxConcurrentTasks':2,'memoryMiB':8192,'labels':{'zone':'b'}},]
pool=s._distributed_worker_pool_plan({'poolId':'deploy-pool','workers':workers})['distributedWorkerPoolArtifact']
sh=s._distributed_shard_plan({'itemCount':12,'shardCount':4})['distributedShardPlanArtifact']
d=s._distributed_dispatch_plan({'workerPoolArtifact':pool,'shardPlanArtifact':sh,'requiredCapabilities':['cpu','inference'],'requiredDevice':'cpu','operation':'workspace.neural.research-package-verify','payloadFingerprint':'a'*64})['distributedDispatchPlanArtifact']
assert d['assignmentCount']==4 and len(s.OPERATIONS)==117
hb=s._distributed_lease_heartbeat({'dispatchPlanArtifact':d,'heartbeats':[{'workerId':'cpu-a','sequence':4,'status':'ready'},{'workerId':'cpu-b','sequence':5,'status':'busy'}]})['distributedLeaseHeartbeatArtifact']; assert hb['activeLeaseCount']==4
f=s._distributed_retry_failover_plan({'dispatchPlanArtifact':d,'workerPoolArtifact':pool,'failedAssignmentIds':[d['assignments'][0]['assignmentId']],'maxAttempts':3})['distributedRetryFailoverArtifact']; assert f['retryCount']==1
receipts=[{'assignmentId':a['assignmentId'],'workerId':a['workerId'],'status':'succeeded','attempt':1,'resultArtifactId':'result-'+a['shardId'],'resultSha256':'b'*64} for a in d['assignments']]
r=s._distributed_execution_receipt({'dispatchPlanArtifact':d,'shardReceipts':receipts})['distributedExecutionReceiptArtifact']; assert r['allSucceeded'] is True
print('NEURAL_V34100_WORKER_POOL=PASS'); print('NEURAL_V34100_SHARD_DISPATCH=PASS'); print('NEURAL_V34100_LEASE_FAILOVER=PASS'); print('NEURAL_V34100_EXECUTION_RECEIPT=PASS'); print('NEURAL_V34100_REGISTRY=PASS')
PYCODE

echo '=== SWITCH TO v3.41.0 ==='; docker rm -f sc-workspace-backend sc-workspace-worker sc-workspace-neural-runtime >/dev/null 2>&1 || true; docker compose --env-file .env -f docker-compose.yml up -d --no-deps sc-workspace-neural-runtime sc-workspace-backend sc-workspace-worker; SWITCHED=1
for i in $(seq 1 60); do code="$(curl -sS -o /tmp/scw34100-health.json -w '%{http_code}' http://127.0.0.1:8094/health 2>/dev/null || true)"; echo "backend health attempt $i: HTTP $code"; [[ "$code" == 200 ]] && break; sleep 2; done
python3 - <<'PYCODE'
import json
x=json.load(open('/tmp/scw34100-health.json')); assert x['ok'] is True and x['version']=='3.41.0',x; assert x.get('neuralRuntimeBoundedOperations')==117,x; assert x.get('distributedNeuralExecutionWorkerFabricRuntime') is True,x; assert x.get('distributedClientSuppliedWorkerEndpointsAllowed') is False,x; print('WORKSPACE_V34100_HEALTH=PASS')
PYCODE
SERVICE_TOKEN="$(awk -F= '$1=="SC_WORKSPACE_SERVICE_TOKEN"{sub($1"=","");print;exit}' .env)"; [[ -n "$SERVICE_TOKEN" ]] || fail 'SC_WORKSPACE_SERVICE_TOKEN blank'; AUTH=(-H "Authorization: Bearer $SERVICE_TOKEN" -H 'X-SC-User-ID: 1'); STAMP="$(date +%s)"
cat >/tmp/scw34100-job.json <<'JSON'
{"schema":"sc-workspace-job-request/1.0","jobType":"workspace-task","targetProduct":"workspace","operation":"workspace.neural.distributed-worker-pool-plan","priority":9,"maxAttempts":1,"idempotencyKey":"deploy-v34100-__STAMP__","payload":{"deviceRequest":"cpu","poolId":"production-certification-pool","workers":[{"workerId":"cert-cpu-a","capabilities":["cpu","training","inference","research-package"],"devices":["cpu"],"maxConcurrentTasks":2,"memoryMiB":8192,"labels":{"zone":"a"}},{"workerId":"cert-cpu-b","capabilities":["cpu","training","inference","research-package"],"devices":["cpu"],"maxConcurrentTasks":2,"memoryMiB":8192,"labels":{"zone":"b"}}]}}
JSON
sed -i "s/__STAMP__/${STAMP}/g" /tmp/scw34100-job.json; curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' --data-binary @/tmp/scw34100-job.json http://127.0.0.1:8094/v1/jobs >/tmp/scw34100-created.json; JOB_ID="$(python3 -c "import json;print(json.load(open('/tmp/scw34100-created.json'))['item']['jobId'])")"
for i in $(seq 1 60); do curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${JOB_ID}" >/tmp/scw34100-state.json; state="$(python3 -c "import json;print(json.load(open('/tmp/scw34100-state.json'))['item']['status'])")"; echo "distributed worker job attempt $i: $state"; [[ "$state" == succeeded ]] && break; [[ "$state" =~ ^(failed|blocked|cancelled)$ ]] && { cat /tmp/scw34100-state.json; exit 1; }; sleep 2; done
python3 - <<'PYCODE'
import json
x=json.load(open('/tmp/scw34100-state.json')); assert x['item']['status']=='succeeded',x; nr=x['result']['polyglot']['result']['remote']['result']; pool=nr['distributedWorkerPoolArtifact']; wa=nr.get('workspaceDistributedNeuralArtifact') or {}; assert pool['workerCount']==2 and pool['workerEndpointsEmbedded'] is False; assert wa.get('artifactId') and wa.get('sha256'); print('DISTRIBUTED_WORKER_POOL_JOB=PASS jobId='+x['item']['jobId']); print('WORKSPACE_DISTRIBUTED_NEURAL_ARTIFACT=PASS artifactId='+wa['artifactId'])
PYCODE

echo '=== RUNTIME REGISTRY ==='; docker exec -i sc-workspace-backend python3 - <<'PYCODE'
from app.polyglot import RUNTIME_BY_LANGUAGE
n=RUNTIME_BY_LANGUAGE['neural']; assert len(n.operations)==117,n; assert 'workspace.neural.distributed-execution-receipt' in n.operations; print('WORKSPACE_V34100_RUNTIME_REGISTRY=PASS')
PYCODE

echo '=== CONTAINER HARDENING ==='; python3 - <<'PYCODE'
import json,subprocess
d=json.loads(subprocess.check_output(['docker','inspect','sc-workspace-neural-runtime']))[0]; assert d['HostConfig']['ReadonlyRootfs'] is True; assert d['Config'].get('User')=='65532:65532'; assert 'ALL' in (d['HostConfig'].get('CapDrop') or []); print('NEURAL_RUNTIME_HARDENING=PASS')
PYCODE
trap - ERR; echo 'PASS: Workspace v3.41.0 backend deployed; distributed worker fabric, deterministic sharding/dispatch, lease/failover state, artifact lineage, 117-operation registry integrity, and hardening verified'
