from __future__ import annotations
import importlib.util, pathlib
from fastapi import HTTPException
P=pathlib.Path(__file__).resolve().parents[1]/"neural-runtime"/"service.py"
spec=importlib.util.spec_from_file_location("sc_neural_v34100",P); s=importlib.util.module_from_spec(spec); spec.loader.exec_module(s)

def workers():
    return [
      {"workerId":"worker-cpu-a","capabilities":["cpu","training","inference","research-package"],"devices":["cpu"],"maxConcurrentTasks":2,"memoryMiB":8192,"labels":{"zone":"a"}},
      {"workerId":"worker-cpu-b","capabilities":["cpu","training","inference","research-package"],"devices":["cpu"],"maxConcurrentTasks":2,"memoryMiB":8192,"labels":{"zone":"b"}},
      {"workerId":"worker-gpu-a","capabilities":["cpu","accelerator","training","inference","vision"],"devices":["cpu","cuda:0"],"maxConcurrentTasks":1,"memoryMiB":24576,"labels":{"zone":"g"}},
    ]

def pool():
    return s._distributed_worker_pool_plan({"poolId":"neural-main","workers":workers()})["distributedWorkerPoolArtifact"]

def shards():
    return s._distributed_shard_plan({"itemCount":10,"shardCount":4})["distributedShardPlanArtifact"]

def dispatch():
    return s._distributed_dispatch_plan({"workerPoolArtifact":pool(),"shardPlanArtifact":shards(),"requiredCapabilities":["cpu","inference"],"requiredDevice":"cpu","operation":"workspace.neural.research-package-verify","payloadFingerprint":"a"*64})["distributedDispatchPlanArtifact"]

def test_health_and_registry():
    h=s.health(); assert h["version"] in {"3.41.0","3.41.0.1","3.42.0"}; assert len(h["operations"])>=117; assert h["distributedNeuralExecutionWorkerFabricRuntime"] is True; assert h["distributedClientSuppliedWorkerEndpointsAllowed"] is False

def test_worker_contract_and_pool_are_endpoint_free():
    w=s._distributed_worker_contract(workers()[0])["distributedWorkerArtifact"]; assert w["workerId"]=="worker-cpu-a" and w["dynamicRegistration"] is False
    p=pool(); assert p["workerCount"]==3 and p["totalConcurrency"]==5 and p["workerEndpointsEmbedded"] is False

def test_capability_match_and_deterministic_shards():
    m=s._distributed_capability_match({"workerPoolArtifact":pool(),"requiredCapabilities":["accelerator","vision"],"requiredDevice":"accelerator","minimumMemoryMiB":16000})["distributedCapabilityMatchArtifact"]
    assert m["eligibleWorkerIds"]==["worker-gpu-a"]
    sh=shards(); assert [x["itemCount"] for x in sh["shards"]]==[3,3,2,2] and sh["shards"][-1]["endIndexExclusive"]==10

def test_dispatch_and_lease_heartbeat_state():
    d=dispatch(); assert d["assignmentCount"]==4 and [x["workerId"] for x in d["assignments"]]==["worker-cpu-a","worker-cpu-b","worker-gpu-a","worker-cpu-a"]
    hb=s._distributed_lease_heartbeat({"dispatchPlanArtifact":d,"leaseSeconds":120,"heartbeats":[{"workerId":"worker-cpu-a","sequence":8,"status":"ready"},{"workerId":"worker-cpu-b","sequence":7,"status":"busy"},{"workerId":"worker-gpu-a","sequence":4,"status":"ready"}]})["distributedLeaseHeartbeatArtifact"]
    assert hb["activeLeaseCount"]==4 and all(x["eligibleToRun"] for x in hb["leases"])

def test_retry_failover_and_execution_receipt():
    d=dispatch(); failed=d["assignments"][0]["assignmentId"]
    f=s._distributed_retry_failover_plan({"dispatchPlanArtifact":d,"workerPoolArtifact":pool(),"failedAssignmentIds":[failed],"maxAttempts":3})["distributedRetryFailoverArtifact"]
    assert f["retries"][0]["retryAllowed"] is True and f["retries"][0]["failoverWorkerId"]=="worker-cpu-b"
    receipts=[]
    for a in d["assignments"]: receipts.append({"assignmentId":a["assignmentId"],"workerId":a["workerId"],"status":"succeeded","attempt":1,"resultArtifactId":"result-"+a["shardId"],"resultSha256":"b"*64})
    r=s._distributed_execution_receipt({"dispatchPlanArtifact":d,"shardReceipts":receipts})["distributedExecutionReceiptArtifact"]
    assert r["complete"] is True and r["allSucceeded"] is True and r["succeededCount"]==4 and r["resultAggregationExecuted"] is False

def test_security_boundaries_and_invalid_inputs():
    for key in ("workerUrl","workerToken","sshHost","sshKey"): assert key in s.BLOCKED_PAYLOAD_KEYS
    try: s._distributed_worker_contract(dict(workers()[0],devices=["https://worker.example"])); raise AssertionError("endpoint-like device should fail")
    except HTTPException: pass
    try: s._distributed_dispatch_plan({"workerPoolArtifact":pool(),"shardPlanArtifact":shards(),"requiredCapabilities":["cpu"],"operation":"workspace.neural.distributed-shard-plan","payloadFingerprint":"a"*64}); raise AssertionError("fabric recursion should fail")
    except HTTPException: pass
