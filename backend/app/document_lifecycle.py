"""SC-PUB-DRAFT-01: Trash, restore and permanent deletion for private drafts and uploaded project files.

Lifecycle state is one ``document-lifecycle`` object in the project package. Every change is stored as a new immutable
Workspace project revision (owner-scoped, with an expected-revision conflict check), so the lifecycle has the same
audit trail as everything else in the project. Nothing here deletes database rows or object-store bytes:

* Moving a saved draft or an uploaded file to Trash only hides it from active lists. Its revisions, bytes,
  provenance and exports stay readable, and Restore brings it back unchanged.
* Permanent deletion is offered only for a private draft that has been in Trash for ``TRASH_RETENTION_DAYS``. It
  removes the draft from the live project and closes it in the Studio, leaving a tombstone. By design its earlier
  revisions remain in the immutable project-revision history and in backups; they are not destroyed.
* Uploaded files are never permanently deleted here; Trash and Restore only.

Protected records: a publication bound to a Research output, or referenced by an approval request, cannot be trashed
(use the Research withdrawal and governance workflows). A file referenced by an active publication, citation record,
figure report, notebook or other project object cannot be removed; figures derived from an imported Word manuscript
and registered research sources are managed with their drafts and register, not removed one by one.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import inspect, select

from . import repository
from .models import NotebookHead, ResearchApprovalRequest
from .schemas import ProjectStoreRequest

SCHEMA = 'sc-document-lifecycle/1.0'
OBJECT_TYPE = 'document-lifecycle'
OBJECT_ID = 'document-lifecycle'
TRASH_RETENTION_DAYS = 30
MAX_EVENTS = 2000
POLICY = {
    'schema': SCHEMA,
    'trash': 'Moving a draft or file to Trash hides it from active lists. Nothing is erased; Restore brings it back.',
    'retentionDays': TRASH_RETENTION_DAYS,
    'permanentDeletion': (f'Only a private draft that has been in Trash for at least {TRASH_RETENTION_DAYS} days can be '
                          'deleted permanently, after you type its title. It is removed from the project and cannot be '
                          'restored in the Studio. Earlier revisions stay in the immutable project history and backups.'),
    'files': 'Uploaded files can be moved to Trash and restored. They are never permanently deleted here.',
    'protected': ('Publications bound to Research or referenced by approvals, and files used by active drafts, '
                  'citations, figures or notebooks, are protected. Use the Research withdrawal workflow for published work.'),
    'automaticPurge': False,
}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(value: datetime) -> str:
    return value.isoformat().replace('+00:00', 'Z')


def state(package: dict) -> dict:
    for obj in package.get('project', {}).get('objects') or []:
        if isinstance(obj, dict) and obj.get('type') == OBJECT_TYPE and isinstance(obj.get('lifecycle'), dict) \
                and obj['lifecycle'].get('schema') == SCHEMA:
            return obj['lifecycle']
    return {'schema': SCHEMA, 'entries': {}, 'events': []}


def entry(package: dict, kind: str, ident: str) -> dict | None:
    return state(package).get('entries', {}).get(f'{kind}:{ident}')


def hidden(package: dict, kind: str) -> set[str]:
    """Ids of this kind that are in Trash or permanently deleted (not shown in active lists)."""
    prefix = kind + ':'
    return {k[len(prefix):] for k in state(package).get('entries', {}) if k.startswith(prefix)}


def trashed(package: dict, kind: str) -> set[str]:
    prefix = kind + ':'
    return {k[len(prefix):] for k, v in state(package).get('entries', {}).items()
            if k.startswith(prefix) and v.get('state') == 'trashed'}


def purged(package: dict, kind: str) -> set[str]:
    prefix = kind + ':'
    return {k[len(prefix):] for k, v in state(package).get('entries', {}).items()
            if k.startswith(prefix) and v.get('state') == 'purged'}


def _with_state(project: dict, lifecycle: dict) -> dict:
    project = deepcopy(project)
    objects = [o for o in project.get('objects') or [] if not (isinstance(o, dict) and o.get('type') == OBJECT_TYPE)]
    objects.append({'id': OBJECT_ID, 'type': OBJECT_TYPE, 'lifecycle': lifecycle})
    project['objects'] = objects
    return project


def _store(db, owner: str, row, project: dict, operation: str):
    payload = ProjectStoreRequest.model_validate({
        'schema': 'sc-workspace-sync-push/1.0', 'sourceProjectId': row.project_id, 'projectTitle': row.title,
        'expectedRevision': row.revision, 'operationId': operation + '-' + uuid4().hex, 'project': project})
    updated, _ = repository.store_project(db, owner, payload)
    return updated


def _check_revision(row, expected: int) -> None:
    if row.revision != expected:
        raise HTTPException(409, 'Workspace project changed. Reload before changing Trash.')


def _record(lifecycle: dict, action: str, kind: str, ident: str, label: str, project_revision: int, **extra) -> dict:
    lifecycle = deepcopy(lifecycle)
    lifecycle.setdefault('entries', {})
    events = lifecycle.setdefault('events', [])
    events.append({'at': _iso(_now()), 'action': action, 'kind': kind, 'id': ident, 'label': label[:300],
                   'projectRevision': project_revision, **extra})
    del events[:-MAX_EVENTS]
    return lifecycle


# Protection ---------------------------------------------------------------------------------------------------------

def publication_protection(db, owner: str, row, document_id: str) -> str | None:
    """Why this publication may not leave the active list through ordinary draft deletion, or None."""
    from .research_outputs import bindings
    if document_id in bindings(row.package):
        return ('This publication is bound to a Research article. Use the Research withdrawal workflow instead of '
                'deleting the draft.')
    if inspect(db.get_bind()).has_table(ResearchApprovalRequest.__tablename__):
        rows = db.scalars(select(ResearchApprovalRequest).where(
            ResearchApprovalRequest.owner_user_key == owner, ResearchApprovalRequest.project_id == row.project_id)).all()
        for r in rows:
            if document_id in r.subject_ref or document_id in json.dumps(r.approval_json, default=str):
                return 'This publication has approval records. Use the Research governance workflow instead.'
    return None


def file_references(db, owner: str, row, artifact_id: str) -> dict:
    """Where an uploaded file is used: by active objects (blocking) and by drafts already in Trash (not blocking)."""
    trashed_docs = trashed(row.package, 'publication')
    active, in_trash = [], []
    needles = ('"' + artifact_id + '"', 'asset:' + artifact_id)
    for obj in row.package.get('project', {}).get('objects') or []:
        if not isinstance(obj, dict) or obj.get('type') == OBJECT_TYPE:
            continue
        blob = json.dumps(obj, default=str)
        if not any(n in blob for n in needles):
            continue
        if obj.get('type') == 'scientific-publication':
            pub = obj.get('publication') or {}
            ref = {'kind': 'publication', 'documentId': pub.get('documentId'), 'title': pub.get('title')}
            (in_trash if pub.get('documentId') in trashed_docs else active).append(ref)
        else:
            active.append({'kind': obj.get('type') or 'project object', 'id': obj.get('id')})
    if inspect(db.get_bind()).has_table(NotebookHead.__tablename__):
        for nb in db.scalars(select(NotebookHead).where(NotebookHead.user_key == owner,
                                                        NotebookHead.project_id == row.project_id)).all():
            if any(n in json.dumps(nb.package, default=str) for n in needles):
                active.append({'kind': 'notebook', 'id': nb.notebook_id, 'title': nb.title})
    return {'active': active, 'trashed': in_trash}


# Publications -------------------------------------------------------------------------------------------------------

def _head(row, document_id: str) -> dict | None:
    for obj in row.package.get('project', {}).get('objects') or []:
        if isinstance(obj, dict) and obj.get('type') == 'scientific-publication' \
                and (obj.get('publication') or {}).get('documentId') == document_id:
            return obj['publication']
    return None


def _source_ids(pub: dict) -> list[str]:
    ids = [((pub.get('source') or {}).get('artifactId'))] + [f.get('artifactId') for f in pub.get('figureSources') or []]
    return [i for i in ids if i]


def trash_publication(db, owner: str, row, document_id: str, expected: int) -> tuple[object, dict]:
    _check_revision(row, expected)
    pub = _head(row, document_id)
    if pub is None or document_id in purged(row.package, 'publication'):
        raise HTTPException(404, 'Publication not found in this project.')
    if document_id in trashed(row.package, 'publication'):
        raise HTTPException(409, 'This draft is already in Trash.')
    reason = publication_protection(db, owner, row, document_id)
    if reason:
        raise HTTPException(409, reason)
    now = _now()
    record = {'kind': 'publication', 'id': document_id, 'state': 'trashed', 'title': pub.get('title'),
              'revision': pub.get('revision'), 'markdownSHA256': pub.get('markdownSHA256'),
              'trashedAt': _iso(now), 'purgeEligibleAt': _iso(now + timedelta(days=TRASH_RETENTION_DAYS))}
    lifecycle = _record(state(row.package), 'trash', 'publication', document_id, pub.get('title') or '', row.revision + 1)
    lifecycle['entries']['publication:' + document_id] = record
    updated = _store(db, owner, row, _with_state(row.package['project'], lifecycle), 'publication-trash')
    return updated, record


def restore_publication(db, owner: str, row, document_id: str, expected: int) -> tuple[object, dict]:
    _check_revision(row, expected)
    current = entry(row.package, 'publication', document_id)
    if not current or current.get('state') != 'trashed':
        raise HTTPException(409, 'This draft is not in Trash.')
    pub = _head(row, document_id)
    waiting = [i for i in _source_ids(pub or {}) if i in trashed(row.package, 'file')]
    if waiting:
        raise HTTPException(409, {'message': 'Restore the files this draft uses first.', 'files': waiting})
    lifecycle = _record(state(row.package), 'restore', 'publication', document_id, current.get('title') or '',
                        row.revision + 1)
    del lifecycle['entries']['publication:' + document_id]
    updated = _store(db, owner, row, _with_state(row.package['project'], lifecycle), 'publication-restore')
    return updated, pub


def purge_publication(db, owner: str, row, document_id: str, expected: int, confirm_title: str) -> tuple[object, dict]:
    _check_revision(row, expected)
    current = entry(row.package, 'publication', document_id)
    if not current or current.get('state') != 'trashed':
        raise HTTPException(409, 'Only a draft in Trash can be deleted permanently.')
    if _now() < datetime.fromisoformat(current['purgeEligibleAt'].replace('Z', '+00:00')):
        raise HTTPException(409, {'message': f'Drafts stay in Trash for {TRASH_RETENTION_DAYS} days before permanent '
                                             'deletion.', 'purgeEligibleAt': current['purgeEligibleAt']})
    reason = publication_protection(db, owner, row, document_id)
    if reason:
        raise HTTPException(409, reason)
    if confirm_title.strip() != (current.get('title') or '').strip():
        raise HTTPException(422, 'Type the draft title exactly to delete it permanently.')
    project = deepcopy(row.package['project'])
    project['objects'] = [o for o in project.get('objects') or [] if not (
        isinstance(o, dict) and o.get('type') == 'scientific-publication'
        and (o.get('publication') or {}).get('documentId') == document_id)]
    tombstone = {k: current.get(k) for k in ('kind', 'id', 'title', 'revision', 'markdownSHA256', 'trashedAt')}
    tombstone.update(state='purged', purgedAt=_iso(_now()), lastLiveProjectRevision=row.revision,
                     history='Earlier revisions remain in the immutable project-revision history and backups.')
    lifecycle = _record(state(row.package), 'purge', 'publication', document_id, current.get('title') or '',
                        row.revision + 1)
    lifecycle['entries']['publication:' + document_id] = tombstone
    updated = _store(db, owner, row, _with_state(project, lifecycle), 'publication-purge')
    return updated, tombstone


# Files ----------------------------------------------------------------------------------------------------------------

def trash_file(db, owner: str, row, artifact, expected: int) -> tuple[object, dict]:
    _check_revision(row, expected)
    if artifact.artifact_id in hidden(row.package, 'file'):
        raise HTTPException(409, 'This file is already in Trash.')
    if (artifact.metadata_json or {}).get('source') == 'docx-import':
        raise HTTPException(409, 'This figure was extracted from an imported Word manuscript and is managed with its drafts.')
    refs = file_references(db, owner, row, artifact.artifact_id)
    if refs['active']:
        raise HTTPException(409, {'message': 'This file is used by active work in the project and cannot be removed.',
                                  'usedBy': refs['active']})
    record = {'kind': 'file', 'id': artifact.artifact_id, 'state': 'trashed', 'filename': artifact.filename,
              'sha256': artifact.sha256, 'bytes': artifact.bytes, 'trashedAt': _iso(_now()),
              'referencedByTrashedDrafts': [r['documentId'] for r in refs['trashed']]}
    lifecycle = _record(state(row.package), 'trash', 'file', artifact.artifact_id, artifact.filename, row.revision + 1)
    lifecycle['entries']['file:' + artifact.artifact_id] = record
    updated = _store(db, owner, row, _with_state(row.package['project'], lifecycle), 'file-trash')
    return updated, record


def restore_file(db, owner: str, row, artifact_id: str, expected: int) -> tuple[object, dict]:
    _check_revision(row, expected)
    current = entry(row.package, 'file', artifact_id)
    if not current or current.get('state') != 'trashed':
        raise HTTPException(409, 'This file is not in Trash.')
    lifecycle = _record(state(row.package), 'restore', 'file', artifact_id, current.get('filename') or '', row.revision + 1)
    del lifecycle['entries']['file:' + artifact_id]
    updated = _store(db, owner, row, _with_state(row.package['project'], lifecycle), 'file-restore')
    return updated, current


def trash_view(row) -> dict:
    entries = state(row.package).get('entries', {})
    now = _now()

    def view(v: dict) -> dict:
        out = dict(v)
        if v.get('state') == 'trashed' and v.get('kind') == 'publication':
            eligible = datetime.fromisoformat(v['purgeEligibleAt'].replace('Z', '+00:00'))
            out['purgeEligible'] = now >= eligible
        return out
    items = sorted((view(v) for v in entries.values() if v.get('state') == 'trashed'),
                   key=lambda v: v.get('trashedAt') or '', reverse=True)
    return {'schema': SCHEMA, 'projectRevision': row.revision, 'policy': POLICY,
            'publications': [v for v in items if v['kind'] == 'publication'],
            'files': [v for v in items if v['kind'] == 'file'],
            'events': state(row.package).get('events', [])[-50:][::-1]}
