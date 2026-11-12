"""SC-RIGHTS-02 Workspace: transactional outbox, ordered delivery, retries, reconciliation and the operator view.

Research is played by ``FakeResearch``, which applies the same chain rules as Research
(``workspace_ingest.apply_source_rights_notice`` and ``source_rights_sync.apply_attestation``) and verifies
Workspace signatures with Workspace's own public key. The real services meet in the staging acceptance.
Needs a disposable PostgreSQL SC_WORKSPACE_DATABASE_URL (skip-locked claiming, advisory locks, triggers).
"""
import base64
import os
import secrets
import threading
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

KEY_DIR = os.environ.setdefault("SC_TEST_KEY_DIR", "/tmp")
SEED_FILE = os.path.join(KEY_DIR, f"sc-research-export-rights02-{os.getpid()}.key")
with open(SEED_FILE, "w") as fh:
    fh.write(base64.b64encode(secrets.token_bytes(32)).decode())
TOKEN_FILE = os.path.join(KEY_DIR, f"sc-rights02-delivery-{os.getpid()}")
OPS_FILE = os.path.join(KEY_DIR, f"sc-rights02-ops-{os.getpid()}")
for path, value in ((TOKEN_FILE, "delivery-test"), (OPS_FILE, "ops-test")):
    with open(path, "w") as fh:
        fh.write(value)
os.environ.update({
    "SC_WORKSPACE_RESEARCH_EXPORT_ENABLED": "true", "SC_WORKSPACE_RESEARCH_EXPORT_SIGNING_KEY_FILE": SEED_FILE,
    "SC_WORKSPACE_RESEARCH_EXPORT_CLIENT_TOKEN": "research-client-test",
    "SC_WORKSPACE_RESEARCH_RIGHTS_DELIVERY_URL": "http://research.invalid/api/research/v1",
    "SC_WORKSPACE_RESEARCH_RIGHTS_DELIVERY_TOKEN_FILE": TOKEN_FILE,
    "SC_WORKSPACE_RESEARCH_RIGHTS_OPS_TOKEN_FILE": OPS_FILE,
    "SC_WORKSPACE_RESEARCH_RIGHTS_MAX_ATTEMPTS": "4", "SC_WORKSPACE_RESEARCH_RIGHTS_BACKOFF_BASE_SECONDS": "2",
    "SC_WORKSPACE_RESEARCH_RIGHTS_BACKOFF_CAP_SECONDS": "60", "SC_WORKSPACE_RESEARCH_RIGHTS_ALERT_RESTRICTION_SECONDS": "0",
})
os.environ.setdefault("SC_WORKSPACE_SERVICE_TOKEN", "workspace-service-test")
os.environ.setdefault("SC_WORKSPACE_OBJECT_STORAGE_ROOT", os.path.join(KEY_DIR, f"sc-objects-{os.getpid()}"))

from cryptography.exceptions import InvalidSignature  # noqa: E402
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey  # noqa: E402
from sqlalchemy import select, text  # noqa: E402

from app import research_exports as rx  # noqa: E402
from app import rights_delivery as rd  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.utils import canonical_bytes, sha256_hex  # noqa: E402

get_settings.cache_clear()
rx._key.cache_clear()
PG = os.getenv("SC_WORKSPACE_DATABASE_URL", "").startswith("postgresql")
pytestmark = pytest.mark.skipif(not PG, reason="needs a disposable PostgreSQL SC_WORKSPACE_DATABASE_URL")
ROUTE = "/v1/research-exports/source-rights"


class FakeResearch:
    """Research's chain and attestation rules, in memory. Trusts the keys in ``self.keys`` (id -> (pub, notAfter))."""

    def __init__(self):
        self.applied = {}  # (owner, sha) -> [(seq, digest, status)]
        self.seen = {}  # digest -> response
        self.audit = []
        self.down = False
        self.drop_ack = 0
        self.refuse = {}  # noticeId -> (status, detail)
        self.calls = []
        self.attestations = []
        self.keys = {}
        self.trust_current()

    def trust_current(self, not_after=None):
        info = rx.public_key_info()
        self.keys[info["keyId"]] = (Ed25519PublicKey.from_public_bytes(base64.b64decode(info["publicKey"])), not_after)

    def _verify(self, domain, doc, when_field):
        sig = doc.get("signature") or {}
        entry = self.keys.get(sig.get("keyId"))
        body = {k: v for k, v in doc.items() if k != "signature"}
        if entry is None:
            return False
        pub, not_after = entry
        if not_after is not None and datetime.fromisoformat(body[when_field]) > not_after:
            return False
        try:
            pub.verify(rx._b64d(sig["value"]), domain.encode() + b"\n" + canonical_bytes(body))
            return True
        except InvalidSignature:
            return False

    def __call__(self, method, path, body=None):
        self.calls.append((method, path))
        if self.down:
            raise rd.TransportError("URLError: connection refused")
        if path.endswith("/source-rights-notices"):
            return self._notice(body["notice"])
        if path.endswith("/source-rights-state"):
            owners = {}
            for (owner, sha), chain in [(k, c) for k, c in self.applied.items() if c]:
                owners.setdefault(owner, []).append({"sourceSha256": sha, "appliedSequence": chain[-1][0],
                                                     "appliedNoticeSha256": chain[-1][1], "liveFigures": 1})
            return 200, {"owners": [{"ownerScope": o, "sources": s} for o, s in owners.items()]}
        if path.endswith("/source-rights-attestations"):
            att = body["attestation"]
            if not self._verify(rd.ATTESTATION_SCHEMA, att, "issuedAt"):
                return 403, {"detail": "Source rights attestation refused"}
            self.attestations.append(att)
            results = []
            for s in att["sources"]:
                chain = self.applied.get((att["ownerScope"], s["sourceSha256"]), [])
                have = chain[-1][0] if chain else 0
                st = ("unknown-to-workspace" if s["known"] is False else "research-behind" if s["sequence"] > have
                      else "attestation-older" if s["sequence"] < have
                      else "divergent" if have and s["noticeSha256"] != chain[-1][1] else "in-sync")
                results.append({"sourceSha256": s["sourceSha256"], "status": st, "researchSequence": have,
                                "attestedSequence": s["sequence"]})
            return 200, {"attestationId": att["attestationId"], "replayed": False, "results": results, "missing": []}
        return 404, {"detail": "Not Found"}

    def _notice(self, n):
        if n["noticeId"] in self.refuse:
            return self.refuse[n["noticeId"]]
        if not self._verify(rx.SOURCE_RIGHTS_SCHEMA, n, "effectiveAt"):
            return 403, {"detail": "Source rights notice refused: signature"}
        digest = sha256_hex(n)
        if digest in self.seen:
            return 200, {**self.seen[digest], "replayed": True}
        k = (n["ownerScope"], n["sourceSha256"])
        chain = self.applied.setdefault(k, [])
        last = chain[-1] if chain else None
        if last and n["sequence"] <= last[0]:
            return 409, {"detail": f"A newer source rights notice (sequence {last[0]}) was already applied for this source"}
        follows = (n["sequence"] == 1 and n["previousNoticeSha256"] is None) if last is None else \
            (n["sequence"] == last[0] + 1 and n["previousNoticeSha256"] == last[1])
        if not follows and n["licenceStatus"] != "restricted":
            return 409, {"detail": "Source rights notice does not follow the last applied notice for this source; deliver the earlier notices in order"}
        chain.append((n["sequence"], digest, n["licenceStatus"]))
        self.audit.append((n["noticeId"], n["sequence"], not follows))
        out = {"noticeId": n["noticeId"], "licenceStatus": n["licenceStatus"], "sequence": n["sequence"], "replayed": False,
               "chainGap": not follows, "revokedObjectIds": [], "figureBytesRemoved": [], "articles": [], "auditEvents": ["e"]}
        self.seen[digest] = out
        if self.drop_ack:
            self.drop_ack -= 1
            raise rd.TransportError("TimeoutError: read timed out after Research applied the notice")
        return 200, out


@pytest.fixture(scope="module")
def client():
    from fastapi.testclient import TestClient
    from app.db import initialize_schema
    from app.main import app
    initialize_schema()
    with TestClient(app) as c:
        yield c


@pytest.fixture
def research(monkeypatch, client):
    from app.db import session_scope
    with session_scope() as db:  # earlier tests' deliveries are settled; notices themselves are never touched
        db.execute(text("UPDATE workspace_research_rights_outbox SET state = 'applied', lease_owner = ''"))
        db.execute(text("DELETE FROM workspace_research_rights_sync_state"))
        db.commit()
    fake = FakeResearch()
    monkeypatch.setattr(rd, "http_call", fake)
    return fake


def hdr(user):
    return {"Authorization": "Bearer " + get_settings().service_token, "X-SC-User-ID": user}


def dataset(client, user, project):
    """A pinned dataset with unique bytes (so each is its own source and its own notice chain)."""
    import json
    from app.db import session_scope
    from app.object_store import store_artifact
    from app.schemas import ArtifactStoreRequest
    sfx = uuid4().hex[:8]
    raw = json.dumps({"rows": [{"t": 0, "y": 1.0}], "nonce": sfx}, sort_keys=True).encode()
    with session_scope() as db:
        store_artifact(db, user, ArtifactStoreRequest.model_validate({"schema": "sc-workspace-artifact-store/1.0",
            "artifactId": f"art-{sfx}", "projectId": project, "filename": "rows.json", "mediaType": "application/json",
            "contentBase64": base64.b64encode(raw).decode(), "expectedRevision": 0, "metadata": {}}))
    r = client.post("/v1/datasets", headers=hdr(user), json={"schema": "sc-workspace-dataset-record/1.0", "datasetId": f"ds-{sfx}",
                    "projectId": project, "name": "Synthetic", "datasetType": "table", "sourceKind": "artifact",
                    "artifactId": f"art-{sfx}", "metadata": {"scientificClassification": "synthetic"}})
    assert r.status_code == 200, r.text
    return f"ds-{sfx}", r.json()["item"]["artifactSha256"]


def owner_with_dataset(client, n=1):
    user, project = f"r02-{uuid4().hex[:8]}", f"p-{uuid4().hex[:6]}"
    return user, project, [dataset(client, user, project) for _ in range(n)]


def issue(client, user, project, ds, status):
    r = client.post(ROUTE, headers=hdr(user), json={"projectId": project, "datasetId": ds, "licenceStatus": status,
                                                    "reason": "SC-RIGHTS-02 synthetic drill"})
    assert r.status_code == 200, r.text
    return r.json()


def rows(user=None):
    from app.db import session_scope
    from app.models import ResearchRightsOutbox as O
    with session_scope() as db:
        q = select(O).order_by(O.sequence)
        if user:
            q = q.where(O.user_key == user)
        return [{c: getattr(r, c) for c in ("notice_id", "state", "attempts", "sequence", "licence_status", "last_error_code",
                                            "next_attempt_at", "research_receipt", "priority")} for r in db.scalars(q)]


def make_due():
    from app.db import session_scope
    with session_scope() as db:
        db.execute(text("UPDATE workspace_research_rights_outbox SET next_attempt_at = now() - interval '1 second' "
                        "WHERE state IN ('queued', 'retrying')"))
        db.commit()


def drain(worker="w1", rounds=20):
    for _ in range(rounds):
        make_due()
        if not rd.deliver_due(worker):
            return


# --- Outbox ------------------------------------------------------------------------------------------

def test_notice_and_outbox_row_commit_together(client, research, monkeypatch):
    user, project, [(ds, sha)] = owner_with_dataset(client)
    n = issue(client, user, project, ds, "restricted")
    [r] = rows(user)
    assert (r["notice_id"], r["state"], r["priority"], r["sequence"]) == (n["noticeId"], "queued", 0, 1)

    def broken(*a, **k):
        raise RuntimeError("outbox unavailable")
    monkeypatch.setattr(rd, "enqueue", broken)
    with pytest.raises(RuntimeError):
        client.post(ROUTE, headers=hdr(user), json={"projectId": project, "datasetId": ds, "licenceStatus": "verified-for-use"})
    listed = client.get(ROUTE, headers=hdr(user), params={"projectId": project}).json()["items"]
    assert [x["noticeId"] for x in listed] == [n["noticeId"]]  # no notice without its delivery row


def test_concurrent_issue_never_forks_the_chain(client, research):
    user, project, [(ds, sha)] = owner_with_dataset(client)
    out = []

    def go(status):
        out.append(client.post(ROUTE, headers=hdr(user), json={"projectId": project, "datasetId": ds, "licenceStatus": status}))
    threads = [threading.Thread(target=go, args=(s,)) for s in ("restricted", "verified-for-use") * 3]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert all(r.status_code == 200 for r in out)
    listed = sorted(client.get(ROUTE, headers=hdr(user), params={"projectId": project}).json()["items"], key=lambda x: x["sequence"])
    assert [x["sequence"] for x in listed] == list(range(1, len(listed) + 1))
    assert all(b["previousNoticeSha256"] == sha256_hex(a) for a, b in zip(listed, listed[1:]))
    assert [r["sequence"] for r in rows(user)] == [x["sequence"] for x in listed]


# --- Delivery ----------------------------------------------------------------------------------------

def test_in_order_delivery_and_receipts(client, research):
    user, project, [(ds, sha)] = owner_with_dataset(client)
    ids = [issue(client, user, project, ds, s)["noticeId"] for s in ("restricted", "verified-for-use", "restricted")]
    # One head per source per pass: never 2 before 1.
    assert rd.deliver_due("w1") == ["applied"]
    assert [a[1] for a in research.audit] == [1]
    drain()
    assert [a[1] for a in research.audit] == [1, 2, 3] and not any(a[2] for a in research.audit)
    assert [r["state"] for r in rows(user)] == ["applied"] * 3
    assert rows(user)[0]["research_receipt"]["noticeId"] == ids[0]


def test_restrictions_go_first_across_sources(client, research):
    user, project, [(a, _), (b, _)] = owner_with_dataset(client, 2)
    issue(client, user, project, a, "verified-for-use")
    issue(client, user, project, b, "restricted")
    from app.db import session_scope
    with session_scope() as db:
        batch = rd.claim(db, "w1", limit=1)
    assert len(batch) == 1 and batch[0]["notice"]["licenceStatus"] == "restricted"


def test_research_down_retries_with_bounded_backoff_then_catches_up(client, research):
    user, project, [(ds, _)] = owner_with_dataset(client)
    issue(client, user, project, ds, "restricted")
    research.down = True
    before = datetime.now(timezone.utc)
    assert rd.deliver_due("w1") == ["retrying"]
    r = rows(user)[0]
    assert r["attempts"] == 1 and r["last_error_code"] == "transport"
    assert before + timedelta(seconds=0.9) <= r["next_attempt_at"] <= before + timedelta(seconds=3)
    assert rd.deliver_due("w1") == []  # not due yet
    research.down = False
    drain()
    assert rows(user)[0]["state"] == "applied" and len(research.audit) == 1


def test_bounded_attempts_block_and_raise_a_critical_alert(client, research):
    user, project, [(ds, _)] = owner_with_dataset(client)
    issue(client, user, project, ds, "restricted")
    research.down = True
    drain()
    r = rows(user)[0]
    assert r["state"] == "blocked" and r["attempts"] == 4 and r["last_error_code"] == "max-attempts:transport"
    from app.db import session_scope
    with session_scope() as db:
        alerts = rd.status(db)["alerts"]
    assert any(a["code"] == "delivery-blocked" and a["severity"] == "critical" for a in alerts), alerts
    assert any(a["code"] == "restriction-unapplied" for a in alerts)


@pytest.mark.parametrize("attempts", range(1, 12))
def test_backoff_is_capped_and_jittered(attempts):
    for _ in range(50):
        d = rd.backoff_seconds(attempts)
        ceiling = min(60, 2 * 2 ** (attempts - 1))
        assert ceiling / 2 <= d <= ceiling


def test_lost_acknowledgement_is_replayed_not_reapplied(client, research):
    user, project, [(ds, _)] = owner_with_dataset(client)
    issue(client, user, project, ds, "restricted")
    research.drop_ack = 1
    assert rd.deliver_due("w1") == ["retrying"]
    drain()
    r = rows(user)[0]
    assert r["state"] == "applied" and r["research_receipt"]["replayed"] is True
    assert len(research.audit) == 1  # one application, one audit event


def test_two_workers_never_claim_the_same_notice(client, research):
    user, project, [(a, _), (b, _)] = owner_with_dataset(client, 2)
    issue(client, user, project, a, "restricted")
    issue(client, user, project, b, "restricted")
    from app.db import session_scope
    with session_scope() as db1, session_scope() as db2:
        one = rd.claim(db1, "w1")
        two = rd.claim(db2, "w2")
    assert len(one) == 2 and two == []


def test_crashed_worker_lease_expires_and_its_late_answer_is_ignored(client, research):
    user, project, [(ds, _)] = owner_with_dataset(client)
    n = issue(client, user, project, ds, "restricted")
    from app.db import session_scope
    with session_scope() as db:
        assert len(rd.claim(db, "crashed")) == 1
    assert rd.deliver_due("w2") == []  # leased by the crashed worker
    with session_scope() as db:
        db.execute(text("UPDATE workspace_research_rights_outbox SET lease_expires_at = now() - interval '1 second'"))
        db.commit()
    assert rd.deliver_due("w2") == ["applied"]
    with session_scope() as db:
        assert rd.record(db, n["noticeId"], "crashed", None, None, "late") is None
    r = rows(user)[0]
    assert r["state"] == "applied" and r["attempts"] == 2


def test_refusals_block_and_a_restriction_passes_a_blocked_notice(client, research):
    user, project, [(ds, _)] = owner_with_dataset(client)
    first = issue(client, user, project, ds, "verified-for-use")
    research.refuse[first["noticeId"]] = (422, {"detail": "Source rights notice is malformed"})
    assert rd.deliver_due("w1") == ["blocked"]
    issue(client, user, project, ds, "restricted")
    drain()
    states = [r["state"] for r in rows(user)]
    assert states == ["blocked", "applied"] and research.audit[-1][2] is True  # Research recorded the gap
    # The operator re-queues the blocked notice once its cause is fixed; it is older than the applied one.
    del research.refuse[first["noticeId"]]
    ops = {"Authorization": "Bearer ops-test"}
    assert client.post("/v1/research-exports/rights-delivery/requeue", headers=ops, json={"noticeId": first["noticeId"]}).status_code == 422
    assert client.post("/v1/research-exports/rights-delivery/requeue", headers=ops,
                       json={"noticeId": first["noticeId"], "reason": "fixed"}).status_code == 200
    drain()
    assert [r["state"] for r in rows(user)] == ["superseded", "applied"]


@pytest.mark.parametrize("status,state", [(401, "blocked"), (403, "blocked"), (404, "blocked"), (503, "retrying"),
                                          (500, "retrying"), (429, "retrying")])
def test_answers_are_classified(status, state):
    assert rd.classify(status, {"detail": "x"})[0] == state


def test_wrong_owner_or_forged_notices_are_never_sent_for_another_owner(client, research):
    user, project, [(ds, _)] = owner_with_dataset(client)
    other = f"r02-{uuid4().hex[:8]}"
    assert client.post(ROUTE, headers=hdr(other), json={"projectId": project, "datasetId": ds,
                                                         "licenceStatus": "restricted"}).status_code == 404
    assert rows(other) == []
    issue(client, user, project, ds, "restricted")
    research.keys.clear()  # Research no longer trusts the key: a 403 blocks rather than retrying forever
    assert rd.deliver_due("w1") == ["blocked"]
    assert rows(user)[0]["last_error_code"] == "refused-signature-or-owner"


# --- Reconciliation and attestation -------------------------------------------------------------------

def test_research_data_loss_is_detected_and_repaired_in_order(client, research):
    user, project, [(ds, sha)] = owner_with_dataset(client)
    issue(client, user, project, ds, "verified-for-use")
    issue(client, user, project, ds, "restricted")
    drain()
    research.applied.clear()  # Research restored from a backup taken before both notices
    research.seen.clear()
    issue(client, user, project, ds, "verified-for-use")
    assert rd.deliver_due("w1") == ["retrying"]  # 3 does not follow
    out = rd.reconcile()
    mine = {r["notice_id"] for r in rows(user)}
    assert len(mine & set(out["requeued"])) == 2  # notices 1 and 2; Research still has nothing for them
    drain()
    chain = research.applied[(f"workspace-user:{user}", sha)]
    assert [c[0] for c in chain] == [1, 2, 3] and [r["state"] for r in rows(user)] == ["applied"] * 3


def test_attestation_is_signed_per_owner_and_recorded(client, research):
    user, project, [(ds, sha)] = owner_with_dataset(client)
    issue(client, user, project, ds, "restricted")
    out = rd.reconcile()
    assert out["results"][sha] == "research-behind"  # issued but not yet delivered: Research must hold
    drain()
    out = rd.reconcile()
    assert out["results"][sha] == "in-sync"
    att = next(a for a in reversed(research.attestations) if a["ownerScope"] == f"workspace-user:{user}")
    assert att["ownerScope"] == f"workspace-user:{user}" and att["sources"][0]["sequence"] == 1 and att["sources"][0]["known"]
    from app.db import session_scope
    with session_scope() as db:
        st = rd.status(db)
    assert any(x["source"] == sha and x["status"] == "in-sync" for x in st["sync"])
    mine = {r["notice_id"] for r in rows(user)}
    assert not [a for a in st["alerts"] if a["code"] == "attestation-stale" or a.get("subject") in mine]


def test_reconciliation_queues_notices_that_have_no_delivery_row(client, research):
    user, project, [(ds, _)] = owner_with_dataset(client)
    n = issue(client, user, project, ds, "restricted")
    from app.db import session_scope
    with session_scope() as db:
        db.execute(text("DELETE FROM workspace_research_rights_outbox WHERE notice_id = :i"), {"i": n["noticeId"]})
        db.commit()
    assert n["noticeId"] in rd.reconcile()["requeued"]
    drain()
    assert rows(user)[0]["state"] == "applied"


def test_research_unreachable_during_reconciliation_is_recorded(client, research):
    research.down = True
    assert rd.reconcile()["ok"] is False


# --- Key rotation --------------------------------------------------------------------------------------

def test_signing_key_rotation_keeps_queued_notices_deliverable(client, research, monkeypatch, tmp_path):
    user, project, [(ds, _)] = owner_with_dataset(client)
    research.down = True
    old = issue(client, user, project, ds, "restricted")
    rd.deliver_due("w1")
    old_kid = rx.public_key_info()["keyId"]
    new_seed = tmp_path / "rotated.key"
    new_seed.write_text(base64.b64encode(secrets.token_bytes(32)).decode())
    monkeypatch.setenv("SC_WORKSPACE_RESEARCH_EXPORT_SIGNING_KEY_FILE", str(new_seed))
    get_settings.cache_clear()
    try:
        assert rx.public_key_info()["keyId"] != old_kid
        new = issue(client, user, project, ds, "verified-for-use")
        assert new["signature"]["keyId"] != old["signature"]["keyId"]
        # Research retires the old key at the rotation instant and trusts the new one.
        research.keys[old_kid] = (research.keys[old_kid][0], datetime.now(timezone.utc))
        research.trust_current()
        research.down = False
        drain()
        assert [r["state"] for r in rows(user)] == ["applied", "applied"]
        assert rd.reconcile()["attested"]  # signed with the new, current key
    finally:
        get_settings.cache_clear()


# --- Operator view --------------------------------------------------------------------------------------

def test_operator_view_is_private_and_escaped(client, research, monkeypatch):
    user, project, [(ds, _)] = owner_with_dataset(client)
    issue(client, user, project, ds, "restricted")
    url = "/v1/research-exports/rights-delivery"
    assert client.get(f"{url}/status").status_code == 401
    assert client.get(f"{url}/status", headers=hdr(user)).status_code == 401  # a Workspace user is not an operator
    st = client.get(f"{url}/status", headers={"Authorization": "Bearer ops-test"})
    assert st.status_code == 200 and "no-store" in st.headers["cache-control"] and st.json()["counts"]["queued"] == 1
    page = client.get(f"{url}/dashboard", headers={"Authorization": "Bearer ops-test"})
    assert page.status_code == 200 and "default-src 'none'" in page.headers["content-security-policy"]
    assert "Source-rights delivery to Research" in page.text and user in page.text
    html = rd.render_dashboard({**st.json(), "items": [{**st.json()["items"][0], "owner": "<script>x</script>"}]})
    assert "<script>x" not in html and "&lt;script&gt;" in html
    monkeypatch.setenv("SC_WORKSPACE_RESEARCH_RIGHTS_OPS_TOKEN_FILE", "")
    get_settings.cache_clear()
    try:
        assert client.get(f"{url}/status", headers={"Authorization": "Bearer ops-test"}).status_code == 503
    finally:
        monkeypatch.undo()
        get_settings.cache_clear()


def test_delivery_events_are_append_only(client, research):
    from app.db import session_scope
    user, project, [(ds, _)] = owner_with_dataset(client)
    issue(client, user, project, ds, "restricted")
    for stmt in ("UPDATE workspace_research_rights_delivery_events SET outcome = 'x'",
                 "DELETE FROM workspace_research_rights_delivery_events"):
        with session_scope() as db, pytest.raises(Exception, match="append-only"):
            db.execute(text(stmt))
            db.commit()


def test_worker_tick_never_raises(monkeypatch, research):
    def boom(*a, **k):
        raise RuntimeError("database gone")
    monkeypatch.setattr(rd, "deliver_due", boom)
    rd.tick("w1")  # logged, not raised
