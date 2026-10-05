from types import SimpleNamespace
import pytest
from app import session_auth
from app.authorization import evaluate

def _settings(secret="test-session-secret"):
    return SimpleNamespace(
        session_signing_secret=secret,
        service_token="legacy-service-secret",
        session_cookie_name="sc_workspace_session",
        session_issuer="sustainable-catalyst-workspace",
        session_audience="workspace.sustainablecatalyst.com",
        session_ttl_seconds=28800,
    )

def test_session_token_round_trip(monkeypatch):
    monkeypatch.setattr(session_auth, "get_settings", lambda: _settings())
    token = session_auth.issue_session_token("42", "Researcher")
    payload = session_auth.decode_session_token(token)
    assert payload["sub"] == "42"
    assert payload["displayName"] == "Researcher"

def test_session_token_rejects_tamper(monkeypatch):
    monkeypatch.setattr(session_auth, "get_settings", lambda: _settings())
    token = session_auth.issue_session_token("42")
    encoded, signature = token.split(".")
    with pytest.raises(ValueError):
        session_auth.decode_session_token(encoded + "." + signature[:-2] + "xx")

def test_workspace_session_principal_authorized():
    identity = SimpleNamespace(
        user_key="42",
        principal_id="workspace-user:42",
        principal_type="workspace-user",
        service_principal="workspace-session",
        authentication_method="signed-http-only-session-cookie",
    )
    assert evaluate(identity, "workspace.read")["effect"] == "allow"
