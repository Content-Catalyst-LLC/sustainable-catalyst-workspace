"""RD-01.2: authenticated scientific manuscript authoring on existing Workspace projects.

No new project identity or database table. Every save is an immutable Workspace
project revision and an append-only scientific-publication snapshot. Imported
legacy research blobs remain immutable; source SHA-256 is rechecked on each read.
"""
from __future__ import annotations

import base64
from copy import deepcopy
import hashlib
from html import escape
from io import BytesIO
import json
from pathlib import Path
import re
from urllib.parse import quote
from uuid import uuid4
from xml.etree import ElementTree as ET

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import text

from . import repository, object_store
from .config import get_settings
from .db import session_scope
from .schemas import ProjectStoreRequest
from .wxr_private_projects import _subject, _write, _project, _locked_project, HEADERS
from .studio_signin import page_subject
from .reporting_project_catalog import read_legacy_artifacts
from . import citation_studio as cite
from . import publication_layout as layout
from . import docx_manuscript
from . import document_lifecycle as lifecycle
from . import scientific_outputs as sco

router = APIRouter(prefix='/publication', tags=['Scientific Publication Studio'])
SCHEMA = 'sc-scientific-publication/1.0'
MAX_MANUSCRIPT = 180_000
MAX_ASSET = 4_000_000

# Brand and document types are shared by every saved revision and export.
# Preview and authoring do not constitute scientific review or publication approval.
PUBLICATION_TYPES = ('report', 'policy-brief', 'working-paper', 'interactive-analysis', 'overview')
PUBLICATION_LABELS = {
    'report': 'Scientific Report', 'policy-brief': 'Policy Brief',
    'working-paper': 'Working Paper', 'interactive-analysis': 'Interactive Analysis',
    'overview': 'Research Overview',
}
BRAND_NAME = 'SUSTAINABLE CATALYST'
BRAND_LINE = 'INDEPENDENT RESEARCH'
BRAND_RED = '#b00020'
BRAND_INK = '#171717'


def _publication_label(pub: dict) -> str:
    return PUBLICATION_LABELS.get(pub.get('publicationType'), PUBLICATION_LABELS['report'])


class Draft(BaseModel):
    model_config = ConfigDict(extra='forbid')
    title: str = Field(min_length=1, max_length=200)
    markdown: str = Field(min_length=1, max_length=MAX_MANUSCRIPT)
    sourceArtifactId: str | None = Field(default=None, max_length=160)
    citationStyle: Literal[cite.STYLES] = cite.DEFAULT_STYLE
    publicationType: Literal['report', 'policy-brief', 'working-paper', 'interactive-analysis', 'overview'] = 'report'


class FigureMove(BaseModel):
    """Preview-only, explicit marker-to-project-SVG layout proposal."""
    model_config = ConfigDict(extra='forbid')
    title: str = Field(min_length=1, max_length=200)
    markdown: str = Field(min_length=1, max_length=MAX_MANUSCRIPT)
    expectedSHA256: str = Field(pattern=r'^[a-f0-9]{64}$')
    marker: str = Field(pattern=r'^FIGURE_[A-Z0-9_]{1,64}$')
    assetId: str = Field(pattern=r'^[A-Za-z0-9_.-]{1,160}$')
    caption: str = Field(default='', max_length=160)


class LifecycleIn(BaseModel):
    model_config=ConfigDict(extra='forbid')
    expectedProjectRevision:int=Field(ge=1)


class PurgeIn(LifecycleIn):
    confirmTitle:str=Field(min_length=1,max_length=300)


class Save(Draft):
    expectedProjectRevision: int = Field(ge=1)
    documentId: str | None = Field(default=None, pattern=r'^publication-[a-f0-9]{32}$')
    expectedDocumentRevision: int = Field(default=0, ge=0)


def _original_asset(db, owner: str, project_id: str, asset_id: str):
    """Retrieve a previously imported source with both owner and project gates."""
    legacy, has_table = read_legacy_artifacts(db, owner, project_id)
    match = next((x for x in legacy if x['artifactId'] == asset_id), None)
    if match:
        name, digest, size = match['filename'], match['sha256'], match['bytes']
        path = Path(get_settings().object_storage_root) / 'private-research' / digest[:2] / digest
        if not path.is_file():
            raise HTTPException(503, 'Research blob is missing.')
        if size > MAX_ASSET:
            raise HTTPException(413, 'Source exceeds document-preview limit.')
        raw = path.read_bytes()
        if len(raw) != size or hashlib.sha256(raw).hexdigest() != digest:
            raise HTTPException(409, 'Source integrity verification failed.')
        return {'artifactId':asset_id,'filename':name,'sha256':digest,
                'storageClass':'legacy-private-research','bytes':size}, raw
    # Native source fallback. Do not ever read a source from a different project.
    native = object_store.get_artifact(db, owner, asset_id)
    if native is None or native.project_id != project_id:
        raise HTTPException(404, 'Research source not found in this project.')
    if native.bytes > MAX_ASSET:
        raise HTTPException(413, 'Source exceeds document-preview limit.')
    raw = object_store.read_artifact_content(native)
    return {'artifactId':asset_id,'filename':native.filename,'sha256':native.sha256,
            'storageClass':'native-research','bytes':native.bytes}, raw


def docx_to_markdown(raw: bytes) -> str:
    """Visible text extraction only; does NOT claim round-trip Word fidelity."""
    from zipfile import ZipFile, BadZipFile
    try:
        with ZipFile(BytesIO(raw)) as archive:
            member = archive.getinfo('word/document.xml')
            if member.file_size > 12_000_000:
                raise HTTPException(413, 'DOCX content exceeds preview limit.')
            xml = archive.read(member)
    except (BadZipFile, KeyError) as exc:
        raise HTTPException(422, 'Invalid DOCX source.') from exc
    if len(xml) > 12_000_000:
        raise HTTPException(413, 'DOCX content exceeds preview limit.')
    namespace = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
    root = ET.fromstring(xml)
    body = root.find(namespace+'body')
    lines = []
    for node in body if body is not None else []:
        if node.tag == namespace+'p':
            value = ''.join(x.text or '' for x in node.iter(namespace+'t'))
            style = node.find('.//'+namespace+'pStyle')
            name = style.attrib.get(namespace+'val','') if style is not None else ''
            if value.strip():
                prefix = '# ' if name.lower() in ('title','heading1') else '## ' if name.lower() == 'heading2' else ''
                lines.append(prefix+value.strip())
        elif node.tag == namespace+'tbl':
            for row in node.findall(namespace+'tr'):
                values=[' '.join(t.text or '' for t in cell.iter(namespace+'t')).strip()
                        for cell in row.findall(namespace+'tc')]
                lines.append(' | '.join(values))
    return '\n\n'.join(lines)[:MAX_MANUSCRIPT]


def snapshots(package: dict, document_id: str | None = None) -> list[dict]:
    objects = package.get('project', {}).get('objects', [])
    found = [x['publication'] for x in objects
             if isinstance(x, dict) and x.get('type')=='scientific-publication'
             and isinstance(x.get('publication'), dict)
             and x['publication'].get('schema') == SCHEMA
             and (document_id is None or x['publication'].get('documentId') == document_id)]
    return sorted(found, key=lambda x:(str(x.get('documentId')),int(x.get('revision',0))))


def latest_documents(package: dict) -> list[dict]:
    """Active saved publications. Drafts in Trash (SC-PUB-DRAFT-01) are listed by the Trash view instead."""
    result={}
    gone=lifecycle.hidden(package,'publication')
    for obj in snapshots(package):
        if obj['documentId'] in gone:continue
        result[obj['documentId']] = obj
    return [dict(documentId=x['documentId'],title=x['title'],revision=x['revision'],
                 updatedAt=x['createdAt'],projectRevision=x['projectRevision']) for x in sorted(result.values(),key=lambda obj:obj['projectRevision'],reverse=True)]


# SC-EDITOR-DOCX-01: Markdown backslash escapes (written by the DOCX converter and by Tiptap) render literally.
# Escaped ASCII punctuation is parked in the private-use plane while inline syntax is applied, then restored.
_ESCAPED=re.compile(r'\\([\\`*_{}\[\]()#+\-.!|$<>~])')
_PARKED=re.compile('[\ue000-\ue07f]')
_LINK=re.compile(r'\[([^\]\n]{1,400})\]\(((?:https?://|mailto:)[^\s()<>"]{1,2000})\)')
_BARE_URL=re.compile(r'(?<![="\w/>])(https?://[^\s<>"]{2,2000}[^\s<>".,;:!?)\]\ue000-\ue07f])')


def _park(text: str) -> str:
    return _ESCAPED.sub(lambda m: chr(0xE000+ord(m.group(1))),text)


def _unpark(text: str, html: bool = True) -> str:
    return _PARKED.sub(lambda m: (escape if html else str)(chr(ord(m.group(0))-0xE000)),text)


def _esc_line(line: str) -> str:
    safe=escape(_park(line))
    safe=re.sub(r'`([^`]{1,240})`',r'<code>\1</code>',safe)
    safe=_LINK.sub(lambda m:'<a href="'+m.group(2)+'" rel="noopener noreferrer">'+m.group(1)+'</a>',safe)
    safe=_BARE_URL.sub(lambda m:'<a href="'+m.group(1)+'" rel="noopener noreferrer">'+m.group(1)+'</a>',safe)
    safe=re.sub(r'\*\*([^*]{1,400})\*\*',r'<strong>\1</strong>',safe)
    safe=re.sub(r'(?<!\*)\*([^*]{1,400})\*(?!\*)',r'<em>\1</em>',safe)
    safe=re.sub(r'\[@([A-Za-z0-9_.:-]{1,80})\]',r'<span class="citation">[\1]</span>',safe)
    return _unpark(safe)


def _cells(line: str) -> list[str]:
    """Split a table row on unescaped pipes; an escaped pipe stays in the cell."""
    row=line.strip()
    row=row[1:] if row.startswith('|') else row
    row=row[:-1] if row.endswith('|') and not row.endswith('\\|') else row
    return [x.strip() for x in re.split(r'(?<!\\)\|',row)]


def mark_references(blocks: list[dict]) -> list[dict]:
    """Paragraphs under a References/Bibliography heading are bibliography entries (rendered with hanging indents)."""
    out,level=[],None
    for block in blocks:
        if block['kind']=='heading':
            if docx_manuscript.REFERENCES_HEADING.match(_unpark(_park(block['text']),False).strip().rstrip(':')):
                level=block['level']
            elif level is not None and block['level']<=level:level=None
        elif block['kind']=='paragraph' and level is not None:
            block={**block,'kind':'reference'}
        out.append(block)
    return out


def parse_blocks(markdown: str) -> list[dict]:
    """Strict, intentionally small Markdown subset. Raw HTML is NEVER honored."""
    lines = markdown.replace('\r\n','\n').replace('\r','\n').split('\n')
    result=[]; i=0
    image=re.compile(r'^!\[([^\]]{0,160})\]\(asset:([A-Za-z0-9_.-]{1,160})\)$')
    while i < len(lines):
        line=lines[i].strip(); i+=1
        if not line: continue
        if line.startswith('```'):
            lang=line[3:][:32].strip()
            code=[]
            while i<len(lines) and not lines[i].startswith('```'):
                code.append(lines[i]);i+=1
            if i<len(lines): i+=1
            result.append({'kind':'code','lang':lang,'text':'\n'.join(code)})
        elif line=='$$':
            math=[]
            while i<len(lines) and lines[i].strip()!='$$':
                math.append(lines[i]); i+=1
            if i<len(lines): i+=1
            result.append({'kind':'math','text':'\n'.join(math)})
        elif image.fullmatch(line):
            match=image.fullmatch(line)
            result.append({'kind':'figure','caption':match.group(1),'assetId':match.group(2)})
        elif re.match(r'^#{1,4}\s+',line):
            level=len(line)-len(line.lstrip('#'))
            result.append({'kind':'heading','level':level,'text':line[level:].strip()})
        elif line.startswith('|') and i<len(lines) and re.fullmatch(r'[|\s:\-]+',lines[i].strip()):
            headers=_cells(line);i+=1
            rows=[]
            while i<len(lines) and lines[i].strip().startswith('|') and len(rows)<100:
                rows.append(_cells(lines[i])); i+=1
            result.append({'kind':'table','headers':headers[:16], 'rows':rows})
        elif re.match(r'^[-*+] ',line):
            items=[line[2:].strip()]
            while i<len(lines) and re.match(r'^\s*[-*+] ',lines[i]):
                items.append(re.sub(r'^\s*[-*+] ','',lines[i]).strip());i+=1
            result.append({'kind':'list','items':items})
        elif re.match(r'^\d{1,3}[.)] ',line):
            items=[re.sub(r'^\d{1,3}[.)] ','',line).strip()]
            while i<len(lines) and re.match(r'^\s*(?:\d{1,3}[.)]|[-*+]) ',lines[i]):
                items.append(re.sub(r'^\s*(?:\d{1,3}[.)]|[-*+]) ','',lines[i]).strip());i+=1
            result.append({'kind':'list','items':items,'ordered':True,'start':int(re.match(r'\d+',line).group(0))})
        elif line.startswith('> '):
            result.append({'kind':'quote','text':line[2:]})
        else:
            parts=[line]
            while i<len(lines) and lines[i].strip() and not (lines[i].startswith(('#','```','|','> ','$$','![')) or re.match(r'^(?:[-*+]|\d{1,3}[.)]) ',lines[i])):
                parts.append(lines[i].strip());i+=1
            result.append({'kind':'paragraph','text':' '.join(parts)})
    return result


def render_html(markdown: str, asset_uri=None, *, document_title: str | None = None) -> tuple[str,list[str]]:
    """Return safe body HTML and referenced figure IDs; asset URI is trusted callback."""
    out=[]; figure_ids=[]
    blocks = parse_blocks(markdown)
    if document_title is not None:
        blocks = layout.without_repeated_title(blocks, document_title)
    for node in mark_references(blocks):
        kind=node['kind']
        if kind=='heading':
            n=node['level'];out.append(f'<h{n}>{_esc_line(node["text"])}</h{n}>')
        elif kind=='paragraph':out.append('<p>'+_esc_line(node['text'])+'</p>')
        elif kind=='reference':out.append('<p class="reference">'+_esc_line(node['text'])+'</p>')
        elif kind=='quote':out.append('<blockquote>'+_esc_line(node['text'])+'</blockquote>')
        elif kind in ('code','math'):
            out.append('<pre class="'+('equation' if kind=='math' else 'code')+'"><code>'+escape(node['text'])+'</code></pre>')
        elif kind=='list':
            tag='ol' if node.get('ordered') else 'ul'
            start=f' start="{node["start"]}"' if node.get('start',1)!=1 else ''
            out.append(f'<{tag}{start}>'+''.join('<li>'+_esc_line(i)+'</li>' for i in node['items'])+f'</{tag}>')
        elif kind=='table':
            cols=len(node['headers']);out.append('<table><thead><tr>'+''.join('<th>'+_esc_line(x)+'</th>' for x in node['headers'])+'</tr></thead><tbody>')
            for row in node['rows']:
                out.append('<tr>'+''.join('<td>'+_esc_line(x)+'</td>' for x in (row+['']*cols)[:cols])+'</tr>')
            out.append('</tbody></table>')
        elif kind=='figure':
            figure_ids.append(node['assetId'])
            cap=_unpark(escape(_park(node['caption'])))
            if asset_uri:
                src=escape(asset_uri(node['assetId']),quote=True)
                out.append(f'<figure><img src="{src}" alt="{cap}"><figcaption>{cap}</figcaption></figure>')
            else:out.append(f'<figure><p>[Source figure: {escape(node["assetId"])}]</p><figcaption>{cap}</figcaption></figure>')
    return '\n'.join(out), list(dict.fromkeys(figure_ids))


SVG_TAGS={'svg','g','defs','path','rect','circle','ellipse','line','polyline','polygon','text','tspan',
          'title','desc','clipPath','use','linearGradient','radialGradient','stop'}
SVG_ATTRS={'width','height','viewBox','x','y','x1','y1','x2','y2','cx','cy','r','rx','ry','d',
           'points','transform','fill','stroke','stroke-width','stroke-linejoin','stroke-linecap',
           'stroke-dasharray','stroke-dashoffset','opacity','fill-opacity','stroke-opacity',
           'font-family','font-size','font-weight','font-style','text-anchor','dominant-baseline',
           'id','clip-path','stop-color','stop-opacity','offset','preserveAspectRatio','xmlns'}
SVG_NS='http://www.w3.org/2000/svg'


# Matplotlib writes the standard SVG 1.1 PUBLIC doctype. DTDs, external entities and internal subsets are never
# resolved: only that exact declaration, at the start of the document, is dropped from the in-memory rendering copy
# before the sanitizer below. Stored source bytes and their SHA-256 are never modified.
_SVG11_DOCTYPE = re.compile(
    rb'\A(?P<before>(?:\xef\xbb\xbf)?[ \t\r\n]*(?:<\?xml[ \t]+[^<>]{1,250}\?>[ \t\r\n]*)?)'
    rb'(?P<doctype><!DOCTYPE[ \t\r\n]+svg[ \t\r\n]+PUBLIC[ \t\r\n]+'
    rb'(?P<quote>["\x27])-//W3C//DTD SVG 1\.1//EN(?P=quote)[ \t\r\n]+'
    rb'(?P<urlquote>["\x27])https?://www\.w3\.org/Graphics/SVG/1\.1/DTD/svg11\.dtd(?P=urlquote)[ \t\r\n]*>)',
    re.IGNORECASE,
)


def _strip_known_svg_doctype(raw: bytes) -> bytes:
    """Remove only an official SVG 1.1 PUBLIC declaration; every other doctype or entity stays refused."""
    if b'<!DOCTYPE' not in raw.upper():
        return raw
    match = _SVG11_DOCTYPE.match(raw)
    if b'<!ENTITY' in raw.upper() or match is None:
        raise HTTPException(422,'SVG document type declarations not allowed.')
    return raw[:match.start('doctype')] + raw[match.end('doctype'):]


def sanitize_svg(raw: bytes) -> bytes:
    raw = _strip_known_svg_doctype(raw)
    if b'<!DOCTYPE' in raw.upper() or b'<!ENTITY' in raw.upper():
        raise HTTPException(422,'SVG document type declarations not allowed.')
    try: root=ET.fromstring(raw)
    except ET.ParseError as exc:raise HTTPException(422,'Invalid SVG source.') from exc
    if root.tag.rsplit('}',1)[-1]!='svg':raise HTTPException(422,'Source is not an SVG.')
    def walk(node):
        if node.tag.startswith('{') and not node.tag.startswith('{'+SVG_NS+'}'):
            raise HTTPException(422, 'Foreign SVG namespace is not supported.')
        for child in list(node):
            if child.tag.rsplit('}',1)[-1] not in SVG_TAGS:node.remove(child)
            else:walk(child)
        for key,value in list(node.attrib.items()):
            short=key.rsplit('}',1)[-1]
            if short == 'style':
                # Convert strictly safe presentation CSS to XML attributes.
                for part in value.split(';'):
                    if ':' not in part: continue
                    prop, val = [x.strip() for x in part.split(':',1)]
                    if prop in SVG_ATTRS and prop not in ('xmlns','id','clip-path') and re.fullmatch(r'[A-Za-z0-9#.,%() +/\-]{1,120}',val):
                        if 'url(' not in val.lower() and 'expression(' not in val.lower():node.set(prop,val)
                del node.attrib[key]
            elif short == 'href':
                if not re.fullmatch(r'#[A-Za-z0-9_.:-]{1,160}',value):del node.attrib[key]
            elif short not in SVG_ATTRS:
                del node.attrib[key]
            elif 'url(' in value.lower() and not re.fullmatch(r'url\(#[A-Za-z0-9_.:-]{1,160}\)',value.strip()):
                del node.attrib[key]
        # No CSS or foreign embedded markup; text nodes are inert.
    walk(root)
    return ET.tostring(root,encoding='utf-8',xml_declaration=True)


def _source_meta(db, owner, project_id, artifact_id):
    if not artifact_id:return None
    meta,_ = _original_asset(db, owner, project_id, artifact_id)
    return meta


def _historical_versions(db, owner, project_id, document_id, max_revisions=250):
    """Read immutable canonical Workspace ProjectRevision rows, newest first.

    Only the latest publication head is retained in the live ProjectHead package.
    This prevents O(revision count) manuscript duplication in every new save.
    """
    found={}
    for item in repository.list_project_revisions(db, owner, project_id)[:max_revisions]:
        archive=repository.get_project_revision(db, owner, project_id, item['revision'])
        if not archive:continue
        versions=snapshots(archive.package,document_id)
        for version in versions:
            found[version['revision']]=version
    return [found[k] for k in sorted(found)]


def _saved(db, owner, project_id, document_id, rev=None):
    row=_project(db, owner, project_id)
    if document_id in lifecycle.purged(row.package,'publication'):
        raise HTTPException(404,'Publication not found in this project.')
    candidates=snapshots(row.package,document_id)
    if rev is not None and not any(x['revision']==rev for x in candidates):
        candidates=_historical_versions(db,owner,project_id,document_id)
    if rev is not None:candidates=[x for x in candidates if x['revision']==rev]
    if not candidates:raise HTTPException(404,'Publication not found in this project.')
    return row, candidates[-1]

RASTER_MAGIC={b'\x89PNG\r\n\x1a\n':'image/png',b'\xff\xd8\xff':'image/jpeg'}
MAX_RASTER_PIXELS=40_000_000


def figure_payload(filename: str, raw: bytes) -> tuple[str, bytes]:
    """(media type, bytes safe to embed) for a verified figure source: sanitized SVG, or a decodable PNG/JPEG
    (SC-EDITOR-DOCX-01: images extracted from Word manuscripts). Anything else is refused."""
    if filename.lower().endswith('.svg'):
        return 'image/svg+xml',sanitize_svg(raw)
    media=next((m for magic,m in RASTER_MAGIC.items() if raw.startswith(magic)),None)
    if media is None or not filename.lower().endswith(('.png','.jpg','.jpeg')):
        raise HTTPException(422,'Figure ID is not an SVG, PNG or JPEG research source.')
    from PIL import Image as PILImage
    try:
        with PILImage.open(BytesIO(raw)) as image:
            if image.width*image.height>MAX_RASTER_PIXELS:raise HTTPException(413,'Figure image is too large.')
            image.verify()
    except HTTPException:raise
    except Exception:
        raise HTTPException(422,'Figure image could not be decoded.') from None
    return media,raw


def _require_active_files(row, artifact_ids):
    """SC-PUB-DRAFT-01: a file in Trash cannot become the source or a figure of new work until it is restored."""
    waiting=[a for a in artifact_ids if a and a in lifecycle.hidden(row.package,'file')]
    if waiting:
        raise HTTPException(409,{'message':'A file this draft uses is in Trash. Restore it first.','files':waiting})


def _verify_figures(db, owner, project_id, figure_ids):
    if len(figure_ids) > 12:
        raise HTTPException(413, 'A publication supports up to 12 linked figures per revision.')
    source=[]
    for aid in figure_ids:
        info,raw=_original_asset(db,owner,project_id,aid)
        media,clean=figure_payload(info['filename'],raw)
        entry={'artifactId':aid,'sha256':info['sha256'],'bytes':len(clean)}
        if media!='image/svg+xml':entry['mediaType']=media
        source.append(entry)
    return source


@router.get('',response_class=HTMLResponse)
def publication_ui(request:Request):
    page_subject(request, _subject)
    script=Path(__file__).with_name('reporting_publication_ui.js').read_text()
    script+='\n'+Path(__file__).with_name('reporting_publication_visual.js').read_text()
    script+='\n'+Path(__file__).with_name('reporting_outputs_ui.js').read_text()
    script+='\n'+Path(__file__).with_name('reporting_scientific_outputs_ui.js').read_text()
    html=Path(__file__).with_name('reporting_publication_ui.html').read_text()
    script_hash=base64.b64encode(hashlib.sha256(script.encode()).digest()).decode()
    # Self-hosted Tiptap bundle. No CDN or external editor service.
    bundle_src='/v1/private-research/reporting-studio/publication/editor.bundle.js'
    inline='<script>'+script+'</script>'
    local_bundle='<script src="'+bundle_src+'" defer></script>'
    return HTMLResponse(html.replace('<!--SCRIPT-->', inline+local_bundle),headers={**HEADERS,
        'Content-Security-Policy':"default-src 'none'; script-src 'self' 'sha256-"+script_hash+"'; style-src 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'"})


@router.get('/editor.bundle.js')
def tiptap_editor_bundle(request:Request):
    """Authenticated same-origin Tiptap asset; no remote JavaScript."""
    _subject(request)
    path=Path(__file__).with_name('reporting_publication_tiptap.bundle.js')
    if not path.is_file():
        raise HTTPException(503,'Tiptap bundle missing from this Reporting Studio image.')
    return Response(path.read_bytes(),media_type='text/javascript; charset=utf-8',
                    headers={**HEADERS,'Cache-Control':'private, no-store',
                             'X-Content-Type-Options':'nosniff'})


@router.get('/projects/{project_id}/sources/{artifact_id}')
def open_source(project_id:str,artifact_id:str,request:Request):
    owner=_subject(request)
    with session_scope() as db:
        _require_active_files(_project(db,owner,project_id),[artifact_id])
        meta,raw=_original_asset(db,owner,project_id,artifact_id)
    ext=meta['filename'].lower()
    if ext.endswith('.md') or ext.endswith('.txt'):
        try:content=raw.decode('utf-8-sig')
        except UnicodeError as exc:raise HTTPException(422,'Source is not UTF-8 text.') from exc
        conversion='exact-utf8-source'
    elif ext.endswith('.docx'):
        # Read-only dry run. Figures are stored by POST .../import-docx before the draft is opened.
        report=_docx_conversion(project_id,meta,raw)
        return JSONResponse({'source':meta,'markdown':report['markdown'],'title':report['title'],
                             'conversion':'docx-structured','import':_public_report(report),
                             'sourcePreserved':True},headers=HEADERS)
    else:raise HTTPException(415,'Choose an existing Markdown, text or DOCX manuscript.')
    return JSONResponse({'source':meta,'markdown':content,'conversion':conversion,
                         'sourcePreserved':True},headers=HEADERS)


def _docx_figure_id(project_id: str, source_sha256: str):
    """Deterministic, project-scoped asset id: re-importing the same DOCX reuses its figures."""
    return lambda media:'docx-figure-'+hashlib.sha256(
        f'{project_id}\0{source_sha256}\0{media["sha256"]}'.encode()).hexdigest()[:24]


def _docx_conversion(project_id: str, meta: dict, raw: bytes) -> dict:
    if len(raw)>MAX_ASSET:raise HTTPException(413,'DOCX exceeds the import limit.')
    report=docx_manuscript.convert_docx(raw,_docx_figure_id(project_id,meta['sha256']))
    if len(report['markdown'])>MAX_MANUSCRIPT:raise HTTPException(413,'Converted manuscript exceeds the authoring limit.')
    if len(report['media'])>12:raise HTTPException(413,'A publication supports up to 12 linked figures per revision.')
    stem=re.sub(r'[^A-Za-z0-9._-]+','_',meta['filename'].rsplit('/',1)[-1].rsplit('.',1)[0])[:80] or 'manuscript'
    for media in report['media']:
        media['filename']=f'docx-import/{stem}/figure-{media["index"]}{media["extension"]}'
    return report


def _public_report(report: dict) -> dict:
    return {'converter':report['converter'],'sourceSha256':report['sourceSha256'],
            'convertedMarkdownSha256':report['markdownSha256'],'outline':report['outline'],
            'unsupported':report['unsupported'],'notes':report['notes'],
            'figures':[{k:m[k] for k in ('assetId','filename','part','sha256','bytes','mediaType')}
                       for m in report['media']]}


@router.post('/projects/{project_id}/sources/{artifact_id}/import-docx',status_code=201)
def import_docx(project_id:str,artifact_id:str,request:Request):
    """SC-EDITOR-DOCX-01: structured import of an existing Word manuscript. The DOCX bytes are never modified; each
    embedded PNG/JPEG becomes an immutable project-owned image with its package provenance (idempotent). The draft
    is returned unsaved; saving it starts a new publication lineage, so existing revisions are untouched."""
    owner=_subject(request);_write(request)
    with session_scope() as db:
        _require_active_files(_locked_project(db,owner,project_id),[artifact_id])
        meta,raw=_original_asset(db,owner,project_id,artifact_id)
        if not meta['filename'].lower().endswith('.docx'):raise HTTPException(415,'Choose a DOCX manuscript.')
        report=_docx_conversion(project_id,meta,raw)
        stored=[]
        from datetime import datetime,timezone
        for media in report['media']:
            existing=object_store.get_artifact(db,owner,media['assetId'])
            if existing is not None:
                if existing.project_id!=project_id or existing.sha256!=media['sha256']:
                    raise HTTPException(409,'An extracted figure id is already used by different content.')
                stored.append({'assetId':media['assetId'],'status':'reused'})
                continue
            from .schemas import ArtifactStoreRequest
            object_store.store_artifact(db,owner,ArtifactStoreRequest.model_validate({
                'schema':'sc-workspace-artifact-store/1.0','artifactId':media['assetId'],'projectId':project_id,
                'filename':media['filename'],'mediaType':media['mediaType'],
                'contentBase64':base64.b64encode(media['raw']).decode('ascii'),'expectedRevision':0,
                'metadata':{'source':'docx-import','converter':report['converter'],
                            'sourceArtifactId':meta['artifactId'],'sourceFilename':meta['filename'],
                            'sourceSha256':meta['sha256'],'sourcePart':media['part'],'mediaSha256':media['sha256'],
                            'altText':media['alt'][:300],'widthEmu':media['widthEmu'],
                            'extractedAt':datetime.now(timezone.utc).isoformat()}}))
            stored.append({'assetId':media['assetId'],'status':'created'})
    return JSONResponse({'source':meta,'markdown':report['markdown'],'title':report['title'],
                         'conversion':'docx-structured','import':_public_report(report),'figures':stored,
                         'sourcePreserved':True,'saved':False},status_code=201,headers=HEADERS)


@router.get('/projects/{project_id}/assets/{asset_id}/svg')
def svg_asset(project_id:str,asset_id:str,request:Request):
    owner=_subject(request)
    with session_scope() as db:
        _project(db,owner,project_id)
        info,raw=_original_asset(db,owner,project_id,asset_id)
        if not info['filename'].lower().endswith('.svg'):raise HTTPException(415,'Not an SVG research source.')
        data=sanitize_svg(raw)
    return Response(data,media_type='image/svg+xml',headers={**HEADERS,
        'Content-Security-Policy':"default-src 'none'; style-src 'none'; sandbox",'X-Research-SHA256':info['sha256']})


@router.get('/projects/{project_id}/assets/{asset_id}/image')
def figure_asset(project_id:str,asset_id:str,request:Request):
    """A verified project figure (sanitized SVG or decoded PNG/JPEG) for the preview and the visual editor."""
    owner=_subject(request)
    with session_scope() as db:
        _project(db,owner,project_id)
        info,raw=_original_asset(db,owner,project_id,asset_id)
        media,data=figure_payload(info['filename'],raw)
    return Response(data,media_type=media,headers={**HEADERS,'X-Content-Type-Options':'nosniff',
        'Content-Security-Policy':"default-src 'none'; style-src 'none'; sandbox",'X-Research-SHA256':info['sha256']})


@router.post('/projects/{project_id}/preview')
def preview_document(project_id:str,body:Draft,request:Request):
    owner=_subject(request)
    with session_scope() as db:
        _project(db,owner,project_id)
        row=_project(db,owner,project_id)
        if body.sourceArtifactId:_source_meta(db,owner,project_id,body.sourceArtifactId)
        frozen=cite.freeze(body.markdown,cite.collection(row.package),body.citationStyle)
        path='/v1/private-research/reporting-studio/publication/projects/'+quote(project_id,safe='')
        html,ids=render_html(cite.resolve(body.markdown,frozen),
                            lambda aid:path+'/assets/'+quote(aid,safe='')+'/image',
                            document_title=body.title)
        sources=_verify_figures(db,owner,project_id,ids)
    return JSONResponse({'html':html,'figures':sources,
                         'layout':layout.audit_layout(body.markdown,body.title),
                         'sourceVerified':bool(body.sourceArtifactId),
                         'citations':frozen,
                         'equations':'LaTeX source displayed, not mathematically executed',
                         'scientificValidationPerformed':False},headers=HEADERS)


@router.post('/projects/{project_id}/layout/move-figure')
def propose_layout_figure_move(project_id: str, body: FigureMove, request: Request):
    """Suggest, but never save, an explicit figure move against verified project sources."""
    owner = _subject(request)
    if hashlib.sha256(body.markdown.encode()).hexdigest() != body.expectedSHA256:
        raise HTTPException(409,'Manuscript changed since layout selection. Refresh the audit.')
    with session_scope() as db:
        _project(db,owner,project_id)
        meta,raw = _original_asset(db,owner,project_id,body.assetId)
        figure_payload(meta['filename'],raw)
        try:
            proposal = layout.propose_figure_move(body.markdown,body.marker,body.assetId,body.caption)
        except ValueError as exc:
            raise HTTPException(422,str(exc)) from exc
        if len(proposal['markdown']) > MAX_MANUSCRIPT:
            raise HTTPException(413,'The proposed manuscript exceeds the authoring limit.')
        _,figure_ids = render_html(proposal['markdown'])
        _verify_figures(db,owner,project_id,figure_ids)
    return JSONResponse({'proposedMarkdown':proposal['markdown'],
                         'beforeSHA256':proposal['beforeSHA256'],
                         'afterSHA256':proposal['afterSHA256'],
                         'movedExistingPlacements':proposal['movedExistingPlacements'],
                         'removedDuplicatePlacements':proposal['removedDuplicatePlacements'],
                         'caption':proposal['caption'],
                         'selectedFigure':{'artifactId':meta['artifactId'],'sha256':meta['sha256']},
                         'layout':layout.audit_layout(proposal['markdown'],body.title),
                         'saved':False,'sourceModified':False},headers=HEADERS)


@router.get('/projects/{project_id}/documents')
def list_documents(project_id:str,request:Request):
    owner=_subject(request)
    with session_scope() as db:
        row=_project(db,owner,project_id)
        return JSONResponse({'documents':latest_documents(row.package),
                             'projectRevision':row.revision},headers=HEADERS)


@router.post('/projects/{project_id}/documents',status_code=201)
def save_document(project_id:str,body:Save,request:Request):
    owner=_subject(request);_write(request)
    with session_scope() as db:
        row=_locked_project(db,owner,project_id)
        if row.revision!=body.expectedProjectRevision:
            raise HTTPException(409,'Workspace project changed. Reload before saving.')
        if body.documentId and body.documentId in lifecycle.hidden(row.package,'publication'):
            raise HTTPException(409,'This draft is in Trash. Restore it before saving a new revision.')
        _require_active_files(row,[body.sourceArtifactId] if body.documentId is None else [])
        former=snapshots(row.package,body.documentId) if body.documentId else []
        last=former[-1] if former else None
        if (last['revision'] if last else 0)!=body.expectedDocumentRevision:
            raise HTTPException(409,'Publication revision changed. Reload before saving.')
        if body.documentId and last is None:
            raise HTTPException(404,'Publication not found in this project.')
        if last and body.sourceArtifactId!=(last.get('source') or {}).get('artifactId'):
            raise HTTPException(409,'Source cannot be changed within a publication lineage.')
        source=_source_meta(db,owner,project_id,body.sourceArtifactId)
        import_record=(last or {}).get('importRecord')
        if last is None and source and source['filename'].lower().endswith('.docx'):
            _,raw=_original_asset(db,owner,project_id,source['artifactId'])
            import_record=_public_report(_docx_conversion(project_id,source,raw))
        _,figures=render_html(body.markdown)
        _require_active_files(row,figures)
        figure_sources=_verify_figures(db,owner,project_id,figures)
        # SC-OUTPUT-01: pin the exact registered output versions this revision inserts (rights gate enforced here).
        output_sources=sco.pins(row.package,figures,parse_blocks(body.markdown))
        sco.verify_pins(db,owner,project_id,{'outputSources':output_sources},_original_asset)
        document_id=body.documentId or 'publication-'+uuid4().hex
        version=(last['revision']+1) if last else 1
        from datetime import datetime,timezone
        publication={'schema':SCHEMA,'documentId':document_id,'revision':version,
              'title':body.title.strip(),'markdown':body.markdown,'publicationType':body.publicationType,'source':source,
              'figureSources':figure_sources,'citations':cite.freeze(body.markdown,cite.collection(row.package),body.citationStyle),
              'createdAt':datetime.now(timezone.utc).isoformat(),
              'projectRevision':row.revision+1,'markdownSHA256':hashlib.sha256(body.markdown.encode()).hexdigest(),
              'scientificStatus':'unreviewed','rightsStatus':'not-redistribution-approved',
              'computationsExecuted':False,'sourceBytesModified':False}
        if import_record:publication['importRecord']=import_record
        if output_sources:publication['outputSources']=output_sources
        project=deepcopy(row.package['project'])
        # Keep one live head per document. Earlier versions are preserved by
        # Workspace's immutable project-revision repository, not duplicated in
        # every subsequent ProjectHead JSON package.
        found=False
        for item in project['objects']:
            if (item.get('type')=='scientific-publication' and
                item.get('publication',{}).get('documentId')==document_id):
                item['publication']=publication
                found=True
                break
        if not found:
            project['objects'].append({'id':'publication-head-'+document_id[12:],
                                       'type':'scientific-publication','publication':publication})
        payload=ProjectStoreRequest.model_validate({'schema':'sc-workspace-sync-push/1.0',
           'sourceProjectId':project_id,'projectTitle':row.title,'expectedRevision':row.revision,
           'operationId':'publication-save-'+uuid4().hex,'project':project})
        updated,_=repository.store_project(db,owner,payload)
        return JSONResponse({'document':publication,'project':repository.project_metadata(updated)},
                            status_code=201,headers=HEADERS)


# SC-PUB-DRAFT-01: Trash, Restore and permanent deletion of private drafts (see document_lifecycle).
@router.get('/projects/{project_id}/trash')
def project_trash(project_id:str,request:Request):
    owner=_subject(request)
    with session_scope() as db:
        return JSONResponse(lifecycle.trash_view(_project(db,owner,project_id)),headers=HEADERS)


@router.post('/projects/{project_id}/documents/{document_id}/trash')
def trash_document(project_id:str,document_id:str,body:LifecycleIn,request:Request):
    owner=_subject(request);_write(request)
    with session_scope() as db:
        updated,record=lifecycle.trash_publication(db,owner,_locked_project(db,owner,project_id),document_id,
                                                   body.expectedProjectRevision)
        return JSONResponse({'trashed':record,'project':repository.project_metadata(updated)},headers=HEADERS)


@router.post('/projects/{project_id}/documents/{document_id}/restore')
def restore_document(project_id:str,document_id:str,body:LifecycleIn,request:Request):
    owner=_subject(request);_write(request)
    with session_scope() as db:
        updated,pub=lifecycle.restore_publication(db,owner,_locked_project(db,owner,project_id),document_id,
                                                  body.expectedProjectRevision)
        return JSONResponse({'restored':{'documentId':document_id,'title':(pub or {}).get('title'),
                                         'revision':(pub or {}).get('revision')},
                             'project':repository.project_metadata(updated)},headers=HEADERS)


@router.post('/projects/{project_id}/documents/{document_id}/purge')
def purge_document(project_id:str,document_id:str,body:PurgeIn,request:Request):
    owner=_subject(request);_write(request)
    with session_scope() as db:
        updated,tombstone=lifecycle.purge_publication(db,owner,_locked_project(db,owner,project_id),document_id,
                                                      body.expectedProjectRevision,body.confirmTitle)
        return JSONResponse({'deleted':tombstone,'project':repository.project_metadata(updated)},headers=HEADERS)


@router.get('/projects/{project_id}/documents/{document_id}/history')
def document_history(project_id:str,document_id:str,request:Request):
    owner=_subject(request)
    with session_scope() as db:
        row=_project(db,owner,project_id)
        versions=_historical_versions(db,owner,project_id,document_id)
        if not versions or document_id in lifecycle.purged(row.package,'publication'):
            raise HTTPException(404,'Publication not found.')
        return JSONResponse({'documentId':document_id,'versions':[
            {'revision':x['revision'],'createdAt':x['createdAt'],
             'projectRevision':x['projectRevision'],'markdownSHA256':x['markdownSHA256']}
            for x in versions]},headers=HEADERS)


@router.get('/projects/{project_id}/documents/{document_id}')
def open_document(project_id:str,document_id:str,request:Request,revision:int|None=None):
    owner=_subject(request)
    with session_scope() as db:
        row,publication=_saved(db,owner,project_id,document_id,revision)
        return JSONResponse({'document':publication,'projectRevision':row.revision},headers=HEADERS)


def _as_html(pub:dict,figures:dict|None=None) -> bytes:
    figures=figures or {}
    body,_=render_html(cite.resolve(pub['markdown'],pub.get('citations')),
                       lambda aid:figures.get(aid,''),document_title=pub['title'])
    title=escape(pub['title'])
    css='''@page{margin:20mm}body{font:11pt/1.65 Georgia,serif;max-width:760px;margin:40px auto;color:#171717;padding:0 18px}h1,h2,h3{font-family:Arial,sans-serif;color:#171717}h1{font-size:26pt}h2{font-size:17pt;margin-top:28px}table{border-collapse:collapse;width:100%;font:9pt Arial}td,th{border:1px solid #ccc;padding:7px;text-align:left}figure{text-align:center;margin:24px 0}figure img{max-width:100%}figcaption{font:9pt Arial;color:#555}pre{white-space:pre-wrap;background:#f7f7f7;padding:12px}.sc-brand{border-top:5px solid #b00020;padding-top:10px;font:700 15pt Arial,sans-serif;letter-spacing:.07em}.sc-type{font:9pt Arial,sans-serif;color:#555;letter-spacing:.09em;margin:4px 0 22px}.meta{font:9pt Arial;color:#666;border-bottom:1px solid #ccc;padding-bottom:16px}blockquote{border-left:3px solid #b00020;padding-left:16px}a{color:#b00020;overflow-wrap:anywhere}p.reference{padding-left:2em;text-indent:-2em;margin:0 0 .55em}@media print{body{margin:0;max-width:none}}'''
    meta=f'Saved revision {pub["revision"]} · SHA-256 {pub["markdownSHA256"]} · Scientific content not independently verified'
    masthead='<header class="sc-brand">SUSTAINABLE CATALYST</header><p class="sc-type">'+escape(BRAND_LINE+' / '+_publication_label(pub))+'</p>'
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>'+title+'</title><style>'+css+'</style></head><body>'+masthead+'<h1>'+title+'</h1><p class="meta">'+escape(meta)+'</p>'+body+'</body></html>').encode()


def _pdf_inline(value: str) -> str:
    """Only ReportLab-supported inline tags, never raw user HTML."""
    return (_esc_line(value)
            .replace('<span class="citation">','<font color="#126b55">')
            .replace('</span>','</font>')
            .replace('<strong>','<b>').replace('</strong>','</b>')
            .replace('<em>','<i>').replace('</em>','</i>')
            .replace('<code>','<font name="Courier">').replace('</code>','</font>')
            .replace(' rel="noopener noreferrer">','>'))


def _pdf_svg_image(raw: bytes):
    """Render a verified SVG chart as a bounded, high-resolution PDF image.

    ReportLab's svglib silently loses Matplotlib clip paths and SVG references,
    producing blank or partial scientific charts. CairoSVG already powers the
    DOCX figure export and correctly resolves those constructs. The original
    SVG remains immutable and is never replaced in project storage.
    """
    import math
    import cairosvg
    from reportlab.platypus import Image

    # The export route already sanitizes source-verified figures. Sanitize again
    # at the renderer boundary so direct callers cannot introduce external SVG
    # references, scripts, or unsafe CSS.
    safe = sanitize_svg(raw)
    root = ET.fromstring(safe)
    viewbox = re.split(r'[\s,]+', (root.attrib.get('viewBox') or '').strip())

    def length(value):
        match = re.fullmatch(r'\s*(\d+(?:\.\d+)?)(?:px|pt|in|cm|mm)?\s*',
                             value or '', re.IGNORECASE)
        return float(match.group(1)) if match else 0.0

    if len(viewbox) == 4:
        try:
            width, height = float(viewbox[2]), float(viewbox[3])
        except ValueError:
            width = height = 0.0
    else:
        width, height = length(root.get('width')), length(root.get('height'))
    if not (math.isfinite(width) and math.isfinite(height) and
            width > 0 and height > 0 and 1 / 50 <= width / height <= 50):
        raise HTTPException(422, 'SVG figure has invalid PDF display dimensions.')

    # Stay inside the A4 document frame. Fixed raster density and maximum page
    # dimensions bound conversion to 1230 x 1125 pixels even for oversized SVG.
    scale = min(492.0 / width, 450.0 / height)
    draw_width, draw_height = width * scale, height * scale
    pixel_width = max(1, round(draw_width * 2.5))
    pixel_height = max(1, round(draw_height * 2.5))
    try:
        png = cairosvg.svg2png(
            bytestring=safe, output_width=pixel_width,
            output_height=pixel_height,
        )
    except Exception:
        # A visible 422 is safer than publishing an apparently complete report
        # with a silently missing, partially interpreted scientific figure.
        raise HTTPException(422, 'Saved SVG figure could not be rendered for PDF export.') from None
    return Image(BytesIO(png), width=draw_width, height=draw_height,
                 hAlign='CENTER')


def _publication_blocks(pub: dict) -> list[dict]:
    """Derived export-only view. Saved Markdown and hash remain unchanged."""
    resolved = cite.resolve(pub['markdown'],pub.get('citations'))
    return mark_references(layout.without_repeated_title(parse_blocks(resolved),pub['title']))


def _pdf_raster_image(raw: bytes):
    """A verified PNG/JPEG figure scaled into the A4 frame, keeping its aspect ratio."""
    from PIL import Image as PILImage
    from reportlab.platypus import Image
    with PILImage.open(BytesIO(raw)) as image:
        width,height=image.size
    scale=min(492.0/width,450.0/height)
    return Image(BytesIO(raw),width=width*scale,height=height*scale,hAlign='CENTER')


def _pdf(pub:dict,figure_bytes:dict[str,bytes]):
    from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Preformatted,Table,TableStyle,Image,KeepTogether
    from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import A4
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='SCBody',parent=styles['BodyText'],fontSize=10.5,leading=16,spaceAfter=9))
    styles.add(ParagraphStyle(name='SCReference',parent=styles['BodyText'],fontSize=10,leading=14,spaceAfter=6,
                              leftIndent=22,firstLineIndent=-22))
    styles.add(ParagraphStyle(name='SCCaption',parent=styles['Normal'],fontSize=9,alignment=TA_CENTER,spaceAfter=12,textColor=colors.HexColor('#555555')))
    styles.add(ParagraphStyle(name='SCBrand',parent=styles['Normal'],fontName='Helvetica-Bold',fontSize=15,
                              leading=19,spaceAfter=5,textColor=colors.HexColor(BRAND_RED)))
    styles.add(ParagraphStyle(name='SCType',parent=styles['Normal'],fontName='Helvetica',
                              fontSize=9,leading=12,spaceAfter=16,textColor=colors.HexColor('#555555')))
    out=BytesIO(); doc=SimpleDocTemplate(out,pagesize=A4,rightMargin=48,leftMargin=48,topMargin=60,bottomMargin=54,title=pub['title'])
    story=[Paragraph(BRAND_NAME,styles['SCBrand']),
           Paragraph(escape(BRAND_LINE+' / '+_publication_label(pub)),styles['SCType']),
           Paragraph(escape(pub['title']),styles['Title']),Spacer(1,10),
           Paragraph('Saved revision '+str(pub['revision'])+' · Scientific verification not performed',styles['SCCaption'])]
    for block in _publication_blocks(pub):
        k=block['kind']
        if k=='heading':story.append(Paragraph(_pdf_inline(block['text']),styles['Heading1' if block['level']<=2 else 'Heading2']))
        elif k=='paragraph':story.append(Paragraph(_pdf_inline(block['text']),styles['SCBody']))
        elif k=='reference':story.append(Paragraph(_pdf_inline(block['text']),styles['SCReference']))
        elif k=='quote':story.append(Paragraph(_pdf_inline(block['text']),styles['SCBody']))
        elif k in ('code','math'):story.append(Preformatted(block['text'][:4000],styles['Code']))
        elif k=='list':
            story.append(KeepTogether([Paragraph((f'{n}.' if block.get('ordered') else '&#8226;')+' '+_pdf_inline(item),styles['SCBody'])
                                       for n,item in enumerate(block['items'],block.get('start',1))]))
        elif k=='table':
            rows=[block['headers']]+block['rows']
            data=[[Paragraph(_pdf_inline(v[:600]),styles['Normal']) for v in row] for row in rows[:101]]
            ncols=len(block['headers']);data=[(r+['']*ncols)[:ncols] for r in data]
            t=Table(data,repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('GRID',(0,0),(-1,-1),.3,colors.grey),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e6eee9')),('VALIGN',(0,0),(-1,-1),'TOP')]))
            story.append(t);story.append(Spacer(1,12))
        elif k=='figure':
            raw=figure_bytes.get(block['assetId'])
            if raw:
                story.append(_pdf_svg_image(raw) if raw.lstrip()[:1]==b'<' else _pdf_raster_image(raw))
            else:story.append(Paragraph('[Figure source unavailable]',styles['SCCaption']))
            story.append(Paragraph(_pdf_inline(block['caption']),styles['SCCaption']))
    def draw_footer(canvas, document):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor(BRAND_RED))
        canvas.line(48, 39, A4[0]-48, 39)
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#555555'))
        canvas.drawString(48, 27, BRAND_NAME+' · '+_publication_label(pub))
        canvas.drawRightString(A4[0]-48, 27, 'Revision '+str(pub['revision'])+' · Page '+str(document.page))
        canvas.restoreState()
    doc.build(story,onFirstPage=draw_footer,onLaterPages=draw_footer)
    return out.getvalue()


def _docx_link(para, text: str, url: str, bold=False, italic=False):
    """A real Word hyperlink (external relationship), not URL text."""
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.opc.constants import RELATIONSHIP_TYPE
    rid=para.part.relate_to(url,RELATIONSHIP_TYPE.HYPERLINK,is_external=True)
    link=OxmlElement('w:hyperlink');link.set(qn('r:id'),rid)
    run=OxmlElement('w:r');props=OxmlElement('w:rPr')
    style=OxmlElement('w:rStyle');style.set(qn('w:val'),'Hyperlink');props.append(style)
    colour=OxmlElement('w:color');colour.set(qn('w:val'),'B00020');props.append(colour)
    for flag,on in (('w:b',bold),('w:i',italic)):
        if on:props.append(OxmlElement(flag))
    run.append(props);t=OxmlElement('w:t');t.text=text;t.set(qn('xml:space'),'preserve');run.append(t)
    link.append(run);para._p.append(link)


def _docx_rich(doc, content: str, style: str | None = None, para=None):
    para=para if para is not None else doc.add_paragraph(style=style)
    parked=_park(content)
    pattern=re.compile(r'(\[[^\]\n]{1,400}\]\((?:https?://|mailto:)[^\s()<>"]{1,2000}\)|https?://[^\s<>"]{2,2000}[^\s<>".,;:!?)\]\ue000-\ue07f]'
                       r'|\*\*\*[^*]+\*\*\*|\*\*[^*]+\*\*|(?<!\*)\*[^*]+\*(?!\*)|`[^`]+`)')
    for part in pattern.split(parked):
        if not part:continue
        link=_LINK.fullmatch(part)
        if link:
            inner=link.group(1);b=inner.startswith('**');i=inner.startswith('***') or (inner.startswith('*') and not b)
            _docx_link(para,_unpark(inner.strip('*'),False),_unpark(link.group(2),False),b,i)
        elif re.fullmatch(r'https?://\S+',part):_docx_link(para,_unpark(part,False),_unpark(part,False))
        elif part.startswith('***') and part.endswith('***'):
            run=para.add_run(_unpark(part[3:-3],False));run.bold=True;run.italic=True
        elif part.startswith('**') and part.endswith('**'):
            para.add_run(_unpark(part[2:-2],False)).bold=True
        elif part.startswith('*') and part.endswith('*') and len(part)>2:
            para.add_run(_unpark(part[1:-1],False)).italic=True
        elif part.startswith('`') and part.endswith('`'):
            run=para.add_run(_unpark(part[1:-1],False));run.font.name='Consolas'
        else:para.add_run(_unpark(part,False))
    return para


def _docx(pub:dict,figure_bytes:dict[str,bytes]):
    from docx import Document
    from docx.shared import Inches,Pt
    doc=Document()
    normal=doc.styles['Normal']
    normal.font.name='Aptos'
    normal.font.size=Pt(10.5)
    section=doc.sections[0]
    header=section.header.paragraphs[0]
    header.text=BRAND_NAME+'  |  '+BRAND_LINE
    header.style=doc.styles['Header']
    if header.runs:
        header.runs[0].bold=True
        header.runs[0].font.color.rgb=__import__('docx').shared.RGBColor(176,0,32)
    footer=section.footer.paragraphs[0]
    footer.text=BRAND_NAME+' · '+_publication_label(pub)+' · Saved revision '+str(pub['revision'])
    footer.style=doc.styles['Footer']
    doc.add_paragraph(_publication_label(pub).upper(),style='Subtitle')
    doc.add_heading(pub['title'],0)
    doc.add_paragraph('Saved revision '+str(pub['revision'])+' · Scientific verification not performed')
    for block in _publication_blocks(pub):
        k=block['kind']
        if k=='heading':
            heading=doc.add_heading('',level=min(block['level'],4));_docx_rich(doc,block['text'],para=heading)
        elif k=='paragraph':_docx_rich(doc,block['text'])
        elif k=='reference':
            entry=_docx_rich(doc,block['text'])
            entry.paragraph_format.left_indent=Inches(0.5);entry.paragraph_format.first_line_indent=Inches(-0.5)
        elif k=='quote':_docx_rich(doc,block['text'],'Quote')
        elif k in ('code','math'):doc.add_paragraph(block['text'],style='Normal')
        elif k=='list':
            for item in block['items']:_docx_rich(doc,item,'List Number' if block.get('ordered') else 'List Bullet')
        elif k=='table':
            cols=len(block['headers']);t=doc.add_table(rows=1,cols=cols);t.style='Table Grid'
            for i,v in enumerate(block['headers']):
                cell=t.rows[0].cells[i].paragraphs[0];_docx_rich(doc,v,para=cell)
                for run in cell.runs:run.bold=True
            for row in block['rows']:
                cells=t.add_row().cells
                for i,v in enumerate(row[:cols]):_docx_rich(doc,v,para=cells[i].paragraphs[0])
        elif k=='figure':
            raw=figure_bytes.get(block['assetId'])
            if raw and raw.lstrip()[:1]!=b'<':
                doc.add_picture(BytesIO(raw),width=Inches(6.0))
            elif raw:
                try:
                    import cairosvg
                    png=cairosvg.svg2png(bytestring=raw,output_width=1100)
                    doc.add_picture(BytesIO(png),width=Inches(6.0))
                except Exception:
                    doc.add_paragraph('[Preserved SVG figure; embedding unavailable]')
            else:doc.add_paragraph('[Figure source unavailable]')
            doc.add_paragraph(_unpark(_park(block['caption']),False),style='Caption')
    buf=BytesIO();doc.save(buf);return buf.getvalue()


@router.get('/projects/{project_id}/documents/{document_id}/export.{format}')
def export_publication(project_id:str,document_id:str,format:str,request:Request,revision:int|None=None):
    if format not in ('html','pdf','docx'):raise HTTPException(404,'Format unsupported.')
    owner=_subject(request)
    with session_scope() as db:
        _,pub=_saved(db,owner,project_id,document_id,revision)
        expected={x['artifactId']:x['sha256'] for x in pub.get('figureSources',[])}
        figures,media_types={},{}
        for aid,digest in expected.items():
            meta,raw=_original_asset(db,owner,project_id,aid)
            if meta['sha256']!=digest:raise HTTPException(409,'Saved figure source hash changed.')
            media_types[aid],figures[aid]=figure_payload(meta['filename'],raw)
        sco.verify_pins(db,owner,project_id,pub,_original_asset)
        if pub.get('source'):
            source_id=pub['source']['artifactId'];meta,_=_original_asset(db,owner,project_id,source_id)
            if meta['sha256']!=pub['source']['sha256']:
                raise HTTPException(409,'Original manuscript hash changed.')
    if format=='html':
        uri={k:'data:'+media_types[k]+';base64,'+base64.b64encode(v).decode('ascii') for k,v in figures.items()}
        data=_as_html(pub,uri); media='text/html; charset=utf-8'
    elif format=='pdf':
        try:data=_pdf(pub,figures)
        except ImportError as exc:raise HTTPException(503,'PDF export dependencies not installed.') from exc
        media='application/pdf'
    else:
        try:data=_docx(pub,figures)
        except ImportError as exc:raise HTTPException(503,'DOCX export dependencies not installed.') from exc
        media='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    filename='scientific-publication-v'+str(pub['revision'])+'.'+format
    return Response(data,media_type=media,headers={**HEADERS,'Content-Disposition':f'attachment; filename="{filename}"',
                'X-Publication-Revision-SHA256':pub['markdownSHA256'],
                 'X-Publication-Layout-Status':layout.audit_layout(pub['markdown'],pub['title'])['status'],
                'Content-Security-Policy':"sandbox" if format=='html' else "default-src 'none'"})


# UCD-RESEARCH-01: Studio -> Research bridge. Read-only: it states an exact saved revision as a Research editorial
# revision payload, which the owner then submits to Research with their own signed session. Nothing is sent from here.
RESEARCH_PUBLICATION_TYPES = ('report','working-paper','policy-brief','interactive-analysis')
RESEARCH_MAX_SECTIONS = 40
FIGURE_LINE = re.compile(r'^!\[([^\]]{0,160})\]\(asset:[A-Za-z0-9_.-]{1,160}\)$')


def research_sections(markdown: str, title: str) -> tuple[list[dict], int]:
    """Split at level-1/2 headings. Workspace figures are not carried: they reach Research only as pinned, released
    figure objects, so each one is replaced by a visible placeholder and counted."""
    sections, heading, body, figures = [], None, [], 0
    for line in markdown.replace('\r\n','\n').replace('\r','\n').split('\n'):
        match = re.match(r'^(#{1,2})\s+(.*\S)\s*$', line)
        if match:
            if heading is not None or ''.join(body).strip():
                sections.append({'heading': heading or 'Overview', 'body': '\n'.join(body).strip()})
            heading, body = match.group(2)[:300], []
            continue
        figure = FIGURE_LINE.fullmatch(line.strip())
        if figure:
            figures += 1
            line = f'*[Figure: {figure.group(1) or "untitled"}. Not yet released to Research.]*'
        body.append(line)
    if heading is not None or ''.join(body).strip():
        sections.append({'heading': heading or 'Overview', 'body': '\n'.join(body).strip()})
    if sections and sections[0]['heading'] == title:  # the manuscript's own title line; Research holds the title
        sections = sections[1:] if not sections[0]['body'] else [{**sections[0], 'heading': 'Overview'}, *sections[1:]]
    if not sections:
        raise HTTPException(422,'The manuscript has no text to submit.')
    if len(sections) > RESEARCH_MAX_SECTIONS:
        raise HTTPException(422,f'Research articles hold at most {RESEARCH_MAX_SECTIONS} sections; '
                                'merge sections before submitting.')
    return sections, figures


def research_revision(project_id: str, pub: dict, publication_type: str, summary: str = '') -> dict:
    if publication_type not in RESEARCH_PUBLICATION_TYPES:
        raise HTTPException(422,'Choose a publication type: '+', '.join(RESEARCH_PUBLICATION_TYPES)+'.')
    # Markers stay in the text so the revision remains editable; the bibliography carries what each one renders as.
    sections, figures = research_sections(pub['markdown'], pub['title'])
    publication = {'type': publication_type, 'derivedFrom': [{
        'relation': 'derived-from', 'kind': 'workspace-studio-revision', 'workspaceProjectId': project_id,
        'documentId': pub['documentId'], 'revision': pub['revision'], 'documentSha256': pub['markdownSHA256'],
        'label': f"Reporting Studio revision {pub['revision']}"}]}
    bibliography = cite.bibliography_record(pub.get('citations'), [s['body'] for s in sections])
    if bibliography:
        publication['bibliography'] = bibliography
    return {'schema': 'sc-studio-research-revision/1.0', 'title': pub['title'], 'summary': summary,
            'sections': sections, 'references': [], 'publication': publication,
            'changeSummary': f"From Reporting Studio revision {pub['revision']} ({pub['markdownSHA256'][:12]})",
            'notCarried': {'figures': figures, 'unresolvedCitations': list((pub.get('citations') or {}).get('unresolved') or []),
                           'scientificStatus': pub.get('scientificStatus'), 'rightsStatus': pub.get('rightsStatus')}}


@router.get('/projects/{project_id}/documents/{document_id}/research-revision')
def research_revision_route(project_id:str,document_id:str,request:Request,revision:int,publicationType:str):
    owner=_subject(request)
    with session_scope() as db:
        _,pub=_saved(db,owner,project_id,document_id,revision)
    return JSONResponse(research_revision(project_id,pub,publicationType),headers=HEADERS)


# SC-CITE-01: Citation Studio, with this Studio's owner, origin and project-revision gates.
def _store_collection(db, owner, row, project, operation):
    payload=ProjectStoreRequest.model_validate({'schema':'sc-workspace-sync-push/1.0','sourceProjectId':row.project_id,
       'projectTitle':row.title,'expectedRevision':row.revision,'operationId':operation,'project':project})
    updated,_=repository.store_project(db,owner,payload)
    return updated


def _library_record(record_id:str)->dict:
    from .library_discovery_v3841 import verified_public_reference,_fetch
    verified_public_reference(record_id)  # published, public, complete provenance; otherwise 404/502/503
    return _fetch('/api/library/v1/research-objects/'+quote(record_id,safe=''),{'include_body':'false'})


def _library_search(q:str)->dict:
    from .library_discovery_v3841 import discover
    return discover(q)


# SC-PUB-ENDTOEND-01: Outputs & Publishing drives Research's editorial lifecycle for this Studio's saved revisions.
from . import research_outputs as outputs
router.include_router(outputs.build_router({'subject':_subject,'write':_write,'project':_project,
    'locked_project':_locked_project,'session':session_scope,'headers':HEADERS,'saved':_saved,
    'store':_store_collection,'research_revision':research_revision,
    'documents':lambda package:[{**d,**{k:s.get(k) for s in snapshots(package,d['documentId'])[-1:]
                                          for k in ('publicationType','scientificStatus','rightsStatus','markdownSHA256','source')}}
                                 for d in latest_documents(package)]}))
router.include_router(sco.build_router({'subject':_subject,'write':_write,'project':_project,
    'locked_project':_locked_project,'store':_store_collection,'session':session_scope,'headers':HEADERS,
    'original_asset':_original_asset,'sanitize_svg':sanitize_svg}))
router.include_router(cite.build_router({'subject':_subject,'write':_write,'project':_project,
    'locked_project':_locked_project,'original_asset':_original_asset,'store':_store_collection,'session':session_scope,
    'headers':HEADERS,'library_record':_library_record,'library_search':_library_search}))
