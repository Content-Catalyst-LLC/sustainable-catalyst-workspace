"""SC-PUB-M1: Research publication approvals are signed only after a fresh SC Identity step-up.

Unit tests (synthetic). The full path (Keycloak step-up login -> Workspace decision -> Research
verification of the signed evidence) is exercised in the isolated staging acceptance.
"""
import time

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app import research_approvals as ra
from app import sc_identity
from app import session_auth
from app.config import get_settings


def request():
    return Request({"type": "http", "method": "POST", "path": "/", "headers": []})


@pytest.fixture
def session(monkeypatch):
    payload = {"sub": "owner", "auth": sc_identity.AUTH_METHOD, "auth_time": int(time.time()) - 10, "amr": ["pwd", "otp"]}
    monkeypatch.setattr(session_auth, "session_payload_from_request", lambda _request: payload)
    return payload


def test_fresh_sc_identity_sign_in_with_mfa_is_step_up_evidence(session):
    ev = sc_identity.step_up_evidence(request())
    assert ev == {"stepUp": True, "deciderAuthTime": session["auth_time"], "deciderAmr": ["pwd", "otp"]}


@pytest.mark.parametrize("change", [
    {"auth": None},                                                   # legacy or exchanged session
    {"auth_time": int(time.time()) - 10 - get_settings().sc_identity_step_up_max_age},  # stale sign-in
    {"auth_time": int(time.time()) + 120},                            # future-dated
    {"auth_time": "x"}, {"auth_time": 0},
    {"amr": ["pwd"]},                                                 # no second factor
])
def test_anything_else_is_not_step_up_evidence(session, change):
    session.update(change)
    assert sc_identity.step_up_evidence(request()) is None


def test_no_session_is_not_step_up_evidence(monkeypatch):
    monkeypatch.setattr(session_auth, "session_payload_from_request", lambda _request: None)
    assert sc_identity.step_up_evidence(request()) is None


def test_approve_without_step_up_is_refused_before_anything_is_signed(monkeypatch, session):
    session["auth_time"] = 1
    monkeypatch.setattr(sc_identity, "enabled", lambda: True)
    monkeypatch.setattr(ra, "_signing_key", lambda: None)
    monkeypatch.setattr(ra, "session_scope", lambda: pytest.fail("no database access before the step-up gate"))
    identity = ra.ServiceIdentity("owner", "owner", "user", "sc-identity-session", "sc-identity-oidc-session")
    with pytest.raises(HTTPException) as exc:
        ra.decide_route("approval_x", ra.DecisionIn(decision="approve"), request(), identity)
    assert exc.value.status_code == 403 and exc.value.detail["code"] == "step-up-required"
    assert exc.value.detail["loginUrl"] == "/v1/auth/login?stepUp=true"
