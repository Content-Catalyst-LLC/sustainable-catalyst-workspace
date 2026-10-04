import pytest
from app.cross_product_research_handoff_consolidation import *

PINNED={"kind":"dataset","objectId":"d1","revision":2,"fingerprint":"abc123"}
BASE={"sourceProduct":"workspace","destinationProduct":"research-lab","intent":"analyze","projectRef":"p1","researchSessionRef":"s1","objects":[PINNED]}

def test_profile():
    p=runtime_profile(); assert p["version"]=="3.68.0"; assert p["registeredDestinationCount"]==9; assert p["boundedOperationCount"]==8; assert p["consolidationValid"] is True

def test_authority_preserved():
    p=runtime_profile(); assert p["existingHandoffFabricRemainsAuthoritative"] is True; assert p["backendPersistenceRemainsAuthoritative"] is True

def test_destination_profiles():
    d=destination_profiles(); assert d["destinationCount"]==9; assert {x["product"] for x in d["items"]}==set(PRODUCTS)

def test_compatibility_checks():
    assert intent_compatibility({"sourceProduct":"workspace","destinationProduct":"workbench","intent":"simulate"})["compatible"] is True
    assert intent_compatibility({"sourceProduct":"workspace","destinationProduct":"decision-studio","intent":"simulate"})["compatible"] is False

def test_same_product_rejected():
    with pytest.raises(ValueError): intent_compatibility({"sourceProduct":"workspace","destinationProduct":"workspace","intent":"analyze"})

def test_plan_requires_pinning():
    with pytest.raises(ValueError): plan({**BASE,"objects":[{"kind":"dataset","objectId":"d1","revision":2}]})

def test_plan_lineage():
    p=plan(BASE); assert p["lineage"]["registryVersion"]=="3.67.0"; assert p["lineage"]["sessionVersion"]=="3.66.0"; assert p["lineage"]["handoffPackageSchema"]=="sc-workspace-research-handoff/1.0"; assert p["dispatchPerformed"] is False; assert len(p["planDigest"])==64

def test_manifest():
    m=manifest(BASE); assert m["portable"] is True and m["readOnly"] is True; assert m["importExecutesAutomatically"] is False; assert m["destinationMustExplicitlyAccept"] is True; assert len(m["manifestDigest"])==64

def test_acceptance_contract():
    a=acceptance_contract({"destinationProduct":"research-lab"}); assert a["destinationMustMatchPreparedHandoff"] is True; assert a["durableReceiptRequired"] is True; assert a["automaticAcceptanceEnabled"] is False

def test_compatibility():
    c=compatibility(); assert c["compatible"] is True; assert c["rollbackTarget"]=="3.67.0"; assert c["databaseMigrationRequired"] is False; assert c["projectSchemaMigrationRequired"] is False

def test_validate():
    v=validate(); assert v["valid"] is True and v["errors"]==[]

def test_snapshot():
    s=snapshot({"handoff":BASE}); assert s["readOnly"] is True and s["portable"] is True; assert s["automaticReplayEnabled"] is False; assert len(s["snapshotDigest"])==64

def test_operation_index():
    x=operation_index(); assert len(x["items"])==8; assert all(i["descriptiveOnly"] for i in x["items"]); assert all(i["mutationAuthority"] is False for i in x["items"])

def test_no_automatic_authority():
    p=runtime_profile(); assert p["automaticHandoffDispatchEnabled"] is False; assert p["automaticDestinationExecutionEnabled"] is False; assert p["automaticAcceptanceEnabled"] is False; assert p["automaticApprovalEnabled"] is False; assert p["automaticDecisionAuthorityEnabled"] is False

def test_execute():
    r=execute("workspace.handoff-consolidation.plan",BASE); assert r["result"]["destinationProduct"]=="research-lab"
    with pytest.raises(ValueError): execute("workspace.handoff-consolidation.magic",{})
