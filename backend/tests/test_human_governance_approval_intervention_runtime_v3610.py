from app.human_governance_approval_intervention_runtime import (
    DEFAULT_BOUNDARIES,
    POLICY_SCHEMA,
    VERSION,
    execute,
    operation_index,
    runtime_profile,
)


def _policy():
    return execute("workspace.governance.register-policy", {
        "policy": {
            "title": "Research governance",
            "approverRoles": ["research_owner", "principal_investigator"],
            "requiredActions": ["model_approval", "claim_promotion"],
        }
    })["policy"]


def _approval(policy, requester="agent-1"):
    return execute("workspace.governance.request-approval", {
        "policy": policy,
        "action": "model_approval",
        "subjectRef": "urn:model:1",
        "requester": {"actorId": requester, "actorType": "agent"},
    })["approval"]


def test_profile_and_operation_index():
    profile = runtime_profile()
    assert profile["version"] == VERSION == "3.61.0"
    assert profile["boundedOperationCount"] == 7
    assert operation_index()["boundedOperationsOnly"] is True


def test_hard_governance_boundaries():
    assert DEFAULT_BOUNDARIES["automaticApprovalEnabled"] is False
    assert DEFAULT_BOUNDARIES["agentApprovalAuthorityEnabled"] is False
    assert DEFAULT_BOUNDARIES["selfApprovalEnabled"] is False
    assert DEFAULT_BOUNDARIES["approvalBypassEnabled"] is False
    assert DEFAULT_BOUNDARIES["automaticResumeEnabled"] is False
    assert DEFAULT_BOUNDARIES["arbitraryCodeExecution"] is False


def test_register_policy_is_human_governed():
    policy = _policy()
    assert policy["schema"] == POLICY_SCHEMA
    assert policy["requireHumanActor"] is True
    assert policy["allowSelfApproval"] is False


def test_required_approval_blocks_execution_until_human_decision():
    policy = _policy()
    approval = _approval(policy)
    assert approval["status"] == "pending"
    decided = execute("workspace.governance.decide", {
        "policy": policy,
        "approval": approval,
        "actor": {"actorId": "human-1", "actorType": "human", "role": "research_owner"},
        "decision": "approve",
    })
    assert decided["approval"]["status"] == "approved"
    assert decided["executionAllowed"] is True
    assert decided["decision"]["immutable"] is True


def test_self_approval_is_prohibited():
    policy = _policy()
    approval = _approval(policy, requester="human-1")
    try:
        execute("workspace.governance.decide", {
            "policy": policy,
            "approval": approval,
            "actor": {"actorId": "human-1", "actorType": "human", "role": "research_owner"},
            "decision": "approve",
        })
    except ValueError as exc:
        assert "self-approval" in str(exc)
    else:
        raise AssertionError("expected self-approval rejection")


def test_agent_cannot_exercise_human_governance_authority():
    policy = _policy()
    approval = _approval(policy)
    try:
        execute("workspace.governance.decide", {
            "policy": policy,
            "approval": approval,
            "actor": {"actorId": "agent-2", "actorType": "agent", "role": "research_owner"},
            "decision": "approve",
        })
    except ValueError as exc:
        assert "actorType=human" in str(exc)
    else:
        raise AssertionError("expected agent authority rejection")


def test_pause_and_human_resume_are_explicit():
    paused = execute("workspace.governance.intervene", {
        "subjectRef": "urn:workflow:1",
        "actor": {"actorId": "human-1", "actorType": "human", "role": "research_owner"},
        "intervention": "pause",
        "reason": "Review evidence",
    })
    assert paused["state"]["status"] == "paused"
    assert paused["executionAllowed"] is False

    resumed = execute("workspace.governance.resume", {
        "state": paused["state"],
        "actor": {"actorId": "human-2", "actorType": "human", "role": "research_owner"},
        "reason": "Review complete",
    })
    assert resumed["state"]["status"] == "active"
    assert resumed["executionAllowed"] is True


def test_snapshot_has_reproducible_digest():
    policy = _policy()
    snap = execute("workspace.governance.snapshot", {"policy": policy})["snapshot"]
    assert snap["schema"] == "sc-workspace-human-governance-snapshot/1.0"
    assert len(snap["governanceDigest"]) == 64
