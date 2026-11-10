"""SC-MODEL-01 — Workspace-authoritative execution exports for Research.

Workspace stays the authority for projects, ownership and execution records. Research
never reads Workspace's database and never asserts an owner. Instead:

1. An authenticated Workspace user asks Workspace for a grant on ONE of their execution
   runs. Workspace checks ownership and project scope, records the grant, and returns
   an Ed25519-signed, short-lived token bound to audience ``sc-research``.
2. Research presents that grant together with its own least-privilege client credential
   (accepted on the fetch route only, never as a general service token).
3. Workspace re-verifies the grant, its revocation state, any owner withdrawal and the
   run's ownership at the source, then returns a signed export built from the existing
   scientific execution provenance (``run_provenance``), runtime receipts and verified
   scientific study packages. Artifact bytes are not exported; only hashes and the
   bounded numeric values the model revision declares in ``researchResultValues``.

Research holds only the public key, so it can verify but never mint grants or exports.
A withdrawal returns a signed notice Research uses to revoke its derived records.
"""
from __future__ import annotations

import base64
import hashlib
import json
import re
import secrets
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any
from uuid import uuid4

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select

from .config import get_settings
from .db import session_scope
from .execution_provenance import run_provenance
from .cell_bindings import KIND as UPSTREAM_KIND
from .input_integrity import VERIFIED as INPUT_VERIFIED
from .notebook_orchestration import verified_cell_run
from .models import (
    ExecutionRun, ExecutionRunOutput, PolyglotExecutionReceipt, ResearchExportGrant,
    ResearchExportWithdrawal, ScientificStudyPackage,
)
from .object_store import get_artifact, read_artifact_content
from .registry import get_execution_run
from .security import ServiceIdentity, require_service_identity
from .study_packages import verify_package
from .utils import canonical_bytes, sha256_hex

GRANT_SCHEMA = "sc-workspace-research-export-grant/1.0"
EXPORT_SCHEMA = "sc-workspace-research-export/1.0"
WITHDRAWAL_SCHEMA = "sc-workspace-research-export-withdrawal/1.0"
AUDIENCE = "sc-research"
ISSUER = "sustainable-catalyst-workspace"
MAX_VALUES = 256
router = APIRouter(prefix="/v1/research-exports", tags=["SC-MODEL-01 Research export"])


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _b64e(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64d(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


@lru_cache
def _key(path: str) -> Ed25519PrivateKey:
    seed = base64.b64decode(Path(path).read_text().strip())
    if len(seed) != 32:
        raise RuntimeError("research export signing key must be a base64 32-byte Ed25519 seed")
    return Ed25519PrivateKey.from_private_bytes(seed)


def _signing_key() -> Ed25519PrivateKey:
    settings = get_settings()
    if not settings.research_export_enabled or not settings.research_export_signing_key_file:
        raise HTTPException(status_code=503, detail="Workspace Research export is not enabled.")
    return _key(settings.research_export_signing_key_file)


def public_key_info() -> dict[str, str]:
    raw = _signing_key().public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    return {"algorithm": "Ed25519", "publicKey": base64.b64encode(raw).decode("ascii"),
            "keyId": hashlib.sha256(raw).hexdigest()[:16]}


def _sign(domain: str, payload: bytes) -> str:
    return _b64e(_signing_key().sign(domain.encode("ascii") + b"\n" + payload))


def sign_document(domain: str, body: dict[str, Any]) -> dict[str, Any]:
    """Attach a detached Ed25519 signature over the canonical document (domain-separated)."""
    return {**body, "signature": {"alg": "Ed25519", "keyId": public_key_info()["keyId"],
                                  "value": _sign(domain, canonical_bytes(body))}}


def issue_grant_token(claims: dict[str, Any]) -> str:
    encoded = _b64e(canonical_bytes(claims))
    return encoded + "." + _sign(GRANT_SCHEMA, encoded.encode("ascii"))


def decode_grant_token(token: str) -> dict[str, Any]:
    """Verify signature and expiry of a grant this Workspace issued."""
    parts = str(token or "").split(".")
    if len(parts) != 2 or len(token) > 4096:
        raise ValueError("malformed-grant")
    encoded, sig = parts
    try:
        _signing_key().public_key().verify(_b64d(sig), GRANT_SCHEMA.encode("ascii") + b"\n" + encoded.encode("ascii"))
        claims = json.loads(_b64d(encoded))
    except HTTPException:
        raise
    except Exception as exc:
        raise ValueError("invalid-grant-signature") from exc
    if claims.get("schema") != GRANT_SCHEMA or claims.get("iss") != ISSUER or claims.get("aud") != AUDIENCE:
        raise ValueError("invalid-grant-scope")
    if int(claims.get("exp") or 0) <= int(_now().timestamp()):
        raise ValueError("expired-grant")
    return claims


# ---------------------------------------------------------------------------
# Export assembly


def _walk(node: Any, predicate) -> Any:
    if predicate(node):
        return node
    if isinstance(node, dict):
        children = node.values()
    elif isinstance(node, list):
        children = node
    else:
        return None
    for child in children:
        found = _walk(child, predicate)
        if found is not None:
            return found
    return None


def _finite(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    value = float(value)
    return value if value == value and abs(value) != float("inf") else None


_PATH_SEGMENT = re.compile(r"[A-Za-z0-9_-]{1,64}")
MAX_PATH_SEGMENTS = 16


def _runtime_root(result_doc: Any) -> Any:
    """The runtime's own result inside the polyglot envelope (``result.remote.result``)."""
    node = result_doc
    for key in ("result", "remote", "result"):
        if not isinstance(node, dict) or key not in node:
            return result_doc
        node = node[key]
    return node


def _resolve_path(root: Any, path: Any) -> float | None:
    if not isinstance(path, str):
        return None
    segments = path.split(".")
    if not 0 < len(segments) <= MAX_PATH_SEGMENTS or not all(_PATH_SEGMENT.fullmatch(s) for s in segments):
        return None
    node = root
    for seg in segments:
        if isinstance(node, dict) and seg in node:
            node = node[seg]
        elif isinstance(node, list) and seg.isdigit() and int(seg) < len(node):
            node = node[int(seg)]
        else:
            return None
    return _finite(node)


def _scalar_paths(paths: Any, root: Any) -> dict[str, float] | str:
    if not isinstance(paths, dict) or not paths:
        return "scalar-paths requires a non-empty name-to-path mapping"
    if len(paths) > MAX_VALUES:
        return "too many result values"
    out: dict[str, float] = {}
    for name, path in paths.items():
        v = _resolve_path(root, path)
        if v is None:
            # Strict: a missing or non-numeric declared value is an error, never a silently shorter set.
            return f"declared path for {str(name)[:64]!r} does not resolve to a finite number"
        out[str(name)] = v
    return out


def extract_result_values(mapping: dict[str, Any], result_doc: Any) -> dict[str, Any]:
    """Apply the model revision's declared ``researchResultValues`` mapping to its own result.

    Supported kinds: ``coefficient-table`` (rows with a name field and value field, e.g. the
    R linear-model coefficients), ``vector`` (a list located by key, with declared names) and
    ``scalar-paths`` (named dotted paths into the runtime result, e.g. a posterior mean or a
    Monte Carlo interval bound; every declared path must resolve to a finite number).
    """
    kind = mapping.get("kind")
    values: dict[str, float] = {}
    uncertainty: dict[str, float] = {}
    if kind == "coefficient-table":
        name_f, value_f = mapping.get("nameField", "term"), mapping.get("valueField", "estimate")
        unc_f, rename = mapping.get("uncertaintyField"), mapping.get("rename") or {}
        table = _walk(result_doc, lambda n: isinstance(n, list) and n and all(isinstance(r, dict) and name_f in r for r in n))
        for row in table or []:
            name = str(rename.get(row[name_f], row[name_f]))
            v = _finite(row.get(value_f))
            if v is not None:
                values[name] = v
            u = _finite(row.get(unc_f)) if unc_f else None
            if u is not None:
                uncertainty[name] = u
    elif kind == "vector":
        key, names = mapping.get("key"), list(mapping.get("names") or [])
        vec = _walk(result_doc, lambda n: isinstance(n, dict) and isinstance(n.get(key), list))
        vec = vec[key] if vec else []
        if len(vec) != len(names):
            return {"values": {}, "error": "declared names do not match the result vector"}
        for name, v in zip(names, vec):
            fv = _finite(v)
            if fv is not None:
                values[str(name)] = fv
    elif kind == "scalar-paths":
        root = _runtime_root(result_doc)
        resolved = _scalar_paths(mapping.get("paths"), root)
        if isinstance(resolved, str):
            return {"values": {}, "error": resolved}
        values = resolved
        if mapping.get("uncertaintyPaths"):
            unc = _scalar_paths(mapping["uncertaintyPaths"], root)
            if isinstance(unc, str):
                return {"values": {}, "error": f"uncertainty: {unc}"}
            if not set(unc) <= set(values):
                return {"values": {}, "error": "uncertainty names must be declared result values"}
            uncertainty = unc
    else:
        return {"values": {}, "error": "no researchResultValues mapping declared on the model revision"}
    if len(values) > MAX_VALUES:
        return {"values": {}, "error": "too many result values"}
    out: dict[str, Any] = {"values": values}
    if uncertainty:
        out["uncertainty"] = {"semantics": mapping.get("uncertaintySemantics", "standard-error"), "values": uncertainty}
    # Seeded runtimes echo their seed. Such values are pseudo-random draws: a same-seed replay
    # shows determinism, not reproduction, and Research must be told so.
    root = _runtime_root(result_doc)
    seed = root.get("seed") if isinstance(root, dict) else None
    seed = seed if isinstance(seed, int) and not isinstance(seed, bool) else None
    if seed is not None or mapping.get("stochastic") is True:
        out["stochastic"] = {"seed": seed}
    return out


DATASET_BINDING_KEYS = ("datasetId", "datasetRevision", "datasetFingerprint", "artifactId", "artifactRevision",
                        "artifactSha256", "format", "rowCount", "rowsSha256", "transform", "derivedPayloadSha256")
UPSTREAM_BINDING_KEYS = ("schema", "kind", "lineage", "planId", "notebookId", "notebookRevision", "notebookPackageSha256",
                         "cellId", "cellSha256", "upstream", "crossChecks", "transform", "upstreamValues",
                         "derivedPayloadSha256", "datasets", "chainSha256")


def project_binding(b: dict[str, Any]) -> dict[str, Any]:
    """The exported view of a receipt's input binding: a pinned dataset, or an upstream-cell chain."""
    return {k: b.get(k) for k in (UPSTREAM_BINDING_KEYS if b.get("kind") == UPSTREAM_KIND else DATASET_BINDING_KEYS)}


def _verification(db, user_key: str, run: ExecutionRun, outputs: list[ExecutionRunOutput]) -> dict[str, Any]:
    """Executed-verified only for a succeeded, job-linked run whose output matches a runtime receipt.

    Runtime receipts are written only by the Workspace worker after a bounded runtime call,
    so owner-supplied state changes or outputs alone never qualify.
    """
    receipts = db.scalars(select(PolyglotExecutionReceipt).where(
        PolyglotExecutionReceipt.user_key == user_key,
        PolyglotExecutionReceipt.execution_run_id == run.run_id)).all()
    output_hashes = {o.sha256 for o in outputs if o.sha256}
    matching = [r for r in receipts if r.status == "succeeded" and r.job_id == run.job_id and r.result_sha256 in output_hashes]
    if run.status != "succeeded":
        status = {"failed": "failed", "cancelled": "cancelled", "blocked": "blocked"}.get(run.status, "incomplete")
    elif not run.job_id or not matching:
        status = "succeeded-without-runtime-receipt"
    else:
        status = "executed-verified"
    # Verified input lineage only when every matching receipt bound its inputs to pinned dataset bytes.
    lineages = {(r.details_json or {}).get("inputLineage") or "unrecorded" for r in matching}
    input_lineage = INPUT_VERIFIED if matching and lineages == {INPUT_VERIFIED} else (
        sorted(lineages - {INPUT_VERIFIED})[0] if matching else "not-executed")
    bindings = [b for r in matching for b in ((r.details_json or {}).get("inputBindings") or [])]
    return {
        "status": status, "runStatus": run.status, "jobId": run.job_id,
        "inputLineage": input_lineage,
        "inputBindings": [project_binding(b) for b in bindings],
        "runtimeReceipts": [{"receiptId": r.receipt_id, "language": r.language, "runtime": r.runtime,
                             "operation": r.operation, "requestFingerprint": r.request_fingerprint,
                             "resultArtifactId": r.result_artifact_id, "resultSha256": r.result_sha256,
                             "transport": r.transport, "status": r.status} for r in matching],
    }


def _study_packages(db, user_key: str, run: ExecutionRun) -> list[dict[str, Any]]:
    """Existing study packages that pin this exact run state, each freshly deep-verified."""
    rows = db.scalars(select(ScientificStudyPackage).where(
        ScientificStudyPackage.user_key == user_key, ScientificStudyPackage.project_id == run.project_id)
        .order_by(ScientificStudyPackage.created_at.asc())).all()
    out = []
    for row in rows:
        pinned = [r for r in (row.manifest_json or {}).get("executionRuns", [])
                  if r.get("run_id") == run.run_id and r.get("reproducibility_fingerprint") == run.reproducibility_fingerprint]
        if not pinned:
            continue
        check = verify_package(db, user_key, row.package_id, deep=True)
        out.append({"schema": (row.manifest_json or {}).get("schema"), "packageId": row.package_id,
                    "manifestFingerprint": row.manifest_fingerprint, "bundleSha256": row.bundle_sha256,
                    "verified": bool(check["ok"]), "errors": check["errors"]})
    return out


def build_export(db, claims: dict[str, Any]) -> dict[str, Any]:
    user_key, project_id, run_id = claims["sub"], claims["projectId"], claims["runId"]
    run = get_execution_run(db, user_key, run_id)
    if run is None or run.project_id != project_id:
        raise HTTPException(status_code=404, detail="Execution run not found for this grant.")
    provenance = run_provenance(db, user_key, project_id, run_id, True, True)
    outputs = list(db.scalars(select(ExecutionRunOutput).where(
        ExecutionRunOutput.user_key == user_key, ExecutionRunOutput.run_id == run_id)).all())
    verification = _verification(db, user_key, run, outputs)
    model = ((provenance.get("inputs") or {}).get("model") or {}).get("resolved") or {}
    mapping = (model.get("metadata") or {}).get("researchResultValues") or {}
    values: dict[str, Any] = {"values": {}, "error": "run is not executed-verified"}
    if verification["status"] == "executed-verified":
        receipt = verification["runtimeReceipts"][0]
        artifact = get_artifact(db, user_key, receipt["resultArtifactId"])
        if artifact is None or artifact.sha256 != receipt["resultSha256"]:
            raise HTTPException(status_code=409, detail="Runtime result artifact does not match its receipt.")
        values = extract_result_values(mapping, json.loads(read_artifact_content(artifact)))
        values["sourceArtifactSha256"] = artifact.sha256
    now = _now()
    body = {
        "schema": EXPORT_SCHEMA, "issuer": ISSUER, "audience": AUDIENCE,
        "grantId": claims["grantId"], "ownerScope": claims["ownerScope"],
        "projectId": project_id, "runId": run_id, "exportedAt": now.isoformat(),
        "provenance": provenance, "verification": verification, "resultValues": values,
        "studyPackages": _study_packages(db, user_key, run),
        "notebookCell": verified_cell_run(db, user_key, run),
        "boundaries": {"artifactBytesIncluded": False, "dispatchPerformed": False,
                       "publicationAuthorityGranted": False, "approvalAuthorityGranted": False},
    }
    return sign_document(EXPORT_SCHEMA, body)


# ---------------------------------------------------------------------------
# Routes


class GrantRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    projectId: str = Field(min_length=1, max_length=160)
    runId: str = Field(min_length=1, max_length=96)


class FetchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    grant: str = Field(min_length=10, max_length=4096)


class WithdrawRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    projectId: str = Field(min_length=1, max_length=160)
    reason: str = Field(default="", max_length=2000)


def _owned_run(db, identity: ServiceIdentity, project_id: str, run_id: str) -> ExecutionRun:
    run = get_execution_run(db, identity.user_key, run_id)
    # Same answer for absent, foreign and wrong-project runs.
    if run is None or run.project_id != project_id:
        raise HTTPException(status_code=404, detail="Workspace execution run not found.")
    return run


def require_research_client(authorization: str | None = Header(default=None)) -> None:
    settings = get_settings()
    token = settings.research_export_client_token.strip()
    if not settings.research_export_enabled or not token:
        raise HTTPException(status_code=503, detail="Workspace Research export is not enabled.")
    if not authorization or not secrets.compare_digest(authorization.strip(), f"Bearer {token}"):
        raise HTTPException(status_code=401, detail="Research export client authentication failed.")


@router.get("/public-key")
def public_key_route():
    return {"schema": "sc-workspace-research-export-key/1.0", **public_key_info()}


@router.post("/grants")
def grant_route(payload: GrantRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    settings = get_settings()
    _signing_key()
    with session_scope() as db:
        run = _owned_run(db, identity, payload.projectId, payload.runId)
        if db.get(ResearchExportWithdrawal, {"user_key": identity.user_key, "run_id": run.run_id}):
            raise HTTPException(status_code=410, detail="This run was withdrawn from Research.")
        now = _now()
        ttl = max(60, min(int(settings.research_export_grant_ttl_seconds), 3600))
        row = ResearchExportGrant(grant_id=f"rxg_{uuid4().hex}", user_key=identity.user_key, project_id=run.project_id,
                                  run_id=run.run_id, audience=AUDIENCE, issued_at=now, expires_at=now + timedelta(seconds=ttl))
        db.add(row)
        db.commit()
        claims = {"schema": GRANT_SCHEMA, "grantId": row.grant_id, "iss": ISSUER, "aud": AUDIENCE,
                  "sub": identity.user_key, "ownerScope": f"workspace-user:{identity.user_key}",
                  "projectId": run.project_id, "runId": run.run_id, "scope": ["execution-run:read", "study-package:read"],
                  "iat": int(now.timestamp()), "exp": int(row.expires_at.timestamp())}
        return {"schema": GRANT_SCHEMA, "grantId": row.grant_id, "expiresAt": row.expires_at.isoformat(),
                "grant": issue_grant_token(claims)}


@router.post("/grants/{grant_id}/revoke")
def revoke_grant_route(grant_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = db.get(ResearchExportGrant, grant_id)
        if row is None or row.user_key != identity.user_key:
            raise HTTPException(status_code=404, detail="Research export grant not found.")
        row.revoked_at = row.revoked_at or _now()
        db.commit()
        return {"grantId": grant_id, "revoked": True}


@router.post("/runs/{run_id}/withdraw")
def withdraw_route(run_id: str, payload: WithdrawRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    """Owner withdraws a run from Research; returns a signed notice for Research to apply."""
    _signing_key()
    with session_scope() as db:
        run = _owned_run(db, identity, payload.projectId, run_id)
        existing = db.get(ResearchExportWithdrawal, {"user_key": identity.user_key, "run_id": run.run_id})
        withdrawn_at = existing.withdrawn_at if existing else _now()
        notice = sign_document(WITHDRAWAL_SCHEMA, {
            "schema": WITHDRAWAL_SCHEMA, "issuer": ISSUER, "audience": AUDIENCE,
            "ownerScope": f"workspace-user:{identity.user_key}", "projectId": run.project_id, "runId": run.run_id,
            "withdrawnAt": withdrawn_at.isoformat(), "reason": existing.reason if existing else payload.reason,
        })
        if existing is None:
            db.add(ResearchExportWithdrawal(user_key=identity.user_key, run_id=run.run_id, project_id=run.project_id,
                                            reason=payload.reason, notice_sha256=sha256_hex(notice), withdrawn_at=withdrawn_at))
            for grant in db.scalars(select(ResearchExportGrant).where(
                    ResearchExportGrant.user_key == identity.user_key, ResearchExportGrant.run_id == run.run_id,
                    ResearchExportGrant.revoked_at.is_(None))).all():
                grant.revoked_at = withdrawn_at
            db.commit()
        return notice


@router.post("/fetch", dependencies=[Depends(require_research_client)])
def fetch_route(payload: FetchRequest):
    try:
        claims = decode_grant_token(payload.grant)
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=f"Research export grant rejected: {exc}") from exc
    with session_scope() as db:
        row = db.get(ResearchExportGrant, claims.get("grantId"))
        # The signed claims must match the recorded grant exactly (no replay onto another run).
        if row is None or (row.user_key, row.project_id, row.run_id) != (claims["sub"], claims["projectId"], claims["runId"]):
            raise HTTPException(status_code=403, detail="Research export grant rejected: unknown-grant")
        if row.revoked_at is not None:
            raise HTTPException(status_code=403, detail="Research export grant rejected: revoked-grant")
        if row.expires_at <= _now():
            raise HTTPException(status_code=403, detail="Research export grant rejected: expired-grant")
        if db.get(ResearchExportWithdrawal, {"user_key": row.user_key, "run_id": row.run_id}):
            raise HTTPException(status_code=410, detail="This run was withdrawn from Research.")
        export = build_export(db, claims)
        row.export_count += 1
        row.last_export_sha256 = sha256_hex(export)
        db.commit()
        return export
