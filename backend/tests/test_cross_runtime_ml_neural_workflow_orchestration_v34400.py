from __future__ import annotations
import importlib.util, pathlib
from copy import deepcopy
from fastapi import HTTPException
P=pathlib.Path(__file__).resolve().parents[1]/"neural-runtime"/"service.py"
spec=importlib.util.spec_from_file_location("sc_neural_v34400",P); s=importlib.util.module_from_spec(spec); spec.loader.exec_module(s)

def workflow():
    steps=[
        {"stepId":"fit-classical","runtime":"ml","operation":"workspace.ml.linear-regression","outputRole":"model"},
        {"stepId":"neural-score","runtime":"neural","operation":"workspace.neural.infer-regression","dependsOn":["fit-classical"],"outputRole":"prediction"},
        {"stepId":"package-neural","runtime":"neural","operation":"workspace.neural.package-create","dependsOn":["neural-score"],"outputRole":"package"},
    ]
    return s._cross_runtime_workflow_contract({"workflowId":"wf-ml-neural-1","steps":steps})["crossRuntimeWorkflowArtifact"]

def test_health_registry_and_guardrails():
    h=s.health(); assert h["version"]=="3.44.0" and len(h["operations"])==141
    assert h["crossRuntimeMLNeuralWorkflowOrchestrationRuntime"] is True
    assert h["crossRuntimeAllowedRuntimes"]==["ml","neural"]
    assert h["crossRuntimeAutomaticExecutionEnabled"] is False
    for key in ("workflowRuntimeUrl","runtimeEndpoint","shellCommand","executable","sshCommand","serializedPayload"):
        assert key in s.BLOCKED_PAYLOAD_KEYS

def test_workflow_contract_and_dependency_order_are_deterministic():
    wf=workflow(); assert wf["stepCount"]==3 and wf["runtimes"]==["ml","neural"]
    dep=s._cross_runtime_dependency_validate({"crossRuntimeWorkflowArtifact":wf})["crossRuntimeDependencyArtifact"]
    assert dep["valid"] is True and dep["topologicalOrder"]==["fit-classical","neural-score","package-neural"]
    assert dep["cycleDetected"] is False

def test_handoff_plan_marks_cross_runtime_transition():
    wf=workflow(); hp=s._cross_runtime_handoff_plan({"crossRuntimeWorkflowArtifact":wf})["crossRuntimeHandoffPlanArtifact"]
    assert hp["handoffCount"]==2 and hp["crossRuntimeHandoffCount"]==1
    assert hp["handoffs"][0]["artifactReferenceMode"]=="workspace-artifact-id-and-sha256"
    assert hp["handoffs"][0]["automaticSerializationConversion"] is False

def test_execution_plan_is_staged_nonexecuting_and_reproducible():
    wf=workflow(); plan=s._cross_runtime_execution_plan({"crossRuntimeWorkflowArtifact":wf})["crossRuntimeExecutionPlanArtifact"]
    assert plan["topologicalOrder"]==["fit-classical","neural-score","package-neural"]
    assert [x["stepIds"] for x in plan["stages"]]==[["fit-classical"],["neural-score"],["package-neural"]]
    assert plan["deterministicPlanning"] is True and plan["automaticExecution"] is False
    rep=s._cross_runtime_reproducibility_manifest({"crossRuntimeWorkflowArtifact":wf,"crossRuntimeExecutionPlanArtifact":plan})["crossRuntimeReproducibilityManifestArtifact"]
    assert rep["artifactDigestsRequired"] is True and rep["environmentCaptureRequired"] is True and rep["automaticExecution"] is False

def test_run_receipt_requires_sha256_and_preserves_non_evidence_boundary():
    wf=workflow(); plan=s._cross_runtime_execution_plan({"crossRuntimeWorkflowArtifact":wf})["crossRuntimeExecutionPlanArtifact"]
    rec=s._cross_runtime_run_receipt({"crossRuntimeExecutionPlanArtifact":plan,"stepResults":[
        {"stepId":"fit-classical","artifactId":"artifact-ml-1","artifactSha256":"a"*64},
        {"stepId":"neural-score","artifactId":"artifact-neural-1","artifactSha256":"b"*64},
    ]})["crossRuntimeRunReceiptArtifact"]
    assert rec["resultCount"]==2 and rec["automaticRemoteExecution"] is False and rec["isObservedEvidence"] is False
    try:
        s._cross_runtime_run_receipt({"crossRuntimeExecutionPlanArtifact":plan,"stepResults":[{"stepId":"x","artifactId":"a","artifactSha256":"bad"}]})
        raise AssertionError("bad digest should fail")
    except HTTPException: pass

def test_cycles_unknown_operations_and_cross_runtime_self_recursion_are_rejected():
    try:
        s._cross_runtime_workflow_contract({"workflowId":"cycle","steps":[
            {"stepId":"a","runtime":"ml","operation":"workspace.ml.predict","dependsOn":["b"]},
            {"stepId":"b","runtime":"neural","operation":"workspace.neural.infer-regression","dependsOn":["a"]},
        ]})
    except HTTPException:
        pass
    else:
        wf=s._cross_runtime_workflow_contract({"workflowId":"cycle","steps":[
            {"stepId":"a","runtime":"ml","operation":"workspace.ml.predict","dependsOn":["b"]},
            {"stepId":"b","runtime":"neural","operation":"workspace.neural.infer-regression","dependsOn":["a"]},
        ]})["crossRuntimeWorkflowArtifact"]
        try: s._cross_runtime_dependency_validate({"crossRuntimeWorkflowArtifact":wf}); raise AssertionError("cycle should fail")
        except HTTPException: pass
    for bad in [
        {"stepId":"x","runtime":"ml","operation":"workspace.ml.unknown"},
        {"stepId":"x","runtime":"neural","operation":"workspace.neural.cross-runtime-lineage"},
    ]:
        try: s._cross_runtime_step_contract(bad); raise AssertionError("bad operation should fail")
        except HTTPException: pass

def test_lineage_and_workspace_registry_contract():
    wf=workflow(); lineage=s._cross_runtime_lineage({"crossRuntimeWorkflowArtifact":wf})["crossRuntimeLineageArtifact"]
    assert lineage["nodeCount"]==3 and lineage["edgeCount"]==2 and lineage["isObservedEvidence"] is False
    import sys
    ROOT=P.parents[1]
    if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
    from app.polyglot import RUNTIME_BY_LANGUAGE
    n=RUNTIME_BY_LANGUAGE['neural']; assert len(n.operations)==141
    for op in ('workspace.neural.cross-runtime-workflow-contract','workspace.neural.cross-runtime-execution-plan','workspace.neural.cross-runtime-lineage'): assert op in n.operations
    poly=(ROOT/'app'/'polyglot.py').read_text()
    assert 'workspaceCrossRuntimeWorkflowArtifact' in poly and 'sc-workspace-artifact-store/1.0' in poly
