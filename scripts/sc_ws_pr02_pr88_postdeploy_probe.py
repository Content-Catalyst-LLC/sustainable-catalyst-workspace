"""SC-WS-PR-02 / PR #88 post-deployment probe. Read-only by construction.

Run inside the deployed backend container:
    docker exec -i sc-workspace-backend python - < scripts/sc_ws_pr02_pr88_postdeploy_probe.py

For every private-research artifact it attempts a replacement and a deletion
through object_store inside one outer database transaction that is always rolled
back, with each inner commit confined to a savepoint. No blob is written while the guard
is present (it raises before any write), and delete_artifact never unlinks blobs. Identifiers are printed only as short hashes.
Then, only if that passes, the real routes are exercised in-process with the same
rollback-only session. Exit 0 = every attempt returned 409 with the guard message and every record and
blob is unchanged; exit 1 otherwise.
"""
import base64, hashlib, sys, warnings
warnings.filterwarnings("ignore")
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db import get_engine
from app.models import ArtifactHead, ArtifactRevision
from app import object_store
from app.schemas import ArtifactStoreRequest

tag = lambda value: hashlib.sha256(value.encode()).hexdigest()[:10]
engine = get_engine()

def snapshot():
    with Session(engine) as db:
        rows = db.scalars(select(ArtifactHead)).all()
        heads = {(r.user_key, r.artifact_id): (r.revision, r.sha256, r.bytes, r.storage_key, r.updated_at)
                 for r in rows if isinstance(r.metadata_json, dict) and r.metadata_json.get("source") == "private-research"}
        revisions = sorted((r.user_key, r.artifact_id, r.revision, r.sha256) for r in db.scalars(select(ArtifactRevision)).all()
                           if (r.user_key, r.artifact_id) in heads)
        return heads, revisions

def attempt(fn):
    try:
        fn(); return "NO-ERROR (unguarded)"
    except HTTPException as exc:
        return f"{exc.status_code} {exc.detail if isinstance(exc.detail, str) else exc.detail.get('message')}"

from pathlib import Path
from app.config import get_settings
def blob_files():
    root = Path(get_settings().object_storage_root)
    return sum(1 for f in root.rglob("*") if f.is_file()) if root.exists() else 0
blobs_before = blob_files()
before, before_revisions = snapshot()
ok = bool(before)
print(f"private-research artifacts: {len(before)}")
for (user_key, artifact_id), (revision, *_rest) in before.items():
    conn = engine.connect(); outer = conn.begin()
    try:
        db = Session(bind=conn, join_transaction_mode="create_savepoint")
        row = object_store.get_artifact(db, user_key, artifact_id)
        payload = ArtifactStoreRequest.model_validate({
            "schema": "sc-workspace-artifact-store/1.0", "artifactId": artifact_id, "projectId": row.project_id,
            "filename": row.filename, "mediaType": row.media_type,
            "contentBase64": base64.b64encode(b"sc-ws-pr02 probe").decode()})
        put = attempt(lambda: object_store.store_artifact(db, user_key, payload))
        delete = attempt(lambda: object_store.delete_artifact(db, user_key, artifact_id))
        db.close()
    finally:
        outer.rollback(); conn.close()
    good = put == "409 Private research files cannot be replaced." and delete == "409 Private research files cannot be deleted."
    ok &= good
    print(f"  {tag(user_key + '/' + artifact_id)} rev={revision}: replace -> {put}; delete -> {delete}; {'PASS' if good else 'FAIL'}")


# Route level: the real FastAPI routes (POST/DELETE /v1/artifacts, POST /v1/commands/execute),
# run in-process as each owner. Every route session is bound to an outer transaction that
# is rolled back, so nothing can persist even if a guard were missing. No secret is used.
import contextlib
from fastapi.testclient import TestClient
from app import main as workspace_main
from app.security import ServiceIdentity, require_service_identity

def route_checks(user_key, artifact_id, row_project, filename, media_type):
    conn = engine.connect(); outer = conn.begin()
    @contextlib.contextmanager
    def rollback_scope():
        db = Session(bind=conn, join_transaction_mode="create_savepoint", expire_on_commit=False)
        try:
            yield db
        finally:
            db.close()
    original = workspace_main.session_scope
    workspace_main.session_scope = rollback_scope
    workspace_main.app.dependency_overrides[require_service_identity] = lambda: ServiceIdentity(
        user_key=user_key, principal_id="probe:" + tag(user_key), principal_type="user",
        service_principal="sc-ws-pr02-probe", authentication_method="in-process-probe")
    try:
        client = TestClient(workspace_main.app, raise_server_exceptions=False)
        body = {"schema": "sc-workspace-artifact-store/1.0", "artifactId": artifact_id, "projectId": row_project,
                "filename": filename, "mediaType": media_type,
                "contentBase64": base64.b64encode(b"sc-ws-pr02 probe").decode()}
        command = lambda name, payload: client.post("/v1/commands/execute", json={
            "schema": "sc-workspace-command-request/1.0", "command": name, "payload": payload})
        results = {
            "POST /v1/artifacts": client.post("/v1/artifacts", json=body),
            "DELETE /v1/artifacts": client.delete(f"/v1/artifacts/{artifact_id}"),
            "command artifact.put": command("artifact.put", body),
            "command artifact.delete": command("artifact.delete", {"artifactId": artifact_id}),
        }
        # Read-only positives. Ordinary create/replace/delete are covered by the test suite;
        # a live create would leave a content-addressed blob on disk despite the rollback.
        results["list artifacts (expect 200)"] = client.get("/v1/artifacts")
        results["read research file metadata (expect 200)"] = client.get(f"/v1/artifacts/{artifact_id}")
    finally:
        workspace_main.app.dependency_overrides.pop(require_service_identity, None)
        workspace_main.session_scope = original
        outer.rollback(); conn.close()
    good = True
    for name, response in results.items():
        want = 200 if "(expect 200)" in name else 409
        detail = ""
        if response.status_code != 200:
            try:
                body = response.json()  # Workspace error shape: {"ok": false, "message": ...}
                detail = body.get("message") or body.get("detail") or ""
            except Exception:
                detail = response.text[:80]
        passed = response.status_code == want and (want == 200 or "Private research files cannot be" in str(detail))
        good &= passed
        print(f"    {name}: {response.status_code} {detail if isinstance(detail, str) else ''} {'ok' if passed else 'FAIL'}")
    return good

import os
if ok or os.environ.get("SC_PROBE_FORCE_ROUTES") == "1":  # force only for the fail-safety rehearsal
    print("route-level checks (rolled back):")
    with Session(engine) as db:
        targets = [(u, a, object_store.get_artifact(db, u, a)) for (u, a) in before]
    for user_key, artifact_id, row in targets:
        print(f"  {tag(user_key + '/' + artifact_id)}")
        ok &= route_checks(user_key, artifact_id, row.project_id, row.filename, row.media_type)
else:
    print("route-level checks skipped: the transactional probe did not pass")

after, after_revisions = snapshot()
unchanged = after == before and after_revisions == before_revisions
blobs_ok = True
with Session(engine) as db:
    for (user_key, artifact_id) in after:
        row = object_store.get_artifact(db, user_key, artifact_id)
        try:
            object_store.read_artifact_content(row)
        except Exception:
            blobs_ok = False
blobs_after = blob_files()
print(f"records unchanged: {unchanged}; blobs verified: {blobs_ok}; object-store files {blobs_before} -> {blobs_after}")
ok &= unchanged and blobs_ok and blobs_after == blobs_before
print("RESULT:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
