"""Private Workspace reporting bridge; additive, opt-in, no module writes or retrieval.

Reports are reference objects in native immutable project revisions. Scientific
bytes stay in the existing private artifact store. SHA256 verifies bytes, not the
truth of caller-declared origin, rights or scientific evidence.
"""
from __future__ import annotations

import base64
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
from uuid import uuid4
from typing import Literal
from xml.etree import ElementTree as ET

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from . import repository, object_store
from .db import session_scope
from .schemas import ProjectStoreRequest
from .wxr_private_projects import _subject, _write, _project, _locked_project, HEADERS
from .lab_publication_adapter_v3843 import Envelope, render
from .lab_live_figure_acceptance_v3844 import _verify_lab
from .lab_figure_reporting_v3842 import Figure, Scene, _result, _svg
from .reporting_composition import Binding, Composition, compose, resolve_binding
from .reporting_heatmaps import render_heatmap
from .reporting_workbench_bridge import adapt_workbench_handoff

SCHEMA = 'sc-research-visual-asset/1.0'
LAB_REVISION = 'sc-lab-4d-computational-workspace-revision/0.153.0'

def enabled():
    if os.getenv('SC_WORKSPACE_REPORTING_STUDIO_ENABLED') != '1':
        raise HTTPException(503, 'Private Reporting Studio is disabled.')

router = APIRouter(prefix='/v1/private-research/reporting-studio',
                   tags=['Private Reporting Studio'], dependencies=[Depends(enabled)])

class Strict(BaseModel):
    model_config = ConfigDict(extra='forbid')

class Display(Strict):
    color: str = Field(default='#111111', pattern=r'^#[0-9a-fA-F]{6}$')
    line_width: float = Field(default=2.5, ge=0.5, le=6, allow_inf_nan=False)
    frame_index: int = Field(default=0, ge=0, lt=48)
    palette: Literal['sequential','diverging'] = 'sequential'
    color_domain: tuple[float,float] | None = None
    color_transform: Literal['linear','log10'] = 'linear'

class Reference(Strict):
    artifact_id: str = Field(min_length=1, max_length=160)
    sha256: str = Field(pattern=r'^[a-f0-9]{64}$')
    source_revision: int = Field(ge=1)
    expected_project_revision: int = Field(ge=1)
    # Explicitly declared metadata. Never promoted to independently verified.
    heatmap_unit: str | None = Field(default=None,min_length=1,max_length=80)
    evidence_classification: Literal['unverified','derived-mapping','design-sensitivity','modeled'] = 'unverified'
    dataset_refs: list[str] = Field(max_length=100)
    computation_refs: list[str] = Field(max_length=100)
    evidence_refs: list[str] = Field(max_length=100)
    rights_ref: str = Field(min_length=1, max_length=1000)
    reproduction: str = Field(min_length=1, max_length=4000)
    display: Display = Field(default_factory=Display)
    composition: Composition = Field(default_factory=Composition)


def _source(db, subject, project_id, ref):
    row = object_store.get_artifact(db, subject, ref['artifact_id'])
    if row is None or row.project_id != project_id:
        raise HTTPException(404, 'Source artifact not found in this project.')
    if (row.sha256 != ref['sha256'] or row.revision != ref['source_revision']
            or row.metadata_json.get('source') != 'private-research'):
        raise HTTPException(409, 'Source hash, revision or immutable storage class mismatch.')
    raw = object_store.read_artifact_content(row)
    if len(raw) > 1_500_000:
        raise HTTPException(413, 'Reporting JSON exceeds adapter limit.')
    if hashlib.sha256(raw).hexdigest() != ref['sha256']:
        raise HTTPException(409, 'Source bytes failed SHA256 verification.')
    try:
        obj = json.loads(raw, parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
        if not isinstance(obj, dict):
            raise ValueError()
    except (ValueError, UnicodeError):
        raise HTTPException(422, 'A finite JSON scientific export is required.')
    return row, obj


def _adapt(obj, ref):
    """Reuse existing renderers; no normalization is written back to source."""
    try:
        if isinstance(obj.get('manifest'), dict) and obj['manifest'].get('schema') == 'sc-workbench-report-figure-handoff/1.0':
            return adapt_workbench_handoff(obj)
        if obj.get('schema') == 'sc-lab-scientific-visualization/1.0':
            return render_heatmap(obj,ref)
        if obj.get('schema') == 'sc-lab-advanced-statistical-figure/0.115.0':
            _verify_lab(obj)
            semantics = obj.get('semantics', obj.get('statistical_metadata', {}).get('semantics', 'unknown'))
            evidence = 'unknown'  # Lab export does not attest empirical status.
            result = render(Envelope(labResponse=obj, sourceObjectId=ref['artifact_id'],
                sourceFingerprint=ref['sha256'], caption='Source-preserving ECDF reporting view.',
                evidenceStatus='illustrative'))
            return result['svg'], {'owner_module':'lab', 'source_schema':obj['schema'],
                'source_identity': {'fingerprint':obj['fingerprint']},
                'scientific_status':evidence, 'uncertainty':str(semantics),
                'render_type':'ecdf', 'source_provenance': obj.get('provenance', {}),
                'source_fingerprint_verified':True, 'projection':None}
        if obj.get('schemaName') in ('sc-lab-report-figure/1.0', 'sc-lab-report-scene/1.0'):
            kind = 'figure' if obj['schemaName'] == 'sc-lab-report-figure/1.0' else 'scene'
            model = (Figure if kind == 'figure' else Scene).model_validate(obj)
            frame = ref['display']['frame_index']
            if kind == 'scene' and frame >= len(model.frames):
                raise HTTPException(422, 'Frame index outside source time domain.')
            if kind == 'figure' and frame != 0:
                raise HTTPException(422, 'Static figure has no temporal frames.')
            return _svg(_result(kind, model), frame), {
                'owner_module':'lab', 'source_schema':obj['schemaName'],
                'source_identity':{'id':model.provenance.labObjectId,
                    'declared_hash':model.provenance.labObjectHash},
                'source_provenance':obj['provenance'],
                'scientific_status':model.provenance.assessment,
                'uncertainty':'undeclared', 'render_type':kind,
                'source_fingerprint_verified':False,
                'projection':'2D projection only; no 3D or 5D rendering' if kind == 'scene' else None}
        if obj.get('schema') == LAB_REVISION:
            # Preserve an existing persisted Lab scene without inventing a renderer.
            if not all(obj.get(k) for k in ('id','assetId','revision','scene','revisionHash')):
                raise HTTPException(422, 'Incomplete Lab 4D revision envelope.')
            return None, {'owner_module':'lab', 'source_schema':LAB_REVISION,
                'source_identity':{'id':obj['assetId'], 'revision_id':obj['id'],
                                   'revision':obj['revision'], 'declared_hash':obj['revisionHash']},
                'source_provenance':obj.get('provenance',{}),
                'scientific_status':'unknown', 'uncertainty':'undeclared',
                'render_type':'preserved-lab-4d', 'source_fingerprint_verified':False,
                'projection':'Native Lab runtime adapter required; export unavailable'}
    except ValidationError:
        raise HTTPException(422, 'Scientific export does not match the existing Lab contract.')
    except (AttributeError, KeyError, TypeError, ValueError):
        raise HTTPException(422, 'Malformed scientific export envelope.')
    except HTTPException as exc:
        if exc.status_code == 502:
            raise HTTPException(422, exc.detail) from exc
        raise
    raise HTTPException(422, 'Unsupported scientific export schema; module adapter required.')


def _view(db, subject, project_id, ref):
    _, obj = _source(db, subject, project_id, ref)
    svg, metadata = _adapt(obj, ref)
    if svg:
        ns = '{http://www.w3.org/2000/svg}'
        tree = ET.fromstring(svg)
        ET.register_namespace('', 'http://www.w3.org/2000/svg')
        # Preserve data coordinates and labels; allow presentation changes only.
        for node in tree.iter():
            if node.tag == ns+'polyline':
                node.set('stroke', ref['display']['color'])
                node.set('stroke-width', str(ref['display']['line_width']))
        if metadata['render_type'] == 'ecdf':
            points = [p for series in obj['spec']['series'] for p in series['points']]
            xmin = min(p['x'] for p in points); xmax = max(p['x'] for p in points)
            for i in range(5):
                x = 85 + 705*i/4
                tick = ET.SubElement(tree, ns+'text', {'x':str(x),'y':'465',
                    'text-anchor':'middle','font-family':'sans-serif','font-size':'12'})
                tick.text = format(xmin+(xmax-xmin)*i/4, '.4g')
                tick = ET.SubElement(tree, ns+'text', {'x':'75','y':str(449-350*i/4),
                    'text-anchor':'end','font-family':'sans-serif','font-size':'12'})
                tick.text = format(i/4,'.2g')
        # Existing renderers have fixed-height legend layouts. Make room for every
        # legend and scientific boundary instead of clipping publication exports.
        is_workbench = metadata['render_type'] == 'workbench-graph'
        source_box = tree.attrib.get('viewBox', '').split()
        if is_workbench and len(source_box) != 4:
            raise HTTPException(422, 'Workbench SVG viewBox required.')
        canvas_width = float(source_box[2]) if is_workbench else 860
        footer_y = (float(source_box[3])+30 if is_workbench else
            (float(tree.attrib['viewBox'].split()[3])+30 if metadata['render_type'] == 'heatmap'
             else (570 if metadata['render_type'] == 'ecdf' else 690)))
        tree.set('viewBox', f'0 0 {canvas_width:g} {footer_y+130:g}')
        tree.set('width',f'{canvas_width:g}'); tree.set('height',f'{footer_y+130:g}')
        ET.SubElement(tree, ns+'rect', {'x':'0','y':str(footer_y),'width':f'{canvas_width:g}','height':'130','fill':'white'})
        label = ET.SubElement(tree, ns+'text', {'x':'24','y':str(footer_y+30),'font-family':'sans-serif','font-size':'12'})
        label.text = 'Evidence: '+metadata['scientific_status']+' (source declaration; not independently certified)'
        for y, text in [(footer_y+54,metadata['projection'] or 'Display changes only; scientific source unchanged.'),
                        (footer_y+78,'SHA256 '+ref['sha256']),
                        (footer_y+102,'Private research export. Redistribution requires separate rights review.')]:
            ET.SubElement(tree, ns+'text', {'x':'24','y':str(y),'font-family':'sans-serif','font-size':'11'}).text=text
        svg = ET.tostring(tree, encoding='unicode')
    composition = Composition.model_validate(ref.get('composition', {}))
    svg, bindings = compose(svg, composition, lambda pointer: _source(db, subject, project_id, pointer)[1])
    return {'svg':svg, 'bindings':bindings, 'source':metadata, 'source_sha256':ref['sha256'],
            'remote_origin_authenticated':False, 'scientific_verification_performed':False}

@router.post('/projects/{project_id}/preview')
def preview(project_id: str, body: Reference, request: Request):
    subject = _subject(request); _write(request)
    with session_scope() as db:
        _project(db, subject, project_id)
        return JSONResponse(_view(db, subject, project_id, body.model_dump()), headers=HEADERS)

@router.post('/projects/{project_id}/reports', status_code=201)
def save_report(project_id: str, body: Reference, request: Request):
    subject = _subject(request); _write(request)
    with session_scope() as db:
        row = _locked_project(db, subject, project_id)
        if row.revision != body.expected_project_revision:
            raise HTTPException(409, 'Project revision changed; reopen before saving.')
        ref = body.model_dump()
        view = _view(db, subject, project_id, ref)
        report_id = 'report-'+uuid4().hex
        revision = row.revision+1
        report = {'schema':SCHEMA, 'project_id':project_id, 'asset_id':report_id,
            'revision_id':str(revision), 'source':view['source'], 'reference':ref,
            'execution_bindings':view['bindings'],
            'rendered_view':view,
            'render_spec':{'adapter':'sc-workspace-private-reporting/1.0',
                'svg_sha256':hashlib.sha256(view['svg'].encode()).hexdigest() if view['svg'] else None},
            'data_refs':[{'artifact_id':body.artifact_id, 'sha256':body.sha256,
                          'revision':body.source_revision}],
            'axes':[{ 'key':key, 'availability':'undeclared', 'definition':None}
                    for key in ('x','y','z','t','q')],
            'spatial_coverage':None, 'temporal_coverage':None,
            'fifth_dimension':{'availability':'undeclared','semantics':None},
            'rights':{'reference':body.rights_ref, 'redistribution':'not-approved'},
            'provenance_verification':{'source_bytes_sha256':True,
                'remote_origin_authenticated':False, 'scientific_validity':False}}
        if view['source']['render_type']=='heatmap':
            provenance=view['source']['source_provenance']
            spatial=provenance.get('spatial_reference') or {}
            crs=spatial.get('crs')
            for axis in report['axes'][:2]:
                key=axis['key'];axis['availability']='declared'
                axis['definition']={'label':provenance['axis_labels'][key],
                    'kind':'space' if crs else 'analytical','crs':crs,
                    'unit':'m' if crs in ('EPSG:29903','EPSG:2157') else None,
                    'centers':provenance['axes_centers'][key]}
            if crs:
                report['spatial_coverage']={'crs':crs,'basis':'explicit source cell centers',
                    'x':[min(provenance['axes_centers']['x']),max(provenance['axes_centers']['x'])],
                    'y':[min(provenance['axes_centers']['y']),max(provenance['axes_centers']['y'])]}
        project = deepcopy(row.package['project'])
        project['objects'].append({'id':report_id, 'type':'research-report-reference', 'report':report})
        payload = ProjectStoreRequest.model_validate({'schema':'sc-workspace-sync-push/1.0',
            'sourceProjectId':project_id, 'projectTitle':row.title,
            'expectedRevision':body.expected_project_revision,
            'operationId':report_id, 'project':project})
        stored, _ = repository.store_project(db, subject, payload)
        return JSONResponse({'report':report, 'project':repository.project_metadata(stored)},
                            status_code=201, headers=HEADERS)

@router.get('/projects/{project_id}/revisions/{revision}/reports/{report_id}')
def open_report(project_id: str, revision: int, report_id: str, request: Request):
    subject = _subject(request)
    with session_scope() as db:
        _project(db, subject, project_id)
        row = repository.get_project_revision(db, subject, project_id, revision)
        if row is None:
            raise HTTPException(404, 'Reporting revision not found.')
        for item in row.package['project']['objects']:
            report = item.get('report', {})
            if (item.get('type') == 'research-report-reference' and item.get('id') == report_id
                    and report.get('revision_id') == str(revision)):
                # Reopen the exact saved visual snapshot; do not silently rerender
                # historical reports with a changed MathJax/adapter implementation.
                _source(db, subject, project_id, report['reference'])
                for inspection in report.get('execution_bindings', []):
                    _, checked = resolve_binding(Binding.model_validate(inspection['reference']),
                        lambda pointer: _source(db, subject, project_id, pointer)[1])
                    if checked != inspection:
                        raise HTTPException(409, 'Saved execution binding changed.')
                view = report.get('rendered_view') or _view(db, subject, project_id, report['reference'])
                expected = report.get('render_spec', {}).get('svg_sha256')
                if expected and hashlib.sha256(view['svg'].encode()).hexdigest() != expected:
                    raise HTTPException(409, 'Saved visual snapshot integrity mismatch.')
                return JSONResponse({'report':report, 'view':view}, headers=HEADERS)
        raise HTTPException(404, 'Reporting revision not found.')

@router.get('', response_class=HTMLResponse)
def studio(request: Request):
    _subject(request)
    script = Path(__file__).with_name('research_reporting_ui.js').read_text()
    html = Path(__file__).with_name('research_reporting_ui.html').read_text()
    script_hash = base64.b64encode(hashlib.sha256(script.encode()).digest()).decode()
    return HTMLResponse(html.replace('<!--SCRIPT-->', '<script>'+script+'</script>'), headers={**HEADERS,
        'Content-Security-Policy':"default-src 'none'; script-src 'sha256-"+script_hash+"'; style-src 'unsafe-inline'; img-src blob:; connect-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'"})

@router.get('/projects/{project_id}/revisions/{revision}/reports/{report_id}/export.pdf')
def export_pdf(project_id: str, revision: int, report_id: str, request: Request):
    # Authorization and source/binding integrity are rechecked on every export.
    result = json.loads(open_report(project_id, revision, report_id, request).body)
    svg = result['view']['svg']
    if not svg:
        raise HTTPException(422, 'Native Lab runtime required for this scene export.')
    try:
        from io import BytesIO
        from svglib.svglib import svg2rlg
        from reportlab.graphics import renderPDF
    except ImportError as exc:
        raise HTTPException(503, 'Install the optional pinned reporting PDF dependencies.') from exc
    drawing = svg2rlg(BytesIO(svg.encode()))
    if drawing is None:
        raise HTTPException(422, 'Saved SVG cannot be converted to a publication PDF.')
    data = renderPDF.drawToString(drawing, invariant=1)
    return Response(data, media_type='application/pdf', headers={**HEADERS,
        'Content-Disposition':f'attachment; filename="{report_id}.pdf"',
        'X-Research-SHA256':result['view']['source_sha256']})
