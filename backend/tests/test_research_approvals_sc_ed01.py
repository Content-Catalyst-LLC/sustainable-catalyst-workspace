"""SC-ED-01 authenticated, persisted, signed Research publication approvals.

Unit tests always run. PostgreSQL tests (real routes, real identity dependency) run when
SC_WORKSPACE_DATABASE_URL points at a disposable PostgreSQL database. Synthetic data only.
"""
import base64
import os
import secrets
from uuid import uuid4

import pytest

KEY_DIR = os.environ.setdefault("SC_TEST_KEY_DIR", "/tmp")
SEED_FILE = os.path.join(KEY_DIR, f"sc-ed01-approval-{os.getpid()}.key")
with open(SEED_FILE, "w") as fh:
    fh.write(base64.b64encode(secrets.token_bytes(32)).decode())
os.environ.setdefault("SC_WORKSPACE_RESEARCH_EXPORT_ENABLED", "true")
os.environ.setdefault("SC_WORKSPACE_RESEARCH_EXPORT_SIGNING_KEY_FILE", SEED_FILE)
os.environ.setdefault("SC_WORKSPACE_RESEARCH_EXPORT_CLIENT_TOKEN", "research-client-test")
os.environ.setdefault("SC_WORKSPACE_SERVICE_TOKEN", "workspace-service-test")

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey  # noqa: E402

from app import research_approvals as ra  # noqa: E402
from app import research_exports as rx  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.utils import canonical_bytes  # noqa: E402

get_settings.cache_clear()
rx._key.cache_clear()
PG = os.getenv("SC_WORKSPACE_DATABASE_URL", "").startswith("postgresql")
SUBJECT = "research-object:" + str(uuid4()) + "#" + "a" * 64


def verify(doc, domain=ra.RECORD_SCHEMA):
    body = {k: v for k, v in doc.items() if k != "signature"}
    pub = Ed25519PublicKey.from_public_bytes(base64.b64decode(rx.public_key_info()["publicKey"]))
    pub.verify(rx._b64d(doc["signature"]["value"]), domain.encode() + b"\n" + canonical_bytes(body))


def test_decider_rules_are_separate_per_dimension():
    assert ra.may_decide("o", "o", "rev", "scientific", True) == "research_scientific_approver"
    assert ra.may_decide("o", "ed", "o", "ownership", False) == "research_owner"
    with pytest.raises(PermissionError, match="self-approval"):
        ra.may_decide("o", "rev", "rev", "scientific", True)
    with pytest.raises(PermissionError, match="approver:scientific"):
        ra.may_decide("o", "ed", "o", "scientific", False)  # owners do not self-certify science
    with pytest.raises(PermissionError, match="self-approval"):
        ra.may_decide("o", "o", "o", "ownership", False)


@pytest.mark.parametrize("dimension,subject,ok", [
    ("scientific", SUBJECT, True), ("area-publication", "research-area:" + "1" * 8 + "#" + "b" * 64, True),
    ("area-publication", SUBJECT, False), ("rights", "research-area:x#" + "b" * 64, False),
    ("publication", "research-object:x#short", False), ("publication", "anything", False)])
def test_subject_refs_are_typed(dimension, subject, ok):
    if ok:
        ra.check_subject(dimension, subject)
    else:
        with pytest.raises(ValueError):
            ra.check_subject(dimension, subject)


def test_policy_reuses_the_governance_runtime_and_actions_match_research():
    policy = ra._policy()
    assert policy["schema"] == "sc-workspace-human-governance-policy/1.0" and policy["allowSelfApproval"] is False
    assert set(policy["requiredActions"]) == set(ra.ACTIONS.values())
    # Research's convergence contract names the same four object actions.
    assert {k: v for k, v in ra.ACTIONS.items() if k != "area-publication"} == {
        "scientific": "research_scientific_review", "rights": "research_rights_clearance",
        "ownership": "research_ownership_confirmation", "publication": "research_publication"}


# PostgreSQL integration

pg = pytest.mark.skipif(not PG, reason="needs a disposable PostgreSQL SC_WORKSPACE_DATABASE_URL")


@pytest.fixture(scope="module")
def client():
    from fastapi.testclient import TestClient
    from app.db import initialize_schema
    from app.main import app
    initialize_schema()
    with TestClient(app) as c:
        yield c


def hdr(user):
    return {"Authorization": "Bearer " + get_settings().service_token, "X-SC-User-ID": user}


@pytest.fixture
def world(client):
    tag = uuid4().hex[:8]
    users = {k: f"ed01-{k}-{tag}" for k in ("owner", "editor", "sci", "rights", "pub", "stranger")}
    project = f"ed01-proj-{tag}"
    r = client.post("/v1/projects", headers=hdr(users["owner"]), json={
        "schema": "sc-workspace-cloud-backup/1.0", "sourceProjectId": project, "projectTitle": "Synthetic",
        "project": {"schema": "sc-workspace-project/20.0", "id": project, "title": "Synthetic", "objects": []}})
    assert r.status_code == 200, r.text
    for role, who in (("editor", "editor"), ("approver:scientific", "sci"), ("approver:rights", "rights"),
                      ("approver:publication", "pub")):
        r = client.post("/v1/research-approvals/grants", headers=hdr(users["owner"]),
                        json={"granteeUserKey": users[who], "role": role, "projectId": project})
        assert r.status_code == 200, r.text
    return users, project


def ask(client, user, project, dimension, subject=SUBJECT, owner=""):
    return client.post("/v1/research-approvals/requests", headers=hdr(user), json={
        "ownerUserKey": owner, "projectId": project, "dimension": dimension, "subjectRef": subject, "subjectTitle": "T"})


def decide(client, user, approval_id, decision="approve"):
    return client.post(f"/v1/research-approvals/requests/{approval_id}/decide", headers=hdr(user),
                       json={"decision": decision, "note": "synthetic"})


@pg
def test_signed_record_carries_authenticated_actors(client, world):
    users, project = world
    r = ask(client, users["owner"], project, "scientific")
    assert r.status_code == 200, r.text
    aid = r.json()["item"]["approvalId"]
    inbox = client.get("/v1/research-approvals/requests", headers=hdr(users["sci"])).json()["items"]
    assert aid in {i["approvalId"] for i in inbox}
    assert aid not in {i["approvalId"] for i in client.get("/v1/research-approvals/requests", headers=hdr(users["rights"])).json()["items"]}
    r = decide(client, users["sci"], aid)
    assert r.status_code == 200, r.text
    rec = r.json()["record"]
    verify(rec)
    assert rec["approval"]["requester"]["actorId"] == f"workspace-user:{users['owner']}"
    assert rec["decision"]["actor"] == {"actorId": f"workspace-user:{users['sci']}", "actorType": "human",
                                        "role": "research_scientific_approver"}
    assert rec["approval"]["status"] == "approved" and rec["decision"]["decision"] == "approve"
    assert rec["approval"]["decisionRef"] == rec["decision"]["decisionId"]
    assert rec["authentication"]["decider"] == "service-bearer+wordpress-user-context"
    assert client.get(f"/v1/research-approvals/requests/{aid}/record", headers=hdr(users["owner"])).json() == rec
    # Decided requests are final, at the route and in the database.
    assert decide(client, users["sci"], aid, "reject").status_code == 409
    from app.db import session_scope
    from app.models import ResearchApprovalRequest
    with pytest.raises(Exception, match="final"):
        with session_scope() as db:
            db.get(ResearchApprovalRequest, aid).status = "pending"
            db.commit()


@pg
def test_refusals(client, world):
    users, project = world
    aid = ask(client, users["owner"], project, "rights").json()["item"]["approvalId"]
    assert decide(client, users["owner"], aid).status_code == 403          # self-approval
    assert decide(client, users["sci"], aid).status_code == 403            # wrong dimension
    assert decide(client, users["stranger"], aid).status_code == 403       # no grant
    assert ask(client, users["owner"], project, "rights").status_code == 409  # one pending per subject/dimension
    assert ask(client, users["stranger"], project, "rights", owner=users["owner"]).status_code == 404
    assert ask(client, users["owner"], "no-such-project", "rights").status_code == 404
    assert ask(client, users["owner"], project, "rights", subject="research-object:x#bad").status_code == 422
    assert client.get(f"/v1/research-approvals/requests/{aid}/record", headers=hdr(users["stranger"])).status_code == 404
    # Payload cannot name an actor: the schema forbids extra fields.
    r = client.post(f"/v1/research-approvals/requests/{aid}/decide", headers=hdr(users["rights"]),
                    json={"decision": "approve", "actor": {"actorId": "someone-else"}})
    assert r.status_code == 422
    assert client.post("/v1/research-approvals/grants", headers=hdr(users["owner"]),
                       json={"granteeUserKey": users["owner"], "role": "approver:rights", "projectId": project}).status_code == 422


@pg
def test_editor_requests_and_owner_confirms_ownership(client, world):
    users, project = world
    r = ask(client, users["editor"], project, "ownership", owner=users["owner"])
    assert r.status_code == 200, r.text
    aid = r.json()["item"]["approvalId"]
    assert decide(client, users["editor"], aid).status_code == 403
    rec = decide(client, users["owner"], aid).json()["record"]
    assert rec["decision"]["actor"]["role"] == "research_owner" and rec["grantId"] == "owner"
    assert rec["ownerScope"] == f"workspace-user:{users['owner']}"
    grants = client.get("/v1/research-approvals/grants", headers=hdr(users["editor"])).json()["items"]
    editor = next(g for g in grants if g["role"] == "editor")
    att = client.post(f"/v1/research-approvals/grants/{editor['grantId']}/attestation", headers=hdr(users["editor"]))
    assert att.status_code == 200
    verify(att.json(), ra.ATTESTATION_SCHEMA)
    assert att.json()["grantee"] == f"workspace-user:{users['editor']}" and att.json()["projectId"] == project
    # Only the grantee can obtain it, and only for an editor grant.
    assert client.post(f"/v1/research-approvals/grants/{editor['grantId']}/attestation", headers=hdr(users["owner"])).status_code == 404


@pg
def test_revoked_grant_cannot_decide_and_rejection_is_signed(client, world):
    users, project = world
    grants = client.get("/v1/research-approvals/grants", headers=hdr(users["owner"])).json()["items"]
    pub = next(g for g in grants if g["role"] == "approver:publication")
    aid = ask(client, users["owner"], project, "publication").json()["item"]["approvalId"]
    assert client.post(f"/v1/research-approvals/grants/{pub['grantId']}/revoke", headers=hdr(users["owner"])).status_code == 200
    assert decide(client, users["pub"], aid).status_code == 403
    aid2 = ask(client, users["owner"], project, "scientific", subject="research-object:x#" + "c" * 64).json()["item"]["approvalId"]
    rec = decide(client, users["sci"], aid2, "reject").json()["record"]
    verify(rec)
    assert rec["approval"]["status"] == "rejected"


@pg
def test_area_publication_is_owner_wide(client, world):
    users, project = world
    r = client.post("/v1/research-approvals/grants", headers=hdr(users["owner"]),
                    json={"granteeUserKey": users["pub"], "role": "approver:area-publication", "projectId": "*"})
    assert r.status_code == 200
    area = "research-area:" + str(uuid4()) + "#" + "d" * 64
    aid = ask(client, users["owner"], project, "area-publication", subject=area).json()["item"]["approvalId"]
    rec = decide(client, users["pub"], aid).json()["record"]
    assert rec["projectId"] == "*" and rec["action"] == "research_area_publication"
