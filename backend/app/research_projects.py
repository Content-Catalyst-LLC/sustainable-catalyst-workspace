"""SC-RESEARCH-PROJECT-01: New Research Project and its dedicated private project workspace.

One action creates one canonical Workspace project: the existing revisioned project registry
(``repository.store_project``) stores the project with a ``research-project-profile`` object (title, research area,
question, type, status, milestones), and the project is attached to the existing private research store. The project
id is derived from the owner and a browser-held creation key, so a repeated or retried submission returns the same
project instead of creating a second one. If the attachment fails after the project is stored, the project is still a
complete, owner-scoped research project; the dashboard reports the missing attachment and the same idempotent call
completes it.

The dashboard reads the stores that already exist (document registers and the full-document viewer, native and legacy
project files, the Citation Studio collection, notebooks, Reporting Studio reports and Publication Studio outputs) and
links to the tools that edit them. Nothing here publishes, binds an output to Research, changes Research visibility
or modifies a project that has no research profile.
"""
from __future__ import annotations

import base64
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
from html import escape
import re
from typing import Annotated, Literal
from urllib.parse import quote
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from sqlalchemy import inspect, select, text

from . import object_store, repository
from .citation_studio import collection
from .db import session_scope
from .models import NotebookHead
from .reporting_project_catalog import read_legacy_artifacts
from .reporting_publication import latest_documents, snapshots
from .research_documents import STYLE, _page, _summary, project_register, render_docx
from .research_outputs import bindings
from .schemas import ArtifactStoreRequest, ProjectStoreRequest
from .wxr_private_projects import HEADERS, _filename, _locked_project, _project, _subject, _write
from .studio_signin import page_subject
from . import document_lifecycle as lifecycle

router = APIRouter(prefix='/research-projects')

BASE = '/v1/private-research/reporting-studio'
HOME = BASE + '/research-projects'
PROFILE_SCHEMA = 'sc-research-project-profile/1.0'
PROFILE_TYPE = 'research-project-profile'
PROFILE_ID = 'research-project-profile'
PROGRAMME = 'SC-RESEARCH-PROJECT-01'
STORE_TABLE = 'workspace_private_research_projects'
# The institution's research areas (the public hub's areas, private here until an area publication is approved).
INSTITUTIONAL_AREAS = {
    'climate-land-carbon': 'Climate, Land & Carbon',
    'governance-law-institutions': 'Governance, Law & Institutions',
    'sustainable-development': 'Sustainable Development',
    'wellbeing-long-term-resilience': 'Wellbeing & Long-Term Resilience',
}
PROJECT_TYPES = {
    'investigation': 'Research investigation',
    'paper': 'Paper or report',
    'policy-analysis': 'Policy analysis',
    'data-methods': 'Data and methods',
    'other': 'Other',
}
DOCUMENT_ROLES = ('report', 'paper', 'draft', 'source', 'reference', 'data', 'figure', 'other')
FIGURE_EXTENSIONS = ('.svg', '.png', '.jpg', '.jpeg')
REFERENCE_EXTENSIONS = ('.ris', '.json')
DISCLOSURE = 'Author-reviewed: authorized for publication by its author; not independently reviewed.'

Slug = Annotated[str, StringConstraints(pattern=r'^[a-z0-9]+(?:-[a-z0-9]+)*$', max_length=80)]
Line = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=300)]


class Strict(BaseModel):
    model_config = ConfigDict(extra='forbid')


class AreaIn(Strict):
    slug: Slug | None = None
    title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=120)] | None = None


class ProjectIn(Strict):
    creationKey: str = Field(pattern=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
    title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    area: AreaIn
    description: str = Field(default='', max_length=4000)
    researchQuestion: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]
    projectType: Literal[tuple(PROJECT_TYPES)] = 'investigation'


class Milestone(Strict):
    title: Line
    due: str = Field(default='', pattern=r'^(\d{4}-\d{2}-\d{2})?$')
    done: bool = False


class OverviewIn(Strict):
    expectedProjectRevision: int = Field(ge=1)
    researchQuestion: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]
    description: str = Field(default='', max_length=4000)
    objectives: list[Line] = Field(default_factory=list, max_length=20)
    status: Literal['planning', 'active', 'paused', 'completed']
    milestones: list[Milestone] = Field(default_factory=list, max_length=30)


class UploadIn(Strict):
    filename: str = Field(min_length=1, max_length=255)
    contentBase64: str = Field(min_length=1, max_length=35_000_000)
    role: Literal[DOCUMENT_ROLES] = 'draft'


class LifecycleIn(Strict):
    expectedProjectRevision: int = Field(ge=1)


class DeleteIn(Strict):
    confirmTitle: str = Field(min_length=1, max_length=160)


# Profile and identity ------------------------------------------------------------------------------------------------

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def slugify(value: str, fallback: str = 'research-project') -> str:
    return re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')[:40].strip('-') or fallback


def project_id_for(owner: str, creation_key: str, title: str) -> str:
    """Stable for one owner and one creation key, so a retried submission names the same project."""
    digest = hashlib.sha256(f'{PROGRAMME}\0{owner}\0{creation_key}'.encode()).hexdigest()[:12]
    return f'{slugify(title)}-{digest}'


def profile_of(package: dict | None) -> dict | None:
    for obj in ((package or {}).get('project') or {}).get('objects') or []:
        if isinstance(obj, dict) and obj.get('type') == PROFILE_TYPE and \
                (obj.get('profile') or {}).get('schema') == PROFILE_SCHEMA:
            return obj['profile']
    return None


def _with_profile(project: dict, profile: dict) -> dict:
    project = deepcopy(project)
    objects = [o for o in project.get('objects') or [] if not (isinstance(o, dict) and o.get('type') == PROFILE_TYPE)]
    project['objects'] = [{'id': PROFILE_ID, 'type': PROFILE_TYPE, 'profile': profile}, *objects]
    return project


def _store(db, owner: str, project_id: str, title: str, project: dict, expected: int, operation: str):
    payload = ProjectStoreRequest.model_validate({
        'schema': 'sc-workspace-sync-push/1.0', 'sourceProjectId': project_id, 'projectTitle': title,
        'expectedRevision': expected, 'operationId': operation, 'project': project})
    row, _ = repository.store_project(db, owner, payload)
    return row


def store_available(db) -> bool:
    return inspect(db.get_bind()).has_table(STORE_TABLE)


def attached_ids(db, owner: str) -> set[str] | None:
    if not store_available(db):
        return None
    rows = db.execute(text(f'SELECT project_id FROM {STORE_TABLE} WHERE user_key = :u'), {'u': owner}).scalars()
    return set(rows)


def ensure_attached(db, owner: str, project_id: str, title: str) -> str:
    """Idempotent: attach an owned project to the private research store (no-op when already attached)."""
    if not store_available(db):
        return 'unavailable'
    db.execute(text(f'INSERT INTO {STORE_TABLE} (user_key, project_id, title) VALUES (:u, :p, :t) '
                    'ON CONFLICT (user_key, project_id) DO NOTHING'), {'u': owner, 'p': project_id, 't': title})
    db.commit()
    return 'attached'


def _register(db, owner: str, project_id: str) -> dict | None:
    try:
        found = project_register(db, owner, project_id)
    except HTTPException:
        return None
    return _summary(project_id, found) if found else None


def known_areas(db, owner: str) -> list[dict]:
    areas = {slug: {'slug': slug, 'title': title, 'source': 'institutional'}
             for slug, title in INSTITUTIONAL_AREAS.items()}
    for item in repository.list_projects(db, owner):
        row = repository.get_project(db, owner, item['projectId'])
        area = (profile_of(row.package) or {}).get('researchArea') if row else None
        if area and area.get('slug') not in areas:
            areas[area['slug']] = {'slug': area['slug'], 'title': area['title'], 'source': 'owner-defined'}
    return sorted(areas.values(), key=lambda a: a['title'].lower())


def resolve_area(db, owner: str, area: AreaIn) -> dict:
    known = {a['slug']: a for a in known_areas(db, owner)}
    if area.slug:
        if area.slug not in known:
            raise HTTPException(422, 'Unknown research area. Choose an existing area or name a new one.')
        return known[area.slug]
    if not area.title:
        raise HTTPException(422, 'Choose a research area or name a new one.')
    slug = slugify(area.title, 'research-area')
    return known.get(slug) or {'slug': slug, 'title': area.title, 'source': 'owner-defined'}


# Creation -------------------------------------------------------------------------------------------------------------

def create_project(db, owner: str, body: ProjectIn) -> tuple[dict, bool]:
    project_id = project_id_for(owner, body.creationKey, body.title)
    existing = repository.get_project(db, owner, project_id)
    if existing is not None:
        profile = profile_of(existing.package)
        if not profile or profile.get('creationKey') != body.creationKey:
            raise HTTPException(409, 'A different project already uses this identity.')
        # A retried submission: finish any incomplete step and return the same project.
        ensure_attached(db, owner, project_id, existing.title)
        return repository.project_metadata(existing), False
    area = resolve_area(db, owner, body.area)
    profile = {
        'schema': PROFILE_SCHEMA, 'projectId': project_id, 'title': body.title,
        'researchArea': area, 'description': body.description.strip(), 'researchQuestion': body.researchQuestion,
        'projectType': body.projectType, 'objectives': [], 'status': 'active', 'milestones': [],
        'visibility': 'private', 'publication': 'author-controlled',
        'createdAt': _now(), 'updatedAt': _now(), 'createdVia': PROGRAMME, 'creationKey': body.creationKey,
    }
    project = _with_profile({'schema': 'sc-workspace-project/20.0', 'id': project_id, 'title': body.title,
                             'objects': []}, profile)
    row = _store(db, owner, project_id, body.title, project, 0, 'research-project-create-' + body.creationKey)
    meta = repository.project_metadata(row)
    ensure_attached(db, owner, project_id, body.title)
    return meta, True


# Read model -----------------------------------------------------------------------------------------------------------

def _files_for(db, owner: str, project_id: str) -> list[dict]:
    return [f for f in object_store.list_artifacts(db, owner) if f['projectId'] == project_id]


def _ext(name: str) -> str:
    return '.' + name.rsplit('.', 1)[-1].lower() if '.' in name else ''


def _role(item: dict) -> str:
    role = (item.get('metadata') or {}).get('documentRole')
    if role in DOCUMENT_ROLES:
        return role
    ext = _ext(item['filename'])
    return ('figure' if ext in FIGURE_EXTENSIONS else 'reference' if ext == '.ris'
            else 'data' if ext in ('.csv', '.json', '.geojson', '.xlsx') else 'document')


def _file_view(project_id: str, item: dict) -> dict:
    base = HOME + '/' + quote(project_id, safe='') + '/files/' + quote(item['artifactId'], safe='')
    return {'artifactId': item['artifactId'], 'filename': item['filename'], 'mediaType': item['mediaType'],
            'bytes': item['bytes'], 'sha256': item['sha256'], 'createdAt': item['createdAt'], 'role': _role(item),
            'viewUrl': base if _ext(item['filename']) in ('.docx', '.pdf') else None,
            'downloadUrl': base + '/content'}


def project_summary(db, owner: str, item: dict, attached: set[str] | None) -> dict:
    row = repository.get_project(db, owner, item['projectId'])
    profile = profile_of(row.package) if row else None
    area = (profile or {}).get('researchArea')
    if area is None:
        register = _register(db, owner, item['projectId'])
        if register:
            area = {'slug': register['researchArea']['id'], 'title': register['researchArea']['name'],
                    'source': 'document-register'}
    return {
        'projectId': item['projectId'], 'title': item['title'], 'revision': item['revision'],
        'updatedAt': item['backedUpAt'], 'kind': 'research-project' if profile else 'existing-project',
        'researchArea': area, 'status': (profile or {}).get('status'),
        'researchQuestion': (profile or {}).get('researchQuestion'),
        'privateResearchStore': ('unavailable' if attached is None
                                 else 'attached' if item['projectId'] in attached else 'not-attached'),
        'dashboardUrl': HOME + '/' + quote(item['projectId'], safe=''),
    }


def list_view(db, owner: str) -> dict:
    attached = attached_ids(db, owner)
    projects = [project_summary(db, owner, p, attached) for p in repository.list_projects(db, owner)]
    return {'schema': 'sc-research-project-list/1.0', 'projects': projects, 'areas': known_areas(db, owner),
            'projectTypes': [{'id': k, 'title': v} for k, v in PROJECT_TYPES.items()]}


def _notebooks(db, owner: str, project_id: str) -> list[dict]:
    rows = db.scalars(select(NotebookHead).where(NotebookHead.user_key == owner,
                                                 NotebookHead.project_id == project_id)).all()
    return [{'notebookId': r.notebook_id, 'title': r.title, 'revision': r.revision,
             'url': '/v1/desk/notebooks?project=' + quote(project_id, safe='') + '&notebook=' + quote(r.notebook_id, safe='')}
            for r in rows]


def _activity(db, owner: str, project_id: str, files: list[dict]) -> list[dict]:
    events = [{'at': r['backedUpAt'], 'label': f'Project revision {r["revision"]} saved'}
              for r in repository.list_project_revisions(db, owner, project_id)[:10]]
    events += [{'at': f['createdAt'], 'label': f'Added {f["filename"]}'} for f in files]
    return sorted(events, key=lambda e: e['at'] or '', reverse=True)[:12]


def deletable(row, files: list[dict], legacy: list[dict], notebooks: list[dict], db, owner: str) -> bool:
    """Only an untouched project created here may be deleted: no files, records, notebooks or other objects."""
    profile = profile_of(row.package)
    if not profile or profile.get('createdVia') != PROGRAMME or files or legacy or notebooks:
        return False
    if len(row.package.get('project', {}).get('objects') or []) != 1:
        return False
    if not inspect(db.get_bind()).has_table('workspace_private_research_branches'):
        return True
    return db.execute(text('SELECT 1 FROM workspace_private_research_branches WHERE user_key = :u AND project_id = :p'),
                      {'u': owner, 'p': row.project_id}).first() is None


def dashboard(db, owner: str, project_id: str) -> dict:
    row = _project(db, owner, project_id)
    attached = attached_ids(db, owner)
    summary = project_summary(db, owner, {**repository.project_metadata(row), 'projectId': project_id}, attached)
    profile = profile_of(row.package)
    native = _files_for(db, owner, project_id)
    legacy, _ = read_legacy_artifacts(db, owner, project_id)
    register = _register(db, owner, project_id)
    notebooks = _notebooks(db, owner, project_id)
    cites = collection(row.package)['items']
    links = bindings(row.package)
    gone = lifecycle.hidden(row.package, 'file')
    files = [{**_file_view(project_id, f), **_removal(db, owner, row, f)} for f in native if f['artifactId'] not in gone]
    trash = lifecycle.trash_view(row)
    pid = quote(project_id, safe='')
    outputs = []
    for doc in latest_documents(row.package):
        last = (snapshots(row.package, doc['documentId']) or [{}])[-1]
        binding = links.get(doc['documentId'])
        outputs.append({**doc, 'publicationType': last.get('publicationType'),
                        'scientificStatus': last.get('scientificStatus'),
                        'binding': ({'areaSlug': binding['areaSlug'], 'articleSlug': binding['articleSlug']}
                                    if binding else None),
                        'visibility': 'bound to a private Research article' if binding else 'private (Workspace only)'})
    reports = [o for o in row.package.get('project', {}).get('objects') or []
               if isinstance(o, dict) and o.get('type') == 'research-report-reference']
    return {
        'schema': 'sc-research-project-dashboard/1.0',
        'project': {**summary, 'storageMode': row.storage_mode},
        'profile': profile,
        'overview': {
            'status': (profile or {}).get('status'), 'researchQuestion': (profile or {}).get('researchQuestion'),
            'description': (profile or {}).get('description'), 'objectives': (profile or {}).get('objectives', []),
            'milestones': (profile or {}).get('milestones', []), 'projectType': (profile or {}).get('projectType'),
            'recentActivity': _activity(db, owner, project_id, native),
            'editable': profile is not None,
        },
        'documents': {
            'registered': register['documents'] if register else [],
            'registerRevision': register['registerRevision'] if register else None,
            'files': [f for f in files if f['role'] != 'figure'],
            'legacy': [{k: x[k] for k in ('artifactId', 'filename', 'sha256', 'bytes', 'downloadUrl')} for x in legacy],
            'roles': list(DOCUMENT_ROLES),
        },
        'library': {
            'count': len(cites),
            'items': [{'key': x['key'], 'title': x.get('title'), 'year': x.get('year'), 'type': x.get('type')}
                      for x in cites[:200]],
            'referenceFiles': [{'artifactId': f['artifactId'], 'filename': f['filename']} for f in files
                               if _ext(f['filename']) in REFERENCE_EXTENSIONS and f['role'] in ('reference', 'data')],
        },
        'analysis': {
            'notebooks': notebooks,
            'deskUrl': '/v1/desk/notebooks?project=' + pid,
            'datasets': [f for f in files if f['role'] == 'data'],
        },
        'figures': {
            'files': [f for f in files if f['role'] == 'figure'],
            'reports': len(reports),
            'studioUrl': BASE,
        },
        'publications': {
            'outputs': outputs,
            'studioUrl': BASE + '/publication?project=' + pid,
            'defaultArea': (profile or {}).get('researchArea') or summary['researchArea'],
            'policy': ('Every output is private. Nothing is published unless you take it through the Research '
                       'editorial steps for that output and authorize it yourself.'),
            'disclosure': DISCLOSURE,
        },
        'deletable': deletable(row, native, legacy, notebooks, db, owner),
        'trash': {'publications': trash['publications'], 'files': trash['files'], 'policy': trash['policy'],
                  'studioTrashUrl': BASE + '/publication/projects/' + pid + '/trash'},
    }


def _removal(db, owner: str, row, item: dict) -> dict:
    """SC-PUB-DRAFT-01: whether Remove (move to Trash) is offered for this uploaded file, and why not."""
    if (item.get('metadata') or {}).get('source') == 'docx-import':
        return {'removable': False, 'protection': 'Extracted from an imported Word manuscript; managed with its drafts.'}
    used = lifecycle.file_references(db, owner, row, item['artifactId'])['active']
    if used:
        names = ', '.join(u.get('title') or u.get('kind') for u in used[:3])
        return {'removable': False, 'protection': 'Used by ' + names}
    return {'removable': True, 'protection': None}


# API ------------------------------------------------------------------------------------------------------------------

@router.get('/api/projects')
def api_list(request: Request):
    owner = _subject(request)
    with session_scope() as db:
        return JSONResponse(list_view(db, owner), headers=HEADERS)


@router.post('/api/projects')
def api_create(body: ProjectIn, request: Request):
    owner = _subject(request)
    _write(request)
    with session_scope() as db:
        meta, created = create_project(db, owner, body)
    return JSONResponse({'project': meta, 'created': created,
                         'dashboardUrl': HOME + '/' + quote(meta['projectId'], safe='')},
                        status_code=201 if created else 200, headers=HEADERS)


@router.get('/api/projects/{project_id}')
def api_dashboard(project_id: str, request: Request):
    owner = _subject(request)
    with session_scope() as db:
        return JSONResponse(dashboard(db, owner, project_id), headers=HEADERS)


@router.post('/api/projects/{project_id}/setup')
def api_complete_setup(project_id: str, request: Request):
    owner = _subject(request)
    _write(request)
    with session_scope() as db:
        row = _project(db, owner, project_id)
        if profile_of(row.package) is None:
            raise HTTPException(409, 'Only projects created as research projects are set up here.')
        return JSONResponse({'privateResearchStore': ensure_attached(db, owner, project_id, row.title)},
                            headers=HEADERS)


@router.post('/api/projects/{project_id}/overview')
def api_overview(project_id: str, body: OverviewIn, request: Request):
    owner = _subject(request)
    _write(request)
    with session_scope() as db:
        row = _locked_project(db, owner, project_id)
        profile = profile_of(row.package)
        if profile is None:
            raise HTTPException(409, 'This existing project has no research profile; it is not changed here.')
        if row.revision != body.expectedProjectRevision:
            raise HTTPException(409, 'Workspace project changed. Reload before saving.')
        profile = {**profile, 'researchQuestion': body.researchQuestion, 'description': body.description.strip(),
                   'objectives': list(body.objectives), 'status': body.status,
                   'milestones': [m.model_dump() for m in body.milestones], 'updatedAt': _now()}
        updated = _store(db, owner, project_id, row.title, _with_profile(row.package['project'], profile),
                         row.revision, 'research-project-overview-' + uuid4().hex)
        return JSONResponse({'project': repository.project_metadata(updated), 'profile': profile}, headers=HEADERS)


@router.post('/api/projects/{project_id}/documents', status_code=201)
def api_add_document(project_id: str, body: UploadIn, request: Request):
    """Add an immutable file to the project's native store. Same rules as private research uploads: safe names,
    supported types, no replacement of an existing name and no duplicate bytes."""
    owner = _subject(request)
    _write(request)
    filename, media_type = _filename(body.filename)
    from .config import get_settings
    if len(body.contentBase64) > 4 * ((get_settings().max_artifact_bytes + 2) // 3):
        raise HTTPException(413, 'Research upload exceeds the configured limit.')
    try:
        raw = base64.b64decode(body.contentBase64, validate=True)
    except ValueError as exc:
        raise HTTPException(400, 'Invalid research-file encoding.') from exc
    if not raw:
        raise HTTPException(400, 'Empty file.')
    digest = hashlib.sha256(raw).hexdigest()
    with session_scope() as db:
        row = _locked_project(db, owner, project_id)
        gone = lifecycle.hidden(row.package, 'file')
        for item in _files_for(db, owner, project_id):
            if item['sha256'] == digest and item['artifactId'] in gone:
                raise HTTPException(409, {'message': 'This file is in Trash. Restore it instead of uploading it again.',
                                          'artifactId': item['artifactId']})
            if item['sha256'] == digest:
                raise HTTPException(409, 'This file already exists in the project.')
            if item['filename'] == filename:
                raise HTTPException(409, 'This filename already exists; replacement is disabled.')
        payload = ArtifactStoreRequest.model_validate({
            'schema': 'sc-workspace-artifact-store/1.0', 'artifactId': 'research-file-' + uuid4().hex,
            'projectId': project_id, 'filename': filename, 'mediaType': media_type,
            'contentBase64': body.contentBase64, 'expectedRevision': 0,
            'metadata': {'source': 'private-research', 'researchProjectId': project_id,
                         'documentRole': body.role, 'addedVia': PROGRAMME}})
        row = object_store.store_artifact(db, owner, payload)
        return JSONResponse(_file_view(project_id, object_store.artifact_metadata(row)), status_code=201,
                            headers=HEADERS)


@router.post('/api/projects/{project_id}/delete')
def api_delete(project_id: str, body: DeleteIn, request: Request):
    owner = _subject(request)
    _write(request)
    with session_scope() as db:
        row = _locked_project(db, owner, project_id)
        legacy, _ = read_legacy_artifacts(db, owner, project_id)
        if not deletable(row, _files_for(db, owner, project_id), legacy, _notebooks(db, owner, project_id), db, owner):
            raise HTTPException(409, 'Only an empty project created here can be deleted.')
        if body.confirmTitle.strip() != row.title:
            raise HTTPException(422, 'Type the project title exactly to delete it.')
        if store_available(db):
            db.execute(text(f'DELETE FROM {STORE_TABLE} WHERE user_key = :u AND project_id = :p'),
                       {'u': owner, 'p': project_id})
        # delete_project records a deletion receipt and commits the store row removal in the same transaction.
        repository.delete_project(db, owner, project_id)
    return JSONResponse({'deleted': project_id}, headers=HEADERS)


# SC-PUB-DRAFT-01: Remove (move to Trash) and Restore uploaded files. Bytes are never deleted.

@router.get('/api/projects/{project_id}/trash')
def api_trash(project_id: str, request: Request):
    owner = _subject(request)
    with session_scope() as db:
        return JSONResponse(lifecycle.trash_view(_project(db, owner, project_id)), headers=HEADERS)


@router.post('/api/projects/{project_id}/files/{artifact_id}/remove')
def api_remove_file(project_id: str, artifact_id: str, body: LifecycleIn, request: Request):
    owner = _subject(request)
    _write(request)
    with session_scope() as db:
        row = _locked_project(db, owner, project_id)
        artifact = object_store.get_artifact(db, owner, artifact_id)
        if artifact is None or artifact.project_id != project_id:
            raise HTTPException(404, 'Research file not found in this project.')
        updated, record = lifecycle.trash_file(db, owner, row, artifact, body.expectedProjectRevision)
        return JSONResponse({'trashed': record, 'project': repository.project_metadata(updated)}, headers=HEADERS)


@router.post('/api/projects/{project_id}/files/{artifact_id}/restore')
def api_restore_file(project_id: str, artifact_id: str, body: LifecycleIn, request: Request):
    owner = _subject(request)
    _write(request)
    with session_scope() as db:
        updated, record = lifecycle.restore_file(db, owner, _locked_project(db, owner, project_id), artifact_id,
                                                 body.expectedProjectRevision)
        return JSONResponse({'restored': record, 'project': repository.project_metadata(updated)}, headers=HEADERS)


# Native project files -------------------------------------------------------------------------------------------------

def _native(db, owner: str, project_id: str, artifact_id: str):
    _project(db, owner, project_id)
    artifact = object_store.get_artifact(db, owner, artifact_id)
    if artifact is None or artifact.project_id != project_id:
        raise HTTPException(404, 'Research file not found in this project.')
    raw = object_store.read_artifact_content(artifact)
    if hashlib.sha256(raw).hexdigest() != artifact.sha256:
        raise HTTPException(409, 'Research file integrity verification failed.')
    return artifact, raw


@router.get('/{project_id}/files/{artifact_id}', response_class=HTMLResponse)
def view_file(project_id: str, artifact_id: str, request: Request):
    owner = page_subject(request, _subject)
    with session_scope() as db:
        row = _project(db, owner, project_id)
        artifact, raw = _native(db, owner, project_id, artifact_id)
        title = row.title
    content = HOME + '/' + quote(project_id, safe='') + '/files/' + quote(artifact_id, safe='') + '/content'
    crumbs = (f'<nav class="crumbs"><a href="{HOME}">Research projects</a> › '
              f'<a href="{HOME}/{quote(project_id, safe="")}#documents">{escape(title)}</a></nav>')
    facts = (f'<dl class="facts"><dt>File</dt><dd>{escape(artifact.filename)}</dd><dt>SHA-256</dt>'
             f'<dd><code>{artifact.sha256}</code> (verified on this request)</dd></dl>')
    if _ext(artifact.filename) == '.pdf':
        return _page(artifact.filename, crumbs + f'<header class="meta"><h1>{escape(artifact.filename)}</h1>'
                     f'<div class="badges"><span class="badge private">Private</span></div>{facts}'
                     f'<div class="actions"><a href="{content}">Open PDF</a></div></header>')
    if _ext(artifact.filename) != '.docx':
        raise HTTPException(415, 'This file type is downloaded, not viewed.')
    html, stats = render_docx(raw)
    missing = ', '.join(f'{v} {k}' for k, v in stats['unrendered'].items() if v)
    fidelity = (f'Rendered from the original DOCX: {stats["figuresRendered"]} of {stats["figuresInSource"]} figures, '
                f'{stats["tablesRendered"]} of {stats["tablesInSource"]} tables, {stats["footnotes"]} footnotes.'
                + (f' Not rendered: {escape(missing)}. Use the original for these.' if missing else '')
                + ' Page layout and fonts follow this viewer, not Word.')
    return _page(artifact.filename, crumbs + f'<header class="meta"><h1>{escape(artifact.filename)}</h1>'
                 f'<div class="badges"><span class="badge private">Private</span></div>{facts}'
                 f'<div class="actions"><a href="{content}">Download original</a></div>'
                 f'<div class="fidelity{"" if stats["complete"] else " incomplete"}">{fidelity}</div></header>'
                 f'<article class="document">{html}</article>')


@router.get('/{project_id}/files/{artifact_id}/content')
def file_content(project_id: str, artifact_id: str, request: Request):
    owner = _subject(request)
    with session_scope() as db:
        artifact, raw = _native(db, owner, project_id, artifact_id)
    name = quote(artifact.filename, safe='')
    if _ext(artifact.filename) == '.pdf' and raw.startswith(b'%PDF-'):
        return Response(raw, media_type='application/pdf', headers={
            **HEADERS, 'Content-Disposition': f"inline; filename*=UTF-8''{name}", 'X-Research-SHA256': artifact.sha256})
    return Response(raw, media_type='application/octet-stream', headers={
        **HEADERS, 'Content-Disposition': f"attachment; filename*=UTF-8''{name}", 'Content-Security-Policy': 'sandbox',
        'X-Research-SHA256': artifact.sha256})


# Pages ----------------------------------------------------------------------------------------------------------------

APP_STYLE = STYLE + """
main.app{max-width:1040px;margin:0 auto;padding:0 16px 48px;font:15px/1.5 system-ui,sans-serif}
main.app h1{font:600 26px/1.25 system-ui,sans-serif;margin:18px 0 4px}main.app h2{font:600 18px system-ui,sans-serif;margin:22px 0 8px}
.lede{color:var(--muted);margin:0 0 16px}.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:16px;margin:12px 0}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px}.grid .card{margin:0}
.card h3{font:600 16px system-ui,sans-serif;margin:0 0 4px}.muted{color:var(--muted)}a{color:var(--accent)}
button,.button{font:600 14px system-ui,sans-serif;background:var(--accent);color:var(--bg);border:0;border-radius:6px;padding:9px 14px;cursor:pointer;text-decoration:none;display:inline-block}
button.secondary{background:transparent;color:var(--accent);border:1px solid var(--accent)}button:disabled{opacity:.5;cursor:default}
label{display:block;font-weight:600;margin:12px 0 4px}input,select,textarea{width:100%;font:15px system-ui,sans-serif;padding:8px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--fg)}
textarea{min-height:80px}.hint{font-size:13px;color:var(--muted);margin:2px 0}
nav.tabs{display:flex;flex-wrap:wrap;gap:4px;border-bottom:1px solid var(--line);margin:16px 0}
nav.tabs a{padding:8px 12px;text-decoration:none;color:var(--muted);border-bottom:2px solid transparent}
nav.tabs a[aria-current=page]{color:var(--fg);border-color:var(--accent)}
section.panel[hidden]{display:none}ul.items{list-style:none;padding:0;margin:0}ul.items li{padding:8px 0;border-bottom:1px solid var(--line);overflow-wrap:anywhere}
.status{min-height:24px;margin:8px 0}.status.error{color:var(--warn)}dialog{max-width:640px;width:calc(100% - 32px);border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--fg)}
.row{display:flex;flex-wrap:wrap;gap:8px;align-items:center}.row>*{flex:0 0 auto}
"""

COMMON_JS = r"""
const HOME='/v1/private-research/reporting-studio/research-projects', API=HOME+'/api/projects';
const $=id=>document.getElementById(id);
function h(tag,attrs,...kids){const e=document.createElement(tag);for(const[k,v]of Object.entries(attrs||{})){
 if(v==null||v===false)continue;if(k==='onclick'||k==='onsubmit'||k==='onchange')e[k]=v;else e.setAttribute(k,v===true?'':v)}
 for(const k of kids.flat()){if(k!=null&&k!==false)e.append(k)}return e}
function signInPrompt(show){let b=document.getElementById('scSignIn');if(!show){if(b)b.remove();return}if(b)return;b=document.createElement('div');b.id='scSignIn';b.setAttribute('role','alert');b.style.cssText='position:sticky;top:0;z-index:9999;background:#7a1f1f;color:#fff;padding:10px 16px;font:14px system-ui;text-align:center';const a=document.createElement('a');a.href='/v1/auth/login?stepUp=true&returnTo='+encodeURIComponent(location.pathname+location.search);a.target='_blank';a.rel='noopener';a.style.color='#fff';a.style.fontWeight='600';a.textContent='Sign in again (new tab)';b.append('Your session has expired. This page and any unsaved work are kept. ',a,', then return here and retry.');document.body.prepend(b)}
async function api(path,options={}){const r=await fetch(path,{credentials:'same-origin',cache:'no-store',...options,
 headers:{...(options.body?{'Content-Type':'application/json'}:{}),...(options.headers||{})}});
 const t=await r.text();let d=null;try{d=JSON.parse(t)}catch(e){}
 signInPrompt(r.status===401);
 if(!r.ok){const m=d&&d.detail?(typeof d.detail==='string'?d.detail:JSON.stringify(d.detail)):t.slice(0,200);throw Error(m||('Request failed ('+r.status+')'))}
 return d}
function say(msg,error){const s=$('status');s.textContent=msg||'';s.className='status'+(error?' error':'')}
async function busy(btn,fn){btn.disabled=true;try{await fn()}catch(e){say(e.message,true)}finally{btn.disabled=false}}
"""

HUB_JS = COMMON_JS + r"""
const KEY='sc-research-project-creation-key';
function creationKey(){let k=null;try{k=sessionStorage.getItem(KEY)}catch(e){}
 if(!k){k=crypto.randomUUID();try{sessionStorage.setItem(KEY,k)}catch(e){}}return k}
function areaLabel(a){return a?a.title:'No research area'}
async function load(){
 const d=await api(API);const areas=$('area');areas.replaceChildren(
  ...d.areas.map(a=>h('option',{value:a.slug},a.title)),h('option',{value:'__new'},'New research area…'));
 $('type').replaceChildren(...d.projectTypes.map(t=>h('option',{value:t.id},t.title)));
 const list=$('projects');list.replaceChildren();
 const groups={};for(const p of d.projects){const k=areaLabel(p.researchArea);(groups[k]=groups[k]||[]).push(p)}
 for(const k of Object.keys(groups).sort()){list.append(h('h2',{},k));const g=h('div',{class:'grid'});
  for(const p of groups[k])g.append(h('div',{class:'card'},h('h3',{},h('a',{href:p.dashboardUrl},p.title)),
   p.researchQuestion?h('p',{},p.researchQuestion):null,
   h('p',{class:'muted'},p.kind==='research-project'?('Research project · '+(p.status||'active')):'Existing project · not changed here',
    p.privateResearchStore==='not-attached'&&p.kind==='research-project'?' · setup incomplete':'')));
  list.append(g)}
 if(!d.projects.length)list.append(h('p',{class:'muted'},'No projects yet.'))}
$('area').onchange=()=>{$('new-area').hidden=$('area').value!=='__new'};
$('open-create').onclick=()=>{$('create').showModal();$('title').focus()};
$('cancel').onclick=()=>$('create').close();
$('create-form').onsubmit=e=>{e.preventDefault();busy(e.submitter,async()=>{
 const area=$('area').value==='__new'?{title:$('new-area-title').value}:{slug:$('area').value};
 say('Creating your private project workspace…');
 const d=await api(API,{method:'POST',body:JSON.stringify({creationKey:creationKey(),title:$('title').value,area,
  description:$('description').value,researchQuestion:$('question').value,projectType:$('type').value})});
 try{sessionStorage.removeItem(KEY)}catch(e){}location.assign(d.dashboardUrl)})};
load().catch(e=>say(e.message,true));
"""

HUB_HTML = """<main class="app"><nav class="crumbs"><a href="/v1/private-research/reporting-studio">Reporting Studio</a> ›
Research projects</nav><div class="row" style="justify-content:space-between"><div><h1>Research projects</h1>
<p class="lede">Every project has its own private workspace. Nothing is published unless you authorize it.</p></div>
<button id="open-create" type="button">New Research Project</button></div><p id="status" class="status" role="status" aria-live="polite"></p>
<div id="projects"></div></main>
<dialog id="create" aria-labelledby="create-heading"><form id="create-form"><h2 id="create-heading">New Research Project</h2>
<label for="title">Project title</label><input id="title" required maxlength="160">
<label for="area">Research area</label><select id="area"></select>
<div id="new-area" hidden><label for="new-area-title">New area name</label><input id="new-area-title" maxlength="120">
<p class="hint">A new area stays private. It is created in Research only when you later bind an output to it.</p></div>
<label for="question">Research question</label><textarea id="question" required maxlength="2000"></textarea>
<label for="description">Description</label><textarea id="description" maxlength="4000"></textarea>
<label for="type">Project type</label><select id="type"></select>
<p class="hint">The project ID is created for you. The project and its workspace are private.</p>
<div class="row" style="margin-top:16px"><button type="submit">Create project</button>
<button type="button" class="secondary" id="cancel">Cancel</button></div></form></dialog>"""

DASH_JS = COMMON_JS + r"""
const PID=decodeURIComponent(location.pathname.split('/').pop());const PURL=API+'/'+encodeURIComponent(PID);
const TABS=['overview','documents','library','analysis','figures','publications'];let D=null;
function tab(){const t=TABS.includes(location.hash.slice(1))?location.hash.slice(1):'overview';
 for(const n of TABS){$(n).hidden=n!==t;const a=$('tab-'+n);if(n===t)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current')}}
window.onhashchange=tab;
const encode=b=>{let o='';for(let i=0;i<b.length;i+=32768)o+=String.fromCharCode(...b.subarray(i,i+32768));return btoa(o)};
const short=s=>s?s.slice(0,12)+'…':'';
function fileItem(f){return h('li',{},f.viewUrl?h('a',{href:f.viewUrl},f.filename):h('span',{},f.filename),' ',
 h('span',{class:'muted'},'· '+f.role+' · '+f.bytes+' bytes · sha256 '+short(f.sha256)+' · '),h('a',{href:f.downloadUrl},'download'),' ',
 f.removable?h('button',{type:'button',class:'secondary',onclick:e=>removeFile(e.target,f)},'Remove'):h('span',{class:'muted',title:f.protection||''},'· protected'))}
function removeFile(btn,f){if(!window.confirm('Move “'+f.filename+'” to Trash?\n\nIt disappears from this project’s lists. Nothing is erased: you can restore it from Trash, and drafts and revisions that used it are unchanged.'))return;
 busy(btn,async()=>{await api(PURL+'/files/'+encodeURIComponent(f.artifactId)+'/remove',{method:'POST',body:JSON.stringify({expectedProjectRevision:D.project.revision})});
  await reload();say(f.filename+' moved to Trash. Restore it from Trash at any time.')})}
const STUDIO_DOCS='/v1/private-research/reporting-studio/publication/projects/'+encodeURIComponent(PID)+'/documents/';
function trashItem(x){const label=x.kind==='file'?x.filename:x.title,when=(x.trashedAt||'').slice(0,16).replace('T',' ');
 return h('li',{},h('span',{},label),h('span',{class:'muted'},' · '+(x.kind==='file'?'file':'draft')+' · in Trash since '+when+' '),
  h('button',{type:'button',class:'secondary',onclick:e=>busy(e.target,async()=>{
   await api((x.kind==='file'?PURL+'/files/':STUDIO_DOCS)+encodeURIComponent(x.id)+'/restore',{method:'POST',body:JSON.stringify({expectedProjectRevision:D.project.revision})});
   await reload();say(label+' restored.')})},'Restore'))}
function empty(list,msg){if(!list.childElementCount)list.append(h('li',{class:'muted'},msg))}
function render(){const p=D.project,o=D.overview;document.title=p.title+' | Research projects';
 $('title').textContent=p.title;
 $('meta').textContent=(p.researchArea?p.researchArea.title:'No research area')+' · '+(p.kind==='research-project'?'Research project':'Existing project')+' · Private · revision '+p.revision;
 $('setup').hidden=!(p.kind==='research-project'&&p.privateResearchStore==='not-attached');
 // Overview
 $('ov-question').textContent=o.researchQuestion||'—';$('ov-description').textContent=o.description||'—';
 $('ov-status').textContent=o.status||'—';
 $('ov-objectives').replaceChildren(...(o.objectives||[]).map(x=>h('li',{},x)));empty($('ov-objectives'),'No objectives yet.');
 $('ov-milestones').replaceChildren(...(o.milestones||[]).map(m=>h('li',{},(m.done?'✓ ':'○ ')+m.title+(m.due?' · due '+m.due:''))));empty($('ov-milestones'),'No milestones yet.');
 $('ov-activity').replaceChildren(...o.recentActivity.map(a=>h('li',{},h('span',{class:'muted'},(a.at||'').slice(0,16).replace('T',' ')+' '),a.label)));
 $('ov-edit').hidden=!o.editable;$('ov-existing').hidden=o.editable;
 // Documents
 const reg=$('doc-registered');reg.replaceChildren(...D.documents.registered.map(d=>h('li',{},h('a',{href:d.viewUrl},d.title),
  h('span',{class:'sub muted'},' · '+d.revisionLabel+' · '+d.submissionLabel))));empty(reg,'No registered documents.');
 const fl=$('doc-files');fl.replaceChildren(...D.documents.files.map(fileItem));empty(fl,'No files added yet.');
 const lg=$('doc-legacy');lg.replaceChildren(...D.documents.legacy.map(x=>h('li',{},h('a',{href:x.downloadUrl},x.filename),
  h('span',{class:'muted'},' · '+x.bytes+' bytes · sha256 '+short(x.sha256)))));$('doc-legacy-wrap').hidden=!D.documents.legacy.length;
 // Library
 $('lib-count').textContent=D.library.count+' reference'+(D.library.count===1?'':'s')+' in this project.';
 const li=$('lib-items');li.replaceChildren(...D.library.items.map(x=>h('li',{},h('code',{},x.key),' ',x.title||'',x.year?' ('+x.year+')':'')));empty(li,'No references yet.');
 $('lib-file').replaceChildren(h('option',{value:''},'Choose an uploaded .ris or .json reference file'),...D.library.referenceFiles.map(f=>h('option',{value:f.artifactId},f.filename)));
 // Analysis
 $('an-desk').href=D.analysis.deskUrl;
 const nb=$('an-notebooks');nb.replaceChildren(...D.analysis.notebooks.map(n=>h('li',{},h('a',{href:n.url},n.title),h('span',{class:'muted'},' · revision '+n.revision))));empty(nb,'No notebooks for this project yet.');
 const ds=$('an-data');ds.replaceChildren(...D.analysis.datasets.map(fileItem));empty(ds,'No data files yet.');
 // Figures
 const fg=$('fig-files');fg.replaceChildren(...D.figures.files.map(fileItem));empty(fg,'No figure files yet.');
 $('fig-reports').textContent=D.figures.reports+' saved Reporting Studio revision'+(D.figures.reports===1?'':'s')+'.';
 // Publications
 $('pub-studio').href=D.publications.studioUrl;$('pub-policy').textContent=D.publications.policy;
 $('pub-disclosure').textContent=D.publications.disclosure;
 $('pub-area').textContent=D.publications.defaultArea?D.publications.defaultArea.title+' ('+D.publications.defaultArea.slug+')':'None set';
 const po=$('pub-outputs');po.replaceChildren(...D.publications.outputs.map(x=>h('li',{},h('a',{href:D.publications.studioUrl},x.title),
  h('span',{class:'muted'},' · '+(x.publicationType||'output')+' · revision '+x.revision+' · '+x.visibility))));empty(po,'No outputs yet.');
 const tr=$('doc-trash');tr.replaceChildren(...[...D.trash.publications,...D.trash.files].map(trashItem));empty(tr,'Trash is empty.');
 $('trash-policy').textContent=D.trash.policy.trash+' '+D.trash.policy.files+' '+D.trash.policy.permanentDeletion;
 $('danger').hidden=!D.deletable}
async function reload(){D=await api(PURL);render();tab()}
function fillOverview(){const o=D.overview;$('f-question').value=o.researchQuestion||'';$('f-description').value=o.description||'';
 $('f-status').value=o.status||'active';$('f-objectives').value=(o.objectives||[]).join('\n');
 $('f-milestones').value=(o.milestones||[]).map(m=>(m.done?'[x] ':'[ ] ')+m.title+(m.due?' | '+m.due:'')).join('\n')}
$('ov-edit').onclick=()=>{fillOverview();$('overview-dialog').showModal()};
$('ov-cancel').onclick=()=>$('overview-dialog').close();
$('overview-form').onsubmit=e=>{e.preventDefault();busy(e.submitter,async()=>{
 const milestones=$('f-milestones').value.split('\n').map(s=>s.trim()).filter(Boolean).map(s=>{const done=/^\[x\]/i.test(s);
  const [t,due]=s.replace(/^\[[ x]\]\s*/i,'').split('|').map(x=>x.trim());return{title:t,due:due||'',done}});
 await api(PURL+'/overview',{method:'POST',body:JSON.stringify({expectedProjectRevision:D.project.revision,
  researchQuestion:$('f-question').value,description:$('f-description').value,status:$('f-status').value,
  objectives:$('f-objectives').value.split('\n').map(s=>s.trim()).filter(Boolean),milestones})});
 $('overview-dialog').close();await reload();say('Overview saved as a new project revision.')})};
$('upload-form').onsubmit=e=>{e.preventDefault();busy(e.submitter,async()=>{const f=$('upload-file').files[0];if(!f)return;
 say('Adding '+f.name+'…');await api(PURL+'/documents',{method:'POST',body:JSON.stringify({filename:f.name,role:$('upload-role').value,
  contentBase64:encode(new Uint8Array(await f.arrayBuffer()))})});$('upload-file').value='';await reload();say('Added '+f.name+'. It is private and immutable.')})};
const CITE='/v1/private-research/reporting-studio/publication/citations';
$('lib-import').onclick=e=>busy(e.target,async()=>{const id=$('lib-file').value;if(!id)return say('Choose a reference file first.',true);
 const d=await api(CITE+'/projects/'+encodeURIComponent(PID)+'/import-source',{method:'POST',body:JSON.stringify({sourceArtifactId:id,expectedProjectRevision:D.project.revision})});
 await reload();say('Imported '+d.import.added.length+' new, '+d.import.reused.length+' already present, '+d.import.rejected.length+' rejected.')});
$('lib-search-form').onsubmit=e=>{e.preventDefault();busy(e.submitter,async()=>{
 const d=await api(CITE+'/library/search?q='+encodeURIComponent($('lib-q').value));const items=d.items||[];
 $('lib-results').replaceChildren(...items.slice(0,20).map(r=>h('li',{},(r.title||r.libraryObjectId)+' ',h('button',{type:'button',class:'secondary',onclick:ev=>busy(ev.target,async()=>{
  await api(CITE+'/projects/'+encodeURIComponent(PID)+'/import-library',{method:'POST',body:JSON.stringify({recordId:r.libraryObjectId,expectedProjectRevision:D.project.revision})});
  await reload();say('Added to this project’s library.')})},'Add to project'))));empty($('lib-results'),'No Library results.')})};
$('output-form').onsubmit=e=>{e.preventDefault();busy(e.submitter,async()=>{const t=$('output-title').value.trim();
 await api('/v1/private-research/reporting-studio/publication/projects/'+encodeURIComponent(PID)+'/documents',{method:'POST',
  body:JSON.stringify({title:t,markdown:'# '+t+'\n',publicationType:$('output-type').value,expectedProjectRevision:D.project.revision})});
 $('output-title').value='';await reload();say('Private output created. Edit it in Publication Studio.')})};
$('setup-button').onclick=e=>busy(e.target,async()=>{await api(PURL+'/setup',{method:'POST'});await reload();say('Project setup completed.')});
$('delete-form').onsubmit=e=>{e.preventDefault();busy(e.submitter,async()=>{
 await api(PURL+'/delete',{method:'POST',body:JSON.stringify({confirmTitle:$('delete-confirm').value})});location.assign(HOME)})};
reload().catch(e=>say(e.message,true));
"""

DASH_HTML = """<main class="app"><nav class="crumbs"><a href="/v1/private-research/reporting-studio/research-projects">Research projects</a></nav>
<h1 id="title">Loading…</h1><p id="meta" class="lede"></p><p id="status" class="status" role="status" aria-live="polite"></p>
<div id="setup" class="card" hidden><p>Project setup did not finish. Nothing was lost; completing it attaches the project to the private research store.</p>
<button id="setup-button" type="button">Complete setup</button></div>
<nav class="tabs" aria-label="Project sections"><a id="tab-overview" href="#overview">Overview</a><a id="tab-documents" href="#documents">Documents</a>
<a id="tab-library" href="#library">Library</a><a id="tab-analysis" href="#analysis">Analysis</a><a id="tab-figures" href="#figures">Figures</a>
<a id="tab-publications" href="#publications">Publications</a></nav>
<section class="panel" id="overview"><div class="card"><h3>Research question</h3><p id="ov-question"></p><h3>Description</h3><p id="ov-description"></p>
<h3>Status</h3><p id="ov-status"></p><h3>Objectives</h3><ul class="items" id="ov-objectives"></ul><h3>Milestones</h3><ul class="items" id="ov-milestones"></ul>
<p><button id="ov-edit" type="button" class="secondary">Edit overview</button></p><p id="ov-existing" class="muted" hidden>This existing project is shown read-only; it has no research profile and is not changed here.</p></div>
<h2>Recent activity</h2><ul class="items" id="ov-activity"></ul></section>
<section class="panel" id="documents" hidden><div class="card"><h3>Add a document</h3><form id="upload-form" class="row">
<input id="upload-file" type="file" required style="flex:1 1 260px"><select id="upload-role" style="width:auto"><option value="draft">Draft</option><option value="report">Report</option>
<option value="paper">Paper</option><option value="source">Source file</option><option value="reference">References (.ris / .json)</option><option value="data">Data</option><option value="figure">Figure</option><option value="other">Other</option></select>
<button type="submit">Add</button></form><p class="hint">Files are private and immutable; a changed file is added as a new file, never a replacement.</p></div>
<h2>Registered documents</h2><ul class="items" id="doc-registered"></ul><h2>Project files</h2><ul class="items" id="doc-files"></ul>
<div id="doc-legacy-wrap" hidden><h2>Imported research records</h2><ul class="items" id="doc-legacy"></ul></div>
<h2>Trash</h2><p class="hint" id="trash-policy"></p><ul class="items" id="doc-trash"></ul></section>
<section class="panel" id="library" hidden><p id="lib-count"></p><div class="card"><h3>Import references from a project file</h3><div class="row">
<select id="lib-file" style="flex:1 1 260px"></select><button id="lib-import" type="button">Import</button></div></div>
<div class="card"><h3>Find in Sustainable Catalyst Library</h3><form id="lib-search-form" class="row"><input id="lib-q" required style="flex:1 1 260px" placeholder="Search published Library records">
<button type="submit">Search</button></form><ul class="items" id="lib-results"></ul></div><h2>References</h2><ul class="items" id="lib-items"></ul></section>
<section class="panel" id="analysis" hidden><div class="card"><h3>Notebooks, datasets and runtimes</h3><p>Open the Notebook Desk with this project selected to add datasets and run R or Julia cells on the governed runtimes.</p>
<a class="button" id="an-desk" href="#">Open in Notebook Desk</a></div><h2>Notebooks</h2><ul class="items" id="an-notebooks"></ul><h2>Data files</h2><ul class="items" id="an-data"></ul></section>
<section class="panel" id="figures" hidden><div class="card"><h3>Scientific figures</h3><p id="fig-reports"></p><a class="button" href="/v1/private-research/reporting-studio">Open Reporting Studio</a></div>
<h2>Figure files</h2><ul class="items" id="fig-files"></ul></section>
<section class="panel" id="publications" hidden><div class="card"><p id="pub-policy"></p><p class="muted">When you authorize your own work, Research labels it: <q id="pub-disclosure"></q></p>
<p class="muted">Research area for outputs: <span id="pub-area"></span></p><a class="button" id="pub-studio" href="#">Open Publication Studio</a></div>
<div class="card"><h3>New output</h3><form id="output-form" class="row"><input id="output-title" required maxlength="200" placeholder="Output title" style="flex:1 1 260px">
<select id="output-type" style="width:auto"><option value="report">Report</option><option value="policy-brief">Policy brief</option><option value="working-paper">Working paper</option>
<option value="interactive-analysis">Interactive analysis</option><option value="overview">Overview</option></select><button type="submit">Create private output</button></form></div>
<h2>Outputs</h2><ul class="items" id="pub-outputs"></ul></section>
<div id="danger" class="card" hidden><h3>Delete this empty project</h3><p class="hint">Only a project with no files, records or outputs can be deleted. Type its title to confirm.</p>
<form id="delete-form" class="row"><input id="delete-confirm" required style="flex:1 1 260px"><button type="submit" class="secondary">Delete project</button></form></div></main>
<dialog id="overview-dialog" aria-labelledby="ov-heading"><form id="overview-form"><h2 id="ov-heading">Edit overview</h2>
<label for="f-question">Research question</label><textarea id="f-question" required maxlength="2000"></textarea>
<label for="f-description">Description</label><textarea id="f-description" maxlength="4000"></textarea>
<label for="f-status">Status</label><select id="f-status"><option value="planning">Planning</option><option value="active">Active</option><option value="paused">Paused</option><option value="completed">Completed</option></select>
<label for="f-objectives">Objectives (one per line)</label><textarea id="f-objectives"></textarea>
<label for="f-milestones">Milestones (one per line: [ ] title | YYYY-MM-DD)</label><textarea id="f-milestones"></textarea>
<div class="row" style="margin-top:16px"><button type="submit">Save</button><button type="button" class="secondary" id="ov-cancel">Cancel</button></div></form></dialog>"""


def _app_page(title: str, body: str, script: str) -> HTMLResponse:
    digest = base64.b64encode(hashlib.sha256(script.encode()).digest()).decode()
    html = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" '
            f'content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow">'
            f'<title>{escape(title)}</title><style>{APP_STYLE}</style></head><body>{body}<script>{script}</script></body></html>')
    return HTMLResponse(html, headers={**HEADERS, 'Referrer-Policy': 'no-referrer', 'Content-Security-Policy': (
        f"default-src 'none'; script-src 'sha256-{digest}'; style-src 'unsafe-inline'; connect-src 'self'; "
        "img-src data:; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")})


@router.get('', response_class=HTMLResponse)
def hub(request: Request):
    page_subject(request, _subject)
    return _app_page('Research projects', HUB_HTML, HUB_JS)


@router.get('/{project_id}', response_class=HTMLResponse)
def project_page(project_id: str, request: Request):
    owner = page_subject(request, _subject)
    with session_scope() as db:
        _project(db, owner, project_id)
    return _app_page('Research project', DASH_HTML, DASH_JS)
