"""SC-EDITOR-DOCX-01: structure-aware Word import, continuous editing and semantic export fidelity.

Synthetic manuscripts only (the Venezuela paper is exercised when SC_EDITOR_DOCX01_SOURCE points at a local copy).
Runs the real Reporting Studio router, registry, artifact store and private store on isolated SQLite. The original
DOCX is never modified, figures become project-owned images with provenance, existing revisions are untouched.
"""
import base64
import hashlib
import io
import os
import re
import zipfile

import pytest
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE
from docx.shared import Inches, Pt

from app import citation_studio as cite, docx_manuscript, reporting_publication as pub
from tests.test_sc_research_project01_project_workspace import (  # noqa: F401  (fixture)
    ORIGIN, create, env, head, legacy_file, sha)

S = '/v1/private-research/reporting-studio/publication'
TITLE = 'Synthetic Sanctions Paper: Oil, Justice and Sustainability'
REFS = ["ACAPS (2018) 'Synthetic Humanitarian Crisis', ACAPS. → https://www.acaps.org/en/countries/synthetic_crisis",
        "Douhan, A. (2021) 'Synthetic visit report' (A/HRC/0/0), United Nations Human Rights Council. → https://undocs.org/x",
        "Lambertini, S.M. (2023) 'Synthetic organized crime', Journal of Synthetic Economies, 5(2), pp. 139–154. → "
        "https://jied.lse.ac.uk/articles/10.31389/jied.999",
        "Parampil, A. (2024) Synthetic Coup: Venezuela and the End of Empire, OR Books. → https://www.orbooks.com/x",
        "Weisbrot, M. and Sachs, J. (2019) 'Synthetic Sanctions as Collective Punishment', CEPR. → https://cepr.net/x"]


def png(width=60, height=30):
    from PIL import Image
    out = io.BytesIO()
    Image.new('RGB', (width, height), (176, 0, 32)).save(out, 'PNG')
    return out.getvalue()


def _hyperlink(paragraph, text, url):
    rid = paragraph.part.relate_to(url, RELATIONSHIP_TYPE.HYPERLINK, is_external=True)
    link = OxmlElement('w:hyperlink'); link.set(qn('r:id'), rid)
    run = OxmlElement('w:r'); t = OxmlElement('w:t'); t.text = text; run.append(t); link.append(run)
    paragraph._p.append(link)


def manuscript_docx(figure=None):
    """A Venezuela-shaped manuscript: formatted title (Normal style), H1/H2, inline formatting, a link, lists, one
    three-column table with a caption above it, one embedded PNG with its caption below, and a reference list."""
    d = Document()
    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(TITLE); r.bold = True; r.font.size = Pt(18)
    d.add_paragraph('By Synthetic Author').alignment = WD_ALIGN_PARAGRAPH.CENTER
    d.add_heading('Executive Summary', 1)
    p = d.add_paragraph('Implementation has been dominated by ')
    p.add_run('collapse').bold = True
    p.add_run(' and ')
    p.add_run('constraint').italic = True
    p.add_run(' (IMF, 2022; Douhan, 2021). Costs rose 5% and $3 [1] * 2_ times; see ')
    _hyperlink(p, 'the IMF note', 'https://www.imf.org/en/Publications')
    p.add_run('.')
    d.add_paragraph('# not a heading, just text')
    d.add_heading('Background', 1)
    d.add_paragraph('Oil exports financed social programs (ACAPS, 2018).')
    d.add_picture(io.BytesIO(figure or png()), width=Inches(4))
    d.add_paragraph('Figure 1. Binding constraint pathway for synthetic implementation')
    d.add_heading('Food security', 2)
    d.add_paragraph('First recommendation', style='List Number')
    d.add_paragraph('Second recommendation', style='List Number')
    d.add_paragraph('A bullet point', style='List Bullet')
    d.add_paragraph('Table 1. Issues and implementation barriers', style='Caption')
    t = d.add_table(rows=3, cols=3)
    for i, row in enumerate([['Issue area', 'Why it matters', 'Barriers'],
                             ['Food security', 'Hunger and health', 'Import dependence | payment rails'],
                             ['Climate capacity', 'Paris Agreement', 'Limited investment']]):
        for j, value in enumerate(row):
            t.cell(i, j).text = value
    t.cell(1, 0).paragraphs[0].runs[0].bold = True
    d.add_heading('Conclusions', 1)
    d.add_paragraph('Plans cannot scale when the state cannot pay (Weisbrot and Sachs, 2019; Lambertini, 2023).')
    d.add_heading('List of References', 1)
    for ref in REFS:
        d.add_paragraph(ref)
    out = io.BytesIO(); d.save(out)
    return out.getvalue()


def pdf_figures(content: bytes) -> int:
    """Image XObjects in a PDF, not counting the soft masks ReportLab adds for transparent PNGs."""
    return content.count(b'/Subtype /Image') - len(re.findall(rb'/SMask \d+ 0 R', content))


def api(env, method, path, who='owner', **kw):
    headers = {'x-test-sub': who, **(ORIGIN if method != 'GET' else {})}
    return env['client'].request(method, S + path, headers=headers, **kw)


def project_with_docx(env, raw, name='research/Policy_Paper_Synthetic.docx'):
    pid = create(env).json()['project']['projectId']
    legacy_file(env, pid, name, raw)
    return pid, 'legacy-' + sha(raw)[:8]


# Converter -------------------------------------------------------------------------------------------------------

def test_converter_preserves_structure_formatting_figures_and_references():
    figure = png()
    report = docx_manuscript.convert_docx(manuscript_docx(figure))
    md, outline = report['markdown'], report['outline']
    assert report['title'] == TITLE and md.startswith('# ' + TITLE + '\n')
    assert [h for h in outline['headings']] == [
        (1, TITLE), (2, 'Executive Summary'), (2, 'Background'), (3, 'Food security'), (2, 'Conclusions'),
        (2, 'List of References')]
    assert '**collapse**' in md and '*constraint*' in md
    assert '[the IMF note](https://www.imf.org/en/Publications)' in md
    assert r'\# not a heading' in md and r'\$3 \[1\] \* 2\_ times' in md
    assert '1. First recommendation\n1. Second recommendation' in md and '- A bullet point' in md
    assert outline['tables'] == [(3, 3)]
    assert '| Issue area | Why it matters | Barriers |\n|---|---|---|\n| **Food security** |' in md
    assert r'Import dependence \| payment rails' in md
    # The figure is extracted at its position with its caption, and the caption paragraph is consumed.
    media = report['media'][0]
    assert media['sha256'] == sha(figure) and media['part'].startswith('word/media/') and media['mediaType'] == 'image/png'
    fig_line = f'![Figure 1. Binding constraint pathway for synthetic implementation](asset:{media["assetId"]})'
    assert md.index('Oil exports financed') < md.index(fig_line) < md.index('### Food security')
    assert md.count('Figure 1. Binding constraint pathway') == 1
    assert outline['figures'] == 1 and outline['referenceEntries'] == len(REFS)
    assert md.index('Table 1. Issues') < md.index('| Issue area')
    assert any('Title inferred' in n for n in report['notes'])


def test_rendering_honours_escapes_links_tables_lists_and_hanging_references():
    report = docx_manuscript.convert_docx(manuscript_docx())
    html, ids = pub.render_html(report['markdown'], lambda a: '/img/' + a, document_title=TITLE)
    assert ids == [report['media'][0]['assetId']]
    assert '<table><thead><tr><th scope="col">Issue area</th><th scope="col">Why it matters</th><th scope="col">Barriers</th></tr>' in html
    assert '<td>Import dependence | payment rails</td>' in html and '<td><strong>Food security</strong></td>' in html
    assert '<p># not a heading, just text</p>' in html
    assert '$3 [1] * 2_ times' in html and '\\' not in re.sub(r'<[^>]+>', '', html)
    assert '<a href="https://www.imf.org/en/Publications" rel="noopener noreferrer">the IMF note</a>' in html
    assert '<ol><li>First recommendation</li><li>Second recommendation</li></ol>' in html
    assert html.count('<p class="reference">') == len(REFS)
    assert 'href="https://www.acaps.org/en/countries/synthetic_crisis"' in html
    assert '<figure><img src="/img/' in html
    assert '<h1>' not in html  # the title is the document title, not repeated


# Import, edit, save, reopen, export ------------------------------------------------------------------------------

def test_import_creates_project_figures_with_provenance_and_never_changes_the_docx(env):
    raw = manuscript_docx()
    pid, aid = project_with_docx(env, raw)
    blob = env['root'] / 'private-research' / sha(raw)[:2] / sha(raw)
    r = api(env, 'POST', f'/projects/{pid}/sources/{aid}/import-docx')
    assert r.status_code == 201, r.text
    body = r.json()
    assert body['saved'] is False and body['title'] == TITLE and body['figures'][0]['status'] == 'created'
    figure = body['import']['figures'][0]
    assert figure['filename'] == 'docx-import/Policy_Paper_Synthetic/figure-1.png'
    from app import object_store
    with env['factory']() as db:
        art = object_store.get_artifact(db, 'owner', figure['assetId'])
        assert art.project_id == pid and art.media_type == 'image/png' and art.sha256 == figure['sha256']
        assert art.metadata_json['sourceSha256'] == sha(raw) and art.metadata_json['sourcePart'] == figure['part']
        assert art.metadata_json['source'] == 'docx-import'
    again = api(env, 'POST', f'/projects/{pid}/sources/{aid}/import-docx').json()
    assert again['figures'][0] == {'assetId': figure['assetId'], 'status': 'reused'}
    assert again['markdown'] == body['markdown']
    assert sha(blob.read_bytes()) == sha(raw)
    img = api(env, 'GET', f'/projects/{pid}/assets/{figure["assetId"]}/image')
    assert img.status_code == 200 and img.headers['content-type'] == 'image/png' and img.content.startswith(b'\x89PNG')
    # Another account cannot import or read it.
    assert api(env, 'POST', f'/projects/{pid}/sources/{aid}/import-docx', who='intruder').status_code == 404
    assert api(env, 'GET', f'/projects/{pid}/assets/{figure["assetId"]}/image', who='intruder').status_code == 404


def test_edit_save_reopen_and_exports_preserve_the_document(env):
    raw = manuscript_docx()
    pid, aid = project_with_docx(env, raw)
    # An existing publication revision in the same project must stay untouched.
    rev = head(env, pid).revision
    old = api(env, 'POST', f'/projects/{pid}/documents', json={'title': 'Existing brief', 'markdown': '# Existing\n\nKept.\n',
                                                              'expectedProjectRevision': rev})
    assert old.status_code == 201
    old_doc = old.json()['document']
    imported = api(env, 'POST', f'/projects/{pid}/sources/{aid}/import-docx').json()
    md = imported['markdown'].replace('Oil exports financed social programs', 'Oil exports financed public programs')
    preview = api(env, 'POST', f'/projects/{pid}/preview', json={'title': imported['title'], 'markdown': md,
                                                                'sourceArtifactId': aid})
    assert preview.status_code == 200, preview.text
    assert preview.json()['figures'][0]['mediaType'] == 'image/png'
    assert '/image"' in preview.json()['html']
    saved = api(env, 'POST', f'/projects/{pid}/documents', json={
        'title': imported['title'], 'markdown': md, 'sourceArtifactId': aid,
        'expectedProjectRevision': head(env, pid).revision})
    assert saved.status_code == 201, saved.text
    doc = saved.json()['document']
    assert doc['documentId'] != old_doc['documentId'] and doc['revision'] == 1
    assert doc['source']['sha256'] == sha(raw)
    record = doc['importRecord']
    assert record['converter'] == docx_manuscript.CONVERTER and record['sourceSha256'] == sha(raw)
    assert record['convertedMarkdownSha256'] == hashlib.sha256(imported['markdown'].encode()).hexdigest()
    assert record['outline']['tables'] == [[3, 3]] and record['figures'][0]['part'].startswith('word/media/')
    # Second revision keeps the import provenance; reopening returns the exact saved text.
    second = api(env, 'POST', f'/projects/{pid}/documents', json={
        'title': imported['title'], 'markdown': md + '\nA closing note.\n', 'sourceArtifactId': aid,
        'documentId': doc['documentId'], 'expectedDocumentRevision': 1, 'expectedProjectRevision': head(env, pid).revision})
    assert second.status_code == 201 and second.json()['document']['importRecord'] == record
    reopened = api(env, 'GET', f'/projects/{pid}/documents/{doc["documentId"]}?revision=1').json()['document']
    assert reopened['markdown'] == md and reopened['markdownSHA256'] == doc['markdownSHA256']
    kept = api(env, 'GET', f'/projects/{pid}/documents/{old_doc["documentId"]}').json()['document']
    assert kept == old_doc

    original = docx_manuscript.convert_docx(raw)['outline']
    base = f'/projects/{pid}/documents/{doc["documentId"]}/export'
    html = api(env, 'GET', base + '.html?revision=1')
    assert html.status_code == 200
    text = html.text
    assert text.count('<table>') == len(original['tables']) and text.count('<th scope="col">') == 3
    assert text.count('<figure><img src="data:image/png;base64,') == original['figures']
    assert text.count('<p class="reference">') == original['referenceEntries']
    for _, heading in original['headings'][1:]:
        assert f'>{heading}</h' in text
    assert 'Oil exports financed public programs' in text

    exported = api(env, 'GET', base + '.docx?revision=1')
    assert exported.status_code == 200
    again = docx_manuscript.convert_docx(exported.content)['outline']
    assert [h for _, h in again['headings'] if h in {x for _, x in original['headings']}] == \
        [h for _, h in original['headings'][1:]]
    assert again['tables'] == original['tables'] and again['figures'] == original['figures']
    assert again['referenceEntries'] == original['referenceEntries']
    out_doc = Document(io.BytesIO(exported.content))
    refs = [p for p in out_doc.paragraphs if p.text.startswith(('ACAPS (2018)', 'Weisbrot, M.'))]
    assert len(refs) == 2 and all(p.paragraph_format.first_line_indent < 0 for p in refs)
    with zipfile.ZipFile(io.BytesIO(exported.content)) as z:
        rels = z.read('word/_rels/document.xml.rels').decode()
    assert 'https://www.imf.org/en/Publications' in rels

    pdf = api(env, 'GET', base + '.pdf?revision=1')
    assert pdf.status_code == 200 and pdf_figures(pdf.content) == original['figures']
    pypdf = pytest.importorskip('pypdf')
    pdf_text = ' '.join(page.extract_text() for page in pypdf.PdfReader(io.BytesIO(pdf.content)).pages)
    flat = ' '.join(pdf_text.split())
    for _, heading in original['headings'][1:]:
        assert heading in flat
    for cell in ('Issue area', 'Why it matters', 'Import dependence | payment rails', 'Limited investment'):
        assert cell in flat
    for ref in REFS:
        assert ' '.join(ref.split('→')[0].split())[:40] in flat


# Citation Studio ---------------------------------------------------------------------------------------------------

def test_manuscript_references_are_reviewed_flagged_and_imported_without_duplicates(env):
    raw = manuscript_docx()
    pid, aid = project_with_docx(env, raw)
    md = api(env, 'POST', f'/projects/{pid}/sources/{aid}/import-docx').json()['markdown']
    review = api(env, 'POST', f'/citations/projects/{pid}/manuscript-references/review',
                 json={'markdown': md, 'checkLibrary': False})
    assert review.status_code == 200, review.text
    r = review.json()
    assert [e['text'] for e in r['entries']] == REFS  # complete entries, unescaped, in order
    by = {e['text'][:6]: e for e in r['entries']}
    assert by['Paramp']['status'] == 'ambiguous' and by['Paramp']['issues']
    assert by['Weisbr']['fields']['authors'] == [{'family': 'Weisbrot', 'given': 'M.'}, {'family': 'Sachs', 'given': 'J.'}]
    assert by['Lamber']['fields']['doi'] == '10.31389/jied.999' and by['Lamber']['fields']['volume'] == '5'
    assert by['ACAPS ']['inTextMentions'] == 1
    before = head(env, pid).revision  # the review stored nothing
    accept = [e['proposalId'] for e in r['entries'] if e['status'] == 'new']
    stale = api(env, 'POST', f'/citations/projects/{pid}/manuscript-references/import', json={
        'markdown': md + 'x', 'manuscriptSha256': r['manuscriptSha256'], 'accept': accept, 'expectedProjectRevision': before})
    assert stale.status_code == 409
    done = api(env, 'POST', f'/citations/projects/{pid}/manuscript-references/import', json={
        'markdown': md, 'manuscriptSha256': r['manuscriptSha256'], 'accept': accept, 'sourceArtifactId': aid,
        'expectedProjectRevision': before})
    assert done.status_code == 201, done.text
    items = done.json()['items']
    assert len(items) == len(accept) and all(x['provenance']['manuscriptReference'] in REFS for x in items)
    assert all(x['provenance']['metadataAuthority'] == 'manuscript-reference-owner-reviewed' for x in items)
    # A second review flags everything already imported; re-importing adds nothing.
    second = api(env, 'POST', f'/citations/projects/{pid}/manuscript-references/review',
                 json={'markdown': md, 'checkLibrary': False}).json()
    assert second['summary']['duplicate'] == len(accept) and second['summary']['new'] == 0
    repeat = api(env, 'POST', f'/citations/projects/{pid}/manuscript-references/import', json={
        'markdown': md, 'manuscriptSha256': r['manuscriptSha256'], 'accept': accept,
        'expectedProjectRevision': done.json()['projectRevision']})
    assert repeat.status_code == 200 and repeat.json()['import']['added'] == []
    # Linked citations resolve, and the revision's bibliography snapshot keeps the keys.
    key = next(x['key'] for x in items if x['provenance']['manuscriptReference'].startswith('Weisbrot'))
    cited = md.replace('(Weisbrot and Sachs, 2019; Lambertini, 2023)', f'[@{key}]')
    saved = api(env, 'POST', f'/projects/{pid}/documents', json={'title': TITLE, 'markdown': cited, 'sourceArtifactId': aid,
                                                               'expectedProjectRevision': head(env, pid).revision}).json()
    snapshot = saved['document']['citations']
    assert [x['key'] for x in snapshot['items']] == [key] and snapshot['unresolved'] == []
    html = api(env, 'GET', f'/projects/{pid}/documents/{saved["document"]["documentId"]}/export.html').text
    assert '(Weisbrot and Sachs, 2019)' in html and f'[@{key}]' not in html
    # One coherent References section: the manuscript's own entry is not repeated by the generated list.
    assert html.count('<h2>List of References</h2>') == 1 and '<h2>References</h2>' not in html
    assert html.count('<p class="reference">') == len(REFS)


def test_generated_entries_join_an_existing_reference_section():
    item = cite.make_item({'authors': ['Example, A.'], 'year': 2020, 'title': 'A synthetic study', 'container': 'J. Synth.'},
                          {'manuscriptReference': 'not in this manuscript'})
    frozen = {'style': 'harvard', 'items': [item]}
    md = f'# T\n\nText [@{item["key"]}].\n\n## List of References\n\nOther, B. (2019) Kept entry.\n\n## Appendix\n\nA.\n'
    out = cite.resolve(md, frozen)
    assert out.count('References') == 1 and out.index('Example, A. (2020)') < out.index('## Appendix')
    assert 'Other, B. (2019) Kept entry.' in out
    plain = cite.resolve('# T\n\nText [@' + item['key'] + '].\n', frozen)
    assert '## References' in plain  # no reference section yet: one is generated as before


def test_reference_text_parser_handles_harvard_and_apa():
    harvard = cite.parse_reference_text("Hernández, P. (2021) 'Dismantling the Food Supply System', Frontiers in "
                                        "Sustainable Food Systems. → https://www.frontiersin.org/x")
    assert harvard['fields']['authors'] == [{'family': 'Hernández', 'given': 'P.'}] and harvard['issues'] == []
    assert harvard['fields']['title'] == 'Dismantling the Food Supply System' and harvard['fields']['year'] == 2021
    apa = cite.parse_reference_text('Smith, J. A., & Lee, K. (2020). Soil carbon in wetlands. Journal of Soils, 12(3), '
                                    '45–67. https://doi.org/10.1234/soil.2020.1')
    assert apa['fields']['doi'] == '10.1234/soil.2020.1' and apa['fields']['volume'] == '12'
    assert [a['family'] for a in apa['fields']['authors']] == ['Smith', 'Lee']
    org = cite.parse_reference_text("UN (2015) 'Transforming our world', United Nations. → https://undocs.org/A/RES/70/1")
    assert org['fields']['authors'] == [{'literal': 'UN'}] and org['issues'] == []
    assert cite.parse_reference_text('An untitled note without a date')['issues']


# The real acceptance manuscript (local only) -------------------------------------------------------------------

@pytest.mark.skipif(not os.environ.get('SC_EDITOR_DOCX01_SOURCE'), reason='set SC_EDITOR_DOCX01_SOURCE to a local DOCX')
def test_acceptance_manuscript_round_trip(env):
    raw = open(os.environ['SC_EDITOR_DOCX01_SOURCE'], 'rb').read()
    expected = os.environ.get('SC_EDITOR_DOCX01_SHA256')
    if expected:
        assert sha(raw) == expected
    pid, aid = project_with_docx(env, raw, 'research/' + os.path.basename(os.environ['SC_EDITOR_DOCX01_SOURCE']))
    imported = api(env, 'POST', f'/projects/{pid}/sources/{aid}/import-docx').json()
    outline = imported['import']['outline']
    assert outline['tables'] == [[5, 3]] and outline['figures'] == 1 and outline['referenceEntries'] >= 20
    saved = api(env, 'POST', f'/projects/{pid}/documents', json={'title': imported['title'], 'markdown': imported['markdown'],
                                                               'sourceArtifactId': aid,
                                                               'expectedProjectRevision': head(env, pid).revision})
    assert saved.status_code == 201, saved.text
    doc = saved.json()['document']
    base = f'/projects/{pid}/documents/{doc["documentId"]}/export'
    again = docx_manuscript.convert_docx(api(env, 'GET', base + '.docx').content)['outline']
    assert again['tables'] == [(5, 3)] and again['figures'] == 1
    assert again['referenceEntries'] == outline['referenceEntries']
    html = api(env, 'GET', base + '.html').text
    assert html.count('<p class="reference">') == outline['referenceEntries'] and html.count('<table>') == 1
    assert pdf_figures(api(env, 'GET', base + '.pdf').content) == 1
    review = api(env, 'POST', f'/citations/projects/{pid}/manuscript-references/review',
                 json={'markdown': imported['markdown'], 'checkLibrary': False}).json()
    assert len(review['entries']) == outline['referenceEntries']
    print('ACCEPTANCE', outline, review['summary'])
