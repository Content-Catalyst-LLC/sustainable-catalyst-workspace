from copy import deepcopy
import pytest
from app.integrated_research_os_runtime import *

def ctx():
    return create_context({"projectRef":"project:alpha"})["context"]

def test_profile_contract():
    p=runtime_profile()
    assert p["version"]=="3.64.0"
    assert p["researchStageCount"]==9
    assert p["boundedOperationCount"]==8
    assert p["automaticModelExecutionEnabled"] is False
    assert p["automaticAgentExecutionEnabled"] is False
    assert p["automaticApprovalEnabled"] is False
    assert p["automaticPublicationEnabled"] is False
    assert p["automaticDecisionAuthorityEnabled"] is False
    assert p["stageAuthorityPreserved"] is True
    assert p["humanGovernancePreserved"] is True
    assert p["provenancePreserved"] is True

def test_create_requires_project():
    with pytest.raises(ValueError):
        create_context({})

def test_context_zero_authority():
    c=ctx()
    assert not any(c["authority"].values())
    assert list(c["stages"])==list(STAGES)

def test_bind_object():
    out=bind_object({"context":ctx(),"stage":"sources","objectRef":"source:1","objectSchema":"sc-source/1.0"})
    assert out["binding"]["stage"]=="sources"
    assert out["binding"]["sourceMutationPerformed"] is False
    assert out["binding"]["authorityGranted"] is False

def test_bad_stage_rejected():
    with pytest.raises(ValueError):
        bind_object({"context":ctx(),"stage":"magic","objectRef":"x","objectSchema":"s/1"})

def test_stage_link_non_mutating():
    out=link_stage({"context":ctx(),"sourceStage":"sources","targetStage":"analysis"})
    assert out["link"]["automaticHandoff"] is False
    assert out["link"]["automaticMutation"] is False

def test_readiness_descriptive():
    c=bind_object({"context":ctx(),"stage":"projects","objectRef":"p:1","objectSchema":"p/1"})["context"]
    r=readiness({"context":c,"requiredStages":["projects","sources"]})["readiness"]
    assert r["ready"] is False
    assert r["missingStages"]==["sources"]
    assert r["descriptiveOnly"] is True
    assert r["executionPerformed"] is False

def test_handoff_requires_human_acceptance():
    c=bind_object({"context":ctx(),"stage":"analysis","objectRef":"a:1","objectSchema":"a/1"})["context"]
    p=handoff_plan({"context":c,"sourceStage":"analysis","targetStage":"models"})["handoffPlan"]
    assert p["humanAcceptanceRequired"] is True
    assert p["automaticExecution"] is False
    assert p["automaticAcceptance"] is False
    assert p["automaticMutation"] is False

def test_package_non_authoritative():
    c=bind_object({"context":ctx(),"stage":"models","objectRef":"m:1","objectSchema":"m/1"})["context"]
    p=package_context({"context":c})["package"]
    assert len(p["packageDigest"])==64
    assert p["reproducible"] is True
    assert p["executionAllowed"] is False
    assert p["approvalAuthorityGranted"] is False
    assert p["publicationAuthorityGranted"] is False

def test_snapshot():
    s=snapshot({"context":ctx()})
    assert len(s["snapshotDigest"])==64
    assert s["authorityGranted"] is False
    assert s["executionAllowed"] is False

def test_validate_authority_escalation():
    c=ctx()
    c["authority"]["publish"]=True
    assert validate({"context":c})["valid"] is False

def test_operation_index_no_authority():
    i=operation_index()
    assert len(i["items"])==8
    assert all(x["bounded"] for x in i["items"])
    assert all(not x["executionAuthority"] for x in i["items"])
    assert all(not x["approvalAuthority"] for x in i["items"])
    assert all(not x["publicationAuthority"] for x in i["items"])

def test_dispatch():
    out=execute("workspace.research-os.create-context",{"projectRef":"project:beta"})
    assert out["version"]=="3.64.0"
