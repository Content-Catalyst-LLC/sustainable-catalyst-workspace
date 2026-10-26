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
    'https://localhost#x', 'https://*.example.com', 'https://',
    'https://localhost:bad', 'https://localhost:99999', 'https://local\nhost'])
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


def test_existing_login_default_landing_is_preserved(client):
    response = client.get('/v1/private-research/login')
    assert 'location.assign("/v1/private-research/ui")' in response.text


def test_staging_login_lands_in_existing_persistent_workspace(client, monkeypatch):
    from app import erw_identity_bridge as bridge
    settings = bridge.get_settings()
    monkeypatch.setattr(bridge, 'get_settings', lambda: SimpleNamespace(
        **vars(settings), private_research_landing_path='/v1/private-research/persistent-projects/ui'))
    response = client.get('/v1/private-research/login')
    assert 'location.assign("/v1/private-research/persistent-projects/ui")' in response.text


@pytest.mark.parametrize('target', ['https://attacker.invalid', '//attacker.invalid', '/unknown'])
def test_login_destination_cannot_be_an_open_redirect(target):
    with pytest.raises(ValueError):
        config.Settings(private_research_landing_path=target, _env_file=None)
