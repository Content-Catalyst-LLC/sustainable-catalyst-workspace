import secrets
from dataclasses import dataclass

from fastapi import Header, HTTPException, Request, status

from .authorization import SERVICE_PRINCIPAL, authorize_request
from .config import get_settings

@dataclass(frozen=True)
class ServiceIdentity:
    user_key: str
    principal_id: str
    principal_type: str
    service_principal: str
    authentication_method: str

def _session_identity(request: Request) -> ServiceIdentity | None:
    from .session_auth import SESSION_SERVICE_PRINCIPAL, session_payload_from_request
    payload = session_payload_from_request(request)
    if not payload:
        return None
    user_key = str(payload.get("sub") or "").strip()
    if not user_key:
        return None
    return ServiceIdentity(
        user_key=user_key,
        principal_id=f"workspace-user:{user_key}",
        principal_type="workspace-user",
        service_principal=SESSION_SERVICE_PRINCIPAL,
        authentication_method="signed-http-only-session-cookie",
    )

def require_service_identity(
    request: Request,
    authorization: str | None = Header(default=None),
    x_sc_user_id: str | None = Header(default=None, alias="X-SC-User-ID"),
) -> ServiceIdentity:
    session_identity = _session_identity(request)
    if session_identity is not None:
        decision = authorize_request(session_identity, request.method, request.url.path)
        if decision["effect"] != "allow":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code":"authorization-denied","decision":decision})
        return session_identity

    settings = get_settings()
    if not settings.token_configured:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Workspace backend service token is not configured.")
    expected = f"Bearer {settings.service_token}"
    if not authorization or not secrets.compare_digest(authorization, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Valid Workspace identity required.")
    user_key = (x_sc_user_id or "").strip()
    if not user_key or len(user_key) > 128:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A valid user id is required.")
    identity = ServiceIdentity(
        user_key=user_key,
        principal_id=f"wp-user:{user_key}",
        principal_type="wordpress-user",
        service_principal=SERVICE_PRINCIPAL,
        authentication_method="service-bearer+wordpress-user-context",
    )
    decision = authorize_request(identity, request.method, request.url.path)
    if decision["effect"] != "allow":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code":"authorization-denied","decision":decision})
    return identity

def require_runtime_attestation_identity(
    request: Request,
    authorization: str | None = Header(default=None),
    x_sc_user_id: str | None = Header(default=None, alias="X-SC-User-ID"),
    x_sc_runtime_attestation_token: str | None = Header(default=None, alias="X-SC-Runtime-Attestation-Token"),
) -> ServiceIdentity:
    identity = require_service_identity(request=request, authorization=authorization, x_sc_user_id=x_sc_user_id)
    settings = get_settings()
    if not settings.runtime_attestation_token_configured:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Workspace runtime-attestation token is not configured.")
    supplied = (x_sc_runtime_attestation_token or "").strip()
    if not supplied or not secrets.compare_digest(supplied, settings.runtime_attestation_token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid runtime-attestation credential.")
    return identity
