from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .config import get_settings
from .environments import get_environment, get_environment_revision
from .models import RuntimeAdapterHead, RuntimeAdapterRevision
from .schemas import RuntimeAdapterStoreRequest
from .utils import iso, sha256_hex


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _clean_list(values: list[str], limit: int = 100) -> list[str]:
    out, seen = [], set()
    for raw in values:
        value = str(raw).strip()[:160]
        if not value:
            continue
        key = value.casefold()
        if key in seen:
            continue
        seen.add(key); out.append(value)
    return out[:limit]


def adapter_metadata(row) -> dict:
    return {
        "adapterId": row.adapter_id,
        "projectId": row.project_id,
        "name": row.name,
        "description": row.description,
        "runtimeFamily": row.runtime_family,
        "runtimeVersion": row.runtime_version,
        "adapterType": row.adapter_type,
        "revision": int(row.revision),
        "fingerprint": row.fingerprint,
        "dependencyManagers": row.dependency_managers_json,
        "container": row.container_json,
        "platformConstraints": row.platform_constraints_json,
        "capabilities": row.capabilities_json,
        "configuration": row.configuration_json,
        "metadata": row.metadata_json,
        "arbitraryCommandExecution": False,
        "createdAt": iso(row.created_at),
        "updatedAt": iso(getattr(row, "updated_at", row.created_at)),
    }


def _document(payload: RuntimeAdapterStoreRequest) -> dict:
    return {
        "runtimeFamily": payload.runtimeFamily,
        "runtimeVersion": payload.runtimeVersion.strip(),
        "adapterType": payload.adapterType,
        "dependencyManagers": _clean_list(payload.dependencyManagers, 20),
        "container": payload.container,
        "platformConstraints": payload.platformConstraints,
        "capabilities": _clean_list(payload.capabilities, 100),
        "configuration": payload.configuration,
    }


def store_adapter(db: Session, user_key: str, payload: RuntimeAdapterStoreRequest):
    settings = get_settings()
    adapter_id = payload.adapterId.strip()
    existing = db.get(RuntimeAdapterHead, {"user_key": user_key, "adapter_id": adapter_id})
    operation_id = (payload.operationId or "").strip()
    document = _document(payload)
    fingerprint = sha256_hex(document)
    if existing is not None and operation_id and existing.last_operation_id == operation_id:
        if existing.fingerprint != fingerprint:
            raise HTTPException(status_code=409, detail="Runtime-adapter operationId was already used for a different descriptor.")
        return existing, True
    current = int(existing.revision) if existing is not None else 0
    if existing is None:
        if payload.expectedRevision not in (None, 0):
            raise HTTPException(status_code=409, detail={"message":"Workspace runtime-adapter revision conflict.","currentRevision":0,"current":None})
        count = int(db.scalar(select(func.count()).select_from(RuntimeAdapterHead).where(RuntimeAdapterHead.user_key == user_key)) or 0)
        if count >= settings.max_runtime_adapters_per_account:
            raise HTTPException(status_code=409, detail="Workspace runtime-adapter registry limit reached.")
    elif payload.expectedRevision is None or int(payload.expectedRevision) != current:
        raise HTTPException(status_code=409, detail={"message":"Workspace runtime-adapter revision conflict.","currentRevision":current,"current":adapter_metadata(existing)})
    revision = current + 1; now = _now()
    values = dict(
        project_id=(payload.projectId or "").strip(), name=payload.name.strip(), description=payload.description.strip(),
        runtime_family=document["runtimeFamily"], runtime_version=document["runtimeVersion"], adapter_type=document["adapterType"],
        revision=revision, fingerprint=fingerprint, dependency_managers_json=document["dependencyManagers"],
        container_json=document["container"], platform_constraints_json=document["platformConstraints"], capabilities_json=document["capabilities"],
        configuration_json=document["configuration"], metadata_json=payload.metadata,
    )
    if existing is None:
        existing = RuntimeAdapterHead(user_key=user_key, adapter_id=adapter_id, last_operation_id=operation_id, created_at=now, updated_at=now, **values)
        db.add(existing)
    else:
        for key, value in values.items(): setattr(existing, key, value)
        existing.last_operation_id=operation_id; existing.updated_at=now
    db.add(RuntimeAdapterRevision(user_key=user_key, adapter_id=adapter_id, operation_id=operation_id, created_at=now, **values))
    try:
        db.commit()
    except IntegrityError:
        db.rollback(); raise HTTPException(status_code=409, detail="A concurrent Workspace runtime-adapter revision was detected.")
    db.refresh(existing); return existing, False


def get_adapter(db: Session, user_key: str, adapter_id: str):
    return db.get(RuntimeAdapterHead, {"user_key": user_key, "adapter_id": adapter_id})


def get_adapter_revision(db: Session, user_key: str, adapter_id: str, revision: int):
    return db.get(RuntimeAdapterRevision, {"user_key": user_key, "adapter_id": adapter_id, "revision": revision})


def list_adapters(db: Session, user_key: str, project_id: str | None = None) -> list[dict]:
    stmt=select(RuntimeAdapterHead).where(RuntimeAdapterHead.user_key==user_key)
    if project_id: stmt=stmt.where(RuntimeAdapterHead.project_id==project_id)
    return [adapter_metadata(r) for r in db.scalars(stmt.order_by(RuntimeAdapterHead.updated_at.desc())).all()]


def list_adapter_revisions(db: Session, user_key: str, adapter_id: str) -> list[dict]:
    rows=db.scalars(select(RuntimeAdapterRevision).where(RuntimeAdapterRevision.user_key==user_key, RuntimeAdapterRevision.adapter_id==adapter_id).order_by(RuntimeAdapterRevision.revision.desc())).all()
    return [adapter_metadata(r) for r in rows]


def resolve_runtime_adapter_ref(db: Session, user_key: str, ref) -> tuple[dict, object | None]:
    if ref is None:
        return {}, None
    row=get_adapter_revision(db,user_key,ref.adapterId,ref.revision) if ref.revision else get_adapter(db,user_key,ref.adapterId)
    if row is None:
        raise HTTPException(status_code=409, detail="Execution run references an unavailable Workspace runtime adapter.")
    return {"adapterId":row.adapter_id,"revision":int(row.revision),"fingerprint":row.fingerprint}, row


def _norm_version(value: str) -> tuple[int, ...] | None:
    value=(value or "").strip().lower().lstrip("v")
    if not value: return None
    parts=[]
    for piece in value.split("."):
        digits="".join(ch for ch in piece if ch.isdigit())
        if not digits: break
        parts.append(int(digits))
    return tuple(parts) if parts else None


def check_environment_compatibility(db: Session, user_key: str, adapter_row, environment_ref) -> dict:
    env=get_environment_revision(db,user_key,environment_ref.environmentId,environment_ref.revision) if environment_ref.revision else get_environment(db,user_key,environment_ref.environmentId)
    if env is None:
        raise HTTPException(status_code=409, detail="Runtime compatibility check references an unavailable execution environment.")
    runtime=env.runtime_json or {}; deps=env.dependencies_json or {}; container=env.container_json or {}
    checks=[]
    family=str(runtime.get("language") or runtime.get("family") or "").lower().strip()
    family_ok=bool(family) and family==adapter_row.runtime_family
    checks.append({"check":"runtime-family","status":"pass" if family_ok else ("unknown" if not family else "fail"),"expected":adapter_row.runtime_family,"actual":family})
    expected_version=_norm_version(adapter_row.runtime_version); actual_version=_norm_version(str(runtime.get("version") or ""))
    version_ok=(expected_version is None) or (actual_version is not None and actual_version[:len(expected_version)]==expected_version)
    checks.append({"check":"runtime-version","status":"pass" if version_ok else ("unknown" if actual_version is None else "fail"),"expected":adapter_row.runtime_version,"actual":str(runtime.get("version") or "")})
    manager=str(deps.get("manager") or "").lower().strip(); supported=[x.lower() for x in adapter_row.dependency_managers_json]
    manager_ok=(not supported) or (manager in supported)
    checks.append({"check":"dependency-manager","status":"pass" if manager_ok else ("unknown" if not manager else "fail"),"expected":supported,"actual":manager})
    expected_image=str((adapter_row.container_json or {}).get("image") or "").strip(); actual_image=str(container.get("image") or "").strip()
    strict=bool((adapter_row.configuration_json or {}).get("strictContainerIdentity",False))
    container_ok=(not strict) or (bool(expected_image) and expected_image==actual_image)
    checks.append({"check":"container-identity","status":"pass" if container_ok else ("unknown" if not actual_image else "fail"),"expected":expected_image,"actual":actual_image,"strict":strict})
    failed=any(x["status"]=="fail" for x in checks); unknown=any(x["status"]=="unknown" for x in checks)
    readiness="incompatible" if failed else ("insufficient-metadata" if unknown else "ready")
    return {
        "schema":"sc-workspace-runtime-compatibility-result/1.0",
        "adapterRef":{"adapterId":adapter_row.adapter_id,"revision":int(adapter_row.revision),"fingerprint":adapter_row.fingerprint},
        "environmentRef":{"environmentId":env.environment_id,"revision":int(env.revision),"fingerprint":env.fingerprint},
        "compatible":not failed,
        "readiness":readiness,
        "checks":checks,
        "executionPerformed":False,
    }
