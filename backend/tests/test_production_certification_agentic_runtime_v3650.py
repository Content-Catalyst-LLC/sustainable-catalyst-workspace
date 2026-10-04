import pytest
from app.production_certification_agentic_runtime import *

def test_profile():
    p=runtime_profile()
    assert p["schema"]==RUNTIME_SCHEMA
    assert p["version"]=="3.65.0"
    assert p["certifiedRuntimeCount"]==5
    assert p["boundedOperationCount"]==8
    assert p["databaseMigrationRequired"] is False
    assert p["projectMigrationRequired"] is False

def test_runtime_chain_certifies():
    r=certify_runtime_chain()
    assert r["certified"] is True
    assert r["runtimeCount"]==5
    assert all(x["certified"] for x in r["items"])

def test_chain_versions_exact():
    r=certify_runtime_chain()
    assert [x["version"] for x in r["items"]]==["3.60.0","3.61.0","3.62.0","3.63.0","3.64.0"]

def test_routes():
    r=route_inventory()
    assert r["expectedRouteCount"]==13
    assert "/v1/production-certification-agentic-runtime/report" in r["expectedRoutes"]

def test_compatibility():
    r=compatibility_report()
    assert r["compatible"] is True
    assert r["rollbackTarget"]=="3.64.0"
    assert r["databaseMigrationRequired"] is False
    assert r["projectSchemaMigrationRequired"] is False

def test_recovery():
    r=recovery_readiness()
    assert r["ready"] is True
    assert r["restartSafe"] is True
    assert r["automaticRollbackEnabled"] is False
    assert r["automaticReplayEnabled"] is False

def test_host_parity_deferred_without_evidence():
    r=host_parity({})
    assert r["parity"] is None
    assert r["certificationDeferredWithoutEvidence"] is True

def test_host_parity_passes_with_complete_evidence():
    a=list(EXPECTED_HOST_ASSETS)
    r=host_parity({"wordpressAssets":a,"standaloneAssets":a})
    assert r["parity"] is True
    assert r["wordpressMissing"]==[]
    assert r["standaloneMissing"]==[]

def test_host_parity_detects_missing():
    a=list(EXPECTED_HOST_ASSETS[:-1])
    r=host_parity({"wordpressAssets":a,"standaloneAssets":a})
    assert r["parity"] is False
    assert "sc-workspace-production-certification-agentic-v3650.js" in r["wordpressMissing"]

def test_package_integrity():
    manifest={
      "version":"3.65.0",
      "runtimeSchema":RUNTIME_SCHEMA,
      "certifiedRuntimeVersions":["3.60.0","3.61.0","3.62.0","3.63.0","3.64.0"],
    }
    r=package_integrity({"manifest":manifest})
    assert r["verified"] is True
    assert len(r["manifestDigest"])==64

def test_package_integrity_rejects_wrong_chain():
    manifest={"version":"3.65.0","runtimeSchema":RUNTIME_SCHEMA,"certifiedRuntimeVersions":[]}
    assert package_integrity({"manifest":manifest})["verified"] is False

def test_report():
    r=certification_report()
    assert r["certified"] is True
    assert len(r["reportDigest"])==64
    assert r["certificationIsDescriptiveOnly"] is True
    assert r["runtimeMutationEnabled"] is False

def test_operation_index_no_authority():
    r=operation_index()
    assert len(r["items"])==8
    assert all(x["bounded"] for x in r["items"])
    assert all(not x["executionAuthority"] for x in r["items"])
    assert all(not x["approvalAuthority"] for x in r["items"])
    assert all(not x["publicationAuthority"] for x in r["items"])
    assert all(not x["mutationAuthority"] for x in r["items"])

def test_snapshot():
    r=snapshot({})
    assert r["schema"]==SNAPSHOT_SCHEMA
    assert len(r["snapshotDigest"])==64
    assert r["authorityGranted"] is False
    assert r["mutationPerformed"] is False

def test_dispatch():
    out=execute("workspace.production-certification.certify-runtime-chain",{})
    assert out["version"]=="3.65.0"
    assert out["result"]["certified"] is True

def test_unknown_operation_rejected():
    with pytest.raises(ValueError):
        execute("workspace.production-certification.magic",{})
