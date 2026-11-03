"""Isolated mocked native Workspace artifact-store contract tests.

Covers route authorization/validation, owner lookup and per-artifact revisions.
Does NOT replace a real PostgreSQL/database deployment test.
"""
import base64
import hashlib
import importlib.util
import pathlib
import sys
import types
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import String, Integer, select, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

ROOT = pathlib.Path(__file__).resolve().parents[1]
ORIGIN = 'https://workspace.sustainablecatalyst.com'
ROOT_API = '/v1/private-research/persistent-projects'


@dataclass
class Head:
    user_key: str
    artifact_id: str
    project_id: str
    filename: str
    media_type: str
    bytes: int
    sha256: str
    revision: int
    metadata_json: dict
    storage_key: str
    raw: bytes


@pytest.fixture()
def environment(monkeypatch):
    # The production module imports the application's DB/store/auth APIs; this fixture
    # replaces them with fakes so no real account, object bytes or DB can be touched.
    heads = {}
    history = {}
    projects = {('owner-a', 'wexford-project'), ('owner-b', 'other-project'),
                ('owner-a', 'metrics-project')}
    fake = types.ModuleType('app')
    fake.__path__ = [str(ROOT / 'backend' / 'app')]
    monkeypatch.setitem(sys.modules, 'app', fake)
    names = {}
    for name in ('db', 'repository', 'object_store', 'models', 'schemas', 'session_auth'):
        module = types.ModuleType('app.' + name)
        monkeypatch.setitem(sys.modules, 'app.' + name, module)
        names[name] = module
        setattr(fake, name, module)

    # Exercise the real SQLAlchemy owner/revision filters against SQLite.
    # Shared in-memory pool lets FastAPI's worker thread see the same schema.
    from sqlalchemy.pool import StaticPool
    class TestBase(DeclarativeBase):
        pass

    class RevisionModel(TestBase):
        __tablename__ = 'revisions'
        user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
        artifact_id: Mapped[str] = mapped_column(String(160), primary_key=True)
        revision: Mapped[int] = mapped_column(Integer, primary_key=True)
        project_id: Mapped[str] = mapped_column(String(160))
        filename: Mapped[str] = mapped_column(String(200))
        media_type: Mapped[str] = mapped_column(String(200))
        bytes: Mapped[int] = mapped_column(Integer)
        sha256: Mapped[str] = mapped_column(String(64))
        storage_key: Mapped[str] = mapped_column(String(64))

    engine = create_engine('sqlite://', connect_args={'check_same_thread': False},
                           poolclass=StaticPool)
    TestBase.metadata.create_all(engine)
    SessionMaker = sessionmaker(bind=engine)

    @contextmanager
    def session_scope():
        with SessionMaker() as session:
            yield session

    names['db'].session_scope = session_scope
    names['models'].ArtifactRevision = RevisionModel
    names['repository'].get_project = lambda db, owner, project: (
        object() if (owner, project) in projects else None)
    names['session_auth'].session_payload_from_request = lambda request: (
        {'sub': request.cookies['session']} if request.cookies.get('session') else None)

    class StoreRequest:
        @classmethod
        def model_validate(cls, data):
            return SimpleNamespace(**data)

    names['schemas'].ArtifactStoreRequest = StoreRequest

    def get_artifact(db, owner, artifact_id):
        return heads.get((owner, artifact_id))

    def store_artifact(db, owner, payload):
        key = (owner, payload.artifactId)
        prior = heads.get(key)
        expected = prior.revision if prior else 0
        if payload.expectedRevision != expected:
            from fastapi import HTTPException
            raise HTTPException(409, 'Native artifact revision conflict')
        raw = base64.b64decode(payload.contentBase64)
        digest = hashlib.sha256(raw).hexdigest()
        row = Head(owner, payload.artifactId, payload.projectId,
                   payload.filename, payload.mediaType, len(raw), digest,
                   expected + 1, payload.metadata, digest, raw)
        heads[key] = row
        history[(owner, row.artifact_id, row.revision)] = row
        db.add(RevisionModel(user_key=owner, artifact_id=row.artifact_id,
            revision=row.revision, project_id=row.project_id, filename=row.filename,
            media_type=row.media_type, bytes=row.bytes, sha256=row.sha256, storage_key=row.storage_key))
        db.commit()
        return row

    names['object_store'].get_artifact = get_artifact
    names['object_store'].store_artifact = store_artifact
    names['object_store'].read_artifact_content = lambda row: row.raw

    # Fake the SQLAlchemy model lookup specifically for the history-detail endpoint.
    class WrappedSession:
        def __init__(self, session):
            self.session = session
        def __getattr__(self, key):
            return getattr(self.session, key)
        def get(self, model, pk):
            if model is RevisionModel:
                return history.get((pk['user_key'], pk['artifact_id'], pk['revision']))
            return self.session.get(model, pk)
        def scalars(self, statement):
            # SQL executes against the strict user-scoped where clause; return
            # matched synthetic version records based on the selected identity rows.
            rows = self.session.scalars(statement).all()
            out = []
            for item in rows:
                out.append(history[(item.user_key, item.artifact_id, item.revision)])
            return SimpleNamespace(all=lambda: out)
    @contextmanager
    def wrapped_session_scope():
        with SessionMaker() as session:
            yield WrappedSession(session)
    names['db'].session_scope = wrapped_session_scope

    module_name = 'app.rd014_publication_records'
    spec = importlib.util.spec_from_file_location(module_name,
        ROOT / 'backend' / 'app' / 'rd014_publication_records.py')
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, module_name, module)
    spec.loader.exec_module(module)
    app = FastAPI()
    app.include_router(module.router)
    client = TestClient(app)

    def upload(owner, project, art_id, content=b'PDF', media='application/pdf', metadata=None):
        with names['db'].session_scope() as db:
            payload = SimpleNamespace(
                artifactId=art_id, projectId=project, filename=art_id+'.pdf',
                mediaType=media, contentBase64=base64.b64encode(content).decode(),
                expectedRevision=0, metadata=metadata or {'source': 'test'},
            )
            return store_artifact(db, owner, payload)

    def create(kind, owner='owner-a', project='wexford-project', **overrides):
        body = {'contentMarkdown': '# My document\n', 'expectedRevision': 0}
        body.update(overrides)
        return client.post(f'{ROOT_API}/{project}/publications/{kind}',
            cookies={'session': owner}, headers={'origin': ORIGIN}, json=body)

    yield SimpleNamespace(client=client, create=create, upload=upload, heads=heads,
                          history=history, module=module, projects=projects)
    engine.dispose()


def test_empty_catalog_shows_expected_kinds(environment):
    e = environment
    r = e.client.get(f'{ROOT_API}/wexford-project/publications', cookies={'session':'owner-a'})
    assert r.status_code == 200 and r.json()['publications'] == []
    assert set(r.json()['expectedKinds']) == {'scientific-report','policy-brief'}


def test_two_publications_created_without_colliding(environment):
    e = environment
    first = e.create('scientific-report')
    second = e.create('policy-brief')
    assert (first.status_code, second.status_code) == (201, 201)
    assert first.json()['publicationId'] != second.json()['publicationId']
    result = e.client.get(f'{ROOT_API}/wexford-project/publications',cookies={'session':'owner-a'}).json()
    assert {x['kind'] for x in result['publications']} == {'scientific-report','policy-brief'}


def test_save_reopen_and_independent_revisions(environment):
    e=environment
    e.create('scientific-report')
    e.create('policy-brief')
    path=f'{ROOT_API}/wexford-project/publications/scientific-report'
    r=e.client.put(path,cookies={'session':'owner-a'},headers={'origin':ORIGIN},json={
        'contentMarkdown':'# Revised science\n','expectedRevision':1})
    assert r.status_code==200 and r.json()['revision']==2
    assert e.client.get(path,cookies={'session':'owner-a'}).json()['contentMarkdown']=='# Revised science\n'
    b=e.client.get(f'{ROOT_API}/wexford-project/publications/policy-brief',cookies={'session':'owner-a'}).json()
    assert b['revision']==1 and b['contentMarkdown']=='# My document\n'


def test_revision_history_is_retrievable(environment):
    e=environment
    e.create('scientific-report')
    e.client.put(f'{ROOT_API}/wexford-project/publications/scientific-report',cookies={'session':'owner-a'},headers={'origin':ORIGIN},json={
        'contentMarkdown':'new\n','expectedRevision':1})
    p=f'{ROOT_API}/wexford-project/publications/scientific-report'
    revs=e.client.get(p+'/revisions',cookies={'session':'owner-a'})
    assert revs.status_code==200, revs.text
    assert [r['revision'] for r in revs.json()['revisions']]==[1,2]
    old=e.client.get(p+'/revisions/1',cookies={'session':'owner-a'})
    assert old.status_code==200,old.text
    assert old.json()['contentMarkdown']=='# My document\n'
    assert old.json()['revision']==1


def test_missing_session_is_401(environment):
    e=environment
    assert e.client.get(f'{ROOT_API}/wexford-project/publications').status_code==401
    assert e.client.post(f'{ROOT_API}/wexford-project/publications/policy-brief',json={'contentMarkdown':'x','expectedRevision':0},headers={'origin':ORIGIN}).status_code==401


def test_bad_origin_denied(environment):
    e=environment
    r=e.client.post(f'{ROOT_API}/wexford-project/publications/policy-brief',cookies={'session':'owner-a'},headers={'origin':'https://bad.example'},json={'contentMarkdown':'# hello','expectedRevision':0})
    assert r.status_code==403 and not e.heads


def test_other_user_cannot_access_or_create(environment):
    e=environment
    assert e.create('policy-brief',owner='owner-b').status_code==404
    e.create('scientific-report')
    url=f'{ROOT_API}/wexford-project/publications/scientific-report'
    assert e.client.get(url,cookies={'session':'owner-b'}).status_code==404
    assert e.client.get(url+'/revisions',cookies={'session':'owner-b'}).status_code==404


def test_metrics_is_untouched(environment):
    e=environment
    e.create('policy-brief')
    assert not [head for head in e.heads.values() if head.project_id=='metrics-project']


def test_retry_create_conflicts_without_replacing(environment):
    e=environment
    assert e.create('scientific-report').status_code==201
    assert e.create('scientific-report',contentMarkdown='REPLACE').status_code==409
    assert e.client.get(f'{ROOT_API}/wexford-project/publications/scientific-report',cookies={'session':'owner-a'}).json()['revision']==1


def test_stale_update_conflicts(environment):
    e=environment
    e.create('policy-brief')
    r=e.client.put(f'{ROOT_API}/wexford-project/publications/policy-brief',cookies={'session':'owner-a'},headers={'origin':ORIGIN},json={'contentMarkdown':'Stale','expectedRevision':0})
    assert r.status_code==409


def test_unknown_type_rejected(environment):
    assert environment.create('blog-post').status_code==404


def test_original_submission_must_exist_and_be_owned(environment):
    e=environment
    assert e.create('scientific-report', originalSubmissionArtifactId='missing').status_code==404
    e.upload('owner-b','other-project','private.pdf')
    assert e.create('scientific-report', originalSubmissionArtifactId='private.pdf').status_code==404


def test_original_submission_is_linked_not_overwritten(environment):
    e=environment
    original=e.upload('owner-a','wexford-project','submitted.pdf',b'PDF source bytes')
    r=e.create('scientific-report', originalSubmissionArtifactId='submitted.pdf')
    assert r.status_code==201,r.text
    assert r.json()['originalSubmission']['sha256']==original.sha256
    assert e.heads[('owner-a','submitted.pdf')].raw==b'PDF source bytes'


def test_original_cannot_be_replaced_or_removed(environment):
    e=environment
    e.upload('owner-a','wexford-project','submitted.pdf')
    e.upload('owner-a','wexford-project','different.pdf')
    e.create('scientific-report', originalSubmissionArtifactId='submitted.pdf')
    p=f'{ROOT_API}/wexford-project/publications/scientific-report'
    r=e.client.put(p,cookies={'session':'owner-a'},headers={'origin':ORIGIN},json={'contentMarkdown':'x','expectedRevision':1,'originalSubmissionArtifactId':'different.pdf'})
    assert r.status_code==409
    r=e.client.put(p,cookies={'session':'owner-a'},headers={'origin':ORIGIN},json={'contentMarkdown':'x','expectedRevision':1})
    assert r.status_code==200 and r.json()['originalSubmission']['artifactId']=='submitted.pdf'


def test_fake_figure_reference_rejected(environment):
    e=environment
    r=e.create('policy-brief',figures=[{'figureId':'FIG-PB01','artifactId':'not-uploaded','sha256':'0'*64}])
    assert r.status_code==422


def test_review_only_figure_cannot_be_embedded(environment):
    e=environment
    uploaded=e.upload('owner-a','wexford-project','geo.png',b'geo',media='image/png',metadata={'publicationReview':{'status':'review-only'}})
    r=e.create('policy-brief',figures=[{'figureId':'FIG-GEO01','artifactId':'geo.png','sha256':uploaded.sha256,'includeInExport':True}])
    assert r.status_code==422


def test_pending_figure_can_be_linked_without_embedding(environment):
    e=environment
    uploaded=e.upload('owner-a','wexford-project','geo.png',b'geo',media='image/png',metadata={'publicationReview':{'status':'review-only'}})
    r=e.create('policy-brief',figures=[{'figureId':'FIG-GEO01','artifactId':'geo.png','sha256':uploaded.sha256,'includeInExport':False}])
    assert r.status_code==201 and not r.json()['figures'][0]['includeInExport']


def test_approved_evidence_bound_figure_can_be_included(environment):
    e=environment
    review={'publicationReview':{'status':'approved','rights':'approved','science':'approved'}}
    uploaded=e.upload('owner-a','wexford-project','pb01.png',b'figure',media='image/png',metadata=review)
    r=e.create('policy-brief',figures=[{'figureId':'FIG-PB01','artifactId':'pb01.png','sha256':uploaded.sha256,'includeInExport':True}])
    assert r.status_code==201,r.text


def test_figure_sha_mismatch_denied(environment):
    e=environment
    e.upload('owner-a','wexford-project','pb01.png',b'figure',media='image/png')
    assert e.create('policy-brief',figures=[{'figureId':'FIG-PB01','artifactId':'pb01.png','sha256':'f'*64}]).status_code==422


def test_draft_content_max_size_rejected(environment):
    assert environment.create('policy-brief',contentMarkdown='a'*500001).status_code==422


def test_non_docx_pdf_source_is_rejected(environment):
    e=environment
    e.upload('owner-a','wexford-project','figure.png',b'foo',media='image/png')
    assert e.create('scientific-report',originalSubmissionArtifactId='figure.png').status_code==422


def test_duplicate_figure_id_rejected(environment):
    e=environment
    a=e.upload('owner-a','wexford-project','a.png',b'one',media='image/png')
    b=e.upload('owner-a','wexford-project','b.png',b'two',media='image/png')
    refs=[{'figureId':'FIG-PB01','artifactId':'a.png','sha256':a.sha256},
          {'figureId':'FIG-PB01','artifactId':'b.png','sha256':b.sha256}]
    assert e.create('policy-brief',figures=refs).status_code==422


def test_publication_id_deterministic_and_owner_project_scoped(environment):
    mod=environment.module
    assert mod._publication_id('wexford-project','policy-brief')==mod._publication_id('wexford-project','policy-brief')
    assert mod._publication_id('wexford-project','policy-brief')!=mod._publication_id('metrics-project','policy-brief')


def test_unknown_project_does_not_create_data(environment):
    e=environment
    assert e.create('policy-brief',project='unknown-project').status_code==404
    assert not e.heads


def test_geo01_cannot_be_promoted_by_metadata(environment):
    e=environment
    review={'publicationReview':{'status':'approved','rights':'approved','science':'approved'}}
    uploaded=e.upload('owner-a','wexford-project','geo.png',b'geo',media='image/png',metadata=review)
    r=e.create('policy-brief',figures=[{'figureId':'FIG-GEO01','artifactId':'geo.png','sha256':uploaded.sha256,'includeInExport':True}])
    assert r.status_code==422


def test_response_is_never_cacheable(environment):
    e=environment
    e.create('scientific-report')
    r=e.client.get(f'{ROOT_API}/wexford-project/publications/scientific-report',cookies={'session':'owner-a'})
    assert r.headers['cache-control']=='private, no-store'
    assert r.headers['x-content-type-options']=='nosniff'


def test_original_source_updated_outside_publication_is_detected(environment):
    e=environment
    original=e.upload('owner-a','wexford-project','submitted.pdf',b'original')
    e.create('scientific-report',originalSubmissionArtifactId='submitted.pdf')
    original.sha256='e'*64  # Simulate an external artifact revision/tamper.
    p=f'{ROOT_API}/wexford-project/publications/scientific-report'
    r=e.client.put(p,cookies={'session':'owner-a'},headers={'origin':ORIGIN},json={'contentMarkdown':'change','expectedRevision':1})
    assert r.status_code==409


def test_review_ui_requires_auth_and_owned_project(environment):
    e=environment
    u=f'{ROOT_API}/wexford-project/publications/ui'
    assert e.client.get(u).status_code==401
    assert e.client.get(u,cookies={'session':'owner-b'}).status_code==404
    r=e.client.get(u,cookies={'session':'owner-a'})
    assert r.status_code==200
    assert 'Assignment 1' in r.text and 'Assignment 2' in r.text
    assert "frame-ancestors 'none'" in r.headers['content-security-policy']


def test_update_without_figures_preserves_previous_links(environment):
    e=environment
    original=e.upload('owner-a','wexford-project','pb01.png',b'figure',media='image/png')
    refs=[{'figureId':'FIG-PB01','artifactId':'pb01.png','sha256':original.sha256}]
    assert e.create('policy-brief',figures=refs).status_code==201
    p=f'{ROOT_API}/wexford-project/publications/policy-brief'
    r=e.client.put(p,cookies={'session':'owner-a'},headers={'origin':ORIGIN},json={'contentMarkdown':'edited','expectedRevision':1})
    assert r.status_code==200
    assert len(r.json()['figures'])==1