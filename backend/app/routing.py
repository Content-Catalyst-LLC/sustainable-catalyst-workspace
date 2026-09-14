import httpx

from .config import get_settings
from .object_store import verify_artifact_storage
from .recovery import create_snapshot, snapshot_metadata
from .compute import ComputeCancelled, execute_scientific_operation
from .jobs import update_job_progress


class RouteBlocked(Exception):
    pass


class RemoteExecutionError(Exception):
    pass


def route_registry() -> dict[str, dict]:
    s = get_settings()
    pairs = {
        "core": (s.route_core_url, s.route_core_token),
        "lab": (s.route_lab_url, s.route_lab_token),
        "workbench": (s.route_workbench_url, s.route_workbench_token),
        "decision-studio": (s.route_decision_studio_url, s.route_decision_studio_token),
        "library": (s.route_library_url, s.route_library_token),
        "site-intelligence": (s.route_site_intelligence_url, s.route_site_intelligence_token),
    }
    registry = {
        "workspace": {
            "targetProduct": "workspace",
            "configured": True,
            "transport": "in-process",
            "serverConfiguredOnly": True,
        }
    }
    for name, (url, token) in pairs.items():
        registry[name] = {
            "targetProduct": name,
            "configured": bool(url.strip()),
            "transport": "server-configured-http",
            "serviceCredentialConfigured": bool(token.strip()),
            "serverConfiguredOnly": True,
        }
    return registry


def configured_route_count() -> int:
    return sum(1 for item in route_registry().values() if item.get("configured"))


def execute_job(db, row) -> dict:
    payload = row.payload or {}
    job_payload = payload.get("payload") or {}

    if row.target_product == "workspace":
        if row.operation.startswith("workspace.compute."):
            try:
                return execute_scientific_operation(
                    db,
                    row,
                    progress_callback=lambda progress, details: update_job_progress(db, row.user_key, row.job_id, progress, details),
                )
            except ComputeCancelled:
                return {"schema": "sc-workspace-job-result/1.0", "cancelled": True, "operation": row.operation}
        if row.operation == "workspace.echo":
            return {"schema": "sc-workspace-job-result/1.0", "echo": job_payload}
        if row.operation == "workspace.storage-integrity":
            return {"schema": "sc-workspace-job-result/1.0", "storageIntegrity": verify_artifact_storage(db, row.user_key)}
        if row.operation == "workspace.recovery-snapshot":
            reason = str(job_payload.get("reason") or "background-job")[:160]
            snapshot = create_snapshot(db, row.user_key, reason)
            return {"schema": "sc-workspace-job-result/1.0", "recoverySnapshot": snapshot_metadata(snapshot)}
        raise RouteBlocked(f"Workspace operation is not registered: {row.operation}")

    settings = get_settings()
    route_map = {
        "core": (settings.route_core_url, settings.route_core_token),
        "lab": (settings.route_lab_url, settings.route_lab_token),
        "workbench": (settings.route_workbench_url, settings.route_workbench_token),
        "decision-studio": (settings.route_decision_studio_url, settings.route_decision_studio_token),
        "library": (settings.route_library_url, settings.route_library_token),
        "site-intelligence": (settings.route_site_intelligence_url, settings.route_site_intelligence_token),
    }
    url, token = route_map.get(row.target_product, ("", ""))
    if not url.strip():
        raise RouteBlocked(f"No server-side orchestration route is configured for {row.target_product}.")

    handoff = {
        "schema": "sc-workspace-compute-handoff/1.0",
        "workspaceVersion": settings.service_version,
        "jobId": row.job_id,
        "targetProduct": row.target_product,
        "operation": row.operation,
        "projectId": row.project_id,
        "inputArtifactIds": payload.get("inputArtifactIds") or [],
        "payload": job_payload,
        "requestFingerprint": row.request_fingerprint,
        "executionPolicy": payload.get("executionPolicy") or {},
        "resourceBudget": payload.get("resourceBudget") or {},
        "sandbox": payload.get("sandbox") or {},
        "humanOwnedRequest": True,
        "automaticApproval": False,
    }
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    if token.strip():
        headers["Authorization"] = f"Bearer {token.strip()}"
    try:
        response = httpx.post(url, json=handoff, headers=headers, timeout=settings.orchestration_timeout_seconds)
    except httpx.HTTPError as exc:
        raise RemoteExecutionError(f"Route transport failed: {exc.__class__.__name__}") from exc
    if response.status_code < 200 or response.status_code >= 300:
        raise RemoteExecutionError(f"Route returned HTTP {response.status_code}.")
    try:
        body = response.json()
    except ValueError:
        body = {"text": response.text[:4000]}
    return {
        "schema": "sc-workspace-job-result/1.0",
        "handoff": handoff,
        "remote": body,
        "httpStatus": response.status_code,
    }
