"""SC-OUTPUT-01 — registered scientific outputs for the Publication Studio.

A scientific output is a chart and its data table from one executed-verified Workspace notebook cell run. Nothing here
computes science or draws charts of its own:

* the computation, its receipt and the figure package are SC-FIG-02B's (``notebook_figure_bundle.verified_package``);
* the chart is the projected rows drawn by the pinned existing Lab engine (``reporting_math/output_chart.cjs``);
* the bytes (chart SVG, full-precision CSV, figure bundle) are ordinary immutable project artifacts in the existing
  artifact store, so the Studio's figure line, ``figureSources`` pinning and export re-verification apply unchanged;
* the registry is one object in the project's immutable store, like the citation collection (no new table).

Versions are append-only. A new computation registers version N+1 under new artifact ids; saved manuscript revisions
keep pointing at the exact version they inserted. Every output is private and owner-scoped: there is no route that
makes one public, and insertion is refused until the owner has declared rights for it and for every input dataset.
"""
from __future__ import annotations

import base64
import csv
import hashlib
import io
import json
import os
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import re
import subprocess
from typing import Any, Callable, Literal
from urllib.parse import quote
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, ConfigDict, Field

from . import notebook_figure_bundle as fb
from . import object_store
from .schemas import ArtifactStoreRequest

REGISTRY_SCHEMA = 'sc-scientific-output-registry/1.0'
VERSION_SCHEMA = 'sc-scientific-output/1.0'
OBJECT_TYPE = 'scientific-output-registry'
ENGINE = {'name': 'Lab scientific visualization engine', 'version': '0.44.0',
          'sha256': '45ae0694bb1d8e48a47c43e235df442cf6c7e5ce0920f0fea811cde18c1c3a80',
          'adapter': 'reporting_math/output_chart.cjs'}
MAX_TABLE_ROWS = 200
CAPTION = re.compile(r'^[^\[\]\n]{15,160}$')
OUTPUT_ID = fb.FIGURE_ID


class Rights(BaseModel):
    model_config = ConfigDict(extra='forbid')
    status: Literal['owner-declared', 'pending']
    license: str = Field(min_length=2, max_length=120)
    rightsHolder: str = Field(min_length=2, max_length=200)
    statement: str = Field(min_length=20, max_length=600)
    # Each input dataset needs its own licence; holding a dataset is not a right to publish it (SC-FIG-02B).
    sourceLicences: dict[str, str] = Field(default_factory=dict, max_length=12)


class TableSpec(BaseModel):
    model_config = ConfigDict(extra='forbid')
    caption: str = Field(min_length=15, max_length=300)
    significantFigures: int = Field(default=4, ge=2, le=8)


class Register(BaseModel):
    model_config = ConfigDict(extra='forbid')
    notebookId: str = Field(min_length=1, max_length=160)
    revision: int = Field(ge=1)
    cellId: str = Field(min_length=1, max_length=160)
    figure: fb.FigureRequest
    table: TableSpec
    rights: Rights
    citation: str = Field(min_length=20, max_length=600)
    expectedProjectRevision: int = Field(ge=1)


class RightsUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    rights: Rights
    expectedProjectRevision: int = Field(ge=1)


def registry(package: dict) -> dict:
    for obj in package.get('project', {}).get('objects', []):
        if isinstance(obj, dict) and obj.get('type') == OBJECT_TYPE and (obj.get('registry') or {}).get('schema') == REGISTRY_SCHEMA:
            return obj['registry']
    return {'schema': REGISTRY_SCHEMA, 'outputs': []}


def versions_by_chart(package: dict) -> dict[str, dict]:
    """Every registered version, keyed by its chart artifact id (the id a manuscript figure line names)."""
    return {v['artifacts']['chart']['artifactId']: v for o in registry(package)['outputs'] for v in o['versions']}


def rights_blockers(version: dict) -> list[str]:
    rights = version['rights'][-1]
    out = [] if rights['status'] == 'owner-declared' else ['Output rights are pending.']
    for src in version['dataset']:
        if not (rights.get('sourceLicences') or {}).get(src['sourceId']):
            out.append(f"No licence declared for input {src['sourceId']}.")
    return out


# Chart, table and artifacts ---------------------------------------------------------------------------------------

def _axis_label(field: dict) -> str:
    return field['label'] if field['unit'] in ('1', 'category') else f"{field['label']} ({field['unit']})"


def chart_spec(req: fb.FigureRequest, view: dict) -> dict:
    """The Lab engine's line/scatter grammar from the figure view's projected rows (no resampling or smoothing)."""
    if req.x.type != 'quantitative' or req.mark == 'bar':
        raise HTTPException(422, {'code': 'output-chart-unsupported',
                                  'message': 'This release draws line or point charts over a quantitative x field.'})
    sc = view['usermeta']['sc']
    unc = sc['uncertainty']
    points = []
    for row in view['data']['values']:
        p = {'x': row[req.x.field], 'y': row[req.y.field]}
        if unc['kind'] != 'none' and row.get(fb.LOWER) is not None and row.get(fb.UPPER) is not None:
            p.update(yLow=row[fb.LOWER], yHigh=row[fb.UPPER])
        points.append(p)
    label = req.y.label + (f" with {fb.KIND_TEXT[unc['kind']]}" if unc['kind'] != 'none' else '')
    return {'schema': 'sc-lab-scientific-visualization/1.0', 'kind': 'line-scatter' if req.mark == 'line' else 'scatter',
            'title': req.title, 'description': req.altText, 'xLabel': _axis_label(sc['fields'][req.x.field]),
            'yLabel': _axis_label(sc['fields'][req.y.field]),
            'series': [{'label': label[:120], 'mode': 'line-scatter' if req.mark == 'line' else 'scatter', 'points': points}],
            'publication': {'showLegend': True}}


def render_chart(spec: dict) -> bytes:
    worker = Path(__file__).resolve().parent.parent / 'reporting_math' / 'output_chart.cjs'
    try:
        result = subprocess.run([os.getenv('SC_REPORTING_NODE_BIN', 'node'), '--max-old-space-size=160', str(worker)],
                                input=json.dumps({'spec': spec}), text=True, capture_output=True, timeout=20,
                                cwd=worker.parent, env={k: v for k, v in os.environ.items() if k in ('PATH', 'SYSTEMROOT', 'TMPDIR')})
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise HTTPException(503, 'The Lab chart renderer is unavailable or timed out.') from exc
    if result.returncode or not result.stdout.startswith('<svg'):
        raise HTTPException(503, 'The Lab chart renderer refused the output chart.')
    return result.stdout.encode('utf-8')


def _sig(value: Any, digits: int) -> str:
    """Display value at the declared significant figures, trailing zeros kept (1.0999 -> 1.100); integers as given."""
    if value is None:
        return '—'
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, float):
        return format(value, f'#.{digits}g').rstrip('.')
    return str(value).replace('|', '/')


def table_of(view: dict, digits: int) -> tuple[dict, bytes]:
    """(display table, full-precision CSV bytes). Columns follow the view's declared fields and units."""
    fields = view['usermeta']['sc']['fields']
    keys = [k for k in fields if k != fb.EVIDENCE_FIELD]
    rows = view['data']['values']
    if len(rows) > MAX_TABLE_ROWS:
        raise HTTPException(422, {'code': 'output-table-too-long',
                                  'message': f'A manuscript table holds at most {MAX_TABLE_ROWS} rows.'})
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator='\n')
    writer.writerow([f"{fields[k]['label']} [{fields[k]['unit']}]" for k in keys] + ['Evidence class'])
    for row in rows:
        writer.writerow(['' if row.get(k) is None else repr(row[k]) if isinstance(row[k], float) else row[k] for k in keys]
                        + [row[fb.EVIDENCE_FIELD]])
    display = {'columns': [{'field': k, 'label': fields[k]['label'], 'unit': fields[k]['unit']} for k in keys],
               'headers': [_axis_label(fields[k]).replace('|', '/') for k in keys],
               'rows': [[_sig(row.get(k), digits) for k in keys] for row in rows], 'significantFigures': digits}
    return display, buf.getvalue().encode('utf-8')


def table_markdown(table: dict) -> str:
    lines = ['| ' + ' | '.join(table['headers']) + ' |', '|' + ' --- |' * len(table['headers'])]
    lines += ['| ' + ' | '.join(r) + ' |' for r in table['rows']]
    return '\n'.join(lines)


def insertion_markdown(v: dict) -> str:
    src = '; '.join(f"input {s['sourceId']}" + (f" (sha256 {s['sha256'][:12]})" if s.get('sha256') else '')
                    + f", licence {v['rights'][-1]['sourceLicences'].get(s['sourceId'], 'not declared')}" for s in v['dataset'])
    t = v['table']
    return '\n\n'.join([
        f"![{v['caption']}](asset:{v['artifacts']['chart']['artifactId']})",
        f"**Table: {t['caption']}** Values rounded to {t['significantFigures']} significant figures; the exact values "
        f"are in the pinned CSV (sha256 {v['artifacts']['table']['sha256'][:12]}).",
        table_markdown(t),
        f"*Source:* {v['citation']} Scientific output {v['outputId']} version {v['version']} (bundle sha256 "
        f"{v['artifacts']['bundle']['sha256'][:16]}), computed by notebook {v['notebook']['notebookId']} revision "
        f"{v['notebook']['revision']}, cell {v['notebook']['cellId']}, run {v['run']['runId']}; {src}. "
        f"Evidence class: {v['evidenceClass']}. {v['asset']['uncertainty']['statement']} Licence: {v['asset']['license']}.",
    ]) + '\n'


def _store(db, owner: str, project_id: str, artifact_id: str, filename: str, media: str, raw: bytes, meta: dict) -> dict:
    digest = hashlib.sha256(raw).hexdigest()
    existing = object_store.get_artifact(db, owner, artifact_id)
    if existing is not None:
        if existing.project_id != project_id or existing.sha256 != digest:
            raise HTTPException(409, 'An output artifact id is already used by different content.')
    else:
        object_store.store_artifact(db, owner, ArtifactStoreRequest.model_validate({
            'schema': 'sc-workspace-artifact-store/1.0', 'artifactId': artifact_id, 'projectId': project_id,
            'filename': filename, 'mediaType': media, 'contentBase64': base64.b64encode(raw).decode('ascii'),
            'expectedRevision': 0, 'metadata': meta}))
    return {'artifactId': artifact_id, 'sha256': digest, 'bytes': len(raw), 'mediaType': media, 'filename': filename}


def verify_artifacts(db, owner: str, project_id: str, version: dict, read: Callable) -> dict[str, str]:
    """Each pinned artifact re-read and re-hashed: 'verified', or why it is not."""
    out = {}
    for role, art in version['artifacts'].items():
        try:
            meta, raw = read(db, owner, project_id, art['artifactId'])
            out[role] = 'verified' if meta['sha256'] == art['sha256'] == hashlib.sha256(raw).hexdigest() else 'changed'
        except HTTPException as exc:
            out[role] = 'missing' if exc.status_code == 404 else 'unreadable'
    return out


# Manuscript pins --------------------------------------------------------------------------------------------------

def pins(package: dict, figure_ids: list[str], blocks: list[dict]) -> list[dict]:
    """The exact output versions a manuscript revision inserts (by chart artifact id). Refuses a version whose rights
    are not declared: the insertion gate is enforced on save, not only in the browser."""
    known = versions_by_chart(package)
    tables = [(b['headers'], b['rows']) for b in blocks if b['kind'] == 'table']
    out = []
    for aid in figure_ids:
        v = known.get(aid)
        if v is None:
            continue
        blockers = rights_blockers(v)
        if blockers:
            raise HTTPException(409, {'message': f"Scientific output {v['outputId']} v{v['version']} cannot be used yet.",
                                      'blockers': blockers})
        out.append({'outputId': v['outputId'], 'version': v['version'],
                    **{f'{role}ArtifactId': a['artifactId'] for role, a in v['artifacts'].items()},
                    **{f'{role}Sha256': a['sha256'] for role, a in v['artifacts'].items()},
                    'tableVerbatim': (v['table']['headers'], v['table']['rows']) in tables})
    return out


def verify_pins(db, owner: str, project_id: str, pub: dict, read: Callable) -> None:
    for pin in pub.get('outputSources', []):
        for role in ('chart', 'table', 'bundle'):
            meta, raw = read(db, owner, project_id, pin[f'{role}ArtifactId'])
            if meta['sha256'] != pin[f'{role}Sha256'] or hashlib.sha256(raw).hexdigest() != pin[f'{role}Sha256']:
                raise HTTPException(409, f"Scientific output {pin['outputId']} v{pin['version']} {role} changed since this revision was saved.")


# Routes -----------------------------------------------------------------------------------------------------------

def build_router(deps: dict[str, Callable]) -> APIRouter:
    """``deps``: subject, write, project, locked_project, store, session, headers, original_asset, sanitize_svg."""
    router = APIRouter(prefix='/scientific-outputs', tags=['Scientific outputs'])
    H = deps['headers']

    def save(db, owner, row, current, operation):
        project = deepcopy(row.package['project'])
        project['objects'] = [o for o in project.get('objects', []) if not (isinstance(o, dict) and o.get('type') == OBJECT_TYPE)]
        project['objects'].append({'id': OBJECT_TYPE, 'type': OBJECT_TYPE, 'registry': current})
        return deps['store'](db, owner, row, project, operation)

    def find(package, output_id, version):
        for o in registry(package)['outputs']:
            if o['outputId'] == output_id:
                for v in o['versions']:
                    if v['version'] == version:
                        return v
        raise HTTPException(404, 'Scientific output version not found in this project.')

    def summary(v):
        return {'version': v['version'], 'registeredAt': v['registeredAt'], 'title': v['title'], 'caption': v['caption'],
                'evidenceClass': v['evidenceClass'], 'units': v['asset']['units'], 'uncertainty': v['asset']['uncertainty'],
                'rightsStatus': v['rights'][-1]['status'], 'license': v['asset']['license'],
                'insertable': not rights_blockers(v), 'blockers': rights_blockers(v),
                'chart': v['artifacts']['chart'], 'visibility': v['asset']['visibility'], 'run': v['run']['runId']}

    @router.get('/projects/{project_id}')
    def search(project_id: str, request: Request, q: str = ''):
        owner = deps['subject'](request)
        needle = q.strip().lower()[:120]
        with deps['session']() as db:
            row = deps['project'](db, owner, project_id)
            outputs = []
            for o in registry(row.package)['outputs']:
                latest = o['versions'][-1]
                text = ' '.join([o['outputId'], latest['title'], latest['caption'], latest['citation'],
                                 json.dumps(latest['asset']['units'])]).lower()
                if needle and needle not in text:
                    continue
                outputs.append({'outputId': o['outputId'], 'latest': summary(latest),
                                'versions': [summary(v) for v in reversed(o['versions'])]})
            return JSONResponse({'schema': REGISTRY_SCHEMA, 'projectRevision': row.revision, 'outputs': outputs,
                                 'visibility': 'private', 'publicRoute': None}, headers=H)

    @router.post('/projects/{project_id}/register', status_code=201)
    def register(project_id: str, body: Register, request: Request):
        owner = deps['subject'](request)
        deps['write'](request)
        if not CAPTION.match(body.figure.caption):
            raise HTTPException(422, 'A manuscript figure caption is 15–160 characters without square brackets or line breaks.')
        with deps['session']() as db:
            row = deps['locked_project'](db, owner, project_id)
            if row.revision != body.expectedProjectRevision:
                raise HTTPException(409, 'Workspace project changed. Reload before registering.')
            rev, package = fb.verified_package(db, owner, body.notebookId, body.revision, body.cellId, body.figure)
            if rev.project_id != project_id:
                raise HTTPException(404, 'Workspace notebook not found in this project.')
            files = {f['role']: f for f in package['files']}
            bundle, view = json.loads(files['bundle']['text']), json.loads(files['view']['text'])
            unknown = set(body.rights.sourceLicences) - {s['sourceId'] for s in bundle['sourceRefs']}
            if unknown:
                raise HTTPException(422, f'Licences were declared for inputs this run does not use: {sorted(unknown)}.')
            table, csv_bytes = table_of(view, body.table.significantFigures)
            current = deepcopy(registry(row.package))
            entry = next((o for o in current['outputs'] if o['outputId'] == body.figure.figureId), None)
            if entry and entry['versions'][-1]['artifacts']['bundle']['sha256'] == package['bundleSha256']:
                last = entry['versions'][-1]
                return JSONResponse({'created': False, 'output': summary(last), 'projectRevision': row.revision},
                                    status_code=200, headers=H)
            number = len(entry['versions']) + 1 if entry else 1
            svg = deps['sanitize_svg'](render_chart(chart_spec(body.figure, view)))
            base = f"sco-{hashlib.sha256(project_id.encode()).hexdigest()[:10]}-{body.figure.figureId}-v{number}"
            folder = f'scientific-outputs/{body.figure.figureId}/v{number}/{body.figure.figureId}'
            meta = {'source': 'sc-output-01', 'outputId': body.figure.figureId, 'version': number,
                    'bundleSha256': package['bundleSha256'], 'runId': package['run']['runId']}
            now = datetime.now(timezone.utc).isoformat()
            artifacts = {
                'chart': _store(db, owner, project_id, base + '-chart', folder + '.svg', 'image/svg+xml', svg, meta),
                'table': _store(db, owner, project_id, base + '-table', folder + '.csv', 'text/csv', csv_bytes, meta),
                'bundle': _store(db, owner, project_id, base + '-bundle', folder + '.bundle.json', 'application/json',
                                 files['bundle']['text'].encode('utf-8'), meta)}
            sc = view['usermeta']['sc']
            rights = {**body.rights.model_dump(), 'declaredAt': now}
            version = {
                'schema': VERSION_SCHEMA, 'outputId': body.figure.figureId, 'version': number, 'registeredAt': now,
                'title': body.figure.title, 'caption': body.figure.caption, 'altText': body.figure.altText,
                'citation': body.citation, 'evidenceClass': bundle['evidenceClass'],
                'notebook': package['notebook'], 'run': package['run'], 'dataset': bundle['sourceRefs'],
                'calculation': bundle['calculationRefs'], 'provenance': bundle['provenance'],
                'scientificContext': bundle['scientificContext'], 'renderer': ENGINE,
                'table': {**table, 'caption': body.table.caption}, 'artifacts': artifacts, 'rights': [rights],
                'review': bundle['review'], 'publicApproval': 'not-approved',
                # RH-ASSET-01 cross-service contract minimum (SC-UP-01, UP-03).
                'asset': {'source_service': 'workspace-notebook', 'source_object_id':
                          f"workspace-notebook:{rev.notebook_id}#{body.cellId}",
                          'source_revision': f"r{rev.revision}/{package['run']['runId']}",
                          'content_sha256': artifacts['chart']['sha256'], 'parent_project_id': project_id,
                          'owner_scope': 'owner-private', 'media_type': 'image/svg+xml',
                          'preview_uri_or_action': f"/v1/private-research/reporting-studio/publication/projects/"
                                                   f"{quote(project_id, safe='')}/assets/{artifacts['chart']['artifactId']}/image",
                          'license': body.rights.license, 'visibility': 'private', 'rights_status': body.rights.status,
                          'citation': body.citation, 'methodology': [c['method'] for c in bundle['calculationRefs']],
                          'units': {k: f['unit'] for k, f in sc['fields'].items()},
                          'uncertainty': sc['uncertainty'], 'generated_at': bundle['provenance']['generatedAt'],
                          'lineage': bundle['provenance']['lineageRefs'] + bundle['provenance']['sourceSnapshotIds'],
                          'snapshot_receipt': {'registeredAt': now, 'bundleSha256': package['bundleSha256'],
                                               'artifacts': {k: a['sha256'] for k, a in artifacts.items()}}},
            }
            if entry is None:
                entry = {'outputId': body.figure.figureId, 'versions': []}
                current['outputs'].append(entry)
            entry['versions'].append(version)
            updated = save(db, owner, row, current, 'scientific-output-register-' + uuid4().hex)
            return JSONResponse({'created': True, 'output': summary(version), 'projectRevision': updated.revision},
                                status_code=201, headers=H)

    @router.get('/projects/{project_id}/outputs/{output_id}/versions/{version}')
    def inspect(project_id: str, output_id: str, version: int, request: Request):
        owner = deps['subject'](request)
        with deps['session']() as db:
            row = deps['project'](db, owner, project_id)
            v = find(row.package, output_id, version)
            integrity = verify_artifacts(db, owner, project_id, v, deps['original_asset'])
        return JSONResponse({**v, 'integrity': integrity, 'insertable': not rights_blockers(v),
                             'blockers': rights_blockers(v)}, headers=H)

    @router.get('/projects/{project_id}/outputs/{output_id}/versions/{version}/insertion')
    def insertion(project_id: str, output_id: str, version: int, request: Request):
        owner = deps['subject'](request)
        with deps['session']() as db:
            row = deps['project'](db, owner, project_id)
            v = find(row.package, output_id, version)
            blockers = rights_blockers(v)
            if blockers:
                raise HTTPException(409, {'message': 'Declare rights before inserting this output.', 'blockers': blockers})
            integrity = verify_artifacts(db, owner, project_id, v, deps['original_asset'])
            if set(integrity.values()) != {'verified'}:
                raise HTTPException(409, {'message': 'Scientific output integrity check failed.', 'integrity': integrity})
        return JSONResponse({'outputId': output_id, 'version': version, 'markdown': insertion_markdown(v),
                             'chartArtifactId': v['artifacts']['chart']['artifactId'], 'integrity': integrity}, headers=H)

    @router.get('/projects/{project_id}/outputs/{output_id}/versions/{version}/table.csv')
    def table_csv(project_id: str, output_id: str, version: int, request: Request):
        owner = deps['subject'](request)
        with deps['session']() as db:
            row = deps['project'](db, owner, project_id)
            art = find(row.package, output_id, version)['artifacts']['table']
            meta, raw = deps['original_asset'](db, owner, project_id, art['artifactId'])
            if meta['sha256'] != art['sha256'] or hashlib.sha256(raw).hexdigest() != art['sha256']:
                raise HTTPException(409, 'Scientific output table changed since registration.')
        return Response(raw, media_type='text/csv; charset=utf-8', headers={
            **H, 'X-Research-SHA256': art['sha256'],
            'Content-Disposition': f'attachment; filename="{output_id}-v{version}.csv"'})

    @router.post('/projects/{project_id}/outputs/{output_id}/versions/{version}/rights')
    def declare_rights(project_id: str, output_id: str, version: int, body: RightsUpdate, request: Request):
        """Append a rights declaration; earlier declarations and every other field of the version are kept."""
        owner = deps['subject'](request)
        deps['write'](request)
        with deps['session']() as db:
            row = deps['locked_project'](db, owner, project_id)
            if row.revision != body.expectedProjectRevision:
                raise HTTPException(409, 'Workspace project changed. Reload before declaring rights.')
            current = deepcopy(registry(row.package))
            v = find({'project': {'objects': [{'type': OBJECT_TYPE, 'registry': current}]}}, output_id, version)
            unknown = set(body.rights.sourceLicences) - {s['sourceId'] for s in v['dataset']}
            if unknown:
                raise HTTPException(422, f'Licences were declared for inputs this run does not use: {sorted(unknown)}.')
            v['rights'].append({**body.rights.model_dump(), 'declaredAt': datetime.now(timezone.utc).isoformat()})
            v['asset']['license'], v['asset']['rights_status'] = body.rights.license, body.rights.status
            updated = save(db, owner, row, current, 'scientific-output-rights-' + uuid4().hex)
            return JSONResponse({'output': summary(v), 'projectRevision': updated.revision}, headers=H)

    return router
