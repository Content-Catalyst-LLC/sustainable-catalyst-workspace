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
    assert '(Beerling et al., 2020, p. 244)' in body and '(Clarkson and Larkin, 2024; Beerling et al., 2020)' in body
    assert '### Detail' in body and '[@missing2020x]' in body and '## References' not in body
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
