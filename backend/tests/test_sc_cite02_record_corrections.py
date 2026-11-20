"""SC-CITE-02: manuscript references written with Markdown links, access dates, year suffixes and place: publisher are
imported correctly, and the owner can correct an imported record in place without changing its key. Synthetic
references only; offline fakes."""
import importlib
import types

from fastapi import FastAPI
from fastapi.testclient import TestClient

cite = importlib.import_module('app.citation_studio')
pub = importlib.import_module('app.reporting_publication')

REFS = """# A synthetic essay

Claims about guidelines (Synthetic Labour Body, 2015) and two reports (Synthetic Agency, 2024a; Synthetic Agency, 2024b),
a book (Writer, 1990) and an undated page (Synthetic Programme, n.d.).

# References

Writer, A. (1990) *The Synthetic Worlds of Welfare*. Cambridge: Example Press.

Synthetic Labour Body (2015) [Guidelines for a synthetic transition](https://example.org/guidelines).

Synthetic Agency (2024a) [Synthetic policy outlook](https://example.org/outlook.html) (Accessed: 20 November 2026).

Synthetic Agency (2024b) [Synthetic inequality indicator](https://example.org/indicator.html).

Other, B. (2017) [Ring Economics: Seven Synthetic Ways](https://example.org/ring/). London: Example House.

Synthetic Programme (n.d.) [Synthetic development](https://example.org/development).
"""


def review(markdown=REFS, current=None):
    return cite.review_manuscript_references(markdown, current or {'items': []})['entries']


def test_markdown_links_access_dates_suffixes_and_books_are_parsed_into_clean_fields():
    by_title = {e['fields']['title']: e for e in review()}
    assert sorted(by_title) == ['Guidelines for a synthetic transition', 'Ring Economics: Seven Synthetic Ways',
                                'Synthetic development', 'Synthetic inequality indicator', 'Synthetic policy outlook',
                                'The Synthetic Worlds of Welfare']
    for e in by_title.values():
        assert '[' not in e['fields']['title'] and '](' not in e['fields']['title'] and not e['fields']['url'].endswith(')')
    g = by_title['Guidelines for a synthetic transition']['fields']
    assert (g['type'], g['url']) == ('webpage', 'https://example.org/guidelines')
    o = by_title['Synthetic policy outlook']
    assert (o['fields']['year'], o['fields']['yearSuffix'], o['fields']['accessed']) == (2024, 'a', '20 November 2026')
    assert o['formatted']['harvard'] == ('Synthetic Agency (2024a) *Synthetic policy outlook*. Available at: '
                                         'https://example.org/outlook.html (Accessed: 20 November 2026).')
    assert by_title['Synthetic inequality indicator']['fields']['yearSuffix'] == 'b'
    w = by_title['The Synthetic Worlds of Welfare']['fields']
    assert (w['type'], w['publisher'], w['container']) == ('book', 'Cambridge: Example Press', '')
    r = by_title['Ring Economics: Seven Synthetic Ways']['fields']
    assert (r['type'], r['publisher'], r['url']) == ('book', 'London: Example House', 'https://example.org/ring/')


def test_in_text_mentions_count_the_exact_year_label_including_suffixes_and_undated_works():
    counts = {e['fields']['title']: e['inTextMentions'] for e in review()}
    assert counts['Synthetic policy outlook'] == 1 and counts['Synthetic inequality indicator'] == 1
    assert counts['Synthetic development'] == 1 and counts['Guidelines for a synthetic transition'] == 1


def test_records_without_a_suffix_keep_their_existing_fingerprint():
    item = cite.make_item({'type': 'report', 'authors': ['Writer, A.'], 'year': 1990, 'title': 'T'}, {})
    import hashlib, json
    basis = {k: item.get(k) for k in ('type', 'authors', 'year', 'title', 'container', 'volume', 'issue', 'pages',
                                      'publisher', 'doi', 'url', 'accessed')}
    assert item['fingerprint'] == hashlib.sha256(json.dumps(basis, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    assert 'yearSuffix' not in item
    suffixed = cite.make_item({'type': 'report', 'authors': ['Writer, A.'], 'year': 1990, 'yearSuffix': 'b', 'title': 'T'}, {})
    assert suffixed['fingerprint'] != item['fingerprint'] and cite.in_text(suffixed) == '(Writer, 1990b)'


# A record as the earlier importer stored it: link syntax leaked into the title and the URL.
BROKEN = {'type': 'webpage', 'authors': [{'literal': 'Synthetic Agency'}], 'year': 2024,
          'title': '[Synthetic policy outlook](', 'url': 'https://example.org/outlook.html)'}


def collection_with(*fields):
    current, _ = cite.add_items({'schema': cite.COLLECTION_SCHEMA, 'items': []},
                                [(f, {'source': 'manuscript-references'}) for f in fields], {})
    return current


def test_a_correction_keeps_the_key_provenance_and_import_id_and_records_what_it_replaced():
    current = collection_with(BROKEN)
    before = current['items'][0]
    fixed, report = cite.correct_item(current, before['key'], {
        'title': 'Synthetic policy outlook', 'url': 'https://example.org/outlook.html', 'yearSuffix': 'a',
        'accessed': '20 November 2026'}, 'Link syntax leaked into the title and URL.', '2026-11-20T00:00:00+00:00')
    after = fixed['items'][0]
    assert (after['key'], after['addedId'], after['provenance']) == (before['key'], before['addedId'], before['provenance'])
    assert cite.reference(after) == ('Synthetic Agency (2024a) *Synthetic policy outlook*. Available at: '
                                     'https://example.org/outlook.html (Accessed: 20 November 2026).')
    assert after['corrections'] == [{'at': '2026-11-20T00:00:00+00:00', 'reason': 'Link syntax leaked into the title and URL.',
                                     'previous': {k: before[k] for k in (*cite.CORRECTABLE, 'fingerprint') if k in before}}]
    assert report == {'key': before['key'], 'fingerprint': after['fingerprint'], 'corrections': 1}
    assert current['items'][0] == before  # the input collection is not mutated
    # The corrected record is what the manuscript now reads as: a re-review finds it, so nothing is imported twice.
    entry = review('# References\n\nSynthetic Agency (2024a) [Synthetic policy outlook](https://example.org/outlook.html).',
                   fixed)[0]
    assert (entry['status'], entry['existingKey']) == ('duplicate', before['key'])


def test_corrections_that_change_nothing_duplicate_another_record_or_name_unknown_fields_are_refused():
    current = collection_with(BROKEN, {**BROKEN, 'title': 'Another outlook', 'url': 'https://example.org/b'})
    key, other = current['items'][0]['key'], current['items'][1]
    for fields, error in (({'title': BROKEN['title']}, ValueError), ({'colour': 'red'}, ValueError),
                          ({'yearSuffix': 'ab'}, ValueError), ({'title': ''}, ValueError),
                          ({'title': other['title'], 'url': other['url']}, cite.DuplicateRecord)):
        try:
            cite.correct_item(current, key, fields, 'Synthetic test reason.', 'now')
            raise AssertionError(f'{fields} was accepted')
        except error:
            pass
    try:
        cite.correct_item(current, 'no-such-key', {'title': 'X'}, 'Synthetic test reason.', 'now')
        raise AssertionError('unknown key accepted')
    except LookupError:
        pass


def _client(row, stored):
    def store(db, owner, r, project, operation):
        stored.update(project=project, operation=operation)
        return types.SimpleNamespace(revision=r.revision + 1, package={'project': project})

    class FakeDB:
        def __enter__(self): return self
        def __exit__(self, *a): pass

    deps = dict(subject=lambda r: 'owner', write=lambda r: None, project=lambda db, o, p: row,
                locked_project=lambda db, o, p: row, original_asset=None, store=store, session=FakeDB, headers={},
                library_record=None, library_search=None)
    app = FastAPI()
    app.include_router(cite.build_router(deps))
    return TestClient(app)


def test_the_correct_route_is_revision_gated_validated_and_saves_only_on_success():
    current = collection_with(BROKEN)
    key = current['items'][0]['key']
    row = types.SimpleNamespace(revision=4, package={'project': {'objects': [
        {'id': 'citation-collection', 'type': 'citation-collection', 'collection': current}]}})
    stored = {}
    client = _client(row, stored)
    url = f'/citations/projects/p/items/{key}/correct'
    body = {'fields': {'title': 'Synthetic policy outlook', 'url': 'https://example.org/outlook.html'},
            'reason': 'Link syntax leaked into the title and URL.', 'expectedProjectRevision': 4}
    assert client.post(url, json={**body, 'expectedProjectRevision': 3}).status_code == 409
    assert client.post(url, json={**body, 'reason': 'short'}).status_code == 422
    assert client.post(url, json={**body, 'fields': {'colour': 'red'}}).status_code == 422
    assert client.post('/citations/projects/p/items/no-such-key/correct', json=body).status_code == 404
    assert client.post('/citations/projects/p/items/bad%20key/correct', json=body).status_code == 404
    assert stored == {}
    r = client.post(url, json=body)
    assert r.status_code == 200, r.text
    out = r.json()
    assert out['projectRevision'] == 5 and out['correction']['key'] == key and stored['operation'].startswith('citation-correct-')
    item = out['items'][0]
    assert item['title'] == 'Synthetic policy outlook' and item['formatted']['harvard']['inText'] == '(Synthetic Agency, 2024)'
    assert len(item['corrections']) == 1


def test_correcting_needs_a_signed_in_owner():
    app = FastAPI()
    app.include_router(pub.router)
    r = TestClient(app).post('/publication/citations/projects/p/items/k/correct', json={
        'fields': {'title': 'T'}, 'reason': 'Synthetic test reason.', 'expectedProjectRevision': 1})
    assert r.status_code == 401
