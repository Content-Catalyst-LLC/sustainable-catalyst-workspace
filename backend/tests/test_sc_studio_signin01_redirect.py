"""SC-STUDIO-SIGNIN-01: signed-out Studio pages redirect to sign-in; APIs keep 401; nothing else is relaxed.

Uses the SC-RESEARCH-PROJECT-01 isolated SQLite fixture (synthetic data only). The fixture's identity stub
authenticates a request only when it carries ``x-test-sub``.
"""
from urllib.parse import unquote

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app import sc_identity, studio_signin, wxr_private_projects
from test_sc_research_project01_project_workspace import env, existing_project  # noqa: F401 (fixture)

S = '/v1/private-research/reporting-studio'
LOGIN = '/v1/auth/login?stepUp=true&returnTo='
PAGES = [
    '', '/publication', '/publication?project=existing-synthetic', '/documents', '/documents/existing-synthetic/some-doc',
    '/research-projects', '/research-projects/existing-synthetic', '/research-projects/existing-synthetic/files/a1',
]
APIS = ['/catalog/projects', '/publication/projects/existing-synthetic/documents', '/documents/register.json',
        '/research-projects/api/projects', '/research-projects/api/projects/existing-synthetic']


def get(env, path, who=None):
    return env['client'].get(S + path, headers={'x-test-sub': who} if who else {}, follow_redirects=False)


@pytest.mark.parametrize('page', PAGES)
def test_signed_out_page_redirects_to_identity_sign_in_and_returns_to_the_same_page(env, page):
    r = get(env, page)
    assert r.status_code == 303 and r.headers['cache-control'] == 'no-store'
    location = r.headers['location']
    assert location.startswith(LOGIN)
    target = unquote(location[len(LOGIN):])
    assert target == S + page  # path and query preserved exactly
    # The Identity flow accepts it as a same-origin return address (it is checked again there).
    assert sc_identity._safe_return_to(target) == target


@pytest.mark.parametrize('api', APIS)
def test_signed_out_api_keeps_401(env, api):
    r = get(env, api)
    assert r.status_code == 401 and 'location' not in r.headers


def test_signed_in_pages_unchanged_and_other_accounts_still_404(env):
    existing_project(env)
    for page in ('', '/publication', '/documents', '/research-projects', '/research-projects/existing-synthetic'):
        assert get(env, page, 'owner').status_code == 200, page
    other = get(env, '/research-projects/existing-synthetic', 'someone-else')
    assert other.status_code == 404 and 'location' not in other.headers


def test_session_verification_outage_still_fails_closed(env, monkeypatch):
    def offline(_request):
        raise HTTPException(503, 'Workspace session verification unavailable')
    monkeypatch.setattr(wxr_private_projects, 'session_payload_from_request', offline)
    for page in ('', '/publication', '/research-projects'):
        r = get(env, page)
        assert r.status_code == 503 and 'location' not in r.headers


def _request(path, query=''):
    return Request({'type': 'http', 'method': 'GET', 'path': path, 'raw_path': path.encode(), 'query_string': query.encode(),
                    'headers': [], 'scheme': 'https', 'server': ('workspace.sustainablecatalyst.com', 443)})


@pytest.mark.parametrize('path,query', [
    ('/v1/private-research/ui', ''), ('/v1/private-research/reporting-studio-evil', ''), ('//evil.example/x', ''),
    (S + '/publication', 'q=' + 'x' * 600), (S + '/publication', 'a=\x01'), (S + '/a\\b', ''),
])
def test_return_address_falls_back_to_studio_home(path, query):
    assert studio_signin.return_path(_request(path, query)) == S


def test_return_address_is_encoded_and_never_absolute():
    url = studio_signin.sign_in_url(_request(S + '/publication', 'project=p&x=https://evil.example'))
    assert url == LOGIN + '/v1/private-research/reporting-studio/publication%3Fproject%3Dp%26x%3Dhttps%3A//evil.example'
    assert unquote(url[len(LOGIN):]).startswith(S + '/')


def test_pages_offer_sign_in_without_leaving_unsaved_work(env):
    existing_project(env)
    for page in ('', '/publication', '/research-projects', '/research-projects/existing-synthetic'):
        html = get(env, page, 'owner').text
        assert 'function signInPrompt(' in html and 'signInPrompt(r' in html, page
        assert "a.target='_blank'" in html and '/v1/auth/login?stepUp=true&returnTo=' in html
