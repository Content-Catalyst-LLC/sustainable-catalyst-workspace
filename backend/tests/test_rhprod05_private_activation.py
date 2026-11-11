"""Fail-closed private introspection image/secret activation acceptance (synthetic)."""
import asyncio
from pathlib import Path
from types import SimpleNamespace

import pytest

from app import db, session_auth, research_introspection_entry as entry

BACKEND = Path(__file__).resolve().parents[1]


def test_private_image_packages_explicit_security_migration():
    dockerfile = (BACKEND / "Dockerfile").read_text()
    assert "COPY migrations ./migrations" in dockerfile
    assert (BACKEND / "migrations" / "054_workspace_session_revocation.sql").is_file()


def test_cookie_signing_key_file_precedes_legacy_service_fallback(tmp_path, monkeypatch):
    path = tmp_path / "existing-workspace-cookie-key"
    path.write_text("original-existing-cookie-signing-key-at-least-32-bytes")
    settings = SimpleNamespace(
        session_signing_secret_file=str(path),
        session_signing_secret="",
        service_token="legacy-service-credential-must-not-be-used",
    )
    monkeypatch.setattr(session_auth, "get_settings", lambda: settings)
    assert session_auth._secret() == path.read_text()
    path.unlink()
    assert session_auth._secret() == ""


def test_private_lifespan_rejects_generic_service_token_only(monkeypatch):
    settings = SimpleNamespace(
        session_revocation_enforced=True,
        session_signing_secret_file="",
        session_signing_secret="",
        service_token="legacy-service-token-without-cookie-authority",
    )
    monkeypatch.setattr(entry, "get_settings", lambda: settings)
    monkeypatch.setattr(entry, "require_schema", lambda: None)
    monkeypatch.setattr(session_auth, "get_settings", lambda: settings)

    async def boot():
        async with entry.lifespan(None):
            pass

    with pytest.raises(RuntimeError, match="requires the Workspace signing key"):
        asyncio.run(boot())


def test_read_only_authority_database_url_file_no_default_fallback(tmp_path, monkeypatch):
    file = tmp_path / "read-only-workspace-dsn"
    file.write_text("postgresql+psycopg://synthetic_reader:synthetic_only@workspace-db:5432/test")
    settings = SimpleNamespace(
        database_url_file=str(file),
        database_url="postgresql+psycopg://unsafe-fallback",
    )
    monkeypatch.setattr(db, "get_settings", lambda: settings)
    captured = {}
    sentinel = object()

    def fake_create_engine(url, **kwargs):
        captured["url"] = url
        return sentinel

    monkeypatch.setattr(db, "create_engine", fake_create_engine)
    db.get_engine.cache_clear()
    try:
        assert db.get_engine() is sentinel
        assert captured["url"] == file.read_text()
        file.write_text("sqlite:///not-allowed")
        db.get_engine.cache_clear()
        with pytest.raises(RuntimeError, match="credential invalid"):
            db.get_engine()
    finally:
        db.get_engine.cache_clear()


def test_revocation_enforced_session_does_not_reuse_general_service_token(monkeypatch):
    from fastapi import HTTPException
    settings = SimpleNamespace(
        session_revocation_enforced=True,
        session_signing_secret_file="",
        session_signing_secret="",
        service_token="legacy-general-service-token-should-never-sign-cookies",
        session_issuer="workspace",
        session_audience="workspace.example",
        session_cookie_name="sc_workspace_session",
        session_ttl_seconds=3600,
    )
    monkeypatch.setattr(session_auth, "get_settings", lambda: settings)
    assert session_auth._secret() == ""
    profile = session_auth.session_profile()
    assert profile["serviceTokenFallbackActive"] is False
    assert profile["explicitSessionSigningSecretConfigured"] is False
    with pytest.raises(HTTPException) as exc:
        session_auth.issue_session_token("existing-owner")
    assert exc.value.status_code == 503

    # Historical compatibility remains explicitly limited to non-revocable
    # configurations; no existing production token is rotated by this test.
    settings.session_revocation_enforced = False
    assert session_auth._secret() == settings.service_token
    assert session_auth.session_profile()["serviceTokenFallbackActive"] is True

    # A separate configured session signer restores safe token issuance.
    settings.session_revocation_enforced = True
    settings.session_signing_secret = "a-separate-workspace-cookie-signing-key-at-least-32-bytes"
    assert session_auth.session_profile()["serviceTokenFallbackActive"] is False
    assert session_auth.session_profile()["explicitSessionSigningSecretConfigured"] is True
    token = session_auth.issue_session_token("existing-owner")
    assert token.count(".") == 1


def test_session_profile_recognizes_a_separate_signer_file(tmp_path,monkeypatch):
    signing_key=tmp_path/"session-key"
    signing_key.write_text("distinct-cookie-signer-file-at-least-32-bytes")
    settings=SimpleNamespace(
        session_revocation_enforced=True,
        session_signing_secret_file=str(signing_key),
        session_signing_secret="",
        service_token="not-a-cookie-signer",
        session_issuer="workspace",session_audience="workspace.example",
        session_cookie_name="sc_workspace_session",session_ttl_seconds=3600,
    )
    monkeypatch.setattr(session_auth,"get_settings",lambda:settings)
    assert session_auth._secret()==signing_key.read_text()
    profile=session_auth.session_profile()
    assert profile["explicitSessionSigningSecretConfigured"] is True
    assert profile["serviceTokenFallbackActive"] is False
