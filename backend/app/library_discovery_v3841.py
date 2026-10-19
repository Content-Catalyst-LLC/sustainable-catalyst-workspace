"""Workspace 3.84.1 — public-only Knowledge Library discovery and references.

No private source access, no body replication, and no writes. Disabled by
default until the upstream origin is explicitly configured.
"""
from __future__ import annotations

import json
import os
import re
from typing import Any, Callable
from urllib.parse import quote, urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from fastapi import HTTPException

from .library_workspace_bridge import reference

SCHEMA = 'sc-workspace-library-discovery/1.0'
HOST = 'library.sustainablecatalyst.com'
_MAX_RESPONSE = 1_000_000
_ID = re.compile(r'^[A-Za-z0-9_.:-]{1,160}$')


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('Library redirected request; refusing to follow')


def _url(path: str, params: dict[str, Any] | None = None) -> str:
    base = os.environ.get('SC_WORKSPACE_LIBRARY_PUBLIC_API_ORIGIN', '').rstrip('/')
    parsed = urlsplit(base)
    if (parsed.scheme != 'https' or parsed.hostname != HOST
            or parsed.port not in (None, 443) or parsed.username or parsed.password
            or parsed.query or parsed.fragment or parsed.path not in ('', '/')):
        raise HTTPException(503, detail='Certified public Library API origin not configured')
    return base + path + ('?' + urlencode(params) if params else '')


def _fetch(path: str, params: dict | None = None, *, loader: Callable | None = None) -> dict:
    url = _url(path, params)
    if loader is not None:
        result = loader(url)
    else:
        opener = build_opener(_NoRedirect)
        request = Request(url, headers={'Accept': 'application/json', 'User-Agent': 'SC-Workspace/3.84.1'})
        try:
            with opener.open(request, timeout=5) as response:
                if int(response.status) != 200:
                    raise ValueError('Library unavailable')
                if int(response.headers.get('Content-Length', '0') or 0) > _MAX_RESPONSE:
                    raise ValueError('Oversized response')
                raw = response.read(_MAX_RESPONSE + 1)
                if len(raw) > _MAX_RESPONSE:
                    raise ValueError('Oversized response')
                result = json.loads(raw)
        except Exception as exc:
            raise HTTPException(502, detail='Library public API unavailable') from exc
    if not isinstance(result, dict):
        raise HTTPException(502, detail='Invalid Library response')
    return result


def _item_id(item: dict) -> str:
    candidate = item.get('record_id') or item.get('recordId') or item.get('id')
    value = str(candidate or '')
    return value if _ID.fullmatch(value) else ''


def verified_public_reference(record_id: str, *, loader: Callable | None = None) -> dict:
    if not _ID.fullmatch(record_id):
        raise HTTPException(422, detail='Invalid record identifier')
    payload = _fetch(
        f'/api/library/v1/research-objects/{quote(record_id, safe="")}',
        {'include_body': 'false'}, loader=loader,
    )
    if payload.get('schema') != 'sc-library-research-object/1.0':
        raise HTTPException(502, detail='Unexpected Library research-object schema')
    identity = payload.get('identity')
    descriptive = payload.get('descriptive')
    publication = payload.get('publication')
    source = payload.get('source')
    if not all(isinstance(section, dict) for section in (identity, descriptive, publication, source)):
        raise HTTPException(502, detail='Incomplete Library research object')
    if identity.get('record_id') != record_id:
        raise HTTPException(502, detail='Library record identity mismatch')
    if publication.get('status') != 'published' or publication.get('visibility') != 'public':
        raise HTTPException(404, detail='Public Library record unavailable')
    title = descriptive.get('title')
    canonical_url = source.get('canonical_url')
    fingerprint = identity.get('content_hash')
    revision = identity.get('revision')
    if not (isinstance(title, str) and title.strip()
            and isinstance(canonical_url, str) and canonical_url.startswith('https://')
            and isinstance(fingerprint, str) and fingerprint.strip()
            and revision is not None):
        raise HTTPException(502, detail='Incomplete public Library provenance')
    # Native payload is deliberately never returned. In particular, content,
    # abstract, metadata, and unknown fields cannot leak via this projection.
    return reference(
        library_id=record_id, kind='research-object', title=title[:500],
        citation='', canonical_url=canonical_url[:2000],
        fingerprint=fingerprint[:256], revision=str(revision)[:240],
        provenance_url=canonical_url[:2000],
    )


def discover(query: str, *, loader: Callable | None = None) -> dict:
    q = (query or '').strip()
    if not 2 <= len(q) <= 120:
        raise HTTPException(422, detail='Search query must contain 2 to 120 characters')
    raw = _fetch('/api/library/v1/search', {'q': q, 'limit': 10, 'offset': 0}, loader=loader)
    if raw.get('schema') != 'sc-library-api-page/1.0' or not isinstance(raw.get('items'), list):
        raise HTTPException(502, detail='Unknown Library search response')
    out = []
    seen = set()
    for candidate in raw['items'][:10]:
        if not isinstance(candidate, dict):
            continue
        rid = _item_id(candidate)
        if not rid or rid in seen:
            continue
        seen.add(rid)
        try:
            out.append(verified_public_reference(rid, loader=loader))
        except HTTPException as exc:
            if exc.status_code == 503:
                raise
            continue  # Individual hits fail closed; never trust search visibility.
    return {
        'schema': SCHEMA, 'query': q, 'items': out, 'publicOnly': True,
        'noSourceReplication': True, 'requiresExplicitAcceptance': True,
        'mutationPerformed': False,
    }
