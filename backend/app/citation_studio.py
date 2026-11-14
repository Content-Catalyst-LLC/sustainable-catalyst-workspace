"""SC-CITE-01: Citation Studio as a shared publishing capability.

Recovered from the Workbench ERW v1.3.2 Citation Studio (``erw_v132_sources.harvard``, live in production and on the
Workbench recovery branch). Its Harvard output is kept byte-for-byte as the ``harvard-erw-v132`` style so existing
Wexford citations never change; ``harvard`` and ``apa`` are added for new work.

Bibliographic records are never retyped. They enter a project's citation collection only from:
  * the project's own preserved reference files (CSL-JSON, Crossref-verified JSON, RIS, or exported ERW v1.3.2
    approved-citation records), keeping the source artifact ID and SHA-256 as provenance; or
  * verified public Knowledge Library records, keeping Library's record ID, revision and content hash.
Collection items are immutable by key. Each publication revision freezes the items it cites, so its bibliography
survives later collection changes, editorial revisions and every export format.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import re
from typing import Any, Callable
from urllib.parse import urlparse
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

COLLECTION_SCHEMA = 'sc-citation-collection/1.0'
ITEM_SCHEMA = 'sc-citation-item/1.0'
FROZEN_SCHEMA = 'sc-publication-bibliography/1.0'
STYLES = ('harvard', 'apa', 'harvard-erw-v132')
DEFAULT_STYLE = 'harvard'
MAX_ITEMS = 500
DOI = re.compile(r'^10\.\d{4,9}/\S+$', re.I)
KEY = re.compile(r'^[A-Za-z0-9_.:-]{1,80}$')
# One marker holds one or more ``@key`` cites, each with an optional locator: [@a2020], [@a2020, p. 4; @b2021].
MARKER = re.compile(r'\[(@[A-Za-z0-9_.:-]{1,80}(?:,[^;\]\n]{1,40})?(?:;\s*@[A-Za-z0-9_.:-]{1,80}(?:,[^;\]\n]{1,40})?)*)\]')
SITE_AUTHORS = {'wordpress-main': 'Sustainable Catalyst'}  # Library sources whose organisational author is known


def _clean(value: Any, limit: int = 600) -> str:
    return ' '.join(str(value if value is not None else '').strip().split())[:limit]


# ---------------------------------------------------------------------------------------------------------------
# ERW v1.3.2 Harvard formatter, preserved exactly (input: the v1.3.2 CitationFields dict).

def harvard_erw_v132(fields: dict) -> dict:
    if not fields.get('verifiedByResearcher'):
        return {'reference': None, 'inText': None,
                'warnings': ['Researcher must review bibliographic metadata before a final reference is generated']}
    missing = [k for k in ('authors', 'year', 'title') if not fields.get(k)]
    if missing:
        return {'reference': None, 'inText': None, 'warnings': ['Missing required fields: ' + ', '.join(missing)]}
    doi = str(fields.get('doi') or '').strip().removeprefix('https://doi.org/')
    if doi and not DOI.fullmatch(doi):
        raise ValueError('Invalid DOI format')
    names = [_clean(n, 10_000) for n in fields['authors']]
    if any(not n or len(n) > 150 for n in names):
        raise ValueError('Invalid author name')
    label = names[0] if len(names) == 1 else names[0] + ' et al.' if len(names) > 2 else names[0] + ' and ' + names[1]
    authors = ', '.join(names[:-1]) + ' and ' + names[-1] if len(names) > 1 else names[0]
    ref = authors + ' (' + str(fields['year']) + ") '" + _clean(fields['title'], 10_000) + "'."
    for key, prefix, suffix in (('journal', ' ', ''), ('volume', ', ', ''), ('issue', '(', ')'), ('pages', ', pp. ', '')):
        if fields.get(key):
            ref += prefix + _clean(fields[key], 10_000) + suffix
    if fields.get('publisher') and not fields.get('journal'):
        ref += ' ' + _clean(fields['publisher'], 10_000)
    ref += '.'
    if doi:
        ref += ' https://doi.org/' + doi
    elif fields.get('url'):
        ref += ' ' + _clean(fields['url'], 10_000)
    return {'reference': ref, 'inText': '(' + label + ', ' + str(fields['year']) + ')',
            'warnings': ['Harvard styles vary by institution; confirm against UCD instructions. '
                         'Metadata is researcher-reviewed, not independently verified.']}


# ---------------------------------------------------------------------------------------------------------------
# Normalised items

def _person(value: Any) -> dict | None:
    if isinstance(value, dict):
        family, given = _clean(value.get('family'), 150), _clean(value.get('given'), 150)
        literal = _clean(value.get('literal') or value.get('name'), 300)
        if family:
            return {'family': family, 'given': given}
        return {'literal': literal} if literal else None
    text = _clean(value, 300)
    if not text:
        return None
    if ',' in text:
        family, given = [x.strip() for x in text.split(',', 1)]
        return {'family': family, 'given': given}
    return {'literal': text}


def _doi(value: Any) -> str:
    raw = _clean(value, 250)
    raw = re.sub(r'^(https?://(dx\.)?doi\.org/|doi:)', '', raw, flags=re.I)
    if raw and not DOI.fullmatch(raw):
        raise ValueError('Invalid DOI format')
    return raw


def _url(value: Any) -> str:
    raw = _clean(value, 2000)
    return raw if raw and urlparse(raw).scheme in ('http', 'https') else ''


def _year(value: Any) -> int | None:
    if isinstance(value, dict):  # CSL / Crossref date-parts
        parts = value.get('date-parts') or [[None]]
        value = parts[0][0] if parts and parts[0] else None
    match = re.search(r'(1[5-9]\d\d|2[01]\d\d)', str(value or ''))
    return int(match.group(1)) if match else None


def item_fingerprint(item: dict) -> str:
    basis = {k: item.get(k) for k in ('type', 'authors', 'year', 'title', 'container', 'volume', 'issue', 'pages',
                                      'publisher', 'doi', 'url', 'accessed')}
    return hashlib.sha256(json.dumps(basis, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def make_item(fields: dict, provenance: dict) -> dict:
    authors = [p for p in (_person(a) for a in (fields.get('authors') or [])[:100]) if p]
    item = {'schema': ITEM_SCHEMA, 'type': _clean(fields.get('type') or 'article-journal', 40),
            'authors': authors, 'year': _year(fields.get('year')), 'title': _clean(fields.get('title'), 500),
            'container': _clean(fields.get('container'), 350), 'volume': _clean(fields.get('volume'), 50),
            'issue': _clean(fields.get('issue'), 50), 'pages': _clean(fields.get('pages'), 100),
            'publisher': _clean(fields.get('publisher'), 200), 'doi': _doi(fields.get('doi')),
            'url': _url(fields.get('url')), 'accessed': _clean(fields.get('accessed'), 40)}
    if not item['title']:
        raise ValueError('A citation needs a title')
    item['fingerprint'] = item_fingerprint(item)
    item['provenance'] = {k: v for k, v in provenance.items() if v not in (None, '')}
    item['key'] = base_key(item)
    return item


def base_key(item: dict) -> str:
    first = item['authors'][0] if item['authors'] else {}
    name = first.get('family') or first.get('literal') or 'anon'
    word = next((w for w in re.findall(r'[A-Za-z]+', item['title']) if len(w) > 3), 'work')
    raw = re.sub(r'[^A-Za-z0-9]', '', name)[:30].lower() + str(item['year'] or 'nd') + word.lower()[:12]
    return raw or 'ref'


def from_crossref_verified(rows: list) -> list[dict]:
    """Research-package ``references-verified.json``: Crossref metadata with a verification timestamp."""
    out = []
    for row in rows:
        journal = row.get('journal')
        out.append(({'authors': row.get('authors') or [], 'year': row.get('published'), 'title': row.get('title'),
                     'container': journal[0] if isinstance(journal, list) and journal else journal,
                     'volume': row.get('volume'), 'issue': row.get('issue'),
                     'pages': row.get('page') or row.get('article_number'), 'doi': row.get('doi'),
                     'url': row.get('publisher_url')},
                    {'metadataAuthority': 'crossref', 'metadataUrl': row.get('metadata_url'),
                     'metadataVerifiedAt': row.get('verified_utc')}))
    return out


def from_csl(rows: list) -> list[dict]:
    """CSL-JSON, as exported by the Knowledge Library citation workspace."""
    return [({'type': r.get('type'), 'authors': r.get('author') or [], 'year': r.get('issued'), 'title': r.get('title'),
              'container': r.get('container-title'), 'volume': r.get('volume'), 'issue': r.get('issue'),
              'pages': r.get('page'), 'publisher': r.get('publisher'), 'doi': r.get('DOI'), 'url': r.get('URL')},
             {'metadataAuthority': 'csl-json'}) for r in rows]


def from_erw_v132(rows: list) -> list[dict]:
    """Exported Workbench ERW v1.3.2 approved-citation records; only researcher-reviewed ones are accepted."""
    out = []
    for r in rows:
        f = r.get('fields') or {}
        if r.get('schema') != 'sc.erw.approved-citation.v1.3.2' or not f.get('verifiedByResearcher'):
            continue
        out.append(({'authors': f.get('authors'), 'year': f.get('year'), 'title': f.get('title'),
                     'container': f.get('journal'), 'volume': f.get('volume'), 'issue': f.get('issue'),
                     'pages': f.get('pages'), 'publisher': f.get('publisher'), 'doi': f.get('doi'), 'url': f.get('url'),
                     'type': 'article-journal' if f.get('journal') else 'report'},
                    {'metadataAuthority': 'workbench-erw-v1.3.2-researcher-reviewed',
                     'erwV132Reference': (r.get('formattedCitation') or {}).get('reference'),
                     'erwV132InText': (r.get('formattedCitation') or {}).get('inText')}))
    return out


def from_ris(text: str) -> list[dict]:
    out, cur = [], None
    tags = {'TI': 'title', 'T1': 'title', 'JO': 'container', 'JF': 'container', 'T2': 'container', 'VL': 'volume',
            'IS': 'issue', 'PY': 'year', 'Y1': 'year', 'DO': 'doi', 'UR': 'url', 'PB': 'publisher'}
    for line in text.splitlines():
        m = re.match(r'^([A-Z][A-Z0-9])  - ?(.*)$', line)
        if not m:
            continue
        tag, value = m.group(1), m.group(2).strip()
        if tag == 'TY':
            cur = {'authors': [], 'type': 'article-journal' if value == 'JOUR' else 'report'}
        elif cur is None:
            continue
        elif tag == 'ER':
            out.append((cur, {'metadataAuthority': 'ris'})); cur = None
        elif tag in ('AU', 'A1'):
            cur['authors'].append(value)
        elif tag == 'SP':
            cur['pages'] = value
        elif tag == 'EP' and cur.get('pages'):
            cur['pages'] += '–' + value
        elif tag in tags and not cur.get(tags[tag]):
            cur[tags[tag]] = value
    return out


def parse_reference_file(filename: str, raw: bytes) -> list[tuple[dict, dict]]:
    name = filename.lower()
    try:
        text = raw.decode('utf-8-sig')
    except UnicodeError as exc:
        raise ValueError('Reference file is not UTF-8') from exc
    if name.endswith('.ris'):
        return from_ris(text)
    if not name.endswith('.json'):
        raise ValueError('Choose a .ris or .json reference file')
    data = json.loads(text)
    rows = data if isinstance(data, list) else data.get('items') or data.get('references') or []
    if not isinstance(rows, list) or not rows:
        raise ValueError('No references found in this file')
    first = rows[0] if isinstance(rows[0], dict) else {}
    if first.get('schema') == 'sc.erw.approved-citation.v1.3.2':
        return from_erw_v132(rows)
    if 'metadata_url' in first or 'verified_utc' in first:
        return from_crossref_verified(rows)
    return from_csl(rows)


def library_item(record: dict) -> tuple[dict, dict]:
    """A verified public Library research object, cited as a web source. No author is invented."""
    identity, desc, pub, source = (record.get(k) or {} for k in ('identity', 'descriptive', 'publication', 'source'))
    author = SITE_AUTHORS.get(source.get('source_key'))
    return ({'type': 'webpage', 'authors': [{'literal': author}] if author else [], 'year': pub.get('published_at'),
             'title': desc.get('title'), 'publisher': author or '', 'url': source.get('canonical_url')},
            {'metadataAuthority': 'knowledge-library', 'libraryRecordId': identity.get('record_id'),
             'libraryRevision': str(identity.get('revision')), 'libraryContentSha256': identity.get('content_hash'),
             'authorStatus': 'organisation-from-library-source' if author else 'missing-review-required'})


# ---------------------------------------------------------------------------------------------------------------
# Styles

def _initials(given: str, sep: str) -> str:
    return sep.join(p[0] + '.' for p in re.split(r'[\s.\-]+', given) if p)


def _name(p: dict, style: str) -> str:
    if 'literal' in p:
        return p['literal']
    return p['family'] + (', ' + _initials(p['given'], ' ' if style == 'apa' else '') if p.get('given') else '')


def _surname(p: dict) -> str:
    return p.get('family') or p.get('literal') or ''


def _join(names: list[str], amp: str) -> str:
    return names[0] if len(names) == 1 else ', '.join(names[:-1]) + (',' if amp == '&' and len(names) > 2 else '') + f' {amp} ' + names[-1]


def in_text(item: dict, style: str = DEFAULT_STYLE, locator: str = '') -> str:
    if style == 'harvard-erw-v132':
        legacy = (item.get('provenance') or {}).get('erwV132InText')
        if legacy and not locator:
            return legacy
    names = [_surname(p) for p in item['authors']] or [item['title']]
    amp = '&' if style == 'apa' else 'and'
    label = names[0] if len(names) == 1 else f'{names[0]} {amp} {names[1]}' if len(names) == 2 else names[0] + ' et al.'
    year = str(item['year']) if item['year'] else 'n.d.'
    loc = ', ' + locator.strip() if locator.strip() else ''
    return f'({label}, {year}{loc})'


def reference(item: dict, style: str = DEFAULT_STYLE) -> str:
    if style == 'harvard-erw-v132':
        legacy = (item.get('provenance') or {}).get('erwV132Reference')
        if legacy:
            return legacy
        names = [p.get('literal') or (p['family'] + (', ' + p['given'] if p.get('given') else '')) for p in item['authors']]
        return harvard_erw_v132({'authors': names, 'year': item['year'], 'title': item['title'],
                                 'journal': item['container'], 'volume': item['volume'], 'issue': item['issue'],
                                 'pages': item['pages'], 'publisher': item['publisher'], 'doi': item['doi'],
                                 'url': item['url'], 'verifiedByResearcher': True})['reference'] or ''
    year = str(item['year']) if item['year'] else 'n.d.'
    names = [_name(p, style) for p in item['authors']]
    if style == 'apa':
        who = _join(names[:20], '&') if names else item['title']
        out = f'{who} ({year}). '
        out += (f"{item['title']}. *{item['container']}*" if item['container'] else f"*{item['title']}*")
        if item['volume']:
            out += f", *{item['volume']}*" + (f"({item['issue']})" if item['issue'] else '')
        if item['pages']:
            out += f", {item['pages']}"
        out += '.'
        if item['publisher'] and not item['container'] and item['publisher'] not in names:
            out += f" {item['publisher']}."
    else:  # Harvard (author-date, Cite Them Right conventions)
        who = _join(names, 'and') if names else item['title']
        if item['type'] == 'webpage':
            out = f"{who} ({year}) *{item['title']}*."
        elif item['container']:
            out = f"{who} ({year}) '{item['title']}', *{item['container']}*"
            if item['volume']:
                out += f", {item['volume']}" + (f"({item['issue']})" if item['issue'] else '')
            if item['pages']:
                out += f", pp. {item['pages']}" if not item['pages'].isdigit() and not item['pages'].startswith('e') else f", {item['pages']}"
            out += '.'
        else:
            out = f"{who} ({year}) *{item['title']}*." + (f" {item['publisher']}." if item['publisher'] and item['publisher'] != who else '')
    if item['doi']:
        out += f" https://doi.org/{item['doi']}"
    elif item['url']:
        out += f" Available at: {item['url']}" if style == 'harvard' else f" {item['url']}"
        if item.get('accessed') and style == 'harvard':
            out += f" (Accessed: {item['accessed']})"
        out += '.' if style == 'harvard' else ''
    return out


def sort_key(item: dict):
    first = item['authors'][0] if item['authors'] else {}
    return ((_surname(first) or item['title']).casefold(), item['year'] or 0, item['title'].casefold())


# ---------------------------------------------------------------------------------------------------------------
# Collections, markers and frozen bibliographies

def collection(package: dict) -> dict:
    for obj in package.get('project', {}).get('objects', []):
        if isinstance(obj, dict) and obj.get('type') == 'citation-collection' and \
                (obj.get('collection') or {}).get('schema') == COLLECTION_SCHEMA:
            return obj['collection']
    return {'schema': COLLECTION_SCHEMA, 'items': []}


def add_items(current: dict, entries: list[tuple[dict, dict]], common: dict) -> tuple[dict, dict]:
    """Append items; identical records are reused, so re-importing never duplicates. Keys are never reassigned."""
    result = deepcopy(current)
    items = result['items']
    by_fp = {x['fingerprint']: x for x in items}
    by_doi = {x['doi'].lower(): x for x in items if x.get('doi')}
    keys = {x['key'] for x in items}
    added, reused, rejected = [], [], []
    for fields, provenance in entries:
        try:
            item = make_item(fields, {**common, **provenance})
        except ValueError as exc:
            rejected.append({'title': _clean(fields.get('title'), 120), 'reason': str(exc)})
            continue
        twin = by_fp.get(item['fingerprint']) or (by_doi.get(item['doi'].lower()) if item['doi'] else None)
        if twin:
            reused.append(twin['key'])
            continue
        if len(items) >= MAX_ITEMS:
            raise HTTPException(413, 'Citation collection is full.')
        base, n = item['key'], 0
        while item['key'] in keys:
            n += 1
            item['key'] = base + chr(ord('a') + n - 1) if n <= 26 else f'{base}-{n}'
        keys.add(item['key']); by_fp[item['fingerprint']] = item
        if item['doi']:
            by_doi[item['doi'].lower()] = item
        item['addedId'] = uuid4().hex
        items.append(item); added.append(item['key'])
    return result, {'added': added, 'reused': reused, 'rejected': rejected}


def cited_keys(markdown: str) -> list[str]:
    keys = []
    for m in MARKER.finditer(markdown):
        for part in m.group(1).split(';'):
            key = part.strip().lstrip('@').split(',')[0].strip()
            if key not in keys:
                keys.append(key)
    return keys


def freeze(markdown: str, current: dict, style: str) -> dict | None:
    """The per-publication bibliography stored with a revision; None when the text cites nothing."""
    keys = cited_keys(markdown)
    if not keys:
        return None
    if style not in STYLES:
        raise HTTPException(422, 'Unknown citation style.')
    found = {x['key']: x for x in current.get('items', [])}
    items = [deepcopy(found[k]) for k in keys if k in found]
    return {'schema': FROZEN_SCHEMA, 'style': style, 'items': items,
            'unresolved': [k for k in keys if k not in found]}


def resolve(markdown: str, frozen: dict | None) -> str:
    """Replace markers with in-text citations and append the reference list. Text without citations is unchanged."""
    if not frozen or not frozen.get('items'):
        return markdown
    style, found = frozen['style'], {x['key']: x for x in frozen['items']}

    def one(m):
        parts = []
        for part in m.group(1).split(';'):
            key, _, loc = part.strip().lstrip('@').partition(',')
            item = found.get(key.strip())
            if item is None:
                return m.group(0)  # unresolved markers stay visible
            parts.append(in_text(item, style, loc))
        return parts[0] if len(parts) == 1 else '(' + '; '.join(p[1:-1] for p in parts) + ')'
    body = MARKER.sub(one, markdown)
    refs = sorted(frozen['items'], key=sort_key)
    return body.rstrip() + '\n\n## References\n\n' + '\n\n'.join(reference(x, style) for x in refs) + '\n'


# ---------------------------------------------------------------------------------------------------------------
# Routes (mounted under the Reporting Studio publication router)

class ImportSource(BaseModel):
    model_config = ConfigDict(extra='forbid')
    sourceArtifactId: str = Field(min_length=1, max_length=160)
    expectedProjectRevision: int = Field(ge=1)


class ImportLibrary(BaseModel):
    model_config = ConfigDict(extra='forbid')
    recordId: str = Field(min_length=1, max_length=240)
    expectedProjectRevision: int = Field(ge=1)


class FormatRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    keys: list[str] = Field(default_factory=list, max_length=MAX_ITEMS)
    style: str = DEFAULT_STYLE


def build_router(deps: dict[str, Callable]) -> APIRouter:
    """``deps``: subject, write, project, locked_project, original_asset, store, headers, library_record, library_search."""
    router = APIRouter(prefix='/citations', tags=['Citation Studio'])
    H = deps['headers']

    def view(row, current):
        return {'schema': COLLECTION_SCHEMA, 'projectRevision': row.revision, 'styles': list(STYLES),
                'defaultStyle': DEFAULT_STYLE,
                'items': [{**x, 'formatted': {s: {'reference': reference(x, s), 'inText': in_text(x, s)} for s in STYLES}}
                          for x in current.get('items', [])]}

    def save(db, owner, row, current, operation):
        project = deepcopy(row.package['project'])
        objects = [o for o in project.get('objects', []) if not (isinstance(o, dict) and o.get('type') == 'citation-collection')]
        objects.append({'id': 'citation-collection', 'type': 'citation-collection', 'collection': current})
        project['objects'] = objects
        return deps['store'](db, owner, row, project, operation)

    @router.get('/projects/{project_id}')
    def get_collection(project_id: str, request: Request):
        owner = deps['subject'](request)
        with deps['session']() as db:
            row = deps['project'](db, owner, project_id)
            return JSONResponse(view(row, collection(row.package)), headers=H)

    def _import(project_id, request, expected, load):
        owner = deps['subject'](request); deps['write'](request)
        with deps['session']() as db:
            row = deps['locked_project'](db, owner, project_id)
            if row.revision != expected:
                raise HTTPException(409, 'Workspace project changed. Reload before importing.')
            entries, common = load(db, owner)
            current, report = add_items(collection(row.package), entries, common)
            if report['added']:
                row = save(db, owner, row, current, 'citation-import-' + uuid4().hex)
            return JSONResponse({**view(row, current), 'import': report}, status_code=201 if report['added'] else 200, headers=H)

    @router.post('/projects/{project_id}/import-source')
    def import_source(project_id: str, body: ImportSource, request: Request):
        def load(db, owner):
            meta, raw = deps['original_asset'](db, owner, project_id, body.sourceArtifactId)
            try:
                entries = parse_reference_file(meta['filename'], raw)
            except (ValueError, json.JSONDecodeError) as exc:
                raise HTTPException(422, str(exc)) from exc
            return entries, {'sourceArtifactId': meta['artifactId'], 'sourceFilename': meta['filename'],
                             'sourceSha256': meta['sha256']}
        return _import(project_id, request, body.expectedProjectRevision, load)

    @router.post('/projects/{project_id}/import-library')
    def import_library(project_id: str, body: ImportLibrary, request: Request):
        def load(db, owner):
            fields, provenance = library_item(deps['library_record'](body.recordId))
            return [(fields, provenance)], {}
        return _import(project_id, request, body.expectedProjectRevision, load)

    @router.get('/library/search')
    def library_search(q: str, request: Request):
        deps['subject'](request)
        return JSONResponse(deps['library_search'](q), headers=H)

    @router.post('/projects/{project_id}/bibliography')
    def bibliography(project_id: str, body: FormatRequest, request: Request):
        owner = deps['subject'](request)
        if body.style not in STYLES:
            raise HTTPException(422, 'Unknown citation style.')
        with deps['session']() as db:
            items = collection(deps['project'](db, owner, project_id).package)['items']
        chosen = [x for x in items if not body.keys or x['key'] in body.keys]
        return JSONResponse({'style': body.style, 'references': [reference(x, body.style) for x in sorted(chosen, key=sort_key)]},
                            headers=H)

    return router
