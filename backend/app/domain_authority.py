from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import DomainMutationReceipt
from .utils import iso, ordered_sha256_hex, sha256_hex, workspace_project_fingerprint


PROJECT_SCHEMAS = {f"sc-workspace-project/{n}.0" for n in range(12, 21)}
NOTEBOOK_SCHEMA = "sc-workspace-notebook/3.0"


@dataclass(frozen=True)
class DomainValidationError(ValueError):
    message: str
    code: str = "domain-validation-failed"
    path: str = ""

    def as_detail(self) -> dict[str, Any]:
        item: dict[str, Any] = {"message": self.message, "code": self.code}
        if self.path:
            item["path"] = self.path
        return item


def authority_profile() -> dict[str, Any]:
    return {
        "schema": "sc-workspace-domain-authority/1.0",
        "mode": "server-authoritative",
        "canonicalStore": "postgresql",
        "canonicalFingerprint": "SHA-256",
        "clientRole": "presentation-interaction-local-drafts",
        "browserAuthoritativeState": False,
        "backendAuthoritativeState": True,
        "authoritativeConcerns": [
            "schema-validation",
            "revision-preconditions",
            "canonical-fingerprints",
            "mutation-policy",
            "provenance",
            "revision-history",
            "persistence",
            "mutation-receipts",
        ],
        "clientConcerns": [
            "presentation",
            "interaction",
            "local-drafts",
            "selection-state",
            "viewport-state",
            "rendering",
        ],
        "supportedObjectKinds": ["project", "notebook"],
        "automaticBrowserAuthority": False,
        "arbitraryCodeExecution": False,
    }


def _validate_unique_ids(items: Any, *, collection: str) -> tuple[int, list[str]]:
    if items is None:
        return 0, []
    if not isinstance(items, list):
        raise DomainValidationError(f"{collection} must be an array when present.", path=collection)
    seen: set[str] = set()
    identifiers: list[str] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise DomainValidationError(f"{collection}[{index}] must be an object.", path=f"{collection}[{index}]")
        raw_id = item.get("id")
        if raw_id is None:
            continue
        object_id = str(raw_id).strip()
        if not object_id:
            raise DomainValidationError(f"{collection}[{index}].id must not be blank.", path=f"{collection}[{index}].id")
        if len(object_id) > 160:
            raise DomainValidationError(f"{collection}[{index}].id exceeds 160 characters.", path=f"{collection}[{index}].id")
        if object_id in seen:
            raise DomainValidationError(f"Duplicate identifier '{object_id}' in {collection}.", code="duplicate-domain-id", path=collection)
        seen.add(object_id)
        identifiers.append(object_id)
    return len(items), identifiers


def validate_project_document(project: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(project, dict):
        raise DomainValidationError("Workspace project must be a JSON object.", path="project")
    schema = str(project.get("schema") or "")
    if schema not in PROJECT_SCHEMAS:
        raise DomainValidationError(
            "A compatible Workspace project schema (12.0 through 20.0) is required.",
            code="unsupported-project-schema",
            path="project.schema",
        )
    object_count, identifiers = _validate_unique_ids(project.get("objects"), collection="project.objects")
    traceability = project.get("traceability")
    if traceability is not None and not isinstance(traceability, dict):
        raise DomainValidationError("project.traceability must be an object when present.", path="project.traceability")
    if isinstance(traceability, dict) and "lineage" in traceability and not isinstance(traceability.get("lineage"), list):
        raise DomainValidationError("project.traceability.lineage must be an array when present.", path="project.traceability.lineage")
    return {
        "schema": "sc-workspace-domain-validation-result/1.0",
        "objectKind": "project",
        "accepted": True,
        "authorityDecision": "accept",
        "documentSchema": schema,
        "canonicalFingerprint": workspace_project_fingerprint(project),
        "objectCount": object_count,
        "identifiedObjectCount": len(identifiers),
        "duplicateIdentifiers": False,
        "issues": [],
    }


def validate_notebook_document(notebook: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(notebook, dict):
        raise DomainValidationError("Workspace notebook must be a JSON object.", path="notebook")
    schema = str(notebook.get("schema") or "")
    if schema != NOTEBOOK_SCHEMA:
        raise DomainValidationError(
            f"A {NOTEBOOK_SCHEMA} notebook is required.",
            code="unsupported-notebook-schema",
            path="notebook.schema",
        )
    cell_count, identifiers = _validate_unique_ids(notebook.get("cells"), collection="notebook.cells")
    return {
        "schema": "sc-workspace-domain-validation-result/1.0",
        "objectKind": "notebook",
        "accepted": True,
        "authorityDecision": "accept",
        "documentSchema": schema,
        "canonicalFingerprint": ordered_sha256_hex(notebook),
        "cellCount": cell_count,
        "identifiedCellCount": len(identifiers),
        "duplicateIdentifiers": False,
        "issues": [],
    }


def validate_domain_document(object_kind: str, document: dict[str, Any]) -> dict[str, Any]:
    if object_kind == "project":
        return validate_project_document(document)
    if object_kind == "notebook":
        return validate_notebook_document(document)
    raise DomainValidationError(
        f"Unsupported authoritative object kind: {object_kind}",
        code="unsupported-domain-object-kind",
        path="objectKind",
    )


def build_mutation_receipt(
    *,
    user_key: str,
    object_kind: str,
    object_id: str,
    command: str,
    status: str,
    from_revision: int,
    to_revision: int,
    request_payload: Any,
    canonical_fingerprint: str,
    validation: dict[str, Any],
    policy: dict[str, Any],
    provenance: dict[str, Any],
) -> DomainMutationReceipt:
    return DomainMutationReceipt(
        user_key=user_key,
        receipt_id=f"dmr_{uuid4().hex}",
        object_kind=object_kind,
        object_id=object_id,
        command=command,
        status=status,
        from_revision=from_revision,
        to_revision=to_revision,
        request_fingerprint=sha256_hex(request_payload),
        canonical_fingerprint=canonical_fingerprint,
        validation_json=validation,
        policy_json=policy,
        provenance_json=provenance,
    )


def mutation_receipt_metadata(row: DomainMutationReceipt) -> dict[str, Any]:
    return {
        "receiptId": row.receipt_id,
        "objectKind": row.object_kind,
        "objectId": row.object_id,
        "command": row.command,
        "status": row.status,
        "fromRevision": row.from_revision,
        "toRevision": row.to_revision,
        "requestFingerprint": row.request_fingerprint,
        "canonicalFingerprint": row.canonical_fingerprint,
        "validation": row.validation_json,
        "policy": row.policy_json,
        "provenance": row.provenance_json,
        "createdAt": iso(row.created_at),
    }


def list_mutation_receipts(db: Session, user_key: str, limit: int = 100) -> list[dict[str, Any]]:
    rows = db.scalars(
        select(DomainMutationReceipt)
        .where(DomainMutationReceipt.user_key == user_key)
        .order_by(DomainMutationReceipt.created_at.desc())
        .limit(max(1, min(int(limit), 500)))
    ).all()
    return [mutation_receipt_metadata(row) for row in rows]


def get_mutation_receipt(db: Session, user_key: str, receipt_id: str) -> DomainMutationReceipt | None:
    return db.get(DomainMutationReceipt, {"user_key": user_key, "receipt_id": receipt_id})
