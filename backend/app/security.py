import secrets
from dataclasses import dataclass

from fastapi import Header, HTTPException, status

from .config import get_settings


@dataclass(frozen=True)
class ServiceIdentity:
    user_key: str


def require_service_identity(
    authorization: str | None = Header(default=None),
    x_sc_user_id: str | None = Header(default=None, alias="X-SC-User-ID"),
) -> ServiceIdentity:
    settings = get_settings()
    if not settings.token_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Workspace backend service token is not configured.",
        )
    expected = f"Bearer {settings.service_token}"
    if not authorization or not secrets.compare_digest(authorization, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid service credential.")
    user_key = (x_sc_user_id or "").strip()
    if not user_key or len(user_key) > 128 or not user_key.isdigit():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A valid WordPress user id is required.")
    return ServiceIdentity(user_key=user_key)
