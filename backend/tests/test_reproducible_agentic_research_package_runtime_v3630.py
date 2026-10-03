from copy import deepcopy
import pytest
from app.reproducible_agentic_research_package_runtime import *

def pkg(): return create_package({"researchRef":"project:alpha"})["package"]

def test_profile_boundaries():
    p=runtime_profile()
    assert p["version"]=="3.63.0" and p["boundedOperationCount"]==8
    assert p["arbitraryCodeExecution"] is False
    assert p["automaticReplayEnabled"] is False
    assert p["automaticApprovalEnabled"] is False
    assert p["automaticGovernanceBypassEnabled"] is False
    assert p["packageMayGrantAuthority"] is False
    assert p["packageMayModifySourceObjects"] is False
    assert p["provenancePreserved"] and p["governanceHistoryPreserved"] and p["dissentPreserved"]

def test_requires_research_ref():
    with pytest.raises(ValueError): create_package({})

def test_zero_authority():
    assert not any(pkg()["authority"].values())

def test_object_content_addressing():
    o=add_object({"package":pkg(),"kind":"dataset","sourceRef":"dataset:1","content":{"rows":10}})["object"]
    assert len(o["contentDigest"])==64 and o["sourceMutationPerformed"] is False

def test_unknown_object_kind_rejected():
    with pytest.raises(ValueError): add_object({"package":pkg(),"kind":"magic","sourceRef":"x","content":{}})

def test_receipt_and_governance_capture():
    p=add_receipt({"package":pkg(),"receipt":{"schema":"sc-workspace-specialist-result-receipt/1.0","receiptId":"r1"}})["package"]
    g=add_governance({"package":p,"governance":{"schema":"sc-workspace-human-approval-decision/1.0","decisionId":"d1"}})["governanceRecord"]
    assert g["immutableCapture"] and g["approvalAuthorityGranted"] is False

def test_finalize_verify():
    p=add_object({"package":pkg(),"kind":"workflow","sourceRef":"workflow:1","content":{"steps":[]}})["package"]
    p=finalize_package({"package":p})["package"]
    v=verify_package({"package":p})["verification"]
    assert p["status"]=="finalized" and v["verified"] and v["descriptiveOnly"]
    assert v["executionPerformed"] is False and v["approvalPerformed"] is False

def test_tamper_detection():
    p=add_object({"package":pkg(),"kind":"artifact","sourceRef":"artifact:1","content":{"v":1}})["package"]
    p=finalize_package({"package":p})["package"]; t=deepcopy(p); t["objects"][0]["content"]["v"]=2
    assert verify_package({"package":t})["verification"]["verified"] is False

def test_finalized_immutable():
    p=add_object({"package":pkg(),"kind":"artifact","sourceRef":"a:1","content":{}})["package"]
    p=finalize_package({"package":p})["package"]
    with pytest.raises(ValueError): add_object({"package":p,"kind":"artifact","sourceRef":"a:2","content":{}})

def test_authority_escalation_invalid():
    p=pkg(); p["authority"]["approval"]=True
    assert validate({"package":p})["valid"] is False

def test_snapshot_non_authoritative():
    s=snapshot({"package":pkg()})
    assert len(s["snapshotDigest"])==64 and s["executionAllowed"] is False and s["authorityGranted"] is False

def test_operation_index_no_authority():
    i=operation_index()
    assert len(i["items"])==8
    assert all(not x["executionAuthority"] and not x["approvalAuthority"] for x in i["items"])

def test_dispatch():
    r=execute("workspace.research-package.create",{"researchRef":"project:beta"})
    assert r["version"]=="3.63.0"
