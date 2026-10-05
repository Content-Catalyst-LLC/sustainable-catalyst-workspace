import pytest
from app.portable_research_workspace_recovery import *

BASE={"projectRef":"p1","researchSessionRef":"s1","sourceWorkspaceVersion":"3.68.0","projects":[{"projectId":"p1"}],"notebooks":[{"notebookId":"n1"}],"artifacts":[{"artifactId":"a1"}],"datasets":[],"models":[],"executions":[],"handoffs":[],"metadata":{"title":"Demo","token":"secret"}}

def test_profile():
    p=runtime_profile(); assert p["version"]=="3.69.0"; assert p["boundedOperationCount"]==8; assert p["capabilities"]["portableResearchPackages"] is True

def test_manifest_excludes_secret_metadata():
    m=manifest(BASE); assert m["metadata"]["title"]=="Demo"; assert "token" not in m["metadata"]; assert m["wordpressIndependent"] if "wordpressIndependent" in m else True

def test_manifest_lineage():
    m=manifest(BASE); assert m["lineage"]["runtimeRegistryVersion"]=="3.67.0"; assert m["lineage"]["unifiedResearchSessionVersion"]=="3.66.0"; assert m["lineage"]["handoffConsolidationVersion"]=="3.68.0"

def test_package_and_verify():
    p=build_package(BASE); assert p["wordpressIndependent"] is True; assert p["standaloneCompatible"] is True; assert verify({"package":p})["valid"] is True

def test_tamper_fails():
    p=build_package(BASE); p["manifest"]["projectRef"]="tampered"; assert verify({"package":p})["valid"] is False

def test_restore_plan_is_non_mutating():
    p=build_package(BASE); r=restore_plan({"package":p}); assert r["restorePerformed"] is False; assert r["mutationPerformed"] is False; assert r["humanApprovalRequired"] is True; assert len(r["steps"])==8

def test_migration_drill():
    p=build_package(BASE); d=migration_drill({"package":p,"targetWorkspaceVersion":"3.70.0"}); assert d["readyForControlledRestore"] is True; assert d["drillOnly"] is True

def test_compatibility():
    c=compatibility(); assert c["compatible"] is True; assert c["rollbackTarget"]=="3.68.0"; assert c["databaseMigrationRequired"] is False

def test_snapshot():
    s=snapshot(BASE); assert s["readOnly"] is True; assert s["automaticRestoreEnabled"] is False; assert len(s["snapshotDigest"])==64

def test_no_authority():
    p=runtime_profile(); assert p["automaticRestoreEnabled"] is False; assert p["automaticImportEnabled"] is False; assert p["automaticCredentialExportEnabled"] is False; assert p["automaticSecretExportEnabled"] is False

def test_operation_index():
    x=operation_index(); assert len(x["items"])==8; assert all(i["mutationAuthority"] is False for i in x["items"]); assert all(i["restoreAuthority"] is False for i in x["items"])

def test_validate_requires_project():
    assert validate({"projects":[]})["valid"] is False

def test_execute():
    assert execute("workspace.portable-recovery.package",BASE)["result"]["version"]=="3.69.0"
    with pytest.raises(ValueError): execute("workspace.portable-recovery.magic",{})
