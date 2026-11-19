"""SC-RESEARCH-DOCS-01: document register and full-document viewer (synthetic documents only).

The renderer must reproduce text, figures and tables from the original DOCX, escape everything, and say what it
could not render. The register pins originals and renditions by hash, admits only private documents and the
recorded submission-status vocabulary, and every read is re-verified against the store.
"""
import base64
import contextlib
import hashlib
import io
import json
import zipfile

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app import research_documents as rd

PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==')
NS = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
      'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
      'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
      'xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart" '
      'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"')


def drawing(rid, name='Figure one'):
    return (f'<w:r><w:drawing><wp:inline><wp:extent cx="952500" cy="952500"/><wp:docPr id="1" name="{name}" '
            f'descr="{name}"/><a:graphic><a:graphicData><a:blip r:embed="{rid}"/></a:graphicData></a:graphic>'
            '</wp:inline></w:drawing></w:r>')


def docx(body, *, media=None, rels='', footnotes=None, numbering=None):
    files = {
        '[Content_Types].xml': '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>',
        'word/document.xml': f'<w:document {NS}><w:body>{body}</w:body></w:document>',
        'word/_rels/document.xml.rels': ('<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                                         '<Relationship Id="rIdImg" Target="media/image1.png" Type="image"/>'
                                         '<Relationship Id="rIdBmp" Target="media/image2.bmp" Type="image"/>'
                                         '<Relationship Id="rIdWeb" Target="https://example.org/a?b=1&amp;c=2" TargetMode="External" Type="hyperlink"/>'
                                         '<Relationship Id="rIdJs" Target="javascript:alert(1)" TargetMode="External" Type="hyperlink"/>'
                                         f'{rels}</Relationships>'),
        'word/styles.xml': (f'<w:styles {NS}><w:style w:styleId="Heading1"><w:name w:val="heading 1"/></w:style>'
                            '<w:style w:styleId="Title"><w:name w:val="Title"/></w:style>'
                            '<w:style w:styleId="Caption"><w:name w:val="caption"/></w:style></w:styles>'),
    }
    if footnotes:
        files['word/footnotes.xml'] = f'<w:footnotes {NS}>{footnotes}</w:footnotes>'
    if numbering:
        files['word/numbering.xml'] = f'<w:numbering {NS}>{numbering}</w:numbering>'
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w') as z:
        for name, content in files.items():
            z.writestr(name, content)
        for name, raw in (media or {'word/media/image1.png': PNG, 'word/media/image2.bmp': b'BM' + b'\0' * 40}).items():
            z.writestr(name, raw)
    return out.getvalue()


def p(text, style=None, extra=''):
    ppr = f'<w:pPr><w:pStyle w:val="{style}"/>{extra}</w:pPr>' if style else (f'<w:pPr>{extra}</w:pPr>' if extra else '')
    return f'<w:p>{ppr}<w:r><w:t xml:space="preserve">{text}</w:t></w:r></w:p>'


TABLE = ('<w:tbl><w:tr><w:trPr><w:tblHeader/></w:trPr><w:tc><w:tcPr><w:gridSpan w:val="2"/></w:tcPr>' + p('Head') + '</w:tc></w:tr>'
         '<w:tr><w:tc><w:tcPr><w:vMerge w:val="restart"/></w:tcPr>' + p('Merged') + '</w:tc><w:tc>' + p('B1') + '</w:tc></w:tr>'
         '<w:tr><w:tc><w:tcPr><w:vMerge/></w:tcPr><w:p/></w:tc><w:tc>' + p('B2') + '</w:tc></w:tr></w:tbl>')


def test_renders_text_structure_tables_figures_and_footnotes():
    body = (p('Report &lt;script&gt;alert(1)&lt;/script&gt;', 'Title') + p('Methods', 'Heading1')
            + '<w:p><w:r><w:rPr><w:b/></w:rPr><w:t>bold</w:t></w:r><w:r><w:rPr><w:vertAlign w:val="subscript"/></w:rPr>'
              '<w:t>2</w:t></w:r><w:r><w:footnoteReference w:id="5"/></w:r></w:p>'
            + '<w:p>' + drawing('rIdImg') + '</w:p>' + p('Figure 1. Caption', 'Caption') + TABLE
            + '<w:p><w:hyperlink r:id="rIdWeb"><w:r><w:t>safe</w:t></w:r></w:hyperlink>'
              '<w:hyperlink r:id="rIdJs"><w:r><w:t>unsafe</w:t></w:r></w:hyperlink></w:p>'
            + p('item', extra='<w:numPr><w:numId w:val="3"/></w:numPr>')
            + '<w:p><w:del><w:r><w:delText>gone</w:delText></w:r></w:del></w:p>')
    raw = docx(body, footnotes=f'<w:footnote w:id="5">{p("A note.")}</w:footnote>',
               numbering='<w:abstractNum w:abstractNumId="9"><w:lvl><w:numFmt w:val="decimal"/></w:lvl></w:abstractNum>'
                         '<w:num w:numId="3"><w:abstractNumId w:val="9"/></w:num>')
    html, stats = rd.render_docx(raw)
    assert '<h1 class="doc-title">Report &lt;script&gt;alert(1)&lt;/script&gt;</h1>' in html and '<script' not in html
    assert '<h2>Methods</h2>' in html and '<strong>bold</strong>' in html and '<sub>2</sub>' in html
    assert 'src="data:image/png;base64,' in html and 'alt="Figure one"' in html and 'p class="caption"' in html
    assert '<th colspan="2">' in html and '<td rowspan="2"><p>Merged</p></td>' in html and html.count('<tr>') == 3
    assert '<a href="https://example.org/a?b=1&amp;c=2" rel="noopener noreferrer">safe</a>' in html
    assert 'javascript' not in html and 'unsafe' in html
    assert '<ol><li>item</li></ol>' in html and 'gone' not in html
    assert '<li id="fn-5"><p>A note.</p></li>' in html and 'href="#fn-5">1</a>' in html
    assert stats['figuresRendered'] == stats['figuresInSource'] == 1 and stats['tablesRendered'] == 1
    assert stats['unrendered']['trackedDeletions'] == 1 and stats['complete'] is False


def test_reports_what_it_cannot_render():
    body = ('<w:p>' + drawing('rIdBmp') + '</w:p><w:p><m:oMath/></w:p>'
            '<w:p><w:r><w:drawing><wp:inline><a:graphic><a:graphicData><c:chart/></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>')
    html, stats = rd.render_docx(docx(body))
    assert 'unsupported image format' in html and 'Drawing not rendered' in html
    assert stats['figuresInSource'] == 2 and stats['figuresRendered'] == 0
    assert stats['unrendered'] == {'equations': 1, 'textBoxes': 0, 'charts': 1, 'trackedDeletions': 0, 'unsupportedImages': 1}
    assert stats['complete'] is False


def test_rejects_invalid_and_oversized_packages(monkeypatch):
    with pytest.raises(HTTPException) as exc:
        rd.render_docx(b'not a docx')
    assert exc.value.status_code == 422
    monkeypatch.setattr(rd, 'MAX_UNCOMPRESSED', 100)
    with pytest.raises(HTTPException) as exc:
        rd.render_docx(docx(p('x' * 200)))
    assert exc.value.status_code == 413
    monkeypatch.setattr(rd, 'MAX_UNCOMPRESSED', 80 * 1024 * 1024)
    entities = io.BytesIO()
    with zipfile.ZipFile(entities, 'w') as z:
        z.writestr('word/document.xml', f'<!DOCTYPE d [<!ENTITY a "expanded">]><w:document {NS}><w:body>'
                                        '<w:p><w:r><w:t>&a;</w:t></w:r></w:p></w:body></w:document>')
    html, _ = rd.render_docx(entities.getvalue())
    assert 'expanded' not in html  # entities are never resolved


# Register ------------------------------------------------------------------------------------------------------------

ORIGINAL = docx(p('Synthetic investigation report', 'Title') + '<w:p>' + drawing('rIdImg') + '</w:p>' + TABLE)
PDF = b'%PDF-1.4 synthetic\n%%EOF'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def register(**overrides):
    doc = {'documentId': 'synthetic-report', 'title': 'Synthetic report', 'documentType': 'scientific-report',
           'original': {'sha256': sha(ORIGINAL), 'bytes': len(ORIGINAL), 'format': 'docx', 'filename': 'report.docx'},
           'renditions': [{'sha256': sha(PDF), 'bytes': len(PDF), 'format': 'pdf', 'filename': 'report.pdf',
                           'origin': 'author-supplied', 'textCorrespondence': 0.9995}],
           'revisionLabel': 'Revised after submission', 'relatedVersions': [],
           'submissionStatus': 'post-submission-revision', 'authorship': 'PENDING_VERIFICATION',
           'visibility': 'private', **overrides.pop('doc', {})}
    return {'schema': rd.REGISTER_SCHEMA, 'programme': 'SC-RESEARCH-DOCS-01', 'registerRevision': 1,
            'projectId': 'proj-1', 'researchArea': {'id': 'climate-land-carbon', 'name': 'Climate, Land & Carbon'},
            'investigation': {'id': 'synthetic-investigation', 'name': 'Synthetic investigation'},
            'documents': [doc], **overrides}


@pytest.mark.parametrize('change', [
    {'doc': {'visibility': 'public'}},
    {'doc': {'submissionStatus': 'submitted'}},
    {'doc': {'independentlyReviewed': True}},
    {'doc': {'renditions': [{'sha256': 'a' * 64, 'bytes': 1, 'format': 'pdf', 'filename': 'x.pdf',
                             'origin': 'generated', 'textCorrespondence': 1}]}},
    {'programme': 'other'},
])
def test_register_admits_only_private_documents_and_recorded_statuses(change):
    with pytest.raises(ValueError):
        rd.Register.model_validate(register(**change))
    assert rd.Register.model_validate(register()).documents[0].visibility == 'private'


class Store:
    """Owner-scoped legacy artifacts plus a hash-addressed blob store (synthetic)."""

    def __init__(self, files):
        self.blobs = {sha(raw): raw for _, raw in files}
        self.rows = [{'artifactId': f'a{i}', 'filename': name, 'sha256': sha(raw), 'bytes': len(raw),
                      'mediaType': 'application/octet-stream'} for i, (name, raw) in enumerate(files)]

    def install(self, monkeypatch, owner='owner', project='proj-1'):
        def legacy(_db, who, pid):
            return (self.rows if (who, pid) == (owner, project) else []), True

        def blob(digest, size):
            raw = self.blobs.get(digest)
            if raw is None:
                raise HTTPException(503, 'Research blob is missing.')
            if len(raw) != size or sha(raw) != digest:
                raise HTTPException(409, 'Research blob integrity verification failed.')
            return raw

        monkeypatch.setattr(rd, 'read_legacy_artifacts', legacy)
        monkeypatch.setattr(rd, '_blob', blob)
        monkeypatch.setattr(rd, 'session_scope', contextlib.nullcontext)
        monkeypatch.setattr(rd, 'list_projects', lambda _db, who: [{'projectId': project}] if who == owner else [])

        def project_gate(_db, who, pid):
            if (who, pid) != (owner, project):
                raise HTTPException(404, 'Project not found.')
        monkeypatch.setattr(rd, '_project', project_gate)


def reg_bytes(data):
    return json.dumps(data).encode()


def client(monkeypatch, subject='owner'):
    def who(_request):
        if subject is None:
            raise HTTPException(401, 'A valid Workspace browser session is required.')
        return subject
    monkeypatch.setattr(rd, '_subject', who)
    app = FastAPI()
    app.include_router(rd.router, prefix='/v1/private-research/reporting-studio')
    return TestClient(app)


BASE = '/v1/private-research/reporting-studio/documents'


def test_latest_register_wins_and_duplicates_stop_for_review(monkeypatch):
    two = register(registerRevision=2, investigation={'id': 'synthetic-investigation', 'name': 'Renamed'})
    Store([('x/' + rd.REGISTER_FILENAME, reg_bytes(register())), ('y/' + rd.REGISTER_FILENAME, reg_bytes(two)),
           ('report.docx', ORIGINAL)]).install(monkeypatch)
    found = rd.project_register(None, 'owner', 'proj-1')
    assert found['register'].investigation.name == 'Renamed' and len(found['superseded']) == 1
    assert found['documents'][0]['artifactIds'] == ['a2', None]  # the PDF was not imported
    other = register(investigation={'id': 'synthetic-investigation', 'name': 'Other'})
    Store([('x/' + rd.REGISTER_FILENAME, reg_bytes(register())), ('y/' + rd.REGISTER_FILENAME, reg_bytes(other))]).install(monkeypatch)
    with pytest.raises(HTTPException) as exc:
        rd.project_register(None, 'owner', 'proj-1')
    assert exc.value.status_code == 409
    Store([('x/' + rd.REGISTER_FILENAME, reg_bytes(register(projectId='elsewhere')))]).install(monkeypatch)
    with pytest.raises(HTTPException) as exc:
        rd.project_register(None, 'owner', 'proj-1')
    assert exc.value.status_code == 409


def test_viewer_index_original_and_rendition(monkeypatch):
    Store([('r/' + rd.REGISTER_FILENAME, reg_bytes(register())), ('report.docx', ORIGINAL), ('report.pdf', PDF)]).install(monkeypatch)
    c = client(monkeypatch)
    page = c.get(BASE + '/proj-1/synthetic-report')
    assert page.status_code == 200
    assert page.headers['content-security-policy'].startswith("default-src 'none'; img-src data:")
    assert page.headers['cache-control'] == 'private, no-store' and '<script' not in page.text
    assert 'Revised after submission: not the submitted version' in page.text
    assert 'Authorship: pending verification' in page.text and sha(ORIGINAL) in page.text
    assert '1 of 1 figures, 1 of 1 tables' in page.text and 'Synthetic investigation report' in page.text
    assert 'Open author-supplied PDF (text match 99.95%)' in page.text
    index = c.get(BASE)
    assert index.status_code == 200 and 'Climate, Land &amp; Carbon' in index.text and '/proj-1/synthetic-report' in index.text
    listing = c.get(BASE + '/register.json').json()
    assert listing['projects'][0]['documents'][0]['original']['present'] is True
    assert listing['projects'][0]['documents'][0]['visibility'] == 'private'
    original = c.get(BASE + '/proj-1/synthetic-report/original')
    assert original.content == ORIGINAL and original.headers['content-disposition'].startswith('attachment;')
    assert original.headers['x-research-sha256'] == sha(ORIGINAL)
    pdf = c.get(BASE + f'/proj-1/synthetic-report/rendition/{sha(PDF)}')
    assert pdf.content == PDF and pdf.headers['content-type'] == 'application/pdf'
    assert pdf.headers['content-disposition'].startswith('inline;') and pdf.headers['x-content-type-options'] == 'nosniff'
    assert c.get(BASE + f'/proj-1/synthetic-report/rendition/{"0" * 64}').status_code == 404


def test_access_is_owner_only_and_bytes_are_reverified(monkeypatch):
    store = Store([('r/' + rd.REGISTER_FILENAME, reg_bytes(register())), ('report.docx', ORIGINAL)])
    store.install(monkeypatch)
    signed_out = client(monkeypatch, subject=None).get(BASE + '/proj-1/synthetic-report', follow_redirects=False)
    # SC-STUDIO-SIGNIN-01: a signed-out page visit is sent to sign-in (and back), never shown.
    assert signed_out.status_code == 303 and signed_out.headers['location'].startswith('/v1/auth/login?stepUp=true&returnTo=')
    assert client(monkeypatch, subject='someone-else').get(BASE + '/proj-1/synthetic-report').status_code == 404
    assert client(monkeypatch, subject='someone-else').get(BASE + '/register.json').json()['projects'] == []
    c = client(monkeypatch)
    assert c.get(BASE + '/proj-1/unknown').status_code == 404
    store.blobs[sha(ORIGINAL)] = ORIGINAL + b'tampered'
    assert c.get(BASE + '/proj-1/synthetic-report').status_code == 409
    assert c.get(BASE + '/proj-1/synthetic-report/original').status_code == 409


def test_missing_original_is_refused_not_guessed(monkeypatch):
    Store([('r/' + rd.REGISTER_FILENAME, reg_bytes(register()))]).install(monkeypatch)
    assert client(monkeypatch).get(BASE + '/proj-1/synthetic-report').status_code == 409
