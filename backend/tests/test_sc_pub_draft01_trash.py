"""SC-PUB-DRAFT-01: draft deletion, Trash and recovery (synthetic projects only).

Uses the SC-RESEARCH-PROJECT-01 isolated SQLite fixture and the SC-EDITOR-DOCX-01 synthetic Word manuscript. Checks
that Trash is reversible and owner-scoped, that original sources, other documents, immutable history and governance
records are untouched, that protected records are refused, and that nothing is erased from the database or object store.
"""
import base64
import hashlib
from datetime import timedelta

from sqlalchemy import func, select

from app import document_lifecycle as lifecycle, repository
from app.models import ArtifactHead, ArtifactRevision, Base, ProjectRevision, ResearchApprovalRequest
from app.reporting_publication import snapshots
from tests.test_sc_editor_docx01_word_import import manuscript_docx, png
from tests.test_sc_research_project01_project_workspace import (  # noqa: F401  (fixture)
    ORIGIN, create, env, head, legacy_file, sha)

S = '/v1/private-research/reporting-studio'
PUB = S + '/publication/projects/'
RP = S + '/research-projects/api/projects/'


def req(env, method, path, who='owner', origin=True, **kw):
    headers = {'x-test-sub': who, **(ORIGIN if method != 'GET' and origin else {})}
    return env['client'].request(method, path, headers=headers, **kw)


def rev(env, pid):
    return head(env, pid).revision


def save(env, pid, title, markdown='# Draft\n\nText.\n', source=None, doc=None, doc_rev=0):
    r = req(env, 'POST', PUB + pid + '/documents', json={
        'title': title, 'markdown': markdown, 'sourceArtifactId': source, 'documentId': doc,
        'expectedDocumentRevision': doc_rev, 'expectedProjectRevision': rev(env, pid)})
    assert r.status_code == 201, r.text
    return r.json()['document']


def act(env, pid, path, who='owner', expected=None, **body):
    return req(env, 'POST', PUB + pid + path, who=who,
               json={'expectedProjectRevision': expected or rev(env, pid), **body})


def upload(env, pid, name, raw, role='draft'):
    r = req(env, 'POST', RP + pid + '/documents', json={
        'filename': name, 'role': role, 'contentBase64': base64.b64encode(raw).decode()})
    assert r.status_code == 201, r.text
    return r.json()['artifactId']


def listed(env, pid):
    return [d['documentId'] for d in req(env, 'GET', PUB + pid + '/documents').json()['documents']]


def store_counts(env):
    with env['factory']() as db:
        return (db.scalar(select(func.count()).select_from(ArtifactHead)),
                db.scalar(select(func.count()).select_from(ArtifactRevision)),
                sorted(p.name for p in env['root'].rglob('*') if p.is_file()))


def test_trash_and_restore_a_private_draft_without_touching_other_documents(env):
    pid = create(env).json()['project']['projectId']
    keep = save(env, pid, 'Keep me', '# Keep\n\nOther work.\n')
    gone = save(env, pid, 'Unwanted draft', '# Unwanted\n\nv1\n')
    gone = save(env, pid, 'Unwanted draft', '# Unwanted\n\nv2\n', doc=gone['documentId'], doc_rev=1)
    before_keep = snapshots(head(env, pid).package, keep['documentId'])
    revisions_before = rev(env, pid)

    r = act(env, pid, f'/documents/{gone["documentId"]}/trash')
    assert r.status_code == 200, r.text
    assert listed(env, pid) == [keep['documentId']]
    trash = req(env, 'GET', PUB + pid + '/trash').json()
    assert [x['id'] for x in trash['publications']] == [gone['documentId']]
    assert trash['publications'][0]['purgeEligible'] is False and trash['policy']['automaticPurge'] is False
    assert trash['events'][0]['action'] == 'trash'
    # Other document and its history unchanged; the trashed draft stays readable (history, exports) but not writable.
    assert snapshots(head(env, pid).package, keep['documentId']) == before_keep
    assert [v['revision'] for v in req(env, 'GET', PUB + pid + f'/documents/{gone["documentId"]}/history').json()['versions']] == [1, 2]
    assert req(env, 'GET', PUB + pid + f'/documents/{gone["documentId"]}/export.html?revision=1').status_code == 200
    refused = req(env, 'POST', PUB + pid + '/documents', json={
        'title': 'Unwanted draft', 'markdown': '# v3\n', 'documentId': gone['documentId'], 'expectedDocumentRevision': 2,
        'expectedProjectRevision': rev(env, pid)})
    assert refused.status_code == 409 and 'Trash' in refused.text
    dash = req(env, 'GET', RP + pid).json()
    assert [o['documentId'] for o in dash['publications']['outputs']] == [keep['documentId']]
    assert [x['id'] for x in dash['trash']['publications']] == [gone['documentId']]

    r = act(env, pid, f'/documents/{gone["documentId"]}/restore')
    assert r.status_code == 200 and r.json()['restored']['revision'] == 2
    assert set(listed(env, pid)) == {keep['documentId'], gone['documentId']}
    restored = req(env, 'GET', PUB + pid + f'/documents/{gone["documentId"]}').json()['document']
    assert restored['markdownSHA256'] == gone['markdownSHA256'] and restored['revision'] == 2
    assert req(env, 'GET', PUB + pid + '/trash').json()['publications'] == []
    save(env, pid, 'Unwanted draft', '# Unwanted\n\nv3\n', doc=gone['documentId'], doc_rev=2)  # editable again
    assert rev(env, pid) == revisions_before + 3  # trash, restore and the save are each an immutable project revision


def test_duplicate_imported_draft_is_removed_original_docx_kept_and_reimport_still_works(env):
    raw = manuscript_docx(png())
    pid = create(env).json()['project']['projectId']
    legacy_file(env, pid, 'research/Policy_Paper_Synthetic.docx', raw)
    aid = 'legacy-' + sha(raw)[:8]
    imported = req(env, 'POST', PUB + pid + f'/sources/{aid}/import-docx').json()
    first = save(env, pid, imported['title'], imported['markdown'], source=aid)
    duplicate = save(env, pid, imported['title'], imported['markdown'], source=aid)
    figure = imported['figures'][0]['assetId']
    counts = store_counts(env)

    assert act(env, pid, f'/documents/{duplicate["documentId"]}/trash').status_code == 200
    assert listed(env, pid) == [first['documentId']]
    # The original DOCX is untouched and still offered as a source.
    blob = env['root'] / 'private-research' / sha(raw)[:2] / sha(raw)
    assert hashlib.sha256(blob.read_bytes()).hexdigest() == sha(raw)
    catalog = req(env, 'GET', S + f'/catalog/projects/{pid}').json()
    assert aid in [f['artifactId'] for f in catalog['legacyFiles']]
    # Re-importing the same DOCX still works and reuses the same figure; a new draft can be saved from it.
    again = req(env, 'POST', PUB + pid + f'/sources/{aid}/import-docx')
    assert again.status_code == 201 and again.json()['markdown'] == imported['markdown']
    assert again.json()['figures'] == [{'assetId': figure, 'status': 'reused'}]
    third = save(env, pid, imported['title'], imported['markdown'], source=aid)
    assert set(listed(env, pid)) == {first['documentId'], third['documentId']}
    assert store_counts(env) == counts  # no row or byte was deleted (or added) by Trash


def test_unauthorized_or_stale_deletion_is_refused(env):
    pid = create(env).json()['project']['projectId']
    doc = save(env, pid, 'Mine')
    assert act(env, pid, f'/documents/{doc["documentId"]}/trash', who='someone-else').status_code == 404
    no_origin = req(env, 'POST', PUB + pid + f'/documents/{doc["documentId"]}/trash', origin=False,
                    json={'expectedProjectRevision': rev(env, pid)})
    assert no_origin.status_code == 403
    signed_out = env['client'].post(PUB + pid + f'/documents/{doc["documentId"]}/trash', headers=ORIGIN,
                                    json={'expectedProjectRevision': rev(env, pid)})
    assert signed_out.status_code == 401
    stale = act(env, pid, f'/documents/{doc["documentId"]}/trash', expected=rev(env, pid) - 1)
    assert stale.status_code == 409 and 'changed' in stale.text
    assert act(env, pid, '/documents/publication-' + '0' * 32 + '/trash').status_code == 404
    other = create(env, who='someone-else', key='2b7c6a52-6f0e-4c51-9a55-1f1f8a3e2c12').json()['project']['projectId']
    assert req(env, 'GET', PUB + other + '/trash').status_code == 404  # another account's project is not visible
    assert listed(env, pid) == [doc['documentId']]


def test_bound_or_governed_publications_are_protected(env):
    pid = create(env).json()['project']['projectId']
    bound = save(env, pid, 'Bound to Research')
    governed = save(env, pid, 'Has approvals')
    row = head(env, pid)
    project = dict(row.package['project'])
    project['objects'] = list(project['objects']) + [{'id': 'research-output-' + bound['documentId'], 'type': 'research-output',
        'output': {'schema': 'sc-workspace-research-output/1.0', 'documentId': bound['documentId'], 'articleSlug': 'a',
                   'areaSlug': 'b'}}]
    with env['factory']() as db:
        from app.schemas import ProjectStoreRequest
        repository.store_project(db, 'owner', ProjectStoreRequest.model_validate({
            'schema': 'sc-workspace-sync-push/1.0', 'sourceProjectId': pid, 'projectTitle': row.title,
            'expectedRevision': row.revision, 'operationId': 'test-bind', 'project': project}))
        Base.metadata.create_all(db.get_bind(), tables=[ResearchApprovalRequest.__table__])
        db.add(ResearchApprovalRequest(approval_id='ap-1', owner_user_key='owner', requester_user_key='owner',
                                       project_id=pid, dimension='publication', action='publish',
                                       subject_ref='studio:' + governed['documentId'], status='pending',
                                       approval_json={'documentId': governed['documentId']}))
        db.commit()
    r = act(env, pid, f'/documents/{bound["documentId"]}/trash')
    assert r.status_code == 409 and 'withdrawal' in r.text
    r = act(env, pid, f'/documents/{governed["documentId"]}/trash')
    assert r.status_code == 409 and 'approval' in r.text
    assert set(listed(env, pid)) == {bound['documentId'], governed['documentId']}


def test_referenced_files_are_protected_and_trash_restore_order_is_enforced(env):
    raw = manuscript_docx(png())
    pid = create(env).json()['project']['projectId']
    aid = upload(env, pid, 'Policy_Paper_Synthetic.docx', raw)
    spare = upload(env, pid, 'notes.md', b'# Spare notes\n')
    imported = req(env, 'POST', PUB + pid + f'/sources/{aid}/import-docx').json()
    doc = save(env, pid, imported['title'], imported['markdown'], source=aid)
    figure = imported['figures'][0]['assetId']

    used = req(env, 'POST', RP + pid + f'/files/{aid}/remove', json={'expectedProjectRevision': rev(env, pid)})
    assert used.status_code == 409 and imported['title'] in used.text
    derived = req(env, 'POST', RP + pid + f'/files/{figure}/remove', json={'expectedProjectRevision': rev(env, pid)})
    assert derived.status_code == 409 and 'Word manuscript' in derived.text
    files = {f['artifactId']: f for f in req(env, 'GET', RP + pid).json()['documents']['files']}
    assert files[aid]['removable'] is False and files[spare]['removable'] is True

    # An unused file moves to Trash and back; its bytes and other files are untouched.
    counts = store_counts(env)
    assert req(env, 'POST', RP + pid + f'/files/{spare}/remove', json={'expectedProjectRevision': rev(env, pid)}).status_code == 200
    assert spare not in {f['artifactId'] for f in req(env, 'GET', RP + pid).json()['documents']['files']}
    assert spare not in {f['artifactId'] for f in req(env, 'GET', S + f'/catalog/projects/{pid}').json()['files']}
    assert req(env, 'GET', PUB + pid + f'/sources/{spare}').status_code == 409
    again = req(env, 'POST', RP + pid + '/documents', json={'filename': 'notes-copy.md', 'role': 'draft',
                                                            'contentBase64': base64.b64encode(b'# Spare notes\n').decode()})
    assert again.status_code == 409 and 'Restore it' in again.text
    assert req(env, 'GET', RP + pid + '/trash').json()['files'][0]['id'] == spare
    assert req(env, 'POST', RP + pid + f'/files/{spare}/restore', json={'expectedProjectRevision': rev(env, pid)}).status_code == 200
    assert req(env, 'GET', PUB + pid + f'/sources/{spare}').status_code == 200
    assert store_counts(env) == counts

    # Once its only draft is in Trash, the source may be removed explicitly; that draft then needs the file back first.
    assert act(env, pid, f'/documents/{doc["documentId"]}/trash').status_code == 200
    removed = req(env, 'POST', RP + pid + f'/files/{aid}/remove', json={'expectedProjectRevision': rev(env, pid)})
    assert removed.status_code == 200 and removed.json()['trashed']['referencedByTrashedDrafts'] == [doc['documentId']]
    blocked = act(env, pid, f'/documents/{doc["documentId"]}/restore')
    assert blocked.status_code == 409 and aid in blocked.text
    assert req(env, 'POST', PUB + pid + f'/sources/{aid}/import-docx').status_code == 409  # source in Trash
    assert req(env, 'POST', RP + pid + f'/files/{aid}/restore', json={'expectedProjectRevision': rev(env, pid)}).status_code == 200
    assert act(env, pid, f'/documents/{doc["documentId"]}/restore').status_code == 200
    assert store_counts(env) == counts


def test_permanent_deletion_only_after_retention_with_title_and_history_kept(env, monkeypatch):
    pid = create(env).json()['project']['projectId']
    keep = save(env, pid, 'Keep me')
    doc = save(env, pid, 'Old duplicate', '# Old duplicate\n\nText.\n')
    assert act(env, pid, f'/documents/{doc["documentId"]}/purge', confirmTitle='Old duplicate').status_code == 409  # not in Trash
    assert act(env, pid, f'/documents/{doc["documentId"]}/trash').status_code == 200
    early = act(env, pid, f'/documents/{doc["documentId"]}/purge', confirmTitle='Old duplicate')
    assert early.status_code == 409 and '30 days' in early.text

    real_now = lifecycle._now
    monkeypatch.setattr(lifecycle, '_now', lambda: real_now() + timedelta(days=lifecycle.TRASH_RETENTION_DAYS, minutes=1))
    assert req(env, 'GET', PUB + pid + '/trash').json()['publications'][0]['purgeEligible'] is True
    assert act(env, pid, f'/documents/{doc["documentId"]}/purge', confirmTitle='Old duplic').status_code == 422
    assert act(env, pid, f'/documents/{doc["documentId"]}/purge', confirmTitle='Old duplicate', who='someone-else').status_code == 404
    done = act(env, pid, f'/documents/{doc["documentId"]}/purge', confirmTitle='Old duplicate')
    assert done.status_code == 200 and done.json()['deleted']['state'] == 'purged'

    assert listed(env, pid) == [keep['documentId']]
    assert req(env, 'GET', PUB + pid + '/trash').json()['publications'] == []
    for path in ('', '/history', '/export.html?revision=1'):
        assert req(env, 'GET', PUB + pid + f'/documents/{doc["documentId"]}{path}').status_code == 404
    assert act(env, pid, f'/documents/{doc["documentId"]}/restore').status_code == 409
    assert snapshots(head(env, pid).package, doc['documentId']) == []
    # Immutable history is kept by design: earlier project revisions still hold the draft.
    with env['factory']() as db:
        archived = [r for r in db.scalars(select(ProjectRevision).where(ProjectRevision.project_id == pid)).all()
                    if snapshots(r.package, doc['documentId'])]
    assert archived
    tomb = lifecycle.entry(head(env, pid).package, 'publication', doc['documentId'])
    assert tomb['state'] == 'purged' and tomb['markdownSHA256'] == doc['markdownSHA256']
    assert [e['action'] for e in lifecycle.state(head(env, pid).package)['events']] == ['trash', 'purge']
