"""Selective structured-record restoration into existing Workspace projects.

Disabled by default. Source authorization is a protected administrative decision,
not a browser assertion; target authorization is the existing user-scoped registry.
"""
from __future__ import annotations

from copy import deepcopy
import base64
from datetime import datetime, timezone
import hashlib
import hmac
import json
import os

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select

from . import repository
from . import object_store
from .db import session_scope
from .models import ProjectHead, RecoveryRestorationReceipt
from .recovery_reconciliation import plan as inventory_plan, _canonical, _digest, _sha, _text
from .schemas import ProjectStoreRequest, ArtifactStoreRequest
from .session_auth import session_payload_from_request
from .wxr_recovery_review import HEADERS, _read_regular

router = APIRouter(prefix="/v1/private-research/recovery", tags=["Controlled Research Recovery"])
AUTH_SCHEMA = "sc.workspace.controlled-recovery-authorization.v1"
BUNDLE_SCHEMA = "sc.workspace.controlled-recovery-source.v1"


class Selection(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_project_id: str = Field(min_length=1, max_length=160)
    target_project_id: str = Field(min_length=1, max_length=160)
    plan_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    expected_revision: int = Field(ge=1)


class RollbackSelection(Selection):
    batch_id: str = Field(pattern=r"^recovery-[a-f0-9]{40}$")


def _deny():
    raise HTTPException(403, "Recovery selection is not authorized.", headers=HEADERS)


def _context(request: Request, source: str, target: str, *, verify_source=True):
    session = session_payload_from_request(request)
    if not session:
        raise HTTPException(401, "A valid Workspace browser session is required.", headers=HEADERS)
    subject = session["sub"]
    try:
        policy = json.loads(_read_regular(os.getenv("SC_WORKSPACE_RECOVERY_AUTHORIZATION_FILE", ""), 65536, protected=True))
        fields = {"schema", "subject_sha256", "source_project_id", "target_project_id", "catalog_sha256", "bundle_sha256", "record_ids", "issued_at", "expires_at", "ownership_evidence_sha256", "ownership_evidence_reference", "environment_bindings", "approved_plan_sha256", "allowed_actions", "backup_restore_evidence_sha256"}
        if not isinstance(policy, dict) or set(policy) != fields or policy["schema"] != AUTH_SCHEMA:
            raise ValueError("Authorization schema")
        if not hmac.compare_digest(_sha(policy["subject_sha256"]), hashlib.sha256(subject.encode()).hexdigest()):
            _deny()
        if policy["source_project_id"] != source or policy["target_project_id"] != target:
            _deny()
        for key in ("catalog_sha256", "bundle_sha256"):
            _sha(policy[key])
        for key in ("ownership_evidence_sha256", "backup_restore_evidence_sha256", "approved_plan_sha256"):
            if policy[key] is not None:
                _sha(policy[key])
        if policy["ownership_evidence_sha256"] and not (isinstance(policy["ownership_evidence_reference"], str) and policy["ownership_evidence_reference"].strip()):
            raise ValueError("Ownership evidence reference")
        if not isinstance(policy["environment_bindings"], dict):
            raise ValueError("Environment bindings")
        for key, value in policy["environment_bindings"].items():
            _text(key); _sha(value)
        ids, actions = policy["record_ids"], policy["allowed_actions"]
        if not isinstance(ids, list) or not 0 < len(ids) <= 1000 or len(ids) != len(set(ids)):
            raise ValueError("Selection")
        for value in ids:
            _text(value)
        if not isinstance(actions, list) or "plan" not in actions or set(actions) - {"plan", "create-area", "restore", "rollback"}:
            raise ValueError("Actions")
        issued = datetime.fromisoformat(policy["issued_at"].replace("Z", "+00:00"))
        expiry = datetime.fromisoformat(policy["expires_at"].replace("Z", "+00:00"))
        if not issued <= datetime.now(timezone.utc) < expiry or not 0 < (expiry - issued).total_seconds() <= 86400:
            raise ValueError("Expiry")
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        _deny()
    if not verify_source:
        return subject, policy, None, None
    try:
        raw = _read_regular(os.getenv("SC_WORKSPACE_RECOVERY_CATALOG_FILE", ""), 50 * 1024 * 1024)
        bundle_raw = _read_regular(os.getenv("SC_WORKSPACE_RECOVERY_BUNDLE_FILE", ""), 25 * 1024 * 1024)
        if not hmac.compare_digest(hashlib.sha256(raw).hexdigest(), policy["catalog_sha256"]) or not hmac.compare_digest(hashlib.sha256(bundle_raw).hexdigest(), policy["bundle_sha256"]):
            raise ValueError("Source digest")
        catalog, bundle = json.loads(raw), json.loads(bundle_raw)
        if bundle.get("schema") != BUNDLE_SCHEMA or bundle.get("catalog_sha256") != policy["catalog_sha256"] or not isinstance(bundle.get("records"), list):
            raise ValueError("Source bundle")
        catalog["catalog_sha256"] = policy["catalog_sha256"]
        # Select only authorized source project records; arbitrary client IDs never widen scope.
        catalog["projects"] = [p for p in catalog["projects"] if p.get("project_id") == source]
        catalog["calculations"] = [c for c in catalog["calculations"] if c.get("project_id") == source and c.get("record_id") in ids]
        catalog["artifacts"] = []  # No artifact mapping or byte restoration in this slice.
        inventory_plan(catalog)  # Validate before entering a destination session.
        return subject, policy, catalog, bundle
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        raise HTTPException(503, "Verified recovery source is unavailable.", headers=HEADERS) from None


def _target(db, subject: str, target: str, *, lock=False):
    # Same composite owner/project boundary as repository.get_project; row lock serializes
    # writers and prevents races with normal revision-checked Workspace sync operations.
    query = select(ProjectHead).where(ProjectHead.user_key == subject, ProjectHead.project_id == target)
    if lock:
        query = query.with_for_update()
    row = db.scalar(query)
    if row is None:
        _deny()
    return row


def _has_environment_reference(value):
    if isinstance(value, dict):
        return any((key.lower() in {"environmentkey", "environmentid", "activeenvironmentkey", "environmentref"} and item not in (None, "", [])) or _has_environment_reference(item) for key, item in value.items())
    if isinstance(value, list):
        return any(_has_environment_reference(item) for item in value)
    return False


def _build(policy: dict, catalog: dict, bundle: dict, target, subject: str) -> tuple[dict, dict]:
    base = inventory_plan(catalog)
    existing = {str(o.get("id")): o for o in target.package["project"].get("objects", [])}
    source_projects = base["projects"]
    source = source_projects[0] if len(source_projects) == 1 else None
    # The existing ERW bridge signs 'erw:' + the verified Workbench owner. A
    # protected review decision cannot override that source-owner boundary.
    source_owner = subject[4:] if subject.startswith("erw:") else subject
    owner_digest = hashlib.sha256(source_owner.encode()).hexdigest()
    groups = {}
    for record in bundle["records"]:
        if not isinstance(record, dict):
            raise ValueError("Source record")
        groups.setdefault(_text(record.get("record_id")), []).append(record)
    by_id = {r["original_calculation_id"]: r for r in base["calculations"]}
    proposed, records = [], {}
    for record_id in sorted(policy["record_ids"]):
        observed = by_id.get(record_id)
        candidates = groups.get(record_id, [])
        variants = {_digest(r) for r in candidates}
        blockers, classes = [], ["UNMATCHED"]
        if not source or "AMBIGUOUS" in source["classifications"] or not observed:
            blockers.append("source_project_or_calculation_unmatched_or_ambiguous")
        if source and (not hmac.compare_digest(source["original_owner_fingerprint"], owner_digest[:len(source["original_owner_fingerprint"])]) or len(source["original_owner_fingerprint"]) < 16):
            blockers.append("existing_source_owner_authorization_denied")
        if source and source["classification_hint"] == "development_or_certification_candidate":
            blockers.append("development_record_requires_separate_collection")
        if observed and "AMBIGUOUS" in observed["classifications"]:
            blockers.append("ambiguous_catalog_calculation"); classes.append("AMBIGUOUS")
        if len(candidates) > 1 or (observed and observed["source_occurrences"] > 1):
            classes.append("DUPLICATE")
        if len(variants) != 1:
            blockers.append("bundle_record_unmatched_or_ambiguous")
            if len(variants) > 1:
                classes.append("AMBIGUOUS")
        record = min(candidates, key=_canonical) if candidates else None
        if record:
            if not source or record.get("project_id") != policy["source_project_id"] or record.get("owner_fingerprint") != source["original_owner_fingerprint"] or (observed and observed["original_owner_fingerprint"] != record.get("owner_fingerprint")):
                blockers.append("source_owner_or_project_mismatch")
            if not isinstance(record.get("payload"), dict) or record.get("payload_sha256") != _digest(record.get("payload")):
                blockers.append("payload_integrity_failure")
            binding = policy["environment_bindings"].get(record_id)
            independent = record.get("environment_dependencies") == [] and not _has_environment_reference(record.get("payload"))
            if not independent and (not binding or record.get("environment_binding_sha256") != binding):
                blockers.append("research_environment_mapping_unresolved")
            if isinstance(record.get("payload"), dict) and record["payload"].get("schema") in {"sc.erw.pdf-source.v1.3.2", "sc.erw.word-source.v1.3.1"} and not record.get("blob_sha256"):
                blockers.append("source_document_blob_missing")
            if record.get("blob_sha256"):
                try:
                    blob_digest = _sha(record["blob_sha256"])
                    root = os.getenv("SC_WORKSPACE_RECOVERY_BLOB_ROOT", "")
                    if not root or not os.path.isabs(root):
                        raise ValueError("Blob root")
                    blob = _read_regular(os.path.join(root, blob_digest), 25 * 1024 * 1024)
                    if hashlib.sha256(blob).hexdigest() != blob_digest or len(blob) != record.get("blob_size_bytes"):
                        raise ValueError("Blob integrity")
                    document = record.get("payload") if isinstance(record.get("payload"), dict) else {}
                    source_hash = document.get("sha256") or document.get("originalSha256")
                    if source_hash != blob_digest:
                        raise ValueError("Source document hash")
                except (OSError, ValueError, TypeError):
                    blockers.append("source_blob_integrity_failure")
        if not policy["ownership_evidence_sha256"]:
            blockers.append("historical_ownership_unresolved")
        target_id = "recovered-" + _digest(["workbench", policy["source_project_id"], record_id, policy["target_project_id"]])[:40]
        if record and not blockers:
            obj = {"id": target_id, "type": "recovered-research-record", "publication": "disabled", "scientific_validity": "NOT_REASSESSED", "payload": deepcopy(record["payload"]), "recovery_provenance": {"source_system": "workbench", "original_project_id": policy["source_project_id"], "original_calculation_id": record_id, "original_owner_fingerprint": record["owner_fingerprint"], "payload_sha256": record["payload_sha256"], "catalog_sha256": policy["catalog_sha256"], "bundle_sha256": policy["bundle_sha256"], "ownership_evidence_sha256": policy["ownership_evidence_sha256"], "environment_binding_sha256": record.get("environment_binding_sha256") if not independent else None, "environment_dependency": "NO_REFERENCES_DECLARED_AND_DETECTED" if independent else "EVIDENCE_BOUND"}}
            if record.get("blob_sha256"):
                obj["source_blob"] = {"sha256": record["blob_sha256"], "bytes": record["blob_size_bytes"], "filename": _text(record.get("filename")), "media_type": _text(record.get("media_type")), "artifact_id": "recovered-file-" + _digest([target.project_id, record_id])[:40]}
            for field in ("original_created_at", "original_updated_at", "original_calculation_hash"):
                if field in record:
                    obj["recovery_provenance"][field] = deepcopy(record[field])
            records[target_id] = obj
            if target_id in existing:
                if existing[target_id] == obj:
                    classes[0] = "MATCHED"
                else:
                    classes.append("AMBIGUOUS"); blockers.append("destination_identity_conflict")
        if blockers:
            classes.append("BLOCKED")
        proposed.append({"original_project_id": policy["source_project_id"], "original_calculation_id": record_id, "target_object_id": target_id, "classifications": sorted(set(classes)), "blockers": sorted(set(blockers)), "proposed_action": "NONE" if blockers or "MATCHED" in classes else "RESTORE_STRUCTURED_RECORD"})
    result = {"schema": "sc.workspace.controlled-recovery-plan.v1", "mode": "DRY_RUN", "catalog_sha256": policy["catalog_sha256"], "bundle_sha256": policy["bundle_sha256"], "target_project_id": target.project_id, "target_revision": target.revision, "target_fingerprint": target.project_fingerprint, "source_projects": source_projects, "records": proposed, "unmapped_artifact_restoration": "RESTRICTED", "ownership_reassignment": "DISABLED", "publication": "DISABLED", "mutation_performed": False, "rollback_strategy": "new-revision-removes-only-unchanged-batch-objects"}
    result["plan_sha256"] = _digest(result)
    return result, records


def _write_guard(request: Request, policy: dict, action: str):
    if os.getenv("SC_WORKSPACE_CONTROLLED_RECOVERY_ENABLED", "").lower() != "true":
        raise HTTPException(403, "Controlled restoration is disabled.", headers=HEADERS)
    origin = os.getenv("SC_WORKSPACE_RECOVERY_ALLOWED_ORIGIN", "https://workspace.sustainablecatalyst.com")
    if request.headers.get("origin") != origin or request.headers.get("x-recovery-intent") != action:
        _deny()
    if action not in policy["allowed_actions"] or not policy["backup_restore_evidence_sha256"]:
        _deny()


def _verify_backups(policy, records):
    """Verify protected offline backup bytes; never invoke a live backup/restore."""
    try:
        raw = _read_regular(os.getenv("SC_WORKSPACE_RECOVERY_BACKUP_MANIFEST_FILE", ""), 65536, protected=True)
        if hashlib.sha256(raw).hexdigest() != policy["backup_restore_evidence_sha256"]:
            raise ValueError("Backup manifest digest")
        manifest = json.loads(raw)
        if manifest.get("schema") != "sc.workspace.recovery-backup-verification.v1":
            raise ValueError("Backup manifest schema")
        _sha(manifest["restore_rehearsal_evidence_sha256"])
        root = os.getenv("SC_WORKSPACE_RECOVERY_BACKUP_ROOT", "")
        if not os.path.isabs(root):
            raise ValueError("Backup root")
        verified = set()
        from .recovery_reconciliation import _relative_path
        for item in manifest["files"]:
            path = _relative_path(item["relative_path"])
            content = _read_regular(os.path.join(root, path), 512 * 1024 * 1024)
            expected = _sha(item["sha256"])
            if hashlib.sha256(content).hexdigest() != expected:
                raise ValueError("Backup file digest")
            verified.add(expected)
        if not {policy["catalog_sha256"], policy["bundle_sha256"], manifest["database_backup_sha256"]}.issubset(verified):
            raise ValueError("Backup coverage")
        for record in records.values():
            if record.get("source_blob") and record["source_blob"]["sha256"] not in verified:
                raise ValueError("Artifact backup coverage")
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        raise HTTPException(409, "Verified database/artifact backup evidence is required.", headers=HEADERS) from None


def _save(db, subject, target, project, operation):
    if target.storage_mode != "sync-head":
        raise HTTPException(409, "Target must use revision-checked Workspace sync.", headers=HEADERS)
    payload = ProjectStoreRequest.model_validate({"schema": "sc-workspace-sync-push/1.0", "sourceProjectId": target.project_id, "projectTitle": target.title, "expectedRevision": target.revision, "operationId": operation, "project": project})
    expected_revision = target.revision + 1
    row, _ = repository.store_project(db, subject, payload)
    if row.revision != expected_revision or row.package["project"] != project:
        raise HTTPException(409, "Workspace operation identity conflict.", headers=HEADERS)
    return row.revision


@router.get("/plan")
def read_plan(request: Request, source_project_id: str = Query(min_length=1, max_length=160), target_project_id: str = Query(min_length=1, max_length=160)):
    subject, policy, catalog, bundle = _context(request, source_project_id, target_project_id)
    with session_scope() as db:
        target = _target(db, subject, target_project_id)
        try:
            result, _ = _build(policy, catalog, bundle, target, subject)
        except (ValueError, TypeError, KeyError):
            raise HTTPException(503, "Verified recovery plan is unavailable.", headers=HEADERS) from None
    return JSONResponse(result, headers=HEADERS)


@router.post("/restore")
def restore(request: Request, payload: Selection):
    subject, policy, catalog, bundle = _context(request, payload.source_project_id, payload.target_project_id)
    _write_guard(request, policy, "restore")
    if payload.plan_sha256 != policy["approved_plan_sha256"]:
        _deny()
    batch_id = "recovery-" + payload.plan_sha256[:40]
    with session_scope() as db:
        target = _target(db, subject, payload.target_project_id, lock=True)
        project = deepcopy(target.package["project"])
        batches = project.setdefault("traceability", {}).setdefault("recoveryRestorations", {})
        trusted_receipt = db.get(RecoveryRestorationReceipt, {"user_key": subject, "batch_id": batch_id})
        if trusted_receipt is not None and trusted_receipt.project_id != target.project_id:
            _deny()
        previous = trusted_receipt.manifest_json if trusted_receipt is not None else None
        if previous:
            existing = {str(o.get("id")): o for o in project.get("objects", [])}
            if previous["state"] != "RESTORED" or any(_digest(existing.get(k)) != v for k, v in previous["created_object_hashes"].items()):
                raise HTTPException(409, "Prior restoration changed; review required.", headers=HEADERS)
            for artifact_id, expected in previous.get("created_artifacts", {}).items():
                row = object_store.get_artifact(db, subject, artifact_id)
                if row is None or row.project_id != target.project_id or row.sha256 != expected["sha256"] or row.revision != expected["revision"]:
                    raise HTTPException(409, "Prior artifact changed; review required.", headers=HEADERS)
                object_store.read_artifact_content(row)
            return JSONResponse({"state": "ALREADY_RESTORED", "batch_id": batch_id, "revision": target.revision}, headers=HEADERS)
        result, records = _build(policy, catalog, bundle, target, subject)
        if result["plan_sha256"] != payload.plan_sha256 or target.revision != payload.expected_revision:
            raise HTTPException(409, "Recovery plan or target revision changed.", headers=HEADERS)
        eligible = [r for r in result["records"] if not r["blockers"]]
        blocked = [r for r in result["records"] if r["blockers"]]
        if not eligible:
            raise HTTPException(409, "No authorized records are eligible for restoration.", headers=HEADERS)
        created = {r["target_object_id"]: records[r["target_object_id"]] for r in result["records"] if r["proposed_action"] == "RESTORE_STRUCTURED_RECORD"}
        _verify_backups(policy, created)
        created_artifacts = {}
        for obj in created.values():
            blob = obj.get("source_blob")
            if not blob:
                continue
            if object_store.get_artifact(db, subject, blob["artifact_id"]) is not None:
                raise HTTPException(409, "Destination artifact identity already exists.", headers=HEADERS)
            content = _read_regular(os.path.join(os.getenv("SC_WORKSPACE_RECOVERY_BLOB_ROOT", ""), blob["sha256"]), 25 * 1024 * 1024)
            if hashlib.sha256(content).hexdigest() != blob["sha256"] or len(content) != blob["bytes"]:
                raise HTTPException(409, "Source artifact changed.", headers=HEADERS)
            row = object_store.store_artifact(db, subject, ArtifactStoreRequest.model_validate({"schema": "sc-workspace-artifact-store/1.0", "artifactId": blob["artifact_id"], "projectId": target.project_id, "filename": blob["filename"], "mediaType": blob["media_type"], "contentBase64": base64.b64encode(content).decode(), "expectedRevision": 0, "metadata": {"recovery_batch_id": batch_id, "source_provenance": obj["recovery_provenance"]}}), commit=False)
            object_store.read_artifact_content(row)
            created_artifacts[row.artifact_id] = {"sha256": row.sha256, "revision": row.revision}
        project.setdefault("objects", []).extend(created[k] for k in sorted(created))
        batches[batch_id] = {"state": "RESTORED", "plan_sha256": payload.plan_sha256, "source_project_id": payload.source_project_id, "catalog_sha256": policy["catalog_sha256"], "bundle_sha256": policy["bundle_sha256"], "backup_restore_evidence_sha256": policy["backup_restore_evidence_sha256"], "restricted_record_count": len(blocked), "created_artifacts": created_artifacts, "created_object_hashes": {k: _digest(v) for k, v in created.items()}}
        db.add(RecoveryRestorationReceipt(user_key=subject, batch_id=batch_id, project_id=target.project_id, manifest_json=deepcopy(batches[batch_id])))
        revision = _save(db, subject, target, project, batch_id)
    return JSONResponse({"state": "RESTORED", "batch_id": batch_id, "created_objects": len(created), "restricted_records": len(blocked), "revision": revision}, headers=HEADERS)


@router.post("/rollback")
def rollback(request: Request, payload: RollbackSelection):
    subject, policy, _, _ = _context(request, payload.source_project_id, payload.target_project_id, verify_source=False)
    _write_guard(request, policy, "rollback")
    if payload.plan_sha256 != policy["approved_plan_sha256"]:
        _deny()
    with session_scope() as db:
        target = _target(db, subject, payload.target_project_id, lock=True)
        project = deepcopy(target.package["project"])
        trusted_receipt = db.get(RecoveryRestorationReceipt, {"user_key": subject, "batch_id": payload.batch_id})
        if trusted_receipt is None or trusted_receipt.project_id != target.project_id:
            _deny()
        batch = deepcopy(trusted_receipt.manifest_json)
        if not batch or batch["plan_sha256"] != payload.plan_sha256 or batch["source_project_id"] != payload.source_project_id or batch["catalog_sha256"] != policy["catalog_sha256"] or batch["bundle_sha256"] != policy["bundle_sha256"]:
            _deny()
        if batch["state"] == "ROLLED_BACK":
            return JSONResponse({"state": "ALREADY_ROLLED_BACK", "revision": target.revision}, headers=HEADERS)
        if target.revision != payload.expected_revision:
            raise HTTPException(409, "Target revision changed.", headers=HEADERS)
        existing = {str(o.get("id")): o for o in project.get("objects", [])}
        if any(_digest(existing.get(k)) != v for k, v in batch["created_object_hashes"].items()):
            raise HTTPException(409, "Recovered objects changed; automatic rollback refused.", headers=HEADERS)
        for artifact_id, expected in batch.get("created_artifacts", {}).items():
            row = object_store.get_artifact(db, subject, artifact_id)
            if row is None or row.project_id != target.project_id or row.sha256 != expected["sha256"] or row.revision != expected["revision"] or row.metadata_json.get("recovery_batch_id") != payload.batch_id:
                raise HTTPException(409, "Recovered artifact changed; automatic rollback refused.", headers=HEADERS)
            object_store.delete_artifact(db, subject, artifact_id, commit=False)
        project["objects"] = [o for o in project.get("objects", []) if str(o.get("id")) not in batch["created_object_hashes"]]
        batch["state"] = "ROLLED_BACK"
        trusted_receipt.manifest_json = deepcopy(batch)
        project.setdefault("traceability", {}).setdefault("recoveryRestorations", {})[payload.batch_id] = batch
        revision = _save(db, subject, target, project, "rollback-" + payload.batch_id)
    return JSONResponse({"state": "ROLLED_BACK", "revision": revision}, headers=HEADERS)


class AreaSelection(BaseModel):
    model_config = ConfigDict(extra='forbid')
    source_project_id: str = Field(min_length=1, max_length=160)
    target_project_id: str = Field(min_length=1, max_length=160)


@router.post('/area')
def create_area(request: Request, payload: AreaSelection):
    subject, policy, catalog, bundle = _context(request, payload.source_project_id, payload.target_project_id)
    _write_guard(request, policy, 'create-area')
    with session_scope() as db:
        existing = repository.get_project(db, subject, payload.target_project_id)
        if existing is not None:
            return JSONResponse({'state': 'ALREADY_EXISTS', 'project_id': existing.project_id}, headers=HEADERS)
        row, _ = repository.store_project(db, subject, ProjectStoreRequest.model_validate({'schema': 'sc-workspace-sync-push/1.0', 'sourceProjectId': payload.target_project_id, 'projectTitle': 'Private research recovery', 'expectedRevision': 0, 'operationId': 'create-research-area', 'project': {'schema': 'sc-workspace-project/20.0', 'title': 'Private research recovery', 'objects': [], 'publication': 'disabled', 'traceability': {'recoveryRestorations': {}, 'source_records_immutable': True}}}))
    return JSONResponse({'state': 'CREATED', 'project_id': row.project_id, 'restoration_performed': False}, headers=HEADERS)


@router.get('/area-status')
def area_status(request: Request):
    # Read identifiers only to resolve the configured selection; _context verifies
    # the actual signed subject before anything is returned to the browser.
    try:
        policy = json.loads(_read_regular(os.getenv('SC_WORKSPACE_RECOVERY_AUTHORIZATION_FILE', ''), 65536, protected=True))
        source, target_id = policy['source_project_id'], policy['target_project_id']
    except (OSError, ValueError, TypeError, KeyError):
        _deny()
    subject, policy, catalog, bundle = _context(request, source, target_id)
    with session_scope() as db:
        target = repository.get_project(db, subject, target_id)
        if target is None:
            return JSONResponse({'state': 'NOT_CREATED', 'source_project_id': source, 'target_project_id': target_id, 'writes_enabled': os.getenv('SC_WORKSPACE_CONTROLLED_RECOVERY_ENABLED', '').lower() == 'true'}, headers=HEADERS)
        result, _ = _build(policy, catalog, bundle, target, subject)
        project = target.package['project']
        records = [o for o in project.get('objects', []) if o.get('recovery_provenance')]
        return JSONResponse({'state': 'PRIVATE_RESEARCH_AREA', 'source_project_id': source, 'target_project_id': target_id, 'revision': target.revision, 'plan': result, 'records': records, 'restoration_manifests': project.get('traceability', {}).get('recoveryRestorations', {}), 'writes_enabled': os.getenv('SC_WORKSPACE_CONTROLLED_RECOVERY_ENABLED', '').lower() == 'true', 'publication': 'DISABLED'}, headers=HEADERS)


@router.get('/artifacts/{artifact_id}')
def download_recovered_artifact(request: Request, artifact_id: str):
    from fastapi.responses import Response
    from urllib.parse import quote
    try:
        policy = json.loads(_read_regular(os.getenv('SC_WORKSPACE_RECOVERY_AUTHORIZATION_FILE', ''), 65536, protected=True))
        source, target_id = policy['source_project_id'], policy['target_project_id']
    except (OSError, ValueError, TypeError, KeyError):
        _deny()
    subject, _, _, _ = _context(request, source, target_id, verify_source=False)
    with session_scope() as db:
        target = _target(db, subject, target_id)
        row = object_store.get_artifact(db, subject, artifact_id)
        if row is None or row.project_id != target_id or not any(o.get('source_blob', {}).get('artifact_id') == artifact_id for o in target.package['project'].get('objects', [])):
            _deny()
        content = object_store.read_artifact_content(row)
        return Response(content, media_type='application/octet-stream', headers={**HEADERS, 'Content-Disposition': "attachment; filename*=UTF-8''"+quote(row.filename, safe=''), 'Content-Security-Policy': "sandbox; default-src 'none'"})


@router.get('/ui')
def research_area_ui(request: Request):
    from fastapi.responses import HTMLResponse
    from .recovery_area_ui import HTML, SCRIPT
    if not session_payload_from_request(request):
        raise HTTPException(401, 'A valid Workspace browser session is required.', headers=HEADERS)
    script_hash = base64.b64encode(hashlib.sha256(SCRIPT.encode()).digest()).decode()
    return HTMLResponse(HTML, headers={**HEADERS, 'Content-Security-Policy': f"default-src 'none'; script-src 'sha256-{script_hash}'; style-src 'unsafe-inline'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'"})
