import pytest
from app.research_os_runtime_registry import *

def test_profile_contract():
    p=runtime_profile()
    assert p["schema"]==RUNTIME_SCHEMA and p["version"]=="3.67.0"
    assert p["registeredRuntimeCount"]==7 and p["boundedOperationCount"]==8
    assert p["registryValid"] is True

def test_validate_chain():
    r=validate()
    assert r["valid"] is True and r["runtimeCount"]==7 and r["errors"]==[]

def test_list_contains_v360_v366():
    r=list_runtimes()
    assert r["runtimeCount"]==7
    assert r["items"][0]["version"]=="3.60.0"
    assert r["items"][-1]["version"]=="3.66.0"

def test_descriptors_unique():
    items=descriptors()
    assert len({x["runtimeId"] for x in items})==7
    assert len({x["runtimeSchema"] for x in items})==7

def test_descriptors_have_operations_and_digest():
    assert all(x["operationCount"]>0 for x in descriptors())
    assert all(len(x["descriptorDigest"])==64 for x in descriptors())

def test_get_runtime():
    assert get_runtime({"runtimeId":"unified-research-session"})["version"]=="3.66.0"
    assert get_runtime({"version":"3.64.0"})["runtimeId"]=="integrated-research-os"

def test_get_runtime_errors():
    with pytest.raises(ValueError): get_runtime({})
    with pytest.raises(ValueError): get_runtime({"runtimeId":"missing"})

def test_capability_discovery_descriptive():
    r=discover_capabilities({"capability":"session"})
    assert r["descriptiveOnly"] is True and r["activationPerformed"] is False

def test_enabled_capability_filter():
    r=discover_capabilities({"enabledOnly":True})
    assert all(x["enabled"] is True for x in r["items"])

def test_operation_discovery():
    r=discover_operations({"operation":"snapshot"})
    assert r["descriptiveOnly"] is True and r["dispatchPerformed"] is False
    assert all(x["invocationAuthority"] is False for x in r["items"])

def test_operation_discovery_by_runtime():
    r=discover_operations({"runtimeId":"unified-research-session"})
    assert r["matchCount"]==8
    assert all(x["runtimeId"]=="unified-research-session" for x in r["items"])

def test_authority_matrix():
    r=authority_matrix()
    assert r["runtimeCount"]==7
    assert r["registryAuthority"]["invokeRuntime"] is False
    assert r["registryAuthority"]["approveGovernance"] is False
    assert r["registryAuthority"]["publish"] is False

def test_compatibility():
    r=compatibility()
    assert r["compatible"] is True
    assert r["compatibleFrom"]=="3.60.0"
    assert r["discoveredThrough"]=="3.66.0"
    assert r["rollbackTarget"]=="3.66.0"
    assert r["databaseMigrationRequired"] is False
    assert r["projectSchemaMigrationRequired"] is False

def test_snapshot():
    r=snapshot()
    assert r["readOnly"] is True and r["portable"] is True
    assert r["authorityGranted"] is False and len(r["snapshotDigest"])==64

def test_operation_index_boundaries():
    x=operation_index()
    assert len(x["items"])==8
    assert all(i["descriptiveOnly"] for i in x["items"])
    assert all(i["executionAuthority"] is False for i in x["items"])
    assert all(i["mutationAuthority"] is False for i in x["items"])

def test_registry_never_dispatches():
    p=runtime_profile()
    assert p["runtimeInvocationEnabled"] is False
    assert p["automaticOperationDispatchEnabled"] is False
    assert p["automaticCapabilityActivationEnabled"] is False

def test_execute_dispatch():
    assert execute("workspace.runtime-registry.list",{})["result"]["runtimeCount"]==7
    assert execute("workspace.runtime-registry.get-runtime",{"runtimeId":"integrated-research-os"})["result"]["version"]=="3.64.0"

def test_unknown_operation_rejected():
    with pytest.raises(ValueError): execute("workspace.runtime-registry.magic",{})

def test_upstream_authority_preserved():
    p=runtime_profile()
    assert p["upstreamRuntimeAuthorityPreserved"] is True
    assert p["automaticDecisionAuthorityEnabled"] is False
