"""SC-RESEARCH-PROJECT-01: New Research Project and the per-project workspace (synthetic projects only).

Runs the real Reporting Studio router, project registry, artifact store and private research store tables on an
isolated SQLite database with foreign keys enforced. Creation must be idempotent and recoverable, every route
owner-scoped, existing projects untouched, and nothing published.
"""
import base64
import hashlib
import io
import json
import zipfile

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app import db as app_db, repository, wxr_private_projects
from app import research_projects as rp
from app.config import get_settings
from app.models import (ArtifactHead, ArtifactRevision, Base, DomainMutationReceipt, NotebookHead, ProjectHead,
                        ProjectRevision)
from app.schemas import ProjectStoreRequest

ORIGIN = {'Origin': 'https://workspace.sustainablecatalyst.com'}
KEY = '0b7c6a52-6f0e-4c51-9a55-1f1f8a3e2c11'
PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==')
W = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'


@compiles(JSONB, 'sqlite')
def _jsonb(_type, _compiler, **_kw):
    return 'JSON'


STORE_DDL = (
    'CREATE TABLE workspace_private_research_projects (user_key TEXT NOT NULL, project_id TEXT NOT NULL, '
    'title TEXT NOT NULL, created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (user_key, project_id), '
    'FOREIGN KEY (user_key, project_id) REFERENCES workspace_project_heads (user_key, project_id) ON DELETE RESTRICT)',
    'CREATE TABLE workspace_private_research_branches (user_key TEXT NOT NULL, project_id TEXT NOT NULL, '
    'branch_id TEXT NOT NULL, name TEXT NOT NULL, created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, '
    'PRIMARY KEY (user_key, project_id, branch_id))',
    'CREATE TABLE workspace_private_research_artifacts (user_key TEXT NOT NULL, project_id TEXT NOT NULL, '
    'branch_id TEXT NOT NULL, artifact_id TEXT NOT NULL, filename TEXT NOT NULL, media_type TEXT NOT NULL, '
    'sha256 TEXT NOT NULL, byte_count INTEGER NOT NULL, evidence_status TEXT NOT NULL, '
    'created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (user_key, artifact_id))',
)


def docx(*paragraphs):
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w') as z:
        z.writestr('[Content_Types].xml', '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
        body = ''.join(f'<w:p><w:r><w:t>{t}</w:t></w:r></w:p>' for t in paragraphs)
        z.writestr('word/document.xml', f'<w:document {W}><w:body>{body}</w:body></w:document>')
    return out.getvalue()


def b64(raw):
    return base64.b64encode(raw).decode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


@pytest.fixture()
def env(monkeypatch, tmp_path):
    engine = create_engine('sqlite://', poolclass=StaticPool, connect_args={'check_same_thread': False})
    event.listen(engine, 'connect', lambda conn, _r: conn.execute('PRAGMA foreign_keys=ON'))
    Base.metadata.create_all(engine, tables=[t.__table__ for t in (
        ProjectHead, ProjectRevision, DomainMutationReceipt, ArtifactHead, ArtifactRevision, NotebookHead)])
    with engine.begin() as conn:
        for ddl in STORE_DDL:
            conn.execute(text(ddl))
    factory = sessionmaker(bind=engine, expire_on_commit=False, class_=Session)
    monkeypatch.setattr(app_db, 'get_session_factory', lambda: factory)
    monkeypatch.setenv('SC_WORKSPACE_OBJECT_STORAGE_ROOT', str(tmp_path / 'objects'))
    monkeypatch.setenv('SC_WORKSPACE_REPORTING_STUDIO_ENABLED', '1')
    get_settings.cache_clear()
    monkeypatch.setattr(wxr_private_projects, 'session_payload_from_request',
                        lambda request: {'sub': request.headers['x-test-sub']} if request.headers.get('x-test-sub') else None)
    from app.research_reporting import router
    app = FastAPI()
    app.include_router(router)
    yield {'client': TestClient(app, raise_server_exceptions=False), 'factory': factory, 'root': tmp_path / 'objects'}
    get_settings.cache_clear()


def call(env, method, path, who='owner', write=True, **kw):
    headers = {'x-test-sub': who} if who else {}
    if write and method != 'GET':
        headers.update(ORIGIN)
    return env['client'].request(method, '/v1/private-research/reporting-studio/research-projects' + path,
                                 headers=headers, **kw)


def create(env, who='owner', key=KEY, title='Soil carbon in coastal wetlands', area=None):
    return call(env, 'POST', '/api/projects', who, json={
        'creationKey': key, 'title': title, 'area': area or {'slug': 'climate-land-carbon'},
        'researchQuestion': 'How much carbon do restored wetlands store?', 'description': 'Synthetic test project.'})


def existing_project(env, project_id='existing-synthetic', who='owner', title='Existing synthetic project'):
    """A project made elsewhere (for example the Notebook Desk): no research profile."""
    with env['factory']() as db:
        repository.store_project(db, who, ProjectStoreRequest.model_validate({
            'schema': 'sc-workspace-cloud-backup/1.0', 'sourceProjectId': project_id, 'projectTitle': title,
            'project': {'schema': 'sc-workspace-project/20.0', 'id': project_id, 'title': title, 'objects': []}}))
        db.execute(text('INSERT INTO workspace_private_research_projects (user_key, project_id, title) VALUES (:u, :p, :t)'),
                   {'u': who, 'p': project_id, 't': title})
        db.commit()


def legacy_file(env, project_id, name, raw, who='owner'):
    path = env['root'] / 'private-research' / sha(raw)[:2]
    path.mkdir(parents=True, exist_ok=True)
    (path / sha(raw)).write_bytes(raw)
    with env['factory']() as db:
        db.execute(text('INSERT INTO workspace_private_research_artifacts VALUES (:u, :p, :b, :a, :f, :m, :h, :s, :e, CURRENT_TIMESTAMP)'),
                   {'u': who, 'p': project_id, 'b': 'registers', 'a': 'legacy-' + sha(raw)[:8], 'f': name,
                    'm': 'application/octet-stream', 'h': sha(raw), 's': len(raw), 'e': 'unreviewed'})
        db.commit()


def head(env, project_id, who='owner'):
    with env['factory']() as db:
        return repository.get_project(db, who, project_id)


def test_new_project_gets_identity_profile_and_private_workspace(env):
    r = create(env)
    assert r.status_code == 201, r.text
    pid = r.json()['project']['projectId']
    assert pid == rp.project_id_for('owner', KEY, 'Soil carbon in coastal wetlands')
    assert pid.startswith('soil-carbon-in-coastal-wetlands-')
    assert r.json()['dashboardUrl'].endswith('/research-projects/' + pid)
    row = head(env, pid)
    profile = rp.profile_of(row.package)
    assert row.revision == 1 and row.storage_mode == 'sync-head'
    assert profile['researchArea'] == {'slug': 'climate-land-carbon', 'title': 'Climate, Land & Carbon', 'source': 'institutional'}
    assert profile['visibility'] == 'private' and profile['createdVia'] == 'SC-RESEARCH-PROJECT-01'
    d = call(env, 'GET', '/api/projects/' + pid).json()
    assert d['project']['kind'] == 'research-project' and d['project']['privateResearchStore'] == 'attached'
    assert set(d) >= {'overview', 'documents', 'library', 'analysis', 'figures', 'publications'}
    assert d['overview']['researchQuestion'].startswith('How much carbon')
    assert d['analysis']['deskUrl'] == '/v1/desk/notebooks?project=' + pid
    assert d['publications']['outputs'] == [] and 'not independently reviewed' in d['publications']['disclosure']
    page = call(env, 'GET', '/' + pid)
    assert page.status_code == 200 and "script-src 'sha256-" in page.headers['content-security-policy']
    assert page.headers['cache-control'] == 'private, no-store'
    hub = call(env, 'GET', '')
    assert 'New Research Project' in hub.text and 'Project ID' not in hub.text


def test_creation_is_idempotent_per_creation_key(env):
    first = create(env).json()['project']
    again = create(env)
    assert again.status_code == 200 and again.json()['project']['projectId'] == first['projectId']
    assert head(env, first['projectId']).revision == 1
    other = create(env, key='7d1f3c1e-2a44-4b8e-8f0a-6c5d4e3b2a10')
    assert other.status_code == 201 and other.json()['project']['projectId'] != first['projectId']
    assert len(call(env, 'GET', '/api/projects').json()['projects']) == 2


def test_interrupted_creation_is_recovered_without_orphans_or_duplicates(env, monkeypatch):
    real = rp.ensure_attached

    def fail(*_a, **_k):
        raise RuntimeError('simulated failure after the project was stored')
    monkeypatch.setattr(rp, 'ensure_attached', fail)
    assert create(env).status_code == 500
    listed = call(env, 'GET', '/api/projects').json()['projects']
    assert len(listed) == 1 and listed[0]['kind'] == 'research-project'
    assert listed[0]['privateResearchStore'] == 'not-attached'  # usable, reported, never silent
    monkeypatch.setattr(rp, 'ensure_attached', real)
    again = create(env)
    assert again.status_code == 200
    listed = call(env, 'GET', '/api/projects').json()['projects']
    assert len(listed) == 1 and listed[0]['privateResearchStore'] == 'attached'
    assert call(env, 'POST', '/api/projects/' + listed[0]['projectId'] + '/setup').json() == {'privateResearchStore': 'attached'}


def test_projects_are_isolated_between_accounts(env):
    pid = create(env).json()['project']['projectId']
    assert call(env, 'GET', '/api/projects', who='someone-else').json()['projects'] == []
    for method, path, body in (('GET', '/api/projects/' + pid, None), ('GET', '/' + pid, None),
                               ('POST', '/api/projects/' + pid + '/documents', {'filename': 'a.docx', 'contentBase64': b64(docx('x'))}),
                               ('POST', '/api/projects/' + pid + '/setup', None),
                               ('POST', '/api/projects/' + pid + '/delete', {'confirmTitle': 'x'})):
        assert call(env, method, path, who='someone-else', json=body).status_code == 404, path
    assert call(env, 'GET', '/api/projects', who=None).status_code == 401
    assert call(env, 'POST', '/api/projects/' + pid + '/setup', write=False).status_code == 403


def test_add_and_view_documents(env):
    pid = create(env).json()['project']['projectId']
    raw = docx('Draft findings', 'Second paragraph')
    added = call(env, 'POST', f'/api/projects/{pid}/documents', json={'filename': 'draft.docx', 'contentBase64': b64(raw), 'role': 'draft'})
    assert added.status_code == 201, added.text
    view = call(env, 'GET', added.json()['viewUrl'].split('/research-projects', 1)[1])
    assert view.status_code == 200 and 'Draft findings' in view.text and 'Rendered from the original DOCX' in view.text
    assert sha(raw) in view.text and '<script' not in view.text
    content = call(env, 'GET', added.json()['downloadUrl'].split('/research-projects', 1)[1])
    assert content.content == raw and content.headers['x-research-sha256'] == sha(raw)
    assert 'attachment' in content.headers['content-disposition']
    pdf = b'%PDF-1.4 synthetic\n%%EOF'
    added_pdf = call(env, 'POST', f'/api/projects/{pid}/documents', json={'filename': 'paper.pdf', 'contentBase64': b64(pdf), 'role': 'paper'})
    inline = call(env, 'GET', added_pdf.json()['downloadUrl'].split('/research-projects', 1)[1])
    assert inline.headers['content-type'] == 'application/pdf' and inline.headers['content-disposition'].startswith('inline')
    for body, status in (({'filename': 'copy.docx', 'contentBase64': b64(raw)}, 409),
                         ({'filename': 'draft.docx', 'contentBase64': b64(docx('changed'))}, 409),
                         ({'filename': '../x.docx', 'contentBase64': b64(docx('y'))}, 400),
                         ({'filename': 'x.exe', 'contentBase64': b64(b'MZ')}, 415)):
        assert call(env, 'POST', f'/api/projects/{pid}/documents', json=body).status_code == status, body
    docs = call(env, 'GET', '/api/projects/' + pid).json()['documents']['files']
    assert sorted((f['filename'], f['role']) for f in docs) == [('draft.docx', 'draft'), ('paper.pdf', 'paper')]


def test_overview_is_revisioned_and_existing_projects_are_never_changed(env):
    pid = create(env).json()['project']['projectId']
    body = {'expectedProjectRevision': 1, 'researchQuestion': 'Refined question?', 'status': 'active',
            'objectives': ['Measure', 'Model'], 'milestones': [{'title': 'Field season', 'due': '2027-04-01'}]}
    saved = call(env, 'POST', f'/api/projects/{pid}/overview', json=body)
    assert saved.status_code == 200 and saved.json()['project']['revision'] == 2
    assert call(env, 'POST', f'/api/projects/{pid}/overview', json=body).status_code == 409  # stale revision
    d = call(env, 'GET', '/api/projects/' + pid).json()['overview']
    assert d['objectives'] == ['Measure', 'Model'] and d['milestones'][0]['due'] == '2027-04-01'
    existing_project(env)
    before = head(env, 'existing-synthetic')
    assert call(env, 'POST', '/api/projects/existing-synthetic/overview', json={**body, 'expectedProjectRevision': 1}).status_code == 409
    after = head(env, 'existing-synthetic')
    assert (after.revision, after.fingerprint, after.storage_mode) == (before.revision, before.fingerprint, 'manual-backup')
    shown = call(env, 'GET', '/api/projects/existing-synthetic').json()
    assert shown['project']['kind'] == 'existing-project' and shown['overview']['editable'] is False


def test_registered_documents_of_an_existing_project_are_listed_with_the_viewer(env):
    """SC-RESEARCH-DOCS-01 integration: a register in an existing project gives its area and documents."""
    existing_project(env, 'proj-1', title='Synthetic investigation')
    original = docx('Synthetic investigation report')
    register = {'schema': 'sc-research-document-register/1.0', 'programme': 'SC-RESEARCH-DOCS-01', 'registerRevision': 1,
                'projectId': 'proj-1', 'researchArea': {'id': 'climate-land-carbon', 'name': 'Climate, Land & Carbon'},
                'investigation': {'id': 'synthetic', 'name': 'Synthetic investigation'},
                'documents': [{'documentId': 'synthetic-report', 'title': 'Synthetic report', 'documentType': 'scientific-report',
                               'original': {'sha256': sha(original), 'bytes': len(original), 'format': 'docx', 'filename': 'report.docx'},
                               'renditions': [], 'revisionLabel': 'Revised after submission', 'relatedVersions': [],
                               'submissionStatus': 'post-submission-revision', 'authorship': 'PENDING_VERIFICATION',
                               'visibility': 'private'}]}
    legacy_file(env, 'proj-1', 'report.docx', original)
    legacy_file(env, 'proj-1', 'docs01/SC_RESEARCH_DOCS_01_REGISTER.json', json.dumps(register).encode())
    listed = {p['projectId']: p for p in call(env, 'GET', '/api/projects').json()['projects']}
    assert listed['proj-1']['researchArea']['source'] == 'document-register'
    d = call(env, 'GET', '/api/projects/proj-1').json()
    assert [x['documentId'] for x in d['documents']['registered']] == ['synthetic-report']
    assert d['documents']['registered'][0]['viewUrl'] == '/v1/private-research/reporting-studio/documents/proj-1/synthetic-report'
    assert len(d['documents']['legacy']) == 2 and d['deletable'] is False


def test_multiple_private_outputs_under_one_project(env):
    pid = create(env).json()['project']['projectId']
    pub = '/v1/private-research/reporting-studio/publication/projects/' + pid + '/documents'
    for revision, (title, kind) in enumerate((('Field report', 'report'), ('Policy brief', 'policy-brief')), start=1):
        r = env['client'].post(pub, headers={'x-test-sub': 'owner', **ORIGIN}, json={
            'title': title, 'markdown': '# ' + title + '\n', 'publicationType': kind, 'expectedProjectRevision': revision})
        assert r.status_code == 201, r.text
    outputs = call(env, 'GET', '/api/projects/' + pid).json()['publications']['outputs']
    assert sorted(o['title'] for o in outputs) == ['Field report', 'Policy brief']
    assert all(o['binding'] is None and o['visibility'] == 'private (Workspace only)' for o in outputs)
    assert all(o['scientificStatus'] == 'unreviewed' for o in outputs)
    assert rp.profile_of(head(env, pid).package)['visibility'] == 'private'


def test_research_areas_existing_or_new(env):
    r = create(env, area={'title': 'Ocean Systems'})
    pid = r.json()['project']['projectId']
    assert rp.profile_of(head(env, pid).package)['researchArea'] == {'slug': 'ocean-systems', 'title': 'Ocean Systems',
                                                                      'source': 'owner-defined'}
    areas = {a['slug'] for a in call(env, 'GET', '/api/projects').json()['areas']}
    assert {'ocean-systems', 'climate-land-carbon', 'governance-law-institutions'} <= areas
    assert create(env, key='5c2f1b0a-0000-4000-8000-000000000001', area={'slug': 'no-such-area'}).status_code == 422


def test_only_an_empty_project_created_here_can_be_deleted(env):
    pid = create(env).json()['project']['projectId']
    assert call(env, 'GET', '/api/projects/' + pid).json()['deletable'] is True
    assert call(env, 'POST', f'/api/projects/{pid}/delete', json={'confirmTitle': 'wrong'}).status_code == 422
    other = create(env, key='9a9a9a9a-1111-4222-8333-444455556666', title='Has a file').json()['project']['projectId']
    call(env, 'POST', f'/api/projects/{other}/documents', json={'filename': 'a.docx', 'contentBase64': b64(docx('a'))})
    assert call(env, 'POST', f'/api/projects/{other}/delete', json={'confirmTitle': 'Has a file'}).status_code == 409
    existing_project(env)
    assert call(env, 'POST', '/api/projects/existing-synthetic/delete',
                json={'confirmTitle': 'Existing synthetic project'}).status_code == 409
    gone = call(env, 'POST', f'/api/projects/{pid}/delete', json={'confirmTitle': 'Soil carbon in coastal wetlands'})
    assert gone.status_code == 200 and head(env, pid) is None
    with env['factory']() as db:
        assert db.execute(text('SELECT count(*) FROM workspace_private_research_projects WHERE project_id = :p'), {'p': pid}).scalar() == 0
        receipts = db.execute(text(f'SELECT command FROM {DomainMutationReceipt.__tablename__} WHERE object_id = :p'),
                              {'p': pid}).scalars().all()
    assert 'project.delete' in receipts  # the deletion is itself recorded
    assert head(env, 'existing-synthetic') is not None and head(env, other) is not None
