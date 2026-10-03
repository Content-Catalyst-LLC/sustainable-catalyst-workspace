from app.agentic_research_workflow_runtime import (
    DEFAULT_BOUNDARIES,
    VERSION,
    execute,
    operation_index,
    runtime_profile,
)


def _request(review_policy="never"):
    return {
        "goal": {"title": "Research", "question": "What does the evidence support?"},
        "steps": [
            {
                "stepId": "s1",
                "title": "Retrieve",
                "objective": "Retrieve bounded evidence",
                "binding": {
                    "capabilityId": "workspace.search",
                    "operation": "search",
                    "runtimeId": "python",
                    "inputRefs": ["urn:source:1"],
                    "outputKinds": ["research-artifact"],
                },
                "reviewPolicy": review_policy,
            },
            {
                "stepId": "s2",
                "title": "Synthesize",
                "objective": "Synthesize the retrieved material",
                "binding": {
                    "capabilityId": "workspace.synthesis",
                    "operation": "synthesize",
                    "runtimeId": "python",
                },
                "dependsOn": ["s1"],
            },
        ],
    }


def test_profile_and_operation_index():
    profile = runtime_profile()
    assert profile["version"] == VERSION == "3.60.0"
    assert profile["boundedOperationCount"] == 7
    assert operation_index()["boundedOperationsOnly"] is True


def test_hard_boundaries_are_false():
    assert DEFAULT_BOUNDARIES["arbitraryCodeExecution"] is False
    assert DEFAULT_BOUNDARIES["automaticClaimPromotionEnabled"] is False
    assert DEFAULT_BOUNDARIES["automaticEvidenceMutationEnabled"] is False
    assert DEFAULT_BOUNDARIES["automaticModelApprovalEnabled"] is False
    assert DEFAULT_BOUNDARIES["automaticExternalSideEffectsEnabled"] is False


def test_plan_next_step_result_dependency_progression():
    wf = execute("workspace.agent.plan", _request())["workflow"]
    assert wf["steps"][0]["status"] == "ready"
    assert wf["steps"][1]["status"] == "planned"

    nxt = execute("workspace.agent.next-step", {"workflow": wf})
    wf = nxt["workflow"]
    assert nxt["action"] == "execute"
    assert nxt["step"]["stepId"] == "s1"

    result = execute("workspace.agent.record-result", {
        "workflow": wf,
        "stepId": "s1",
        "artifactRefs": ["urn:artifact:1"],
        "provenanceRefs": ["urn:prov:1"],
        "output": {"items": 3},
    })
    wf = result["workflow"]
    assert result["receipt"]["outputDigest"]
    assert wf["steps"][0]["status"] == "succeeded"
    assert wf["steps"][1]["status"] == "ready"


def test_before_execution_human_review_gate():
    wf = execute("workspace.agent.plan", _request("before_execution"))["workflow"]
    nxt = execute("workspace.agent.next-step", {"workflow": wf})
    wf = nxt["workflow"]
    assert nxt["action"] == "review"
    assert wf["steps"][0]["status"] == "waiting_review"

    reviewed = execute("workspace.agent.review", {
        "workflow": wf,
        "stepId": "s1",
        "decision": "approve",
        "reviewerId": "researcher",
    })
    wf = reviewed["workflow"]
    assert wf["steps"][0]["status"] == "ready"


def test_snapshot_is_reproducible_object():
    wf = execute("workspace.agent.plan", _request())["workflow"]
    snap = execute("workspace.agent.snapshot", {"workflow": wf})["snapshot"]
    assert snap["schema"] == "sc-workspace-agentic-workflow-snapshot/1.0"
    assert len(snap["workflowDigest"]) == 64


def test_replan_budget_is_bounded():
    req = _request()
    req["boundaries"] = {"maxReplans": 1}
    wf = execute("workspace.agent.plan", req)["workflow"]
    wf = execute("workspace.agent.replan", {"workflow": wf, "steps": req["steps"]})["workflow"]
    try:
        execute("workspace.agent.replan", {"workflow": wf, "steps": req["steps"]})
    except ValueError as exc:
        assert "maxReplans" in str(exc)
    else:
        raise AssertionError("expected bounded replanning failure")
