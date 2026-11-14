"""SC-CITE-01 Citation Studio: the recovered ERW v1.3.2 Harvard output is preserved exactly for the existing Wexford
citations, records are imported (never retyped) with provenance, each revision freezes its own bibliography, and
HTML, PDF and DOCX exports carry it. Offline: fixtures and fakes only."""
import importlib
import io
import json
from pathlib import Path
import types
from unittest.mock import patch

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

cite = importlib.import_module('app.citation_studio')
pub = importlib.import_module('app.reporting_publication')

FIXTURE = json.loads((Path(__file__).parent / 'fixtures' / 'sc_cite01_wexford_erw_v132_citations.json').read_text())
RECORDS = FIXTURE['records']

# Crossref-shaped verified metadata as in a research package's references-verified.json (public metadata).
VERIFIED = [{
    'doi': '10.1038/s41586-020-2448-9',
    'title': 'Potential for large-scale CO2 removal via enhanced rock weathering with croplands',
    'authors': [{'given': 'David J.', 'family': 'Beerling'}, {'given': 'Euripides P.', 'family': 'Kantzas'},
                {'given': 'Mark R.', 'family': 'Lomas'}],
    'journal': ['Nature'], 'volume': '583', 'page': '242-248', 'published': {'date-parts': [[2020, 7, 8]]},
    'metadata_url': 'https://api.crossref.org/works/10.1038%2Fs41586-020-2448-9',
    'verified_utc': '2026-10-22T21:32:53+00:00', 'publisher_url': 'https://doi.org/10.1038/s41586-020-2448-9',
}, {
    'doi': '10.3389/fclim.2024.1345224',
    'title': 'A review of measurement for quantification of carbon dioxide removal by enhanced weathering in soil',
    'authors': [{'given': 'Matthew O.', 'family': 'Clarkson'}, {'given': 'Christina S.', 'family': 'Larkin'}],
    'journal': ['Frontiers in Climate'], 'volume': '6', 'page': None, 'article_number': '1345224',
    'published': {'date-parts': [[2024]]}, 'metadata_url': 'https://api.crossref.org/works/x', 'verified_utc': 't',
}]
RIS = """TY  - JOUR
TI  - Enhanced weathering in the US Corn Belt delivers carbon removal with agronomic benefits
DO  - 10.1073/pnas.2319436121
AU  - Beerling, David J.
AU  - Epihov, Dimitar Z.
JO  - Proceedings of the National Academy of Sciences
VL  - 121
PY  - 2024
ER  -
"""


# --- 1. Existing Wexford citations are preserved exactly -------------------------------------------------------

@pytest.mark.parametrize('record', RECORDS, ids=lambda r: r['fields']['title'][:40])
def test_the_recovered_v132_formatter_reproduces_every_stored_wexford_citation(record):
    out = cite.harvard_erw_v132(record['fields'])
    assert out['reference'] == record['formattedCitation']['reference']
    assert out['inText'] == record['formattedCitation']['inText']
    assert out['warnings'] == record['formattedCitation']['warnings']


def test_unreviewed_or_incomplete_metadata_never_produces_a_reference():
    fields = dict(RECORDS[0]['fields'], verifiedByResearcher=False)
    assert cite.harvard_erw_v132(fields)['reference'] is None
    assert cite.harvard_erw_v132(dict(RECORDS[0]['fields'], title=''))['warnings'] == ['Missing required fields: title']
    with pytest.raises(ValueError):
        cite.harvard_erw_v132(dict(RECORDS[0]['fields'], doi='not-a-doi'))


def test_imported_v132_records_render_byte_identically_in_the_legacy_style():
    current, report = cite.add_items(cite.collection({}), cite.parse_reference_file('erw.json', json.dumps(RECORDS).encode()), {})
    # Record 2 repeats record 1's DOI (the superseded snapshot), so it is reused, never duplicated.
    assert len(report['added']) == 5 and len(report['reused']) == 1
    by_title = {x['title']: x for x in current['items']}
    for record in (RECORDS[0], RECORDS[2], RECORDS[3], RECORDS[4], RECORDS[5]):
        item = next(v for k, v in by_title.items() if k == record['fields']['title'] and v['doi'] == record['fields']['doi'])
        assert cite.reference(item, 'harvard-erw-v132') == record['formattedCitation']['reference']
        assert cite.in_text(item, 'harvard-erw-v132') == record['formattedCitation']['inText']


def test_a_manuscript_with_its_own_reference_list_is_exported_unchanged():
    md = '# Report\n\nText [3].\n\n## References\n\n1. Beerling DJ et al. (2020). Nature 583:242–248.'
    assert cite.resolve(md, None) == md
    assert cite.resolve(md, cite.freeze(md, {'items': []}, 'harvard')) == md
    html = pub._as_html({'title': 'R', 'markdown': md, 'revision': 1, 'markdownSHA256': 'x'})
    assert b'1. Beerling DJ et al. (2020). Nature 583:242' in html


# --- 2. Styles, in-text citations and bibliographies -------------------------------------------------------------

def _wexford_collection():
    current, _ = cite.add_items(cite.collection({}), cite.from_crossref_verified(VERIFIED),
                                {'sourceArtifactId': 'a1', 'sourceSha256': 'f' * 64})
    return current


def test_harvard_and_apa_formatting_of_imported_records():
    beerling, clarkson = _wexford_collection()['items']
    assert cite.in_text(beerling) == '(Beerling et al., 2020)'
    assert cite.in_text(beerling, 'harvard', 'p. 244') == '(Beerling et al., 2020, p. 244)'
    assert cite.in_text(clarkson) == '(Clarkson and Larkin, 2024)'
    assert cite.in_text(clarkson, 'apa') == '(Clarkson & Larkin, 2024)'
    assert cite.reference(beerling) == ("Beerling, D.J., Kantzas, E.P. and Lomas, M.R. (2020) 'Potential for large-scale "
                                        "CO2 removal via enhanced rock weathering with croplands', *Nature*, 583, pp. 242-248. "
                                        "https://doi.org/10.1038/s41586-020-2448-9")
    assert cite.reference(clarkson) == ("Clarkson, M.O. and Larkin, C.S. (2024) 'A review of measurement for quantification "
                                        "of carbon dioxide removal by enhanced weathering in soil', *Frontiers in Climate*, 6, "
                                        "1345224. https://doi.org/10.3389/fclim.2024.1345224")
    assert cite.reference(beerling, 'apa').startswith('Beerling, D. J., Kantzas, E. P., & Lomas, M. R. (2020). Potential')


def test_ris_and_verified_json_exports_of_one_work_give_the_same_key_and_reference():
    ris = [cite.make_item(f, p) for f, p in cite.parse_reference_file('references.ris', RIS.encode())]
    verified = [cite.make_item(f, p) for f, p in cite.parse_reference_file('references-verified.json', json.dumps([{
        'doi': '10.1073/pnas.2319436121',
        'title': 'Enhanced weathering in the US Corn Belt delivers carbon removal with agronomic benefits',
        'authors': [{'given': 'David J.', 'family': 'Beerling'}, {'given': 'Dimitar Z.', 'family': 'Epihov'}],
        'journal': ['Proceedings of the National Academy of Sciences'], 'volume': '121',
        'published': {'date-parts': [[2024]]}, 'metadata_url': 'https://api.crossref.org/works/y', 'verified_utc': 't',
    }]).encode())]
    assert ris[0]['key'] == verified[0]['key'] == 'beerling2024enhanced'
    assert cite.reference(ris[0]) == cite.reference(verified[0])
    assert cite.in_text(ris[0], 'harvard', None) == '(Beerling and Epihov, 2024)'


def test_markers_resolve_to_in_text_citations_and_a_sorted_reference_list():
    current = _wexford_collection()
    b, c = (x['key'] for x in current['items'])
    md = f'Field trials vary [@{c}; @{b}, p. 244]. Potential is large [@{b}]. Unknown [@missing2020x].'
    frozen = cite.freeze(md, current, 'harvard')
    assert [x['key'] for x in frozen['items']] == [c, b] and frozen['unresolved'] == ['missing2020x']
    out = cite.resolve(md, frozen)
    assert '(Clarkson and Larkin, 2024; Beerling et al., 2020, p. 244)' in out
    assert 'Potential is large (Beerling et al., 2020).' in out
    assert '[@missing2020x]' in out  # unresolved citations stay visible, never silently dropped
    refs = out.split('## References\n\n')[1].strip().split('\n\n')
    assert refs[0].startswith('Beerling') and refs[1].startswith('Clarkson')


# --- 3. Provenance, de-duplication and imports --------------------------------------------------------------------

def test_imports_keep_provenance_and_reuse_identical_records():
    current = _wexford_collection()
    item = current['items'][0]
    assert item['provenance'] == {'sourceArtifactId': 'a1', 'sourceSha256': 'f' * 64, 'metadataAuthority': 'crossref',
                                  'metadataUrl': VERIFIED[0]['metadata_url'], 'metadataVerifiedAt': VERIFIED[0]['verified_utc']}
    again, report = cite.add_items(current, cite.from_crossref_verified(VERIFIED), {})
    assert report['added'] == [] and len(report['reused']) == 2 and again == current
    ris, report = cite.add_items(current, cite.parse_reference_file('references.ris', RIS.encode()), {})
    assert len(report['added']) == 1 and ris['items'][-1]['doi'] == '10.1073/pnas.2319436121'
    assert ris['items'][-1]['authors'][0] == {'family': 'Beerling', 'given': 'David J.'}


def test_library_records_are_cited_without_inventing_authors():
    record = {'identity': {'record_id': 'wordpress:1:post:15670', 'revision': 1, 'content_hash': 'c' * 64},
              'descriptive': {'title': 'Carbon Accumulation and Emissions Pathways'},
              'publication': {'published_at': '2026-06-16T08:56:50Z'},
              'source': {'source_key': 'wordpress-main', 'canonical_url': 'https://sustainablecatalyst.com/carbon/'}}
    fields, provenance = cite.library_item(record)
    item = cite.make_item(fields, provenance)
    assert cite.reference(item) == ('Sustainable Catalyst (2026) *Carbon Accumulation and Emissions Pathways*. '
                                    'Available at: https://sustainablecatalyst.com/carbon/.')
    assert item['provenance']['libraryRecordId'] == 'wordpress:1:post:15670'
    assert item['provenance']['libraryContentSha256'] == 'c' * 64
    other = cite.library_item({**record, 'source': {'source_key': 'external', 'canonical_url': 'https://x.org/a'}})
    assert other[0]['authors'] == [] and other[1]['authorStatus'] == 'missing-review-required'


# --- 4. Revisions freeze their bibliography; every export carries it -----------------------------------------------

def _save(markdown, package, style='harvard'):
    row = types.SimpleNamespace(revision=3, title='Wexford', package=package)
    captured = {}

    def store(db, owner, payload):
        captured.update(payload.data)
        return types.SimpleNamespace(revision=4), False

    class FakeDB:
        def __enter__(self): return self
        def __exit__(self, *a): pass

    payload = types.SimpleNamespace(model_validate=staticmethod(lambda d: types.SimpleNamespace(data=d)))
    with patch.object(pub, 'session_scope', return_value=FakeDB()), patch.object(pub, '_subject', return_value='owner'), \
            patch.object(pub, '_write', return_value=None), patch.object(pub, '_locked_project', return_value=row), \
            patch.object(pub, '_source_meta', return_value=None), patch.object(pub, '_verify_figures', return_value=[]), \
            patch.object(pub, 'ProjectStoreRequest', payload), \
            patch.object(pub.repository, 'store_project', store, create=True), \
            patch.object(pub.repository, 'project_metadata', lambda o: {'revision': o.revision}, create=True):
        r = pub.save_document('wexford', pub.Save(title='Wexford', markdown=markdown, expectedProjectRevision=3,
                                                 citationStyle=style), object())
    assert r.status_code == 201
    return captured['project']['objects'][-1]['publication']


def test_a_saved_revision_keeps_its_bibliography_and_exports_it_in_all_formats():
    current = _wexford_collection()
    key = current['items'][0]['key']
    package = {'project': {'objects': [{'id': 'citation-collection', 'type': 'citation-collection', 'collection': current}]}}
    saved = _save(f'# Scientific assessment\n\nLarge-scale potential has been modelled [@{key}].', package)
    assert saved['citations']['style'] == 'harvard' and saved['citations']['items'][0]['key'] == key
    # The collection can change later; the revision's frozen bibliography does not.
    package['project']['objects'][0]['collection'] = {'schema': cite.COLLECTION_SCHEMA, 'items': []}
    doc = {**saved, 'markdownSHA256': 'x'}
    html = pub._as_html(doc).decode()
    assert '(Beerling et al., 2020)' in html and '<h2>References</h2>' in html and 'https://doi.org/10.1038/s41586-020-2448-9' in html
    from docx import Document
    text = '\n'.join(p.text for p in Document(io.BytesIO(pub._docx(doc, {}))).paragraphs)
    assert '(Beerling et al., 2020)' in text and "Beerling, D.J., Kantzas, E.P. and Lomas, M.R. (2020)" in text
    pdf = pub._pdf(doc, {})
    assert pdf.startswith(b'%PDF') and len(pdf) > 1500


def test_saving_without_citations_records_none_and_unknown_styles_are_refused():
    assert _save('# Plain\n\nNo citations here.', {'project': {'objects': []}})['citations'] is None
    with pytest.raises(Exception):
        pub.Save(title='x', markdown='y', expectedProjectRevision=1, citationStyle='mla')


# --- 5. Routes: owner sessions only, project-revision gate, Library verification ------------------------------------

def _client():
    app = FastAPI()
    app.include_router(pub.router)
    return TestClient(app)


def test_citation_routes_refuse_anonymous_requests():
    client = _client()
    assert client.get('/publication/citations/projects/p').status_code == 401
    assert client.get('/publication/citations/library/search?q=carbon').status_code == 401
    assert client.post('/publication/citations/projects/p/bibliography', json={}).status_code == 401


def test_importing_from_a_project_file_is_owner_scoped_and_revision_gated():
    row = types.SimpleNamespace(revision=3, title='Wexford', project_id='wexford', package={'project': {'objects': []}})
    stored = {}

    def store(db, owner, r, project, operation):
        stored['project'] = project
        return types.SimpleNamespace(revision=4, title='Wexford', project_id='wexford', package={'project': project})

    class FakeDB:
        def __enter__(self): return self
        def __exit__(self, *a): pass

    meta = {'artifactId': 'refs', 'filename': 'wexford-erw-2026/research-package/references-verified.json', 'sha256': 'e' * 64}
    deps = dict(subject=lambda r: 'owner', write=lambda r: None, project=lambda db, o, p: row,
                locked_project=lambda db, o, p: row, original_asset=lambda db, o, p, a: (meta, json.dumps(VERIFIED).encode()),
                store=store, session=FakeDB, headers={}, library_record=None, library_search=None)
    app = FastAPI()
    app.include_router(cite.build_router(deps))
    client = TestClient(app)
    stale = client.post('/citations/projects/wexford/import-source', json={'sourceArtifactId': 'refs', 'expectedProjectRevision': 2})
    assert stale.status_code == 409 and 'project' not in stored
    r = client.post('/citations/projects/wexford/import-source', json={'sourceArtifactId': 'refs', 'expectedProjectRevision': 3})
    assert r.status_code == 201, r.text
    body = r.json()
    assert body['projectRevision'] == 4 and len(body['import']['added']) == 2
    assert body['items'][0]['provenance']['sourceSha256'] == 'e' * 64
    assert body['items'][0]['formatted']['harvard']['inText'] == '(Beerling et al., 2020)'
    collection = [o for o in stored['project']['objects'] if o['type'] == 'citation-collection']
    assert len(collection) == 1 and len(collection[0]['collection']['items']) == 2


def test_library_imports_require_a_verified_public_record():
    def unavailable(record_id):
        raise HTTPException(404, 'Public Library record unavailable')
    row = types.SimpleNamespace(revision=1, title='W', project_id='w', package={'project': {'objects': []}})

    class FakeDB:
        def __enter__(self): return self
        def __exit__(self, *a): pass
    deps = dict(subject=lambda r: 'owner', write=lambda r: None, project=lambda db, o, p: row,
                locked_project=lambda db, o, p: row, original_asset=None, store=None, session=FakeDB, headers={},
                library_record=unavailable, library_search=None)
    app = FastAPI()
    app.include_router(cite.build_router(deps))
    r = TestClient(app).post('/citations/projects/w/import-library', json={'recordId': 'wordpress:1:post:1', 'expectedProjectRevision': 1})
    assert r.status_code == 404
