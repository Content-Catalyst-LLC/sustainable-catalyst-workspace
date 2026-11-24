"""UCD-RESEARCH-01: an exact Reporting Studio revision stated as a Research editorial revision payload."""
import types
from unittest.mock import patch

import pytest
from fastapi import HTTPException

from app import reporting_publication as pub
from tests.test_sc_cite01_citation_studio import _client, _save, _wexford_collection


def _saved():
    current = _wexford_collection()
    b, c = (x['key'] for x in current['items'])
    package = {'project': {'objects': [{'id': 'citation-collection', 'type': 'citation-collection', 'collection': current}]}}
    md = (f'# Wexford\n\n> Working draft.\n\n## Scientific assessment\n\nPotential is large [@{b}, p. 244].\n\n'
          f'![Mineral supply map](asset:figure-private-1)\n\n### Detail\n\nMeasurement varies [@{c}; @{b}]. '
          f'Unknown [@missing2020x].\n\n## Policy\n\nNo citations.')
    return {**_save(md, package), 'documentId': 'publication-' + 'a' * 32, 'markdownSHA256': 'f' * 64}


def test_a_saved_revision_becomes_a_pinned_research_revision_payload():
    saved = _saved()
    out = pub.research_revision('wexford-project', saved, 'report')
    assert [s['heading'] for s in out['sections']] == ['Overview', 'Scientific assessment', 'Policy']
    assert out['sections'][0]['body'] == '> Working draft.'
    body = out['sections'][1]['body']
    b, c = 'beerling2020potential', 'clarkson2024review'
    # Markers stay editable in the text; the bibliography says exactly what each renders as.
    assert f'[@{b}, p. 244]' in body and f'[@{c}; @{b}]' in body and '(Beerling' not in body
    assert '### Detail' in body and '[@missing2020x]' in body and '## References' not in body
    assert out['publication']['bibliography']['markers'] == {
        f'[@{b}, p. 244]': '(Beerling et al., 2020, p. 244)', f'[@{c}; @{b}]': '(Clarkson and Larkin, 2024; Beerling et al., 2020)'}
    assert 'figure-private-1' not in str(out) and '*[Figure: Mineral supply map. Not yet released to Research.]*' in body
    origin = out['publication']['derivedFrom'][0]
    assert origin == {'relation': 'derived-from', 'kind': 'workspace-studio-revision',
                      'workspaceProjectId': 'wexford-project', 'documentId': 'publication-' + 'a' * 32,
                      'revision': saved['revision'], 'documentSha256': 'f' * 64,
                      'label': f"Reporting Studio revision {saved['revision']}"}
    bib = out['publication']['bibliography']
    assert bib['schema'] == 'sc-publication-bibliography/1.0' and bib['style'] == 'harvard'
    assert [x['key'] for x in bib['items']] == ['beerling2020potential', 'clarkson2024review']
    assert bib['items'][0]['reference'].startswith('Beerling, D.J., Kantzas, E.P. and Lomas, M.R. (2020)')
    assert 'provenance' not in str(bib) and bib['unresolved'] == ['missing2020x']
    assert out['references'] == [] and out['notCarried']['figures'] == 1
    assert out['notCarried']['unresolvedCitations'] == ['missing2020x']


def test_a_manuscript_without_citations_carries_no_bibliography():
    saved = {**_save('# Plain\n\nText only.', {'project': {'objects': []}}), 'documentId': 'publication-' + 'b' * 32,
             'markdownSHA256': 'e' * 64}
    out = pub.research_revision('p', saved, 'policy-brief')
    assert 'bibliography' not in out['publication'] and out['sections'] == [{'heading': 'Plain', 'body': 'Text only.'}]


@pytest.mark.parametrize('kind', ['original-submission', 'essay', ''])
def test_a_studio_manuscript_is_never_stated_as_an_original_submission(kind):
    with pytest.raises(HTTPException) as err:
        pub.research_revision('p', _saved(), kind)
    assert err.value.status_code == 422


def test_section_limits_are_reported_not_truncated():
    md = '\n\n'.join(f'## S{i}\n\nx' for i in range(41))
    with pytest.raises(HTTPException, match='at most 40'):
        pub.research_sections(md, 'T')
    with pytest.raises(HTTPException, match='no text'):
        pub.research_sections('# T', 'T')


def test_the_bridge_route_is_owner_scoped_and_reads_the_exact_revision():
    assert _client().get('/publication/projects/p/documents/d/research-revision?revision=1&publicationType=report').status_code == 401
    saved = _saved()
    calls = []

    class FakeDB:
        def __enter__(self): return self
        def __exit__(self, *a): pass

    def fake_saved(db, owner, project_id, document_id, rev=None):
        calls.append((owner, project_id, document_id, rev))
        return types.SimpleNamespace(revision=4), saved

    with patch.object(pub, 'session_scope', return_value=FakeDB()), patch.object(pub, '_subject', return_value='owner'), \
            patch.object(pub, '_saved', fake_saved):
        r = _client().get('/publication/projects/wexford/documents/d/research-revision?revision=1&publicationType=report')
    assert r.status_code == 200 and r.json()['publication']['type'] == 'report'
    assert calls == [('owner', 'wexford', 'd', 1)]


# --- the same snapshot service for Research editorial and the Research Console -------------------------------------

def test_editor_snapshots_use_the_project_collection_and_the_one_formatter():
    from app import citation_studio as cite
    current = _wexford_collection()
    b, c = (x['key'] for x in current['items'])
    sections = [{'heading': 'A', 'body': f'Potential [@{b}].'}, {'heading': 'B', 'body': f'Both [@{c}; @{b}, p. 3].'}]
    snap = cite.snapshot(sections, current, 'apa')
    assert snap['style'] == 'apa' and [x['key'] for x in snap['items']] == [b, c]
    assert snap['markers'] == {f'[@{b}]': '(Beerling et al., 2020)', f'[@{c}; @{b}, p. 3]': '(Clarkson & Larkin, 2024; Beerling et al., 2020, p. 3)'}
    assert snap['items'][0]['reference'] == cite.reference(current['items'][0], 'apa')
    # Identical to what a Studio revision freezes for the same text: one implementation.
    frozen = cite.freeze('\n\n'.join(x['body'] for x in sections), current, 'apa')
    assert snap == cite.bibliography_record(frozen, [x['body'] for x in sections])
    assert cite.snapshot([{'heading': 'x', 'body': 'No citations.'}], current, 'harvard') is None


def test_library_provenance_travels_with_snapshot_items():
    from app import citation_studio as cite
    record = {'identity': {'record_id': 'wordpress:1:post:15670', 'revision': 1, 'content_hash': 'c' * 64},
              'descriptive': {'title': 'Carbon Accumulation and Emissions Pathways'},
              'publication': {'published_at': '2026-06-16T08:56:50Z'},
              'source': {'source_key': 'wordpress-main', 'canonical_url': 'https://sustainablecatalyst.com/carbon/'}}
    current, _ = cite.add_items({'schema': cite.COLLECTION_SCHEMA, 'items': []}, [cite.library_item(record)], {})
    key = current['items'][0]['key']
    snap = cite.snapshot([{'heading': 'x', 'body': f'See [@{key}].'}], current, 'harvard')
    assert snap['items'][0]['library'] == {'recordId': 'wordpress:1:post:15670', 'revision': '1', 'contentSha256': 'c' * 64}
    assert _wexford_collection()['items'][0].get('provenance', {}).get('metadataAuthority') != 'knowledge-library'


def test_the_snapshot_route_is_owner_scoped_and_read_only():
    assert _client().post('/publication/citations/projects/p/snapshot', json={'sections': [{'body': 'x'}]}).status_code == 401
    current = _wexford_collection()
    row = types.SimpleNamespace(revision=3, package={'project': {'objects': [
        {'id': 'citation-collection', 'type': 'citation-collection', 'collection': current}]}})
    seen = []

    class FakeDB:
        def __enter__(self): return self
        def __exit__(self, *a): pass

    def no_write(*a):
        raise AssertionError('the snapshot must not write')

    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from app import citation_studio as cite
    deps = dict(subject=lambda r: 'owner', write=no_write, project=lambda db, o, p: seen.append((o, p)) or row,
                locked_project=no_write, original_asset=no_write, store=no_write, session=FakeDB, headers={},
                library_record=None, library_search=None)
    app = FastAPI()
    app.include_router(cite.build_router(deps))
    client = TestClient(app)
    r = client.post('/citations/projects/wexford/snapshot',
                    json={'sections': [{'heading': 'A', 'body': '[@beerling2020potential]'}], 'style': 'harvard'})
    bad = client.post('/citations/projects/wexford/snapshot', json={'sections': [{'body': 'x'}], 'style': 'mla'})
    assert r.status_code == 200 and r.json()['bibliography']['markers'] == {'[@beerling2020potential]': '(Beerling et al., 2020)'}
    assert bad.status_code == 422 and seen[0] == ('owner', 'wexford')
