"""SC-STUDIO-SIGNIN-01: signed-out Reporting Studio pages send the browser to sign-in instead of a bare 401.

Only full-page GET routes use ``page_subject``; API routes keep their 401 so in-page scripts can keep unsaved work
and offer sign-in themselves. The return address is always the requested Studio path on this origin, and sign-in is
the Sustainable Catalyst Identity step-up flow, whose callback validates ``returnTo`` again (``_safe_return_to``).
Authentication is not relaxed: a valid session is still required, a revocation-store outage still fails closed (503)
and another account's project still 404s after sign-in.
"""
from urllib.parse import quote

from fastapi import HTTPException, Request

from .wxr_private_projects import _subject

STUDIO_BASE = '/v1/private-research/reporting-studio'
SIGN_IN = '/v1/auth/login?stepUp=true&returnTo='
MAX_RETURN = 512


def return_path(request: Request) -> str:
    """The requested Studio page (path and query), or the Studio home when it is not a plain Studio path."""
    path = request.url.path
    query = request.url.query
    target = path + ('?' + query if query else '')
    if (not (path == STUDIO_BASE or path.startswith(STUDIO_BASE + '/')) or path.startswith('//') or '\\' in target
            or len(target) > MAX_RETURN or any(ord(c) < 0x20 or ord(c) == 0x7f for c in target)):
        return STUDIO_BASE
    return target


def sign_in_url(request: Request) -> str:
    return SIGN_IN + quote(return_path(request), safe='/')


def page_subject(request: Request, subject=_subject) -> str:
    """``subject`` (the calling module's ``_subject``) for HTML pages: a missing, expired or invalid session redirects
    (303) to sign-in."""
    try:
        return subject(request)
    except HTTPException as exc:
        if exc.status_code != 401:
            raise
        raise HTTPException(303, 'Sign-in required.', headers={
            'Location': sign_in_url(request), 'Cache-Control': 'no-store', 'Referrer-Policy': 'no-referrer'}) from None
