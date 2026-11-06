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
    assert (BACKEND / "migrations" / "051_workspace_session_revocation.sql").is_file()


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
