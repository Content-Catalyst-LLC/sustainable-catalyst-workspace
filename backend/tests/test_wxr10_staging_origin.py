"""Isolated HTTPS origin selection must not widen production write authority."""
from types import SimpleNamespace
import pytest
from fastapi import HTTPException
from starlette.requests import Request
from app import config, wxr_private_projects as research
from test_existing_erw_identity_bridge import client, upstream, CREDS


def test_default_origin_preserves_production():
    assert config.Settings(_env_file=None).public_origin == research.ORIGIN


@pytest.mark.parametrize('origin', ['*', 'http://localhost:18443', 'https://user:pass@localhost',
    'https://localhost/path', 'https://localhost/', 'https://localhost?q=1',
    'https://localhost#x', 'https://*.example.com', 'https://'])
def test_invalid_public_origins_rejected(origin):
    with pytest.raises(ValueError):
        config.Settings(public_origin=origin, _env_file=None)


def test_configured_staging_origin_replaces_production_authority(monkeypatch):
    staging = 'https://localhost:18443'
    monkeypatch.setattr(config, 'get_settings', lambda: SimpleNamespace(public_origin=staging))
    def request(origin):
        return Request({'type': 'http', 'headers': [(b'origin', origin.encode())]})
    research._write(request(staging))
    for origin in [research.ORIGIN, 'https://attacker.invalid', 'null', '']:
        with pytest.raises(HTTPException) as exc:
            research._write(request(origin))
        assert exc.value.status_code == 403


def test_bridge_existing_login_uses_configured_origin(client, monkeypatch):
    from app import erw_identity_bridge as bridge
    upstream(monkeypatch)
    original = bridge.get_settings()
    monkeypatch.setattr(bridge, 'get_settings', lambda: SimpleNamespace(**vars(original), public_origin='https://localhost:18443'))
    headers = {'Origin': 'https://localhost:18443', 'X-WXR-Login': '1'}
    result = client.post('/v1/private-research/auth/login', headers=headers, json=CREDS)
    assert result.status_code == 200
    assert 'secure' in result.headers['set-cookie'].lower()
    headers['Origin'] = research.ORIGIN
    assert client.post('/v1/private-research/auth/login', headers=headers, json=CREDS).status_code == 403
