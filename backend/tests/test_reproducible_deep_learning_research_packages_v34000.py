from __future__ import annotations
import base64, importlib.util, json, pathlib
from fastapi import HTTPException
P=pathlib.Path(__file__).resolve().parents[1]/"neural-runtime"/"service.py"
spec=importlib.util.spec_from_file_location("sc_neural_v34000",P); s=importlib.util.module_from_spec(spec); spec.loader.exec_module(s)

def components():
    return [
      {"componentId":"dataset","artifactId":"dataset-a","role":"dataset","schema":"sc-workspace-neural-dataset-manifest/1.0","sha256":"1"*64,"bytes":1024,"operation":"workspace.neural.dataset-manifest","requiredForReproduction":True,"dependsOn":[]},
      {"componentId":"model","artifactId":"model-a","role":"model-package","schema":"sc-workspace-neural-model-package/1.0","sha256":"2"*64,"bytes":2048,"operation":"workspace.neural.package-create","requiredForReproduction":True,"dependsOn":["dataset"]},
      {"componentId":"eval","artifactId":"eval-a","role":"evaluation","schema":"sc-workspace-neural-evaluation-artifact/1.0","sha256":"3"*64,"bytes":512,"operation":"workspace.neural.evaluate-regression","requiredForReproduction":False,"dependsOn":["model"]},
    ]

def package():
    return s._research_package_create({"components":components(),"title":"Reproducible test","researchContextRef":"core:research:1","seed":3400,"reproductionPolicy":"strict-digest"})["deepLearningResearchPackage"]

def test_health_and_registry():
    h=s.health(); assert h["version"]=="3.40.0"; assert len(h["operations"])==109; assert h["reproducibleDeepLearningResearchPackagesRuntime"] is True; assert h["deepLearningResearchPackageAutomaticExecution"] is False

def test_plan_create_verify_and_inspect():
    plan=s._research_package_plan({"components":components()})["researchPackagePlanArtifact"]; assert plan["componentCount"]==3; assert plan["orderedComponentIds"]==["dataset","model","eval"]
    pkg=package(); assert pkg["packageId"].startswith("dlrp_") and pkg["evidenceBoundary"]["isObservedEvidence"] is False
    ver=s._research_package_verify({"researchPackage":pkg})["researchPackageVerificationArtifact"]; assert ver["valid"] is True and ver["runtimeCompatible"] is True
    ins=s._research_package_inspect({"researchPackage":pkg})["researchPackageInspectionArtifact"]; assert ins["roles"]["evaluation"]==1

def test_reproduction_plan_verify_export_lineage():
    pkg=package(); rp=s._research_package_reproduction_plan({"researchPackage":pkg})["researchPackageReproductionPlanArtifact"]; assert rp["stepCount"]==3 and rp["automaticExecution"] is False
    exact=s._research_package_reproduction_verify({"researchPackage":pkg,"observedComponents":components()})["researchPackageReproductionVerificationArtifact"]; assert exact["classification"]=="exact"
    compatible=s._research_package_reproduction_verify({"researchPackage":pkg,"observedComponents":components()[:2]})["researchPackageReproductionVerificationArtifact"]; assert compatible["classification"]=="compatible"
    ex=s._research_package_export({"researchPackage":pkg}); raw=base64.b64decode(ex["export"]["contentBase64"]); assert json.loads(raw)["packageId"]==pkg["packageId"]
    lin=s._research_package_lineage({"researchPackage":pkg})["researchPackageLineageArtifact"]; assert lin["nodeCount"]==4 and lin["edgeCount"]==5

def test_digest_and_dependency_validation():
    bad=components(); bad[1]=dict(bad[1],sha256="not-a-digest")
    try: s._research_package_plan({"components":bad}); raise AssertionError("invalid digest should fail")
    except HTTPException: pass
    cyc=components(); cyc[0]=dict(cyc[0],dependsOn=["model"])
    try: s._research_package_plan({"components":cyc}); raise AssertionError("cycle should fail")
    except HTTPException: pass

def test_security_boundaries():
    assert "researchPackageUrl" in s.BLOCKED_PAYLOAD_KEYS and "exportPath" in s.BLOCKED_PAYLOAD_KEYS
    pkg=package(); assert pkg["securityBoundary"]["arbitraryCodeEmbedded"] is False and pkg["securityBoundary"]["credentialsEmbedded"] is False
    source=P.read_text(); assert "torch.load(" not in source and "torch.save(" not in source
