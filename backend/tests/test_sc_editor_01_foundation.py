"""SC-EDITOR-01: immutable authoring exchange, security and integration tests.

The package is not a publication approval or cross-application write grant.
Source provenance and ownership remain enforced by Publication Studio's _saved.
"""
from copy import deepcopy
import hashlib
import importlib
import json
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi import HTTPException

pub = importlib.import_module("app.reporting_publication")


def saved():
    markdown = '# Wexford\n\nEvidence [@Beerling2020].\n\n![Basalt](asset:fig1)'
    return {
        'documentId': 'publication-' + 'a' * 32, 'revision': 3, 'projectRevision': 14,
        'createdAt': '2026-11-15T08:00:00+00:00', 'title': 'Wexford demonstration',
        'publicationType': 'working-paper', 'markdown': markdown,
        'markdownSHA256': hashlib.sha256(markdown.encode()).hexdigest(),
        'source': {'artifactId':'source1','sha256':'1'*64},
        'figureSources': [{'artifactId':'fig1','sha256':'2'*64}],
        'citations': {'schema':'sc-cite-snapshot/1.0', 'items':[{'key':'Beerling2020'}]},
        'scientificStatus': 'unreviewed', 'rightsStatus': 'not-redistribution-approved',
        'computationsExecuted': False, 'sourceBytesModified': False,
    }


def test_immutable_package_preserves_scientific_identity_and_handoff_warning():
    original = saved()
    before = deepcopy(original)
    result = pub.authoring_package('private-project', original)
    assert result['schema'] == 'sc-unified-scientific-authoring/1.0'
    assert result['authority'] == 'workspace-scientific-publication'
    assert result['projectId'] == 'private-project'
    assert result['documentId'] == original['documentId']
    assert result['revision'] == 3
    assert result['manuscript']['body'] == original['markdown']
    assert result['manuscript']['sha256'] == original['markdownSHA256']
    assert result['figureSources'] == original['figureSources']
    assert result['citationSnapshot'] == original['citations']
    assert result['source'] == original['source']
    assert result['handoffStatus'] == 'private-draft-not-published'
    assert result['approval'] is None
    assert result['rightsStatus'] == 'not-redistribution-approved'
    assert '/research-revision?' in result['links']['researchDraft']
    assert 'revision=3' in result['links']['docx']
    assert original == before, 'Producing an authoring package may not mutate a saved revision'


def test_manuscript_hash_is_checked_before_package_is_issued():
    damaged = saved()
    damaged['markdown'] += '\nCorrupted'
    with pytest.raises(HTTPException) as exc:
        pub.authoring_package('private-project', damaged)
    assert exc.value.status_code == 409


def test_package_path_percent_encodes_project_and_document_identifiers():
    doc=saved()
    result=pub.authoring_package('project #1/alpha',doc)
    assert 'project%20%231%2Falpha' in result['links']['html']
    assert '/documents/'+doc['documentId'] in result['links']['html']


def test_route_checks_identity_before_any_project_access():
    with patch.object(pub, '_subject', side_effect=HTTPException(401, 'Authentication required')), \
         patch.object(pub, '_saved') as load:
        with pytest.raises(HTTPException) as exc:
            pub.authoring_package_route('p','doc',object(),revision=2)
        assert exc.value.status_code == 401
        load.assert_not_called()


def test_route_read_is_owner_and_revision_scoped():
    class DummySession:
        def __enter__(self): return self
        def __exit__(self, *args): return False
    doc = saved()
    def load(db, owner, project, document, revision):
        assert (owner,project,document,revision) == ('synthetic-owner','owned','publication-abc',3)
        return None, doc
    with patch.object(pub, '_subject', return_value='synthetic-owner'), \
         patch.object(pub, 'session_scope', return_value=DummySession()), \
         patch.object(pub, '_saved', side_effect=load):
        response=pub.authoring_package_route('owned','publication-abc',object(),revision=3)
        result=json.loads(response.body)
    assert result['revision'] == 3
    assert response.headers['cache-control'] == 'private, no-store'
    assert response.headers['x-content-type-options'] == 'nosniff'


def test_browser_controls_are_save_gated_and_do_not_claim_publication():
    here=Path(pub.__file__).parent
    html=(here/'reporting_publication_ui.html').read_text()
    js=(here/'reporting_publication_ui.js').read_text()
    assert 'id="authoringPackage" disabled' in html
    assert 'id="researchDraft" disabled' in html
    assert "authoringPackage','researchDraft" in js
    assert "NOT submitted or published" in js
    assert "if(!state.saved||state.dirty||!state.documentId)" in js


def test_machine_readable_authoring_schema_matches_issued_package():
    schema_path = Path(__file__).resolve().parents[2] / 'schemas' / 'sc-unified-scientific-authoring-v1.schema.json'
    schema = json.loads(schema_path.read_text())
    package = pub.authoring_package('p', saved())
    assert schema['properties']['schema']['const'] == pub.AUTHORING_SCHEMA
    assert set(schema['required']) == set(package)
    assert schema['properties']['manuscript']['properties']['format']['const'] == 'markdown'
    assert schema['properties']['approval']['type'] == 'null'
    assert schema['properties']['handoffStatus']['const'] == 'private-draft-not-published'
