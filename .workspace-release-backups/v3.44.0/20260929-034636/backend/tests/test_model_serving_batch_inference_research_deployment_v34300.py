from __future__ import annotations
import importlib.util, pathlib
from copy import deepcopy
from fastapi import HTTPException
P=pathlib.Path(__file__).resolve().parents[1]/"neural-runtime"/"service.py"
spec=importlib.util.spec_from_file_location("sc_neural_v34300",P); s=importlib.util.module_from_spec(spec); spec.loader.exec_module(s)

def model_package():
    model={"schema":"sc-workspace-neural-model-spec/1.0","modelType":"linear","inputFeatures":2,"outputFeatures":1,"weights":[[1.0,2.0]],"bias":[0.0]}
    return s._model_package_create({"modelSpec":model,"task":"regression","featureNames":["a","b"]})["modelPackage"]

def binding():
    return s._serving_model_binding({"modelPackage":model_package(),"servingId":"research-linear-v1","audience":"research","maxRequestRows":2,"maxConcurrency":2})["servingModelBindingArtifact"]

def compatibility(b=None):
    b=b or binding(); return s._serving_compatibility_evaluate({"servingModelBindingArtifact":b,"deviceClass":"cpu"})["servingCompatibilityArtifact"]

def plan(b=None):
    b=b or binding(); return s._batch_inference_plan({"servingModelBindingArtifact":b,"features":[[1,2],[3,4],[5,6]],"rowIds":["r1","r2","r3"],"batchSize":2})["batchInferencePlanArtifact"]

def test_health_registry_and_serving_boundaries():
    h=s.health(); assert h["version"]=="3.43.0" and len(h["operations"])==133
    assert h["modelServingBatchInferenceResearchDeploymentRuntime"] is True
    assert h["modelServingPublicNetworkExposureEnabled"] is False and h["researchDeploymentInfrastructureMutationEnabled"] is False
    for k in ("modelEndpoint","servingUrl","deploymentUrl","publicEndpoint","containerImage","dockerImage","deploymentToken","apiKey"): assert k in s.BLOCKED_PAYLOAD_KEYS

def test_model_binding_and_runtime_compatibility_are_immutable_and_private():
    b=binding(); c=compatibility(b)
    assert b["immutableModelBinding"] is True and b["publicNetworkExposure"] is False and b["clientSuppliedEndpointAccepted"] is False
    assert b["modelPackageFingerprint"]==b["modelPackage"]["artifactFingerprint"]
    assert c["compatible"] is True and c["publicEndpointRequired"] is False and c["externalRuntimeImageRequired"] is False

def test_bounded_serving_inference_preserves_prediction_provenance():
    b=binding(); r=s._serving_infer({"servingModelBindingArtifact":b,"requestId":"req-serve","features":[[1,2],[3,4]],"rowIds":["one","two"]})
    a=r["servingInferenceArtifact"]
    assert [x["outputs"][0] for x in r["predictions"]]==[5.0,11.0]
    assert a["modelPackageFingerprint"]==b["modelPackageFingerprint"] and a["predictionArtifact"]["sourceModelPackageId"]==b["modelPackageId"]
    assert a["externalEndpointInvoked"] is False and a["isObservedEvidence"] is False

def test_batch_plan_is_deterministic_and_execution_is_bounded():
    b=binding(); p=plan(b)
    assert p["batchCount"]==2 and [(x["start"],x["stop"]) for x in p["batches"]]==[(0,2),(2,3)]
    r=s._batch_inference_execute({"servingModelBindingArtifact":b,"batchInferencePlanArtifact":p,"features":[[1,2],[3,4],[5,6]],"rowIds":["r1","r2","r3"]})
    a=r["batchInferenceResultArtifact"]
    assert [x["outputs"][0] for x in r["predictions"]]==[5.0,11.0,17.0]
    assert a["batchCount"]==2 and a["externalQueueInvoked"] is False and a["publicNetworkExposure"] is False

def test_research_deployment_readiness_rejects_public_exposure():
    b=binding(); c=compatibility(b)
    ready=s._research_deployment_readiness({"servingModelBindingArtifact":b,"servingCompatibilityArtifact":c,"deploymentPolicy":{"audience":"research","maxConcurrentRequests":1,"publicNetworkExposure":False}})["researchDeploymentReadinessArtifact"]
    assert ready["ready"] is True and ready["operatorApprovalRequired"] is True and ready["infrastructureMutationExecuted"] is False
    try:
        s._research_deployment_readiness({"servingModelBindingArtifact":b,"servingCompatibilityArtifact":c,"deploymentPolicy":{"audience":"research","publicNetworkExposure":True}})
        raise AssertionError("public exposure should fail")
    except HTTPException: pass

def test_manifest_and_receipt_are_operator_controlled_nonexecuting_records():
    b=binding(); c=compatibility(b); p=plan(b)
    ready=s._research_deployment_readiness({"servingModelBindingArtifact":b,"servingCompatibilityArtifact":c,"batchInferencePlanArtifact":p,"deploymentPolicy":{"audience":"internal","maxConcurrentRequests":1}})["researchDeploymentReadinessArtifact"]
    m=s._research_deployment_manifest({"servingModelBindingArtifact":b,"researchDeploymentReadinessArtifact":ready,"deploymentId":"dep-1","title":"Research deployment","researchContextRef":"core:research:343"})["researchDeploymentManifestArtifact"]
    batch=s._batch_inference_execute({"servingModelBindingArtifact":b,"batchInferencePlanArtifact":p,"features":[[1,2],[3,4],[5,6]],"rowIds":["r1","r2","r3"]})["batchInferenceResultArtifact"]
    rec=s._research_deployment_receipt({"researchDeploymentManifestArtifact":m,"batchInferenceResultArtifact":batch,"operatorState":"approved"})["researchDeploymentReceiptArtifact"]
    assert m["deploymentPrepared"] is True and m["deploymentExecuted"] is False and m["externalEndpointProvisioned"] is False
    assert rec["operatorDeclaredState"] is True and rec["workspaceInfrastructureMutationExecuted"] is False and rec["workspacePublicEndpointProvisioned"] is False

def test_tampering_and_external_serving_material_are_rejected():
    b=binding(); bad=deepcopy(b); bad["maxConcurrency"]=99
    try: s._serving_compatibility_evaluate({"servingModelBindingArtifact":bad}); raise AssertionError("tampering should fail")
    except HTTPException: pass
    try:
        s.execute({"schema":"sc-workspace-polyglot-execution-envelope/1.0","language":"neural","operation":"workspace.neural.serving-model-binding","arbitraryCodeExecution":False,"payload":{"modelPackage":model_package(),"servingUrl":"https://example.invalid"}},authorization="Bearer test")
    except HTTPException as e: assert e.status_code in {400,401,503}

def test_workspace_registry_and_artifact_persistence_contract():
    import sys
    ROOT=P.parents[1]
    if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
    from app.polyglot import RUNTIME_BY_LANGUAGE
    n=RUNTIME_BY_LANGUAGE['neural']; assert len(n.operations)==133
    for op in ('workspace.neural.serving-model-binding','workspace.neural.serving-infer','workspace.neural.batch-inference-execute','workspace.neural.research-deployment-receipt'): assert op in n.operations
    poly=(ROOT/'app'/'polyglot.py').read_text()
    assert 'workspaceModelServingArtifact' in poly and 'sc-workspace-artifact-store/1.0' in poly
    assert 'application/vnd.sc.workspace.neural-research-deployment-manifest+json' in poly
