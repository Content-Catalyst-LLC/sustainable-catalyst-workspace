"""RH-PROD-05.1 private introspection authentication contract tests."""
import pytest
from fastapi import HTTPException

from app.research_session_introspection import verify_service_credential


def test_private_introspection_requires_dedicated_secret():
    with pytest.raises(HTTPException) as err:
        verify_service_credential(None, expected="")
    assert err.value.status_code == 503


def test_private_introspection_rejects_missing_invalid_or_legacy_bearer():
    secret = "test-only-research-service-secret-" + "x" * 32
    for supplied in (None, "Bearer wrong", "Basic anything", "Bearer " + secret[:-1]):
        with pytest.raises(HTTPException) as err:
            verify_service_credential(supplied, expected=secret)
        assert err.value.status_code == 401


def test_private_introspection_accepts_only_exact_dedicated_secret():
    secret = "test-only-research-service-secret-" + "x" * 32
    assert verify_service_credential("Bearer " + secret, expected=secret) is None
