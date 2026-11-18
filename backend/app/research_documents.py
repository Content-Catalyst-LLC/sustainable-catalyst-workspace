"""SC-RESEARCH-DOCS-01: owner-only register and full-document viewer for private research documents.

A project's documents are declared by an immutable register artifact (``sc-research-document-register/1.0``) imported
into the owner's private research store beside the documents it names. The register pins every original and
rendition by SHA-256; nothing here uploads, edits, publishes or changes visibility.

The viewer renders the original DOCX on the server into static HTML (headings, paragraphs, run formatting, tables
with merged cells, inline figures, footnotes) and reports what it could not render, so a reader can tell when the
page is a complete rendering of the source. The page carries no script; figures are inline data URIs and every
byte is re-verified against the register and the artifact store on each request.
"""
from __future__ import annotations

import base64
import hashlib
import json
from html import escape
from io import BytesIO
from pathlib import Path
import posixpath
import re
from typing import Annotated, Literal
from urllib.parse import quote
from zipfile import BadZipFile, ZipFile

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, ValidationError

from .config import get_settings
from .db import session_scope
from .reporting_project_catalog import read_legacy_artifacts
from .repository import list_projects
from .wxr_private_projects import HEADERS, _project, _subject

router = APIRouter(prefix='/documents', tags=['Research documents'])

REGISTER_SCHEMA = 'sc-research-document-register/1.0'
REGISTER_FILENAME = 'SC_RESEARCH_DOCS_01_REGISTER.json'
MAX_REGISTER = 256 * 1024
MAX_DOCUMENT = 25 * 1024 * 1024
MAX_UNCOMPRESSED = 80 * 1024 * 1024
MAX_PART = 16 * 1024 * 1024
MAX_MEMBERS = 2000
DOCX = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
PAGE_CSP = ("default-src 'none'; img-src data:; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'; "
            "frame-ancestors 'none'")

SUBMISSION_LABELS = {
    'submission-candidate-unverified': 'Submission candidate: not verified against the university record',
    'post-submission-revision': 'Revised after submission: not the submitted version',
    'not-a-submission': 'Independent research document: not a university submission',
    'undetermined': 'Submission status not determined',
}


class Strict(BaseModel):
    model_config = ConfigDict(extra='forbid')


Sha = Annotated[str, StringConstraints(pattern=r'^[a-f0-9]{64}$')]
Slug = Annotated[str, StringConstraints(pattern=r'^[a-z0-9][a-z0-9-]{1,100}$')]


class FileRef(Strict):
    sha256: Sha
    bytes: int = Field(ge=1, le=MAX_DOCUMENT)
    format: Literal['docx', 'pdf']
    filename: str = Field(min_length=1, max_length=300)


class Rendition(FileRef):
    format: Literal['pdf']
    origin: Literal['author-supplied']
    textCorrespondence: float = Field(ge=0, le=1)
    note: str = Field(default='', max_length=500)


class PublicRecord(Strict):
    url: str = Field(pattern=r'^https://[^\s]{1,400}$')
    sha256: Sha
    relation: Literal['identical-bytes-to-rendition', 'identical-bytes-to-original']
    visibility: Literal['public']
    note: str = Field(default='', max_length=500)


class Document(Strict):
    documentId: Slug
    title: str = Field(min_length=1, max_length=400)
    documentType: Literal['scientific-report', 'policy-brief', 'policy-paper', 'essay', 'working-paper']
    original: FileRef
    renditions: list[Rendition] = Field(default_factory=list, max_length=4)
    revisionLabel: str = Field(min_length=1, max_length=300)
    relatedVersions: list[str] = Field(default_factory=list, max_length=40)
    submissionStatus: Literal[tuple(SUBMISSION_LABELS)]
    submissionNote: str = Field(default='', max_length=1000)
    authorship: Literal['PENDING_VERIFICATION', 'CONFIRMED_BY_OWNER']
    visibility: Literal['private']
    existingPublicRecords: list[PublicRecord] = Field(default_factory=list, max_length=4)


class Named(Strict):
    id: Slug
    name: str = Field(min_length=1, max_length=200)


class Register(Strict):
    schema_: Literal[REGISTER_SCHEMA] = Field(alias='schema')
    programme: Literal['SC-RESEARCH-DOCS-01']
    registerRevision: int = Field(ge=1)
    projectId: str = Field(min_length=1, max_length=160)
    researchArea: Named
    investigation: Named
    documents: list[Document] = Field(min_length=1, max_length=50)


# DOCX rendering ------------------------------------------------------------------------------------------------------

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
PR = 'http://schemas.openxmlformats.org/package/2006/relationships'
VML = 'urn:schemas-microsoft-com:vml'
MATH = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
CHART = 'http://schemas.openxmlformats.org/drawingml/2006/chart'
IMAGE_TYPES = {b'\x89PNG\r\n\x1a\n': 'image/png', b'\xff\xd8\xff': 'image/jpeg', b'GIF87a': 'image/gif',
               b'GIF89a': 'image/gif'}


def w(tag: str) -> str:
    return f'{{{W}}}{tag}'


def _xml(raw: bytes):
    from lxml import etree
    parser = etree.XMLParser(resolve_entities=False, no_network=True, huge_tree=False, load_dtd=False)
    return etree.fromstring(raw, parser)


class _Package:
    def __init__(self, raw: bytes):
        try:
            self.zip = ZipFile(BytesIO(raw))
            infos = self.zip.infolist()
        except BadZipFile as exc:
            raise HTTPException(422, 'The original is not a valid DOCX package.') from exc
        if len(infos) > MAX_MEMBERS or sum(i.file_size for i in infos) > MAX_UNCOMPRESSED:
            raise HTTPException(413, 'The DOCX package exceeds viewer limits.')
        self.names = {i.filename for i in infos}
        if 'word/document.xml' not in self.names:
            raise HTTPException(422, 'The original is not a valid DOCX package.')

    def read(self, name: str) -> bytes | None:
        if name not in self.names:
            return None
        if self.zip.getinfo(name).file_size > MAX_PART:
            raise HTTPException(413, 'A DOCX part exceeds viewer limits.')
        return self.zip.read(name)

    def rels(self, part: str) -> dict[str, tuple[str, str]]:
        folder, name = posixpath.split(part)
        raw = self.read(posixpath.join(folder, '_rels', name + '.rels'))
        out = {}
        for rel in (_xml(raw) if raw else []):
            mode = rel.get('TargetMode', '')
            target = rel.get('Target', '')
            out[rel.get('Id')] = (target if mode == 'External' else posixpath.normpath(posixpath.join(folder, target)),
                                  mode)
        return out


class DocxRenderer:
    """Static, escaped HTML from WordprocessingML. Unknown constructs are counted, never passed through."""

    def __init__(self, raw: bytes):
        self.pkg = _Package(raw)
        self.rels = self.pkg.rels('word/document.xml')
        self.styles = self._styles()
        self.numbering = self._numbering()
        self.footnotes = self._footnotes()
        self.used_notes: list[str] = []
        self.stats = {'paragraphs': 0, 'headings': 0, 'tablesInSource': 0, 'tablesRendered': 0,
                      'figuresInSource': 0, 'figuresRendered': 0, 'footnotes': 0,
                      'unrendered': {'equations': 0, 'textBoxes': 0, 'charts': 0, 'trackedDeletions': 0,
                                     'unsupportedImages': 0}}

    def _styles(self) -> dict[str, str]:
        raw = self.pkg.read('word/styles.xml')
        if not raw:
            return {}
        out = {}
        for style in _xml(raw).iter(w('style')):
            name = style.find(w('name'))
            out[style.get(w('styleId'))] = (name.get(w('val')) if name is not None else '').lower()
        return out

    def _numbering(self) -> dict[str, str]:
        raw = self.pkg.read('word/numbering.xml')
        if not raw:
            return {}
        root = _xml(raw)
        abstract = {}
        for node in root.iter(w('abstractNum')):
            fmt = node.find(f'{w("lvl")}/{w("numFmt")}')
            abstract[node.get(w('abstractNumId'))] = fmt.get(w('val')) if fmt is not None else 'bullet'
        out = {}
        for num in root.iter(w('num')):
            ref = num.find(w('abstractNumId'))
            out[num.get(w('numId'))] = abstract.get(ref.get(w('val')) if ref is not None else '', 'bullet')
        return out

    def _footnotes(self) -> dict[str, object]:
        raw = self.pkg.read('word/footnotes.xml')
        if not raw:
            return {}
        return {n.get(w('id')): n for n in _xml(raw).iter(w('footnote'))
                if n.get(w('type')) not in ('separator', 'continuationSeparator', 'continuationNotice')}

    # Blocks

    def render(self) -> tuple[str, dict]:
        root = _xml(self.pkg.read('word/document.xml'))
        body = root.find(w('body'))
        self.stats['figuresInSource'] = len(root.findall(f'.//{w("drawing")}')) + len(root.findall(f'.//{{{VML}}}imagedata'))
        self.stats['tablesInSource'] = len(root.findall(f'.//{w("tbl")}'))
        self.stats['unrendered']['equations'] = len(root.findall(f'.//{{{MATH}}}oMath'))
        self.stats['unrendered']['textBoxes'] = len(root.findall(f'.//{w("txbxContent")}'))
        self.stats['unrendered']['charts'] = len(root.findall(f'.//{{{CHART}}}chart'))
        self.stats['unrendered']['trackedDeletions'] = len(root.findall(f'.//{w("del")}'))
        html = self.blocks(body if body is not None else [])
        if self.used_notes:
            items = ''.join(f'<li id="fn-{escape(n)}">{self.blocks(self.footnotes[n])}</li>' for n in self.used_notes)
            html += f'<section class="footnotes" aria-label="Footnotes"><hr><ol>{items}</ol></section>'
        self.stats['footnotes'] = len(self.used_notes)
        u = self.stats['unrendered']
        self.stats['complete'] = (self.stats['figuresRendered'] == self.stats['figuresInSource']
                                  and self.stats['tablesRendered'] == self.stats['tablesInSource']
                                  and not any(u.values()))
        return html, self.stats

    def blocks(self, parent) -> str:
        out, open_list = [], None
        for node in parent:
            tag = node.tag
            if tag == w('sdt'):
                content = node.find(w('sdtContent'))
                out.append(self.blocks(content if content is not None else []))
                continue
            kind = self._list_kind(node) if tag == w('p') else None
            if kind != open_list:
                if open_list:
                    out.append(f'</{open_list}>')
                if kind:
                    out.append(f'<{kind}>')
                open_list = kind
            if tag == w('p'):
                out.append(self.paragraph(node, in_list=bool(kind)))
            elif tag == w('tbl'):
                out.append(self.table(node))
        if open_list:
            out.append(f'</{open_list}>')
        return ''.join(out)

    def _list_kind(self, p) -> str | None:
        style = p.find(f'{w("pPr")}/{w("pStyle")}')
        name = self.styles.get(style.get(w('val')), '') if style is not None else ''
        if name == 'title' or name.startswith('heading'):
            return None
        num = p.find(f'{w("pPr")}/{w("numPr")}/{w("numId")}')
        if num is None or num.get(w('val')) in (None, '0'):
            return None
        return 'ul' if self.numbering.get(num.get(w('val')), 'bullet') in ('bullet', 'none') else 'ol'

    def paragraph(self, p, in_list: bool = False) -> str:
        ppr = p.find(w('pPr'))
        style = ''
        align = ''
        if ppr is not None:
            ps = ppr.find(w('pStyle'))
            if ps is not None:
                style = self.styles.get(ps.get(w('val')), ps.get(w('val'), '')).lower()
            jc = ppr.find(w('jc'))
            if jc is not None and jc.get(w('val')) in ('center', 'right', 'both'):
                align = {'center': 'center', 'right': 'right', 'both': 'justify'}[jc.get(w('val'))]
        content = self.inline(p)
        if not content.strip():
            return ''
        attr = f' style="text-align:{align}"' if align else ''
        if in_list:
            return f'<li{attr}>{content}</li>'
        self.stats['paragraphs'] += 1
        match = re.fullmatch(r'heading ([1-6])', style)
        if style == 'title':
            self.stats['headings'] += 1
            return f'<h1 class="doc-title"{attr}>{content}</h1>'
        if match:
            self.stats['headings'] += 1
            level = min(int(match.group(1)) + 1, 6)
            return f'<h{level}{attr}>{content}</h{level}>'
        cls = ' class="subtitle"' if style == 'subtitle' else ' class="caption"' if style == 'caption' else ''
        return f'<p{cls}{attr}>{content}</p>'

    def inline(self, parent) -> str:
        out = []
        for node in parent:
            tag = node.tag
            if tag == w('r'):
                out.append(self.run(node))
            elif tag == w('hyperlink'):
                inner = self.inline(node)
                target = self.rels.get(node.get(f'{{{R}}}id'), ('', ''))
                if target[1] == 'External' and re.match(r'^https?://', target[0]):
                    out.append(f'<a href="{escape(target[0], quote=True)}" rel="noopener noreferrer">{inner}</a>')
                else:
                    out.append(inner)
            elif tag in (w('ins'), w('smartTag'), w('fldSimple'), w('customXml')):
                out.append(self.inline(node))
            elif tag == w('sdt'):
                content = node.find(w('sdtContent'))
                if content is not None:
                    out.append(self.inline(content))
        return ''.join(out)

    def run(self, r) -> str:
        parts = []
        for node in r:
            tag = node.tag
            if tag == w('t'):
                parts.append(escape(node.text or ''))
            elif tag == w('tab'):
                parts.append('&emsp;')
            elif tag in (w('br'), w('cr')):
                parts.append('<br>')
            elif tag == w('noBreakHyphen'):
                parts.append('&#8209;')
            elif tag == w('drawing'):
                parts.append(self.drawing(node))
            elif tag == w('pict'):
                parts.append(self.vml(node))
            elif tag == w('footnoteReference'):
                ident = node.get(w('id'))
                if ident in self.footnotes:
                    if ident not in self.used_notes:
                        self.used_notes.append(ident)
                    n = self.used_notes.index(ident) + 1
                    parts.append(f'<sup class="fnref"><a href="#fn-{escape(ident)}">{n}</a></sup>')
        text = ''.join(parts)
        if not text:
            return ''
        rpr = r.find(w('rPr'))
        if rpr is not None:
            def on(tag):
                el = rpr.find(w(tag))
                return el is not None and el.get(w('val')) not in ('0', 'false', 'none')
            va = rpr.find(w('vertAlign'))
            if va is not None and va.get(w('val')) == 'superscript':
                text = f'<sup>{text}</sup>'
            elif va is not None and va.get(w('val')) == 'subscript':
                text = f'<sub>{text}</sub>'
            if on('strike'):
                text = f'<s>{text}</s>'
            if on('u'):
                text = f'<u>{text}</u>'
            if on('i'):
                text = f'<em>{text}</em>'
            if on('b'):
                text = f'<strong>{text}</strong>'
        return text

    def _image(self, rid: str | None, alt: str, width_emu: int | None = None) -> str:
        target = self.rels.get(rid or '')
        raw = self.pkg.read(target[0]) if target and target[1] != 'External' else None
        media = next((m for magic, m in IMAGE_TYPES.items() if raw and raw.startswith(magic)), None)
        if not media:
            self.stats['unrendered']['unsupportedImages'] += 1
            return '<span class="unrendered">[Figure not rendered: unsupported image format]</span>'
        self.stats['figuresRendered'] += 1
        width = ''
        if width_emu:
            width = f' style="width:min(100%,{round(width_emu / 9525)}px)"'
        data = base64.b64encode(raw).decode()
        return f'<img class="figure" alt="{escape(alt, quote=True)}" src="data:{media};base64,{data}"{width}>'

    def drawing(self, node) -> str:
        blip = node.find(f'.//{{{A}}}blip')
        doc_pr = node.find('.//{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}docPr')
        extent = node.find('.//{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}extent')
        alt = (doc_pr.get('descr') or doc_pr.get('title') or doc_pr.get('name') or '') if doc_pr is not None else ''
        if blip is None:
            return '<span class="unrendered">[Drawing not rendered]</span>'
        width = int(extent.get('cx')) if extent is not None and (extent.get('cx') or '').isdigit() else None
        return self._image(blip.get(f'{{{R}}}embed'), alt, width)

    def vml(self, node) -> str:
        data = node.find(f'.//{{{VML}}}imagedata')
        return self._image(data.get(f'{{{R}}}id'), data.get('title', '')) if data is not None else ''

    def table(self, tbl) -> str:
        rows, spans = [], {}
        for tr in tbl.findall(w('tr')):
            cells, col = [], 0
            for tc in tr.findall(w('tc')):
                pr = tc.find(w('tcPr'))
                span = 1
                merge = None
                if pr is not None:
                    gs = pr.find(w('gridSpan'))
                    if gs is not None and (gs.get(w('val')) or '').isdigit():
                        span = max(1, int(gs.get(w('val'))))
                    vm = pr.find(w('vMerge'))
                    if vm is not None:
                        merge = vm.get(w('val')) or 'continue'
                if merge == 'continue' and col in spans:
                    spans[col]['rowspan'] += 1
                else:
                    cell = {'html': self.blocks(tc), 'colspan': span, 'rowspan': 1,
                            'header': tr.find(f'{w("trPr")}/{w("tblHeader")}') is not None}
                    cells.append(cell)
                    if merge == 'restart':
                        spans[col] = cell
                    else:
                        spans.pop(col, None)
                col += span
            rows.append(cells)
        self.stats['tablesRendered'] += 1
        body = []
        for cells in rows:
            tds = []
            for c in cells:
                tag = 'th' if c['header'] else 'td'
                attrs = (f' colspan="{c["colspan"]}"' if c['colspan'] > 1 else '') + \
                        (f' rowspan="{c["rowspan"]}"' if c['rowspan'] > 1 else '')
                tds.append(f'<{tag}{attrs}>{c["html"]}</{tag}>')
            body.append('<tr>' + ''.join(tds) + '</tr>')
        return '<div class="table-wrap"><table>' + ''.join(body) + '</table></div>'


def render_docx(raw: bytes) -> tuple[str, dict]:
    if len(raw) > MAX_DOCUMENT:
        raise HTTPException(413, 'The original exceeds viewer limits.')
    return DocxRenderer(raw).render()


# Register and verified reads -----------------------------------------------------------------------------------------

def _blob(sha256: str, size: int) -> bytes:
    path = Path(get_settings().object_storage_root) / 'private-research' / sha256[:2] / sha256
    if not path.is_file():
        raise HTTPException(503, 'Research blob is missing.')
    raw = path.read_bytes()
    if len(raw) != size or hashlib.sha256(raw).hexdigest() != sha256:
        raise HTTPException(409, 'Research blob integrity verification failed.')
    return raw


def project_register(db, owner: str, project_id: str) -> dict | None:
    """The highest register revision imported into this owner's project, verified, with artifact ids resolved."""
    legacy, _ = read_legacy_artifacts(db, owner, project_id)
    candidates = [a for a in legacy if a['filename'].rsplit('/', 1)[-1] == REGISTER_FILENAME]
    if not candidates:
        return None
    by_hash = {}
    for item in legacy:
        by_hash.setdefault(item['sha256'], item)
    registers = []
    for item in candidates:
        if item['bytes'] > MAX_REGISTER:
            raise HTTPException(413, 'Document register exceeds limits.')
        try:
            register = Register.model_validate(json.loads(_blob(item['sha256'], item['bytes'])))
        except (ValueError, ValidationError) as exc:
            raise HTTPException(422, 'Document register is invalid.') from exc
        if register.projectId != project_id:
            raise HTTPException(409, 'Document register names a different project.')
        registers.append((register.registerRevision, item, register))
    registers.sort(key=lambda r: r[0])
    if len(registers) > 1 and registers[-1][0] == registers[-2][0]:
        raise HTTPException(409, 'Two document registers share a revision; stop for review.')
    revision, item, register = registers[-1]
    documents = []
    for doc in register.documents:
        files = [doc.original, *doc.renditions]
        resolved = []
        for ref in files:
            match = by_hash.get(ref.sha256)
            if match is None or match['bytes'] != ref.bytes:
                resolved.append(None)
            else:
                resolved.append(match['artifactId'])
        documents.append({'document': doc, 'artifactIds': resolved})
    return {'register': register, 'artifact': item, 'documents': documents,
            'superseded': [r[1]['sha256'] for r in registers[:-1]]}


def _document(db, owner: str, project_id: str, document_id: str):
    found = project_register(db, owner, project_id)
    entry = next((d for d in (found or {}).get('documents', []) if d['document'].documentId == document_id), None)
    if entry is None:
        raise HTTPException(404, 'Research document not found.')
    return found, entry


def _summary(project_id: str, found: dict) -> dict:
    reg = found['register']
    base = '/v1/private-research/reporting-studio/documents/' + quote(project_id, safe='')
    return {
        'projectId': project_id, 'registerRevision': reg.registerRevision,
        'registerSha256': found['artifact']['sha256'], 'supersededRegisters': found['superseded'],
        'researchArea': reg.researchArea.model_dump(), 'investigation': reg.investigation.model_dump(),
        'documents': [{
            'documentId': d['document'].documentId, 'title': d['document'].title,
            'documentType': d['document'].documentType, 'revisionLabel': d['document'].revisionLabel,
            'submissionStatus': d['document'].submissionStatus,
            'submissionLabel': SUBMISSION_LABELS[d['document'].submissionStatus],
            'authorship': d['document'].authorship, 'visibility': d['document'].visibility,
            'original': {**d['document'].original.model_dump(), 'present': d['artifactIds'][0] is not None},
            'renditions': [{**r.model_dump(), 'present': a is not None}
                           for r, a in zip(d['document'].renditions, d['artifactIds'][1:])],
            'existingPublicRecords': [p.model_dump() for p in d['document'].existingPublicRecords],
            'viewUrl': base + '/' + d['document'].documentId,
        } for d in found['documents']],
    }


def owner_registers(db, owner: str) -> list[dict]:
    out = []
    for project in list_projects(db, owner):
        found = project_register(db, owner, project['projectId'])
        if found:
            out.append(_summary(project['projectId'], found))
    return out


# Pages ---------------------------------------------------------------------------------------------------------------

STYLE = """
:root{color-scheme:light dark;--bg:#fbfaf7;--fg:#1b1b1b;--muted:#5d5d5d;--line:#d9d6cf;--card:#fff;--accent:#1f5f4a;
--warn:#8a4b00;--warnbg:#fff4e0}
@media (prefers-color-scheme:dark){:root{--bg:#141514;--fg:#ecebe7;--muted:#a9a7a0;--line:#3a3b38;--card:#1c1d1b;
--accent:#7cc4a6;--warn:#ffbf69;--warnbg:#2f2410}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 Georgia,'Times New Roman',serif}
header.meta,main,nav.crumbs,section.index{max-width:860px;margin:0 auto;padding:0 16px}
nav.crumbs{font:13px/1.4 system-ui,sans-serif;color:var(--muted);padding-top:20px}
nav.crumbs a{color:var(--accent)}
header.meta{font:14px/1.5 system-ui,sans-serif;padding-bottom:12px;border-bottom:1px solid var(--line)}
header.meta h1{font:600 24px/1.25 system-ui,sans-serif;margin:8px 0}
.badges{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0}
.badge{border:1px solid var(--line);border-radius:999px;padding:2px 10px;font-size:12px}
.badge.private{border-color:var(--accent);color:var(--accent)}.badge.status{background:var(--warnbg);color:var(--warn);border-color:var(--warn)}
dl.facts{display:grid;grid-template-columns:max-content 1fr;gap:2px 12px;margin:8px 0}dl.facts dt{color:var(--muted)}
dl.facts dd{margin:0;overflow-wrap:anywhere}code{font:12px ui-monospace,Menlo,monospace}
.actions a{display:inline-block;margin:6px 8px 0 0;color:var(--accent)}
.fidelity{margin-top:8px;padding:8px 10px;border-left:3px solid var(--accent);background:var(--card)}
.fidelity.incomplete{border-color:var(--warn)}
article.document{background:var(--card);border:1px solid var(--line);margin:20px auto 40px;padding:32px clamp(16px,5vw,56px);max-width:860px}
article.document h1.doc-title{font-size:26px;line-height:1.25}article.document img.figure{display:block;max-width:100%;height:auto;margin:12px auto}
.table-wrap{overflow-x:auto;margin:12px 0}table{border-collapse:collapse;font-size:14px;width:100%}
td,th{border:1px solid var(--line);padding:6px 8px;vertical-align:top}td p,th p{margin:0 0 4px}
p.caption{font-size:14px;color:var(--muted)}.unrendered{color:var(--warn);font-style:italic}
section.footnotes{font-size:14px}section.index h2{font:600 18px system-ui,sans-serif;margin:28px 0 4px}
section.index h3{font:600 15px system-ui,sans-serif;margin:12px 0 4px;color:var(--muted)}
section.index li{margin:8px 0;font:15px/1.45 system-ui,sans-serif}section.index .sub{display:block;font-size:13px;color:var(--muted)}
@media print{nav.crumbs,.actions{display:none}article.document{border:0;margin:0;padding:0}}
"""


def _page(title: str, body: str) -> HTMLResponse:
    html = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" '
            f'content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow">'
            f'<title>{escape(title)}</title><style>{STYLE}</style></head><body>{body}</body></html>')
    return HTMLResponse(html, headers={**HEADERS, 'Content-Security-Policy': PAGE_CSP,
                                       'Referrer-Policy': 'no-referrer'})


@router.get('/register.json')
def register_json(request: Request):
    owner = _subject(request)
    with session_scope() as db:
        return JSONResponse({'schema': 'sc-research-document-index/1.0', 'projects': owner_registers(db, owner)},
                            headers=HEADERS)


@router.get('', response_class=HTMLResponse)
def index(request: Request):
    owner = _subject(request)
    with session_scope() as db:
        projects = owner_registers(db, owner)
    areas: dict[str, dict] = {}
    for p in projects:
        areas.setdefault(p['researchArea']['id'], {'name': p['researchArea']['name'], 'projects': []})['projects'].append(p)
    parts = ['<nav class="crumbs"><a href="/v1/private-research/reporting-studio">Reporting Studio</a> › '
             '<a href="/v1/private-research/reporting-studio/research-projects">Research projects</a> › Research documents</nav>',
             '<header class="meta"><h1>Research documents</h1><p>Private to your account. Nothing here is public '
             'unless it is listed under an existing public record.</p></header><section class="index">']
    if not areas:
        parts.append('<p>No document registers have been imported yet.</p>')
    for area in sorted(areas.values(), key=lambda a: a['name']):
        parts.append(f'<h2>{escape(area["name"])}</h2>')
        for p in area['projects']:
            parts.append(f'<h3>{escape(p["investigation"]["name"])}</h3><ul>')
            for d in p['documents']:
                parts.append(f'<li><a href="{escape(d["viewUrl"], quote=True)}">{escape(d["title"])}</a>'
                             f'<span class="sub">{escape(d["revisionLabel"])} · {escape(d["submissionLabel"])}</span></li>')
            parts.append('</ul>')
    parts.append('</section>')
    return _page('Research documents', ''.join(parts))


@router.get('/{project_id}/{document_id}', response_class=HTMLResponse)
def view(project_id: str, document_id: str, request: Request):
    owner = _subject(request)
    with session_scope() as db:
        _project(db, owner, project_id)
        found, entry = _document(db, owner, project_id, document_id)
        doc = entry['document']
        if entry['artifactIds'][0] is None:
            raise HTTPException(409, 'The registered original is not in this project.')
        raw = _blob(doc.original.sha256, doc.original.bytes)
    html, stats = render_docx(raw)
    reg = found['register']
    base = '/v1/private-research/reporting-studio/documents/' + quote(project_id, safe='') + '/' + doc.documentId
    links = [f'<a href="{base}/original">Download original DOCX</a>']
    for r, a in zip(doc.renditions, entry['artifactIds'][1:]):
        if a is not None:
            links.append(f'<a href="{base}/rendition/{r.sha256}">Open author-supplied PDF '
                         f'(text match {r.textCorrespondence:.2%})</a>')
    publics = ''.join(f'<dd>{escape(p.url)} — {escape(p.relation.replace("-", " "))}. {escape(p.note)}</dd>'
                      for p in doc.existingPublicRecords)
    u = stats['unrendered']
    missing = ', '.join(f'{v} {k}' for k, v in u.items() if v)
    fidelity = (f'Rendered from the original DOCX: {stats["figuresRendered"]} of {stats["figuresInSource"]} figures, '
                f'{stats["tablesRendered"]} of {stats["tablesInSource"]} tables, {stats["footnotes"]} footnotes.'
                + (f' Not rendered: {escape(missing)}. Use the original for these.' if missing else '')
                + ' Page layout and fonts follow this viewer, not Word.')
    body = (
        f'<nav class="crumbs"><a href="/v1/private-research/reporting-studio/documents">Research documents</a> › '
        f'{escape(reg.researchArea.name)} › {escape(reg.investigation.name)}</nav>'
        f'<header class="meta"><h1>{escape(doc.title)}</h1><div class="badges"><span class="badge private">Private</span>'
        f'<span class="badge status">{escape(SUBMISSION_LABELS[doc.submissionStatus])}</span>'
        f'<span class="badge">Authorship: {"pending verification" if doc.authorship == "PENDING_VERIFICATION" else "confirmed by owner"}</span></div>'
        f'<dl class="facts"><dt>Version</dt><dd>{escape(doc.revisionLabel)}</dd>'
        + (f'<dt>Submission note</dt><dd>{escape(doc.submissionNote)}</dd>' if doc.submissionNote else '')
        + f'<dt>Original</dt><dd>{escape(doc.original.filename)}</dd>'
        f'<dt>SHA-256</dt><dd><code>{doc.original.sha256}</code> (verified on this request)</dd>'
        f'<dt>Register</dt><dd>revision {reg.registerRevision}, <code>{found["artifact"]["sha256"][:16]}…</code></dd>'
        + (f'<dt>Existing public record</dt>{publics}' if publics else '')
        + f'</dl><div class="actions">{"".join(links)}</div>'
        f'<div class="fidelity{"" if stats["complete"] else " incomplete"}">{fidelity}</div></header>'
        f'<article class="document">{html}</article>')
    return _page(doc.title, body)


@router.get('/{project_id}/{document_id}/original')
def original(project_id: str, document_id: str, request: Request):
    owner = _subject(request)
    with session_scope() as db:
        _project(db, owner, project_id)
        _, entry = _document(db, owner, project_id, document_id)
        doc = entry['document']
        if entry['artifactIds'][0] is None:
            raise HTTPException(409, 'The registered original is not in this project.')
        raw = _blob(doc.original.sha256, doc.original.bytes)
    return Response(raw, media_type=DOCX, headers={
        **HEADERS, 'Content-Disposition': f"attachment; filename*=UTF-8''{quote(doc.original.filename)}",
        'X-Research-SHA256': doc.original.sha256})


@router.get('/{project_id}/{document_id}/rendition/{sha256}')
def rendition(project_id: str, document_id: str, sha256: str, request: Request):
    owner = _subject(request)
    with session_scope() as db:
        _project(db, owner, project_id)
        _, entry = _document(db, owner, project_id, document_id)
        doc = entry['document']
        match = next(((r, a) for r, a in zip(doc.renditions, entry['artifactIds'][1:]) if r.sha256 == sha256), None)
        if match is None or match[1] is None:
            raise HTTPException(404, 'Rendition not found.')
        raw = _blob(match[0].sha256, match[0].bytes)
    if not raw.startswith(b'%PDF-'):
        raise HTTPException(415, 'Registered rendition is not a PDF.')
    return Response(raw, media_type='application/pdf', headers={
        **HEADERS, 'Content-Disposition': f"inline; filename*=UTF-8''{quote(match[0].filename)}",
        'X-Research-SHA256': match[0].sha256})
