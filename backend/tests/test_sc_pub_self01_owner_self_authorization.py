"""SC-PUB-SELF-01: owner self-authorization for single-operator deployments.

The owner may authorize their own request only through an explicit, enabled, step-up-gated decision whose signed
record says it is not an independent review. Every other separation-of-duties rule is unchanged. Unit tests always
run; the PostgreSQL test runs when SC_WORKSPACE_DATABASE_URL points at a disposable database. Synthetic data only.
"""
import time
from uuid import uuid4

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from test_research_approvals_sc_ed01 import PG, SUBJECT, ask, client, hdr, verify  # noqa: F401  (fixture reuse)

from app import human_governance_approval_intervention_runtime as hg
from app import research_approvals as ra
from app import sc_identity

ROLE = ra.OWNER_SELF_ROLE
DECLARATION = "Checked the data, methods, figures and rights myself."


def request():
    return Request({"type": "http", "method": "POST", "path": "/", "headers": []})


def owner_identity():
    return ra.ServiceIdentity("owner", "owner", "user", "sc-identity-session", "sc-identity-oidc-session")


# Pure rules ----------------------------------------------------------------------------------------------------------

def test_only_the_owner_can_self_authorize_and_other_rules_are_unchanged():
    assert ra.may_decide("o", "o", "o", "scientific", False, self_authorization=True) == ROLE
    assert ra.may_decide("o", "ed", "o", "publication", False, self_authorization=True) == ROLE
    with pytest.raises(PermissionError, match="only the project owner"):
        ra.may_decide("o", "o", "rev", "scientific", True, self_authorization=True)
    # Without the explicit request, nothing changes: no self-approval, owners do not certify science.
    with pytest.raises(PermissionError, match="self-approval"):
        ra.may_decide("o", "o", "o", "ownership", False)
    with pytest.raises(PermissionError, match="approver:scientific"):
        ra.may_decide("o", "ed", "o", "scientific", False)


def _pending(requester="workspace-user:o"):
    policy = ra._policy()
    approval = hg.request_approval({"policy": policy, "action": ra.ACTIONS["scientific"], "subjectRef": SUBJECT,
                                    "requester": {"actorId": requester, "actorType": "human"}})["approval"]
    return policy, approval


def test_governance_runtime_labels_self_authorization_and_refuses_anything_less():
    policy, approval = _pending()
    actor = {"actorId": "workspace-user:o", "actorType": "human", "role": ROLE}
    out = hg.decide({"policy": policy, "approval": approval, "decision": "approve", "actor": actor,
                     "ownerSelfAuthorization": True})
    assert out["approval"]["status"] == "approved"
    assert out["decision"]["reviewKind"] == "owner-self-authorization" and out["decision"]["independentReview"] is False
    with pytest.raises(ValueError, match="self-approval"):  # the role alone is not enough
        hg.decide({"policy": policy, "approval": approval, "decision": "approve", "actor": actor})
    with pytest.raises(ValueError, match="self-approval"):  # the flag with another role is not enough
        hg.decide({"policy": policy, "approval": approval, "decision": "approve", "ownerSelfAuthorization": True,
                   "actor": {**actor, "role": "research_scientific_approver"}})
    # A separate reviewer's decision carries no self-authorization label.
    other = hg.decide({"policy": policy, "approval": approval, "decision": "approve",
                       "actor": {"actorId": "workspace-user:rev", "actorType": "human", "role": "research_scientific_approver"}})
    assert "reviewKind" not in other["decision"]


def test_review_disclosure_never_calls_the_owner_independent():
    assert ra.review_disclosure(ROLE, "o", "o", "o") == {
        "kind": "owner-self-authorization", "independent": False, "statement": ra.SELF_AUTHORIZATION_DISCLOSURE}
    assert ra.review_disclosure("research_owner", "o", "ed", "o") == {"kind": "owner-confirmation", "independent": False}
    assert ra.review_disclosure("research_scientific_approver", "o", "o", "rev") == {"kind": "separate-reviewer", "independent": True}
    assert ra.review_disclosure("research_scientific_approver", "o", "ed", "ed")["independent"] is False


def test_profile_discloses_the_capability():
    p = ra.profile_route()["ownerSelfAuthorization"]
    assert p["independentReview"] is False and p["role"] == ROLE and "sc-identity-step-up" in p["requires"]


# Gates, all before any database access -------------------------------------------------------------------------------

@pytest.fixture
def gated(monkeypatch):
    state = {"enabled": True, "step_up": {"stepUp": True, "deciderAuthTime": int(time.time()), "deciderAmr": ["pwd", "otp"]}}
    monkeypatch.setattr(ra, "owner_self_authorization_enabled", lambda: state["enabled"])
    monkeypatch.setattr(sc_identity, "step_up_evidence", lambda _r: state["step_up"])
    monkeypatch.setattr(ra, "_signing_key", lambda: None)
    monkeypatch.setattr(ra, "session_scope", lambda: pytest.fail("no database access before the gates"))
    return state


@pytest.mark.parametrize("change,payload,status,code", [
    ({"enabled": False}, {}, 403, "owner-self-authorization-disabled"),
    ({"step_up": None}, {}, 403, "step-up-required"),
    ({}, {"decision": "reject"}, 422, None),
    ({}, {"expectedSubjectRef": None}, 422, "exact-revision-confirmation-required"),
    ({}, {"attestation": "  looks fine  "}, 422, "attestation-required"),
])
def test_self_authorization_gates(gated, change, payload, status, code):
    gated.update(change)
    body = {"decision": "approve", "expectedSubjectRef": SUBJECT, "ownerSelfAuthorization": True,
            "attestation": DECLARATION, **payload}
    with pytest.raises(HTTPException) as exc:
        ra.decide_route("approval_x", ra.DecisionIn(**body), request(), owner_identity())
    assert exc.value.status_code == status
    if code:
        assert exc.value.detail["code"] == code


# PostgreSQL integration ----------------------------------------------------------------------------------------------

pg = pytest.mark.skipif(not PG, reason="needs a disposable PostgreSQL SC_WORKSPACE_DATABASE_URL")


@pg
def test_owner_self_authorization_is_signed_and_labelled(client, monkeypatch):
    owner, project = f"self01-owner-{uuid4().hex[:8]}", f"self01-proj-{uuid4().hex[:8]}"
    r = client.post("/v1/projects", headers=hdr(owner), json={
        "schema": "sc-workspace-cloud-backup/1.0", "sourceProjectId": project, "projectTitle": "Synthetic",
        "project": {"schema": "sc-workspace-project/20.0", "id": project, "title": "Synthetic", "objects": []}})
    assert r.status_code == 200, r.text
    aid = ask(client, owner, project, "scientific").json()["item"]["approvalId"]
    body = {"decision": "approve", "expectedSubjectRef": SUBJECT, "ownerSelfAuthorization": True, "attestation": DECLARATION}
    url = f"/v1/research-approvals/requests/{aid}/decide"
    monkeypatch.setattr(ra, "owner_self_authorization_enabled", lambda: False)
    r = client.post(url, headers=hdr(owner), json=body)
    assert r.status_code == 403 and "owner-self-authorization-disabled" in r.text
    monkeypatch.setattr(ra, "owner_self_authorization_enabled", lambda: True)
    monkeypatch.setattr(sc_identity, "step_up_evidence",
                        lambda _r: {"stepUp": True, "deciderAuthTime": int(time.time()), "deciderAmr": ["pwd", "otp"]})
    # Not the owner: refused even with every gate satisfied.
    r = client.post(url, headers=hdr("self01-stranger"), json=body)
    assert r.status_code == 403 and "only the project owner" in r.text
    r = client.post(url, headers=hdr(owner), json=body)
    assert r.status_code == 200, r.text
    rec = r.json()["record"]
    verify(rec)
    assert rec["decision"]["actor"] == {"actorId": f"workspace-user:{owner}", "actorType": "human", "role": ROLE}
    assert rec["decision"]["reviewKind"] == "owner-self-authorization" and rec["decision"]["independentReview"] is False
    assert rec["review"] == {"kind": "owner-self-authorization", "independent": False,
                             "statement": ra.SELF_AUTHORIZATION_DISCLOSURE, "attestation": DECLARATION}
    assert rec["grantId"] == ROLE and rec["authentication"]["stepUp"] is True
    assert rec["authentication"]["revisionConfirmed"] is True
    item = r.json()["item"]
    assert item["status"] == "approved" and item["review"]["independent"] is False
