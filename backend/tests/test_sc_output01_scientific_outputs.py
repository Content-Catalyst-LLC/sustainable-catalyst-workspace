"""SC-OUTPUT-01: a verified notebook run registered as a project scientific output (chart + table + provenance), inserted
into a manuscript at an exact version, pinned on save and re-verified on export. Synthetic data; offline fakes."""
import hashlib
import importlib
import json
import types
from datetime import datetime, timezone
from io import BytesIO

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

fb = importlib.import_module('app.notebook_figure_bundle')
sco = importlib.import_module('app.scientific_outputs')
pub = importlib.import_module('app.reporting_publication')

PROJECT = 'syn-proj'
SOURCE = 'workspace-dataset:ds-1@r1'
# What the R runtime's linear model returns with confidenceLevel 0.95 and bands ["confidence"] (SC-FIG-05.3).
BANDS = {'coefficients': [], 'bands': [{'semantics': 'confidence-band', 'points': [
    {'x': 1, 'fit': 2.05, 'lower': 1.5124, 'upper': 2.5876},
    {'x': 2, 'fit': 3.1, 'lower': 2.7, 'upper': 3.5},
    {'x': 3, 'fit': 4.15, 'lower': 3.6124, 'upper': 4.6876}]}]}


def figure(**kw):
    body = {'figureId': 'SYN-dose-response', 'title': 'SYNTHETIC fitted response with a 95% confidence band',
            'rowsPath': 'bands.0.points', 'mark': 'line',
            'x': {'field': 'x', 'label': 'Dose', 'unit': 'mg'}, 'y': {'field': 'fit', 'label': 'Fitted response', 'unit': 'units'},
            'uncertainty': {'kind': 'ci95', 'lowerField': 'lower', 'upperField': 'upper',
                            'statement': 'Student-t 95% confidence band from stats::predict.lm.'},
            'evidenceClass': 'modelled', 'caption': 'SYNTHETIC fitted response by dose with its 95% confidence band',
            'altText': 'A rising straight line from 2.05 at 1 mg to 4.15 at 3 mg inside a narrow shaded band.',
            'interpretation': 'Synthetic fit used to exercise the scientific-output path.',
            'limitations': ['Synthetic data with no scientific meaning']}
    body.update(kw)
    return body


def package(result=BANDS, run='run-1', **kw):
    rev = types.SimpleNamespace(notebook_id='nb-syn', revision=1, project_id=PROJECT)
    ev = {'runId': run, '_run': types.SimpleNamespace(finished_at=datetime(2026, 11, 20, 9, 0, tzinfo=timezone.utc),
                                                     created_at=None, input_fingerprint='a' * 64, project_id=PROJECT),
          'verification': {'status': 'executed-verified', 'inputLineage': 'artifact-bound-verified',
                           'inputBindings': [{'datasetId': 'ds-1', 'datasetRevision': 1, 'artifactSha256': 'b' * 64}],
                           'runtimeReceipts': [{'receiptId': 'rcpt-' + run, 'language': 'r', 'runtime': 'R 4.5',
                                                'operation': 'workspace.polyglot.r.linear-model', 'resultSha256': 'c' * 64}]}}
    return rev, fb.build_package(rev, 'fit', 'd' * 64, ev, result, fb.FigureRequest(**figure(**kw)))


def test_rows_path_indexes_lists_and_the_band_rows_project():
    rows = fb._rows(BANDS, 'bands.0.points')
    assert [r['x'] for r in rows] == [1, 2, 3]
    with pytest.raises(HTTPException):
        fb._rows(BANDS, 'bands.4.points')


def test_the_chart_is_drawn_by_the_pinned_lab_engine_deterministically():
    _, pkg = package()
    view = json.loads(pkg['files'][1]['text'])
    spec = sco.chart_spec(fb.FigureRequest(**figure()), view)
    assert spec['kind'] == 'line-scatter' and spec['series'][0]['points'][0] == {'x': 1, 'y': 2.05, 'yLow': 1.5124, 'yHigh': 2.5876}
    assert spec['xLabel'] == 'Dose (mg)' and spec['yLabel'] == 'Fitted response (units)'
    svg = pub.sanitize_svg(sco.render_chart(spec))
    assert svg == pub.sanitize_svg(sco.render_chart(spec))  # same rows, same bytes
    text = svg.decode()
    assert 'title>SYNTHETIC fitted response' in text and 'desc>A rising straight line' in text  # title + desc (alt text)
    assert ':polygon' in text and ':polyline' in text and 'script' not in text.lower()
    with pytest.raises(HTTPException):
        sco.chart_spec(fb.FigureRequest(**figure(mark='bar')), view)


def test_the_table_keeps_exact_values_in_the_csv_and_rounds_only_the_display():
    _, pkg = package()
    table, raw = sco.table_of(json.loads(pkg['files'][1]['text']), 3)
    assert table['headers'] == ['Dose (mg)', 'Fitted response (units)', 'Lower bound (95% confidence interval) (units)',
                                'Upper bound (95% confidence interval) (units)']
    assert table['rows'][0] == ['1', '2.05', '1.51', '2.59']
    assert [sco._sig(v, 4) for v in (1.09999, 0.95184, 4.03, 1234.0, 2, None)] == ['1.100', '0.9518', '4.030', '1234', '2', '—']
    assert raw.decode().splitlines()[1] == '1,2.05,1.5124,2.5876,modelled'


class Store:
    """In-memory artifact store and project row standing in for Workspace."""

    def __init__(self):
        self.artifacts, self.row = {}, types.SimpleNamespace(
            revision=1, package={'project': {'objects': []}}, project_id=PROJECT, title='Synthetic')

    def get(self, db, owner, aid):
        a = self.artifacts.get((owner, aid))
        return types.SimpleNamespace(**a) if a else None

    def put(self, db, owner, payload):
        import base64
        raw = base64.b64decode(payload.contentBase64)
        self.artifacts[(owner, payload.artifactId)] = {'project_id': payload.projectId, 'sha256': hashlib.sha256(raw).hexdigest(),
                                                       'raw': raw, 'filename': payload.filename}

    def read(self, db, owner, project_id, aid):
        a = self.artifacts.get((owner, aid))
        if a is None or a['project_id'] != project_id:
            raise HTTPException(404, 'not found')
        return {'artifactId': aid, 'sha256': a['sha256'], 'filename': a['filename']}, a['raw']


@pytest.fixture
def env(monkeypatch):
    s = Store()
    runs = {'current': 'run-1'}
    monkeypatch.setattr(sco.object_store, 'get_artifact', s.get)
    monkeypatch.setattr(sco.object_store, 'store_artifact', s.put)

    def verified(db, owner, nb, rev, cell, req):
        if owner != 'owner' or nb != 'nb-syn':
            raise HTTPException(404, 'Workspace notebook revision not found.')
        r, pkg = package(run=runs['current'], **{k: v for k, v in req.model_dump().items() if k in ('caption',)})
        return r, pkg
    monkeypatch.setattr(sco.fb, 'verified_package', verified)

    def project(db, owner, project_id):
        if owner != 'owner' or project_id != PROJECT:
            raise HTTPException(404, 'Project not found.')
        return s.row

    def store(db, owner, row, project, operation):
        s.row = types.SimpleNamespace(revision=row.revision + 1, package={'project': project}, project_id=PROJECT, title='Synthetic')
        return s.row

    class DB:
        def __enter__(self): return self
        def __exit__(self, *a): pass

    def subject(request):
        who = request.headers.get('x-test-user')
        if not who:
            raise HTTPException(401, 'A valid Workspace browser session is required.')
        return who
    app = FastAPI()
    app.include_router(sco.build_router({'subject': subject, 'write': lambda r: None, 'project': project,
                                         'locked_project': project, 'store': store, 'session': DB, 'headers': {},
                                         'original_asset': s.read, 'sanitize_svg': pub.sanitize_svg}))
    return s, runs, TestClient(app)


RIGHTS = {'status': 'owner-declared', 'license': 'CC-BY-4.0', 'rightsHolder': 'Synthetic Author',
          'statement': 'Synthetic computation written for this test; no third-party material.',
          'sourceLicences': {SOURCE: 'CC0-1.0'}}


def body(s, **kw):
    b = {'notebookId': 'nb-syn', 'revision': 1, 'cellId': 'fit', 'figure': figure(),
         'table': {'caption': 'SYNTHETIC fitted response by dose', 'significantFigures': 4}, 'rights': RIGHTS,
         'citation': 'Synthetic Author (2026) SYNTHETIC dose response.', 'expectedProjectRevision': s.row.revision}
    b.update(kw)
    return b


def call(client, method, url, user='owner', **kw):
    return client.request(method, '/scientific-outputs/projects/' + url, headers={'x-test-user': user} if user else {}, **kw)


def test_register_records_the_full_contract_and_versions_are_append_only(env):
    s, runs, client = env
    r = call(client, 'POST', f'{PROJECT}/register', json=body(s))
    assert r.status_code == 201, r.text
    v1 = sco.registry(s.row.package)['outputs'][0]['versions'][0]
    asset = v1['asset']
    for k in ('source_service', 'source_object_id', 'source_revision', 'content_sha256', 'parent_project_id', 'owner_scope',
              'media_type', 'preview_uri_or_action', 'license', 'visibility', 'rights_status', 'citation', 'methodology',
              'units', 'uncertainty', 'generated_at', 'lineage', 'snapshot_receipt'):
        assert asset[k], k
    assert asset['visibility'] == 'private' and v1['publicApproval'] == 'not-approved'
    assert asset['units'] == {'x': 'mg', 'fit': 'units', 'lower': 'units', 'upper': 'units', 'evidenceClass': 'category'}
    assert v1['dataset'][0]['sha256'] == 'b' * 64 and 'receipt rcpt-run-1' in v1['calculation'][0]['method']
    assert asset['content_sha256'] == v1['artifacts']['chart']['sha256']
    assert {a['sha256'] for a in v1['artifacts'].values()} == {s.read(None, 'owner', PROJECT, a['artifactId'])[0]['sha256']
                                                               for a in v1['artifacts'].values()}
    # The same verified run again changes nothing.
    again = call(client, 'POST', f'{PROJECT}/register', json=body(s))
    assert again.status_code == 200 and again.json()['created'] is False
    # A new computation is version 2 under new artifact ids; version 1 is byte-for-byte what it was.
    runs['current'] = 'run-2'
    r2 = call(client, 'POST', f'{PROJECT}/register', json=body(s))
    assert r2.status_code == 201 and r2.json()['output']['version'] == 2
    versions = sco.registry(s.row.package)['outputs'][0]['versions']
    assert versions[0] == v1 and versions[1]['artifacts']['chart']['artifactId'].endswith('-v2-chart')
    found = call(client, 'GET', f'{PROJECT}?q=dose').json()['outputs']
    assert [v['version'] for v in found[0]['versions']] == [2, 1] and call(client, 'GET', f'{PROJECT}?q=nothing').json()['outputs'] == []


def test_registration_gates(env):
    s, _, client = env
    assert call(client, 'POST', f'{PROJECT}/register', user=None, json=body(s)).status_code == 401
    assert call(client, 'POST', f'{PROJECT}/register', user='stranger', json=body(s)).status_code == 404
    assert call(client, 'POST', f'{PROJECT}/register', json=body(s, expectedProjectRevision=9)).status_code == 409
    assert call(client, 'POST', f'{PROJECT}/register', json=body(s, notebookId='nb-other')).status_code == 404
    assert call(client, 'POST', f'{PROJECT}/register', json=body(s, figure=figure(caption='Has [brackets] in a caption'))).status_code == 422
    assert call(client, 'POST', f'{PROJECT}/register', json=body(s, figure=figure(evidenceClass='observed'))).status_code == 422
    assert call(client, 'POST', f'{PROJECT}/register', json=body(s, rights={**RIGHTS, 'sourceLicences': {'x': 'y'}})).status_code == 422
    assert sco.registry(s.row.package)['outputs'] == [] and s.artifacts == {}


def test_rights_gate_then_insertion_of_the_exact_version(env):
    s, _, client = env
    pending = {**RIGHTS, 'status': 'pending', 'sourceLicences': {}}
    assert call(client, 'POST', f'{PROJECT}/register', json=body(s, rights=pending)).status_code == 201
    url = f'{PROJECT}/outputs/SYN-dose-response/versions/1'
    r = call(client, 'GET', url + '/insertion')
    assert r.status_code == 409 and len(r.json()['detail']['blockers']) == 2
    ok = call(client, 'POST', url + '/rights', json={'rights': RIGHTS, 'expectedProjectRevision': s.row.revision})
    assert ok.status_code == 200 and ok.json()['output']['insertable']
    v = sco.registry(s.row.package)['outputs'][0]['versions'][0]
    assert [x['status'] for x in v['rights']] == ['pending', 'owner-declared']  # declarations are appended
    ins = call(client, 'GET', url + '/insertion').json()
    md = ins['markdown']
    assert md.startswith(f"![SYNTHETIC fitted response by dose with its 95% confidence band](asset:{v['artifacts']['chart']['artifactId']})\n")
    assert '| 1 | 2.050 | 1.512 | 2.588 |' in md and 'Evidence class: modelled.' in md and 'licence CC0-1.0' in md
    blocks = pub.parse_blocks(md)
    assert [b['kind'] for b in blocks] == ['figure', 'paragraph', 'table', 'paragraph']
    csv = call(client, 'GET', url + '/table.csv')
    assert csv.status_code == 200 and hashlib.sha256(csv.content).hexdigest() == v['artifacts']['table']['sha256']
    inspect = call(client, 'GET', url).json()
    assert set(inspect['integrity'].values()) == {'verified'}
    assert call(client, 'GET', url, user='stranger').status_code == 404


def test_integrity_failure_blocks_insertion_and_is_reported(env):
    s, _, client = env
    call(client, 'POST', f'{PROJECT}/register', json=body(s))
    v = sco.registry(s.row.package)['outputs'][0]['versions'][0]
    s.artifacts[('owner', v['artifacts']['chart']['artifactId'])]['sha256'] = 'e' * 64  # replaced behind the registry
    url = f'{PROJECT}/outputs/SYN-dose-response/versions/1'
    assert call(client, 'GET', url).json()['integrity']['chart'] == 'changed'
    assert call(client, 'GET', url + '/insertion').status_code == 409


def test_save_pins_exact_versions_refuses_pending_rights_and_exports_render_the_output(env):
    s, runs, client = env
    call(client, 'POST', f'{PROJECT}/register', json=body(s))
    runs['current'] = 'run-2'
    call(client, 'POST', f'{PROJECT}/register', json=body(s))
    v1 = sco.registry(s.row.package)['outputs'][0]['versions'][0]
    md = '# Synthetic\n\nIntro.\n\n' + call(client, 'GET', f'{PROJECT}/outputs/SYN-dose-response/versions/1/insertion').json()['markdown']
    html, figures = pub.render_html(md)
    pins = sco.pins(s.row.package, figures, pub.parse_blocks(md))
    assert pins == [{'outputId': 'SYN-dose-response', 'version': 1,
                     **{f'{k}ArtifactId': a['artifactId'] for k, a in v1['artifacts'].items()},
                     **{f'{k}Sha256': a['sha256'] for k, a in v1['artifacts'].items()}, 'tableVerbatim': True}]
    edited = md.replace('| 2 | 3.100 |', '| 2 | 3.200 |')
    assert edited != md
    assert sco.pins(s.row.package, figures, pub.parse_blocks(edited))[0]['tableVerbatim'] is False
    sco.verify_pins(None, 'owner', PROJECT, {'outputSources': pins}, s.read)
    s.artifacts[('owner', v1['artifacts']['bundle']['artifactId'])]['raw'] += b' '
    with pytest.raises(HTTPException) as exc:
        sco.verify_pins(None, 'owner', PROJECT, {'outputSources': pins}, s.read)
    assert exc.value.status_code == 409
    # A pending version cannot be saved into a revision even if its figure line is typed by hand.
    registry = sco.registry(s.row.package)
    registry['outputs'][0]['versions'][1]['rights'].append({**RIGHTS, 'status': 'pending', 'declaredAt': 'now'})
    v2_chart = registry['outputs'][0]['versions'][1]['artifacts']['chart']['artifactId']
    with pytest.raises(HTTPException) as exc:
        sco.pins(s.row.package, [v2_chart], [])
    assert exc.value.status_code == 409
    # The three export formats render the inserted figure, caption, table and source note.
    svg = pub.sanitize_svg(s.read(None, 'owner', PROJECT, v1['artifacts']['chart']['artifactId'])[1])
    doc = {'title': 'Synthetic', 'markdown': md, 'revision': 1, 'publicationType': 'report', 'citations': None,
           'markdownSHA256': hashlib.sha256(md.encode()).hexdigest(), 'figureSources': [], 'outputSources': pins}
    chart = v1['artifacts']['chart']['artifactId']
    out = pub._as_html(doc, {chart: 'data:image/svg+xml;base64,' + __import__('base64').b64encode(svg).decode()}).decode()
    assert '<img src="data:image/svg+xml;base64,' in out and '<th>Dose (mg)</th>' in out and '<td>2.588</td>' in out and '<td>2.050</td>' in out
    assert 'Scientific output SYN-dose-response version 1' in out
    pdf = pub._pdf(doc, {chart: svg})
    assert pdf.startswith(b'%PDF')
    from docx import Document
    d = Document(BytesIO(pub._docx(doc, {chart: svg})))
    assert len(d.tables) == 1 and d.tables[0].rows[1].cells[3].text == '2.588'
    assert len(d.inline_shapes) == 1 and any('SYN-dose-response version 1' in p.text for p in d.paragraphs)


def test_every_route_needs_a_signed_in_owner():
    app = FastAPI()
    app.include_router(pub.router)
    c = TestClient(app)
    base = '/publication/scientific-outputs/projects/p'
    assert c.get(base).status_code == 401
    assert c.get(base + '/outputs/o/versions/1').status_code == 401
    assert c.get(base + '/outputs/o/versions/1/insertion').status_code == 401
    assert c.post(base + '/register', json=body(types.SimpleNamespace(row=types.SimpleNamespace(revision=1)))).status_code == 401
