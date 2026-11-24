"""SC-OUTPUT-02: cross-application scientific outputs. A Workbench calculation (through its governed Workspace adapter)
over a byte-pinned dataset whose variables and units the Library describes, registered with one common source
reference, filtered by application, inserted once, numbered consistently in every export. Synthetic data; offline fakes."""
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
o1 = importlib.import_module('tests.test_sc_output01_scientific_outputs')

PROJECT, SOURCE = o1.PROJECT, o1.SOURCE
OP = 'workspace.workbench.uncertainty-propagation'  # with dataset-bound rows (Workbench #54)
# What the Workbench adapter returns for rate*f*k per plot (first-order, ± one standard uncertainty), inside the
# polyglot envelope Workspace stores for the run.
ROWS = [{'rate': 0.0, 'value': 0.0, 'standardUncertainty': 0.0, 'lower': 0.0, 'upper': 0.0},
        {'rate': 10.0, 'value': 0.33, 'standardUncertainty': 0.0687, 'lower': 0.2613, 'upper': 0.3987},
        {'rate': 20.0, 'value': 0.6, 'standardUncertainty': 0.1616, 'lower': 0.4384, 'upper': 0.7616}]
RESULT = {'schema': fb.POLYGLOT_RESULT, 'result': {'remote': {'ok': True, 'schema': 'sc-workbench-workspace-adapter-result/1.0',
          'result': {'schema': 'sc-workbench-uncertainty-rows-result/1.0', 'rows': ROWS}}}}
DESCRIPTOR = {'sourceId': SOURCE, 'title': 'SYNTHETIC Wexford-style basalt plot trial',
              'kind': 'simulation', 'provider': 'Sustainable Catalyst (synthetic test data)',
              'variables': [{'name': 'rate', 'role': 'treatment', 'unit': 't/ha'},
                            {'name': 'f', 'role': 'outcome', 'unit': '1'}, {'name': 'f_sd', 'role': 'other', 'unit': '1'}]}


def figure(**kw):
    body = {'figureId': 'SYN-basalt-cdr', 'title': 'SYNTHETIC estimated CO2 removal by basalt application rate',
            'rowsPath': 'rows', 'mark': 'line',
            'x': {'field': 'rate', 'label': 'Basalt application rate', 'unit': 't/ha'},
            'y': {'field': 'value', 'label': 'Estimated CO2 removal', 'unit': 't CO2/ha'},
            'uncertainty': {'kind': 'sd', 'lowerField': 'lower', 'upperField': 'upper',
                            'statement': 'Bounds are ± one standard uncertainty from Workbench first-order propagation.'},
            'evidenceClass': 'modelled', 'caption': 'SYNTHETIC estimated CO2 removal by basalt application rate',
            'altText': 'A rising line from 0 at 0 t/ha to 0.6 t CO2/ha at 20 t/ha with a widening band.',
            'interpretation': 'Synthetic propagation used to exercise the cross-application path.',
            'limitations': ['Synthetic data; not observed Wexford evidence']}
    body.update(kw)
    return body


def package(run='wb-1', language='workbench', **kw):
    rev = types.SimpleNamespace(notebook_id='nb-syn', revision=1, project_id=PROJECT)
    ev = {'runId': run, '_run': types.SimpleNamespace(finished_at=datetime(2026, 11, 20, 9, 0, tzinfo=timezone.utc),
                                                     created_at=None, input_fingerprint='a' * 64, project_id=PROJECT),
          'verification': {'status': 'executed-verified', 'inputLineage': 'artifact-bound-verified',
                           'inputBindings': [{'datasetId': 'ds-1', 'datasetRevision': 1, 'artifactSha256': 'b' * 64}],
                           'runtimeReceipts': [{'receiptId': 'rcpt-' + run, 'language': language,
                                                'runtime': 'workbench-calculation-engine', 'operation': OP,
                                                'resultSha256': 'c' * 64}]}}
    return rev, fb.build_package(rev, 'cdr', 'd' * 64, ev, RESULT, fb.FigureRequest(**figure(**kw)))


def library_fake(calls):
    def post(url, body):
        calls.append((url, body))
        ds = body['datasets'][0]
        return {'schema': 'sc-library-dataset-profile/1.0', 'profile_id': 'dataset-profile:' + 'f' * 32,
                'profile_fingerprint_sha256': hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest(),
                'library_version': '6.23.0', 'backend_version': '6.38.0',
                'dataset': {'dataset_id': ds['dataset_id'], 'title': ds['title'],
                            'variables': [{'name': v['name'], 'role': v['role'], 'unit': v['unit'] or None} for v in ds['variables']]}}
    return post


@pytest.fixture
def env(monkeypatch):
    s = o1.Store()
    state = {'run': 'wb-1', 'language': 'workbench', 'library': []}
    monkeypatch.setattr(sco.object_store, 'get_artifact', s.get)
    monkeypatch.setattr(sco.object_store, 'store_artifact', s.put)
    monkeypatch.setenv('SC_WORKSPACE_LIBRARY_PROFILE_ORIGIN', 'http://library-profile:8080')

    def verified(db, owner, nb, rev, cell, req):
        if owner != 'owner' or nb != 'nb-syn':
            raise HTTPException(404, 'Workspace notebook revision not found.')
        if state['language'] == 'r':
            return o1.package(run=state['run'])
        return package(run=state['run'], language=state['language'])
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
                                         'original_asset': s.read, 'sanitize_svg': pub.sanitize_svg,
                                         'library_post': library_fake(state['library'])}))
    return s, state, TestClient(app)


def body(s, **kw):
    b = {'notebookId': 'nb-syn', 'revision': 1, 'cellId': 'cdr', 'figure': figure(),
         'table': {'caption': 'SYNTHETIC estimated CO2 removal by application rate', 'significantFigures': 3},
         'rights': o1.RIGHTS, 'citation': 'Synthetic Author (2026) SYNTHETIC basalt plot trial (not observed evidence).',
         'library': DESCRIPTOR, 'expectedProjectRevision': s.row.revision}
    b.update(kw)
    return b


call = o1.call


def test_workbench_output_carries_the_common_source_reference_and_library_profile(env):
    s, state, client = env
    r = call(client, 'POST', f'{PROJECT}/register', json=body(s))
    assert r.status_code == 201, r.text
    assert r.json()['output']['application'] == 'workbench' and r.json()['output']['library']
    url, sent = state['library'][0]
    assert url == 'http://library-profile:8080/api/library/v1/statistical-evidence/dataset-profile'
    assert 'rows' not in json.dumps(sent) and sent['datasets'][0]['variables'][0]['unit'] == 't/ha'  # no rows leave Workspace
    v = call(client, 'GET', f'{PROJECT}/outputs/SYN-basalt-cdr/versions/1').json()
    ref = v['sourceReference']
    assert ref['schema'] == 'sc-scientific-source-reference/1.0' and ref['application'] == 'workbench'
    assert ref['computedBy']['operation'] == OP and ref['computedBy']['language'] == 'workbench'
    assert ref['binding'] == {'ownerScope': 'owner-private', 'projectId': PROJECT, 'visibility': 'private',
                              'publicApproval': 'not-approved'}
    assert ref['artifact']['immutableVersion'] == 'SYN-basalt-cdr@v1' and set(ref['artifact']['hashes']) == {'chart', 'table', 'bundle'}
    assert ref['lineage']['datasets'] == [{'sourceId': SOURCE, 'sha256': 'b' * 64, 'identityStatus': 'source-hash-verified'}]
    assert ref['lineage']['library']['profileSha256'] and ref['units']['rate'] == 't/ha' and ref['evidenceClass'] == 'modelled'
    assert ref['rights']['license'] == 'CC-BY-4.0' and ref['rights']['sourceLicences'] == {SOURCE: 'CC0-1.0'}
    assert ref['verification']['status'] == 'receipt-and-bytes-verified'
    assert ref['verification']['scientificConclusions'] == 'not-independently-verified'
    md = call(client, 'GET', f'{PROJECT}/outputs/SYN-basalt-cdr/versions/1/insertion').json()['markdown']
    assert f'computed by Workbench {OP} through its governed Workspace adapter' in md
    assert 'Library dataset profile dataset-profile:' in md and 'scientific conclusions are not independently verified' in md
    assert '| 10.0 | 0.330 | 0.261 | 0.399 |' in md


def test_library_gates_units_inputs_and_bad_profiles(env, monkeypatch):
    s, state, client = env
    wrong = {**DESCRIPTOR, 'variables': [{'name': 'rate', 'role': 'treatment', 'unit': 'kg/ha'}]}
    r = call(client, 'POST', f'{PROJECT}/register', json=body(s, library=wrong))
    assert r.status_code == 422 and r.json()['detail']['code'] == 'library-unit-mismatch'
    other = {**DESCRIPTOR, 'sourceId': 'workspace-dataset:other@r1'}
    r = call(client, 'POST', f'{PROJECT}/register', json=body(s, library=other))
    assert r.status_code == 422 and r.json()['detail']['code'] == 'library-dataset-not-an-input'
    assert s.artifacts == {} and sco.registry(s.row.package)['outputs'] == []
    with pytest.raises(HTTPException) as exc:  # a profile that does not echo the declared units is refused
        sco.library_profile(sco.LibraryDescriptor(**DESCRIPTOR), lambda u, b: {**library_fake([])(u, b), 'dataset': {
            'dataset_id': SOURCE, 'variables': [{'name': 'rate', 'unit': 'kg/ha'}]}})
    assert exc.value.status_code == 502
    for origin in ('', 'https://evil.example', 'http://10.0.0.1:8080', 'https://library.sustainablecatalyst.com/x'):
        monkeypatch.setenv('SC_WORKSPACE_LIBRARY_PROFILE_ORIGIN', origin)
        monkeypatch.delenv('SC_WORKSPACE_LIBRARY_PUBLIC_API_ORIGIN', raising=False)
        with pytest.raises(HTTPException) as exc:
            sco._library_origin()
        assert exc.value.status_code == 503, origin
    monkeypatch.setenv('SC_WORKSPACE_LIBRARY_PROFILE_ORIGIN', 'https://library.sustainablecatalyst.com')
    assert sco._library_origin() == 'https://library.sustainablecatalyst.com'
    # The discovery origin alone never enables dataset profiles: a descriptor is refused (503) and nothing is sent.
    monkeypatch.delenv('SC_WORKSPACE_LIBRARY_PROFILE_ORIGIN')
    monkeypatch.setenv('SC_WORKSPACE_LIBRARY_PUBLIC_API_ORIGIN', 'https://library.sustainablecatalyst.com')
    with pytest.raises(HTTPException) as exc:
        sco._library_origin()
    assert exc.value.status_code == 503
    sent = []
    with pytest.raises(HTTPException) as exc:
        sco.library_profile(sco.LibraryDescriptor(**DESCRIPTOR), lambda u, b: sent.append(u))
    assert exc.value.status_code == 503 and sent == []
    # Without a Library descriptor the output still registers (the descriptor is optional), as before.
    assert call(client, 'POST', f'{PROJECT}/register', json=body(s, library=None)).status_code == 201


def test_search_filters_by_application_and_reports_the_latest_version(env):
    s, state, client = env
    assert call(client, 'POST', f'{PROJECT}/register', json=body(s)).status_code == 201
    state.update(run='wb-2')
    assert call(client, 'POST', f'{PROJECT}/register', json=body(s)).status_code == 201
    state.update(language='r', run='run-1')
    assert call(client, 'POST', f'{PROJECT}/register', json=o1.body(s)).status_code == 201
    every = call(client, 'GET', PROJECT).json()
    assert {o['outputId']: o['application'] for o in every['outputs']} == {'SYN-basalt-cdr': 'workbench',
                                                                          'SYN-dose-response': 'workspace-notebook'}
    assert {a['application']: a['outputs'] for a in every['applications']} == {'workspace-notebook': 1, 'workbench': 1,
                                                                               'decision-studio': 0}
    wb = call(client, 'GET', f'{PROJECT}?application=workbench').json()['outputs']
    assert [o['outputId'] for o in wb] == ['SYN-basalt-cdr'] and wb[0]['latestVersion'] == 2
    assert [v['version'] for v in wb[0]['versions']] == [2, 1]
    assert call(client, 'GET', f'{PROJECT}?q=wexford').json()['outputs'][0]['outputId'] == 'SYN-basalt-cdr'  # Library title
    assert call(client, 'GET', f'{PROJECT}?application=lab').status_code == 422
    v1 = call(client, 'GET', f'{PROJECT}/outputs/SYN-basalt-cdr/versions/1').json()
    assert v1['latestVersion'] == 2 and v1['version'] == 1
    # SC-OUTPUT-01 versions (no receipt language recorded) are Workspace notebook outputs.
    legacy = {**v1, 'run': {k: x for k, x in v1['run'].items() if k != 'language'}}
    assert sco.application_of(legacy) == 'workspace-notebook'


def test_duplicate_output_versions_are_refused_on_save_but_two_versions_may_coexist(env):
    s, state, client = env
    call(client, 'POST', f'{PROJECT}/register', json=body(s))
    state.update(run='wb-2')
    call(client, 'POST', f'{PROJECT}/register', json=body(s))
    ins = lambda n: call(client, 'GET', f'{PROJECT}/outputs/SYN-basalt-cdr/versions/{n}/insertion').json()['markdown']
    both = 'Intro.\n\n' + ins(1) + '\nMiddle.\n\n' + ins(2)
    _, figures = pub.render_html(both)
    assert [p['version'] for p in sco.pins(s.row.package, figures, pub.parse_blocks(both))] == [1, 2]
    twice = 'Intro.\n\n' + ins(1) + '\nMiddle.\n\n' + ins(1)
    _, figures = pub.render_html(twice)
    with pytest.raises(HTTPException) as exc:
        sco.pins(s.row.package, figures, pub.parse_blocks(twice))
    assert exc.value.status_code == 409 and exc.value.detail['code'] == 'output-duplicate'


def test_exports_number_figures_and_tables_consistently_and_keep_every_row(env):
    s, state, client = env
    call(client, 'POST', f'{PROJECT}/register', json=body(s))
    v = sco.registry(s.row.package)['outputs'][0]['versions'][0]
    chart = v['artifacts']['chart']['artifactId']
    md = ('Opening.\n\n![Plain photograph of the site](asset:photo-1)\n\n'
          + call(client, 'GET', f'{PROJECT}/outputs/SYN-basalt-cdr/versions/1/insertion').json()['markdown']
          + '\n| a | b |\n| --- | --- |\n' + ''.join(f'| {i} | {i * 2} |\n' for i in range(150)))
    blocks = pub.number_blocks(pub.parse_blocks(md))
    assert [b.get('label') for b in blocks if b['kind'] in ('figure', 'table')] == ['Figure 1.', 'Figure 2.', 'Table 1.', None]
    assert len([b for b in blocks if b['kind'] == 'table'][1]['rows']) == 150  # more than the former 100-row cut
    svg = pub.sanitize_svg(s.read(None, 'owner', PROJECT, chart)[1])
    from PIL import Image
    buf = BytesIO(); Image.new('RGB', (40, 20), 'white').save(buf, 'PNG')
    figures = {chart: svg, 'photo-1': buf.getvalue()}
    doc = {'title': 'Synthetic', 'markdown': md, 'revision': 1, 'publicationType': 'report', 'citations': None,
           'markdownSHA256': hashlib.sha256(md.encode()).hexdigest(), 'figureSources': []}
    html = pub._as_html(doc, {k: 'data:image/png;base64,' for k in figures}).decode()
    assert '<figcaption><strong>Figure 2.</strong> SYNTHETIC estimated CO2 removal' in html
    assert '<table><caption><strong>Table 1.</strong> SYNTHETIC estimated CO2 removal by application rate' in html
    assert '<th scope="col">Basalt application rate (t/ha)</th>' in html and html.count('<th scope="col">') == 6
    assert '**Table:' not in html and html.count('<tr>') == 1 + 3 + 1 + 150
    from docx import Document
    d = Document(BytesIO(pub._docx(doc, figures)))
    captions = [p.text for p in d.paragraphs if p.style.name == 'Caption']
    assert captions[:3] == ['Figure 1. Plain photograph of the site', 'Figure 2. SYNTHETIC estimated CO2 removal by basalt application rate',
                            captions[2]] and captions[2].startswith('Table 1. SYNTHETIC estimated CO2 removal by application rate')
    assert len(d.tables) == 2 and len(d.tables[1].rows) == 151 and d.tables[0].rows[2].cells[0].text == '10.0'
    pdf = pub._pdf(doc, figures)
    from pypdf import PdfReader
    text = ''.join(p.extract_text() for p in PdfReader(BytesIO(pdf)).pages)
    assert 'Figure 2.' in text and 'Table 1.' in text and '| 149 |' not in text and '298' in text
    figure = pub._pdf_svg_image(svg)
    assert figure.imageWidth >= 2000  # 300 dpi static figure


def test_numbering_keeps_captions_that_are_already_numbered():
    blocks = pub.number_blocks(pub.parse_blocks('![Figure 3: imported caption](asset:a1)\n\n![Second](asset:a2)\n'))
    assert [b['label'] for b in blocks] == ['', 'Figure 2.']
    html, _ = pub.render_html('**Table: Not followed by a table** text\n\nParagraph.\n')
    assert '<p><strong>Table: Not followed by a table</strong> text</p>' in html


def test_isolation_tampering_and_missing_artifacts(env):
    s, state, client = env
    call(client, 'POST', f'{PROJECT}/register', json=body(s))
    url = f'{PROJECT}/outputs/SYN-basalt-cdr/versions/1'
    assert call(client, 'GET', url, user=None).status_code == 401
    assert call(client, 'GET', url, user='stranger').status_code == 404
    assert call(client, 'GET', PROJECT, user='stranger').status_code == 404
    v = sco.registry(s.row.package)['outputs'][0]['versions'][0]
    s.artifacts[('owner', v['artifacts']['table']['artifactId'])]['raw'] += b'1'  # altered bytes
    r = call(client, 'GET', url).json()
    assert r['integrity']['table'] == 'changed' and call(client, 'GET', url + '/insertion').status_code == 409
    assert call(client, 'GET', url + '/table.csv').status_code == 409
    del s.artifacts[('owner', v['artifacts']['chart']['artifactId'])]  # missing source artifact
    assert call(client, 'GET', url).json()['integrity']['chart'] == 'missing'
    assert call(client, 'GET', f'{PROJECT}/outputs/SYN-basalt-cdr/versions/9').status_code == 404  # stale/unknown version


def test_unsupported_figures_are_refused(env):
    s, _, client = env
    assert call(client, 'POST', f'{PROJECT}/register', json=body(s, figure=figure(mark='bar'))).status_code == 422
    nominal = figure(x={'field': 'rate', 'label': 'Rate', 'unit': 't/ha', 'type': 'nominal'})
    assert call(client, 'POST', f'{PROJECT}/register', json=body(s, figure=nominal)).status_code == 422
    assert s.artifacts == {}
