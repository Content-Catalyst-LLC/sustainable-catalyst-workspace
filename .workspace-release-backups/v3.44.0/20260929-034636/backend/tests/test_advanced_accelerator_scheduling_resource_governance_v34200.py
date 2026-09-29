from __future__ import annotations
import importlib.util, pathlib
from fastapi import HTTPException
P=pathlib.Path(__file__).resolve().parents[1]/"neural-runtime"/"service.py"
spec=importlib.util.spec_from_file_location("sc_neural_v34200",P); s=importlib.util.module_from_spec(spec); spec.loader.exec_module(s)

def pool():
    return s._distributed_worker_pool_plan({"poolId":"accelerator-pool","workers":[
      {"workerId":"cpu-a","capabilities":["cpu","training","inference"],"devices":["cpu"],"maxConcurrentTasks":2,"memoryMiB":8192},
      {"workerId":"gpu-a","capabilities":["cpu","accelerator","training","inference","vision"],"devices":["cpu","cuda:0"],"maxConcurrentTasks":2,"memoryMiB":24576},
      {"workerId":"gpu-b","capabilities":["cpu","accelerator","training","inference","vision"],"devices":["cpu","cuda:1"],"maxConcurrentTasks":2,"memoryMiB":24576},
    ]})["distributedWorkerPoolArtifact"]

def inventory():
    return s._accelerator_inventory_contract({"workerPoolArtifact":pool(),"accelerators":[
      {"acceleratorId":"gpu-a-0","workerId":"gpu-a","device":"cuda:0","memoryMiB":24576,"supportedPrecisions":["float32","float16"],"status":"available","currentReservations":0,"maxConcurrentReservations":1},
      {"acceleratorId":"gpu-b-1","workerId":"gpu-b","device":"cuda:1","memoryMiB":24576,"supportedPrecisions":["float32","float16"],"status":"busy","currentReservations":0,"maxConcurrentReservations":1},
    ]})["acceleratorInventoryArtifact"]

def request(count=1, priority="normal", budget=3600):
    return s._accelerator_resource_request({"requestId":"req-1","acceleratorCount":count,"minimumMemoryMiBPerAccelerator":16000,"precision":"float16","maxRuntimeSeconds":3600,"priorityClass":priority,"requiredCapabilities":["accelerator","inference"],"budgetUnits":budget})["acceleratorResourceRequestArtifact"]

def quota(req=None):
    req=req or request()
    return s._accelerator_quota_evaluate({"acceleratorResourceRequestArtifact":req,"quotaPolicy":{"policyId":"research-quota","maxAcceleratorsPerRequest":2,"maxMemoryMiBPerAccelerator":24576,"maxRuntimeSeconds":7200,"budgetLimitUnits":20000,"allowedPriorityClasses":["low","normal","high"],"allowedPrecisions":["float32","float16"]},"currentUsage":{"activeReservations":0,"consumedBudgetUnits":1000}})["acceleratorQuotaEvaluationArtifact"]

def admission(req=None, inv=None, q=None):
    req=req or request(); inv=inv or inventory(); q=q or quota(req)
    return s._accelerator_admission_decision({"acceleratorResourceRequestArtifact":req,"acceleratorInventoryArtifact":inv,"acceleratorQuotaEvaluationArtifact":q})["acceleratorAdmissionDecisionArtifact"]

def placement(req=None, inv=None, adm=None):
    req=req or request(); inv=inv or inventory(); adm=adm or admission(req,inv)
    return s._accelerator_placement_plan({"acceleratorResourceRequestArtifact":req,"acceleratorInventoryArtifact":inv,"acceleratorAdmissionDecisionArtifact":adm})["acceleratorPlacementPlanArtifact"]

def test_health_registry_and_boundaries():
    h=s.health(); assert h["version"] in {"3.42.0","3.43.0"}; assert len(h["operations"])>=125
    assert h["advancedAcceleratorSchedulingResourceGovernanceRuntime"] is True
    assert h["acceleratorSchedulingInfrastructureMutationEnabled"] is False
    assert h["acceleratorClientSuppliedSchedulerEndpointsAllowed"] is False
    for k in ("schedulerUrl","clusterUrl","cloudCredentials","reservationToken","kubeconfig","slurmConfig"): assert k in s.BLOCKED_PAYLOAD_KEYS

def test_inventory_is_bound_to_governed_worker_pool():
    inv=inventory(); assert inv["acceleratorCount"]==2 and inv["clientSuppliedEndpointsAccepted"] is False
    try:
        s._accelerator_inventory_contract({"workerPoolArtifact":pool(),"accelerators":[{"acceleratorId":"bad","workerId":"cpu-a","device":"cuda:9","memoryMiB":1024}]})
        raise AssertionError("undeclared accelerator should fail")
    except HTTPException: pass

def test_quota_admission_and_deterministic_placement():
    req=request(); inv=inventory(); q=quota(req); adm=admission(req,inv,q); pl=placement(req,inv,adm)
    assert q["withinQuota"] is True and adm["admitted"] is True
    assert pl["placementReady"] is True and pl["assignments"][0]["acceleratorId"]=="gpu-a-0" and pl["placementExecuted"] is False

def test_required_worker_capabilities_are_enforced_at_admission():
    req=s._accelerator_resource_request({"requestId":"req-gnn","acceleratorCount":1,"minimumMemoryMiBPerAccelerator":8000,"precision":"float16","maxRuntimeSeconds":1000,"priorityClass":"normal","requiredCapabilities":["accelerator","gnn"],"budgetUnits":1000})["acceleratorResourceRequestArtifact"]
    q=quota(req); adm=admission(req,inventory(),q)
    assert adm["admitted"] is False and adm["eligibleAcceleratorCount"]==0 and "insufficient-eligible-accelerators" in adm["reasons"]

def test_quota_denial_is_explicit_and_nonexecuting():
    req=request(count=2,budget=99999); q=quota(req); adm=admission(req,inventory(),q)
    assert q["withinQuota"] is False and "budget" in q["violations"] and adm["admitted"] is False

def test_reservation_preemption_and_receipt_are_plans_only():
    req=request(priority="high"); inv=inventory(); q=quota(req); adm=admission(req,inv,q); pl=placement(req,inv,adm)
    rp=s._accelerator_reservation_plan({"acceleratorResourceRequestArtifact":req,"acceleratorPlacementPlanArtifact":pl,"reservationId":"res-1","leaseSeconds":1800})["acceleratorReservationPlanArtifact"]
    assert rp["reservationReady"] is True and rp["reservationCommitted"] is False and rp["serverCommitRequired"] is True
    pre=s._accelerator_preemption_plan({"incomingResourceRequestArtifact":req,"activeReservations":[{"reservationItemId":"old:0","acceleratorId":"gpu-a-0","priorityClass":"low","preemptible":True,"ageSeconds":500}]})["acceleratorPreemptionPlanArtifact"]
    assert pre["preemptionNeeded"] is True and pre["automaticPreemptionExecuted"] is False and pre["operatorApprovalRequired"] is True
    rec=s._accelerator_scheduling_receipt({"acceleratorAdmissionDecisionArtifact":adm,"acceleratorPlacementPlanArtifact":pl,"acceleratorReservationPlanArtifact":rp})["acceleratorSchedulingReceiptArtifact"]
    assert rec["admitted"] is True and rec["infrastructureMutationExecuted"] is False and rec["clientSuppliedSchedulerEndpointAccepted"] is False

def test_security_boundary_rejects_top_level_scheduler_endpoint():
    try:
        s.execute({"schema":"sc-workspace-polyglot-execution-envelope/1.0","language":"neural","operation":"workspace.neural.accelerator-resource-request","arbitraryCodeExecution":False,"payload":{"requestId":"x","schedulerUrl":"https://example.invalid"}}, authorization="Bearer test")
    except HTTPException as e:
        assert e.status_code in {401,503,400}
