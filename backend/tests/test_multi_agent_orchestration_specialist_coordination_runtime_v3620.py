import pytest

from app.multi_agent_orchestration_specialist_coordination_runtime import (
    ASSIGNMENT_SCHEMA,
    GOVERNANCE_HANDOFF_SCHEMA,
    RECEIPT_SCHEMA,
    RUNTIME_SCHEMA,
    SPECIALIST_SCHEMA,
    TEAM_SCHEMA,
    create_team,
    delegate,
    execute,
    governance_handoff,
    operation_index,
    reconcile,
    record_result,
    register_specialist,
    runtime_profile,
    snapshot,
    validate,
)


def specialist(role="research_evidence", caps=None, sid=None):
    return register_specialist({
        "specialist": {
            "specialistId": sid,
            "roleFamily": role,
            "capabilityIds": caps or ["research.search"],
        }
    })["specialist"]


def team_with_two():
    return create_team({
        "teamId": "team_test",
        "coordinator": {"coordinatorId": "coord_1"},
        "specialists": [
            specialist("research_evidence", ["research.search"], "s1"),
            specialist("data_quantitative_analysis", ["stats.analyze"], "s2"),
        ],
    })["team"]


def test_profile_is_bounded_and_links_upstream_governance():
    p = runtime_profile()
    assert p["schema"] == RUNTIME_SCHEMA
    assert p["version"] == "3.62.0"
    assert p["boundedOperationCount"] == 8
    assert p["specialistRoleFamilyCount"] == 8
    assert p["coordinatorApprovalAuthorityEnabled"] is False
    assert p["specialistApprovalAuthorityEnabled"] is False
    assert p["automaticGovernanceBypassEnabled"] is False
    assert p["arbitraryCodeExecution"] is False
    assert p["dissentPreserved"] is True
    assert p["upstreamRuntimeSchemas"]["humanGovernance"].endswith("/1.0")


def test_operation_index_is_bounded_and_governance_delegated():
    idx = operation_index()
    assert len(idx["items"]) == 8
    assert all(x["bounded"] for x in idx["items"])
    assert idx["coordinatorApprovalAuthorityEnabled"] is False
    assert idx["governanceDelegatedTo"] == "sc-workspace-human-governance-approval-intervention-runtime/1.0"


def test_register_specialist_requires_capabilities_and_rejects_elevated_authority():
    s = specialist()
    assert s["schema"] == SPECIALIST_SCHEMA
    assert s["authority"]["approve"] is False
    with pytest.raises(ValueError):
        register_specialist({"specialist": {"roleFamily": "visualization", "capabilityIds": []}})
    with pytest.raises(ValueError):
        register_specialist({"specialist": {"roleFamily": "visualization", "capabilityIds": ["viz.render"], "authority": {"approve": True}}})


def test_create_team_preserves_coordinator_boundary():
    team = team_with_two()
    assert team["schema"] == TEAM_SCHEMA
    assert team["coordinator"]["approvalAuthority"] is False
    assert len(team["specialists"]) == 2


def test_delegate_enforces_specialist_capability_constraint():
    team = team_with_two()
    out = delegate({"team": team, "specialistId": "s1", "capabilityId": "research.search", "objective": "Find evidence"})
    assert out["assignment"]["schema"] == ASSIGNMENT_SCHEMA
    assert out["executionAllowed"] is True
    with pytest.raises(ValueError):
        delegate({"team": team, "specialistId": "s1", "capabilityId": "stats.analyze"})


def test_sensitive_delegation_requires_governance():
    team = team_with_two()
    out = delegate({
        "team": team,
        "specialistId": "s1",
        "capabilityId": "research.search",
        "actionType": "claim_promotion",
        "objective": "Promote a claim",
    })
    assert out["governanceRequired"] is True
    assert out["executionAllowed"] is False
    assert out["assignment"]["status"] == "waiting_governance"


def test_record_result_creates_receipt_for_executable_assignment():
    team = team_with_two()
    delegated = delegate({"team": team, "specialistId": "s1", "capabilityId": "research.search", "objective": "Find evidence"})
    out = record_result({
        "team": delegated["team"],
        "assignmentId": delegated["assignment"]["assignmentId"],
        "status": "succeeded",
        "artifactRefs": ["artifact:1"],
        "limitations": ["sample limited"],
    })
    assert out["receipt"]["schema"] == RECEIPT_SCHEMA
    assert out["receipt"]["status"] == "succeeded"
    assert out["team"]["assignments"][0]["status"] == "succeeded"


def test_record_result_blocks_unsatisfied_governance_assignment():
    team = team_with_two()
    delegated = delegate({"team": team, "specialistId": "s1", "capabilityId": "research.search", "actionType": "model_approval"})
    with pytest.raises(ValueError):
        record_result({"team": delegated["team"], "assignmentId": delegated["assignment"]["assignmentId"]})


def test_reconcile_preserves_conflict_and_dissent_without_truth_determination():
    team = team_with_two()
    receipts = [
        {"receiptId": "r1", "specialistId": "s1"},
        {"receiptId": "r2", "specialistId": "s2"},
    ]
    out = reconcile({
        "team": team,
        "receipts": receipts,
        "agreementSummary": ["Both accept source A"],
        "disagreements": [{
            "topic": "effect size",
            "positions": [{"specialistId": "s1", "position": "large"}, {"specialistId": "s2", "position": "small"}],
            "humanResolutionRequired": True,
        }],
    })
    assert out["synthesis"]["dissentPreserved"] is True
    assert out["synthesis"]["automaticTruthDetermination"] is False
    assert out["conflicts"][0]["status"] == "unresolved"
    assert out["team"]["status"] == "needs_human_resolution"


def test_governance_handoff_targets_v361_and_does_not_approve():
    team = team_with_two()
    delegated = delegate({"team": team, "specialistId": "s1", "capabilityId": "research.search", "actionType": "external_side_effect"})
    out = governance_handoff({
        "team": delegated["team"],
        "assignmentId": delegated["assignment"]["assignmentId"],
        "policy": {"schema": "sc-workspace-human-governance-policy/1.0", "policyId": "p1"},
        "reason": "Needs a human decision",
    })
    assert out["handoff"]["schema"] == GOVERNANCE_HANDOFF_SCHEMA
    assert out["handoff"]["targetOperation"] == "workspace.governance.request-approval"
    assert out["handoff"]["coordinatorMayApprove"] is False
    assert out["executionAllowed"] is False


def test_snapshot_and_validate_and_execute_dispatch():
    team = team_with_two()
    snap = snapshot({"team": team})
    assert snap["schema"] == "sc-workspace-multi-agent-coordination-snapshot/1.0"
    assert len(snap["coordinationDigest"]) == 64
    assert validate({"team": team})["valid"] is True
    result = execute("workspace.multi-agent.snapshot", {"team": team})
    assert result["bounded"] is True
    with pytest.raises(ValueError):
        execute("workspace.multi-agent.unbounded", {})
