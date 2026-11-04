"""Publisher-source heatmap adapter and native reporting integration regressions."""
from copy import deepcopy
from io import BytesIO
import base64
import csv
import hashlib
import json
import os
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import pytest
from test_research_reporting import setup, env, stage, save, url, REPORTING
from test_wxr_private_projects import ROOT, ORIGIN
from app import session_auth

FIXTURE = Path(__file__).parent/'fixtures/sc_rvf_01/epa_136_table_2_4.json'


def source(): return json.loads(Path(os.getenv('SC_RVF_LAB_FIGURE', str(FIXTURE))).read_text())


def reference(setup, obj=None):
    ref, raw = stage(setup, source() if obj is None else obj)
    ref.update(heatmap_unit='t C/ha', evidence_classification='modeled',
        dataset_refs=['EPA:136:Table2.4:without-peat:grassland-average:arable'],
        computation_refs=['published-estimates:no-new-calculation'],
        evidence_refs=['EPA:136:printed-page19:pdf-page26'],
        rights_ref='EPA PDF p. ii reproduction with source acknowledgment.',
        reproduction='Use the pinned Table 2.4 extract. No pooling or summation; human extraction review pending.')
    return ref, raw


def test_epa_values_and_semantics():
    obj = source()
    assert [(c['z'], c['standardError']) for c in obj['cells']] == [
        (52.2,.6),(29.9,1.6),(127.1,1.7),(81.3,4.5),
        (170.9,2.7),(117.6,7.2),(213.8,4.5),(167.5,12.2)]
    assert obj['axisLabels']['x'][0] == 'Grassland + rough grazing'
    assert obj['scientificContext']['source']['extraction_review']['human_review'] == 'pending'
    assert obj['scientificContext']['source']['library_binding'] is None
    assert obj['scientificContext']['source']['core_binding'] is None


@pytest.mark.parametrize('mutation', ['unit','missing-se','negative-se','boolean-se','bad-labels','crs','wrong-interval','missing-warning','missing-hash'])
def test_bad_scientific_metadata_fails_closed(setup, mutation):
    obj = source()
    if mutation == 'unit': obj['scientificContext']['unit'] = 't CO2/ha'
    if mutation == 'missing-se': obj['cells'][0].pop('standardError')
    if mutation == 'negative-se': obj['cells'][0]['standardError'] = -1
    if mutation == 'boolean-se': obj['cells'][0]['standardError'] = True
    if mutation == 'bad-labels': obj['axisLabels']['y'] = ['0-10']
    if mutation == 'crs': obj['spatialReference'] = {'crs':'EPSG:2157'}
    if mutation == 'wrong-interval': obj['scientificContext']['uncertainty_kind'] = '95% CI'
    if mutation == 'missing-warning': obj['scientificContext'].pop('warning')
    if mutation == 'missing-hash': obj['scientificContext']['source'].pop('sha256')
    ref, _ = reference(setup, obj)
    client, _, _, pid = setup
    response = client.post(f'{REPORTING}/projects/{pid}/reports',json=ref,headers=ORIGIN)
    assert response.status_code == 422, response.text
    assert client.get(f'{ROOT}/{pid}').json()['project']['revision'] == 1


def test_published_heatmap_save_reopen_and_exports(setup):
    client, _, _, pid = setup
    ref, raw = reference(setup)
    report = save(client, pid, ref)
    target = url(pid, report)
    original = client.get(target).json()
    assert report['axes'][0]['definition']['kind'] == 'categorical'
    svg = original['view']['svg']
    assert '52.2 ± 0.6 SE' in svg and '213.8 ± 4.5 SE' in svg
    assert 'Grassland + rough grazing' in svg
    assert 'Cumulative depths overlap; do not sum.' in svg
    assert original['view']['scientific_verification_performed'] is False
    client.cookies.clear()
    assert client.get(target).status_code == 401
    client.cookies.set('sc_workspace_session', session_auth.issue_session_token('alice'))
    assert client.get(target).json() == original
    response = client.get(target+'/export.csv')
    assert response.status_code == 200
    rows = list(csv.DictReader(response.text.splitlines()))
    assert len(rows) == 8 and rows[6]['standard_error'] == '4.5'
    assert rows[6]['x'] == 'Grassland + rough grazing'
    pdf = client.get(target+'/export.pdf')
    assert pdf.status_code == 200 and pdf.content.startswith(b'%PDF')
    png = client.get(target+'/export.png')
    assert png.status_code == 200 and png.content.startswith(b'\x89PNG')
    word = client.get(target+'/export.docx')
    assert word.status_code == 200, word.text if word.status_code != 200 else ''
    assert client.get(target+'/export.docx').content == word.content
    assert client.get(target+'/export.pdf').content == pdf.content
    with ZipFile(BytesIO(word.content)) as archive:
        source_xml = ET.fromstring(archive.read('customXml/sc-source.xml'))
        assert json.loads(base64.b64decode(source_xml.text)) == source()
        svg_xml = ET.fromstring(archive.read('customXml/sc-figure.xml'))
        assert base64.b64decode(svg_xml.text).decode() == svg
        assert archive.read('word/media/image1.png') == png.content
        text = archive.read('word/document.xml').decode()
        assert '213.8' in text and '4.5' in text and 'Cumulative depths overlap' in text
    assert word.headers['x-research-sha256'] == hashlib.sha256(raw).hexdigest()
    # Optional evidence capture uses the real HTTP persistence/export routes with
    # isolated SQLite, a temporary object store, and a synthetic signed session.
    if os.getenv('SC_RVF_EVIDENCE_DIR'):
        dest = Path(os.environ['SC_RVF_EVIDENCE_DIR']); dest.mkdir(parents=True,exist_ok=True)
        for name, data in [('heatmap.svg',svg.encode()), ('heatmap.csv',response.content),
                           ('heatmap.pdf',pdf.content), ('heatmap.docx',word.content), ('heatmap.png',png.content),
                           ('heatmap-source.json',raw), ('saved-report.json',json.dumps(original,indent=2).encode())]:
            (dest/name).write_bytes(data)
    client.cookies.set('sc_workspace_session', session_auth.issue_session_token('bob'))
    for suffix in ['', '/export.csv', '/export.pdf', '/export.docx', '/export.png']:
        assert client.get(target+suffix).status_code == 404


def test_new_display_revision_does_not_change_saved_source(setup):
    client, _, _, pid = setup
    ref, raw = reference(setup)
    first = save(client,pid,ref)
    old = client.get(url(pid,first)).json()
    ref['expected_project_revision'] = 2
    ref['display']['palette'] = 'diverging'
    second = save(client,pid,ref)
    assert client.get(url(pid,first)).json() == old
    assert client.get(url(pid,second)).json()['view']['svg'] != old['view']['svg']
    assert client.get(f"{ROOT}/{pid}/files/{ref['artifact_id']}/download").content == raw
