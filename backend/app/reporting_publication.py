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
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import text

from . import repository, object_store
from .config import get_settings
from .db import session_scope
from .schemas import ProjectStoreRequest
from .wxr_private_projects import _subject, _write, _project, _locked_project, HEADERS
from .reporting_project_catalog import read_legacy_artifacts

router = APIRouter(prefix='/publication', tags=['Scientific Publication Studio'])
SCHEMA = 'sc-scientific-publication/1.0'
MAX_MANUSCRIPT = 180_000
MAX_ASSET = 4_000_000


class Draft(BaseModel):
    model_config = ConfigDict(extra='forbid')
    title: str = Field(min_length=1, max_length=200)
    markdown: str = Field(min_length=1, max_length=MAX_MANUSCRIPT)
    sourceArtifactId: str | None = Field(default=None, max_length=160)


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
    result={}
    for obj in snapshots(package):
        result[obj['documentId']] = obj
    return [dict(documentId=x['documentId'],title=x['title'],revision=x['revision'],
                 updatedAt=x['createdAt'],projectRevision=x['projectRevision']) for x in sorted(result.values(),key=lambda obj:obj['projectRevision'],reverse=True)]


def _esc_line(line: str) -> str:
    safe=escape(line)
    safe=re.sub(r'`([^`]{1,240})`',r'<code>\1</code>',safe)
    safe=re.sub(r'\*\*([^*]{1,400})\*\*',r'<strong>\1</strong>',safe)
    safe=re.sub(r'(?<!\*)\*([^*]{1,400})\*(?!\*)',r'<em>\1</em>',safe)
    safe=re.sub(r'\[@([A-Za-z0-9_.:-]{1,80})\]',r'<span class="citation">[\1]</span>',safe)
    return safe


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
            headers=[x.strip() for x in line.strip('|').split('|')];i+=1
            rows=[]
            while i<len(lines) and lines[i].strip().startswith('|') and len(rows)<100:
                rows.append([x.strip() for x in lines[i].strip().strip('|').split('|')]); i+=1
            result.append({'kind':'table','headers':headers[:16], 'rows':rows})
        elif re.match(r'^[-*] ',line):
            items=[line[2:].strip()]
            while i<len(lines) and re.match(r'^\s*[-*] ',lines[i]):
                items.append(re.sub(r'^\s*[-*] ','',lines[i]).strip());i+=1
            result.append({'kind':'list','items':items})
        elif line.startswith('> '):
            result.append({'kind':'quote','text':line[2:]})
        else:
            parts=[line]
            while i<len(lines) and lines[i].strip() and not (lines[i].startswith(('#','```','|','> ','$$','![')) or re.match(r'^[-*] ',lines[i])):
                parts.append(lines[i].strip());i+=1
            result.append({'kind':'paragraph','text':' '.join(parts)})
    return result


def render_html(markdown: str, asset_uri=None) -> tuple[str,list[str]]:
    """Return safe body HTML and referenced figure IDs; asset URI is trusted callback."""
    out=[]; figure_ids=[]
    for node in parse_blocks(markdown):
        kind=node['kind']
        if kind=='heading':
            n=node['level'];out.append(f'<h{n}>{_esc_line(node["text"])}</h{n}>')
        elif kind=='paragraph':out.append('<p>'+_esc_line(node['text'])+'</p>')
        elif kind=='quote':out.append('<blockquote>'+_esc_line(node['text'])+'</blockquote>')
        elif kind in ('code','math'):
            out.append('<pre class="'+('equation' if kind=='math' else 'code')+'"><code>'+escape(node['text'])+'</code></pre>')
        elif kind=='list':out.append('<ul>'+''.join('<li>'+_esc_line(i)+'</li>' for i in node['items'])+'</ul>')
        elif kind=='table':
            cols=len(node['headers']);out.append('<table><thead><tr>'+''.join('<th>'+_esc_line(x)+'</th>' for x in node['headers'])+'</tr></thead><tbody>')
            for row in node['rows']:
                out.append('<tr>'+''.join('<td>'+_esc_line(x)+'</td>' for x in (row+['']*cols)[:cols])+'</tr>')
            out.append('</tbody></table>')
        elif kind=='figure':
            figure_ids.append(node['assetId'])
            cap=escape(node['caption'])
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


def sanitize_svg(raw: bytes) -> bytes:
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
    candidates=snapshots(row.package,document_id)
    if rev is not None and not any(x['revision']==rev for x in candidates):
        candidates=_historical_versions(db,owner,project_id,document_id)
    if rev is not None:candidates=[x for x in candidates if x['revision']==rev]
    if not candidates:raise HTTPException(404,'Publication not found in this project.')
    return row, candidates[-1]

def _verify_figures(db, owner, project_id, figure_ids):
    if len(figure_ids) > 12:
        raise HTTPException(413, 'A publication supports up to 12 linked figures per revision.')
    source=[]
    for aid in figure_ids:
        info,raw=_original_asset(db,owner,project_id,aid)
        if not info['filename'].lower().endswith('.svg'):
            raise HTTPException(422,'Figure ID is not an SVG research source.')
        clean=sanitize_svg(raw)
        source.append({'artifactId':aid,'sha256':info['sha256'],'bytes':len(clean)})
    return source


@router.get('',response_class=HTMLResponse)
def publication_ui(request:Request):
    _subject(request)
    script=Path(__file__).with_name('reporting_publication_ui.js').read_text()
    html=Path(__file__).with_name('reporting_publication_ui.html').read_text()
    script_hash=base64.b64encode(hashlib.sha256(script.encode()).digest()).decode()
    return HTMLResponse(html.replace('<!--SCRIPT-->', '<script>'+script+'</script>'),headers={**HEADERS,
        'Content-Security-Policy':"default-src 'none'; script-src 'sha256-"+script_hash+"'; style-src 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'"})


@router.get('/projects/{project_id}/sources/{artifact_id}')
def open_source(project_id:str,artifact_id:str,request:Request):
    owner=_subject(request)
    with session_scope() as db:
        _project(db,owner,project_id)
        meta,raw=_original_asset(db,owner,project_id,artifact_id)
    ext=meta['filename'].lower()
    if ext.endswith('.md') or ext.endswith('.txt'):
        try:content=raw.decode('utf-8-sig')
        except UnicodeError as exc:raise HTTPException(422,'Source is not UTF-8 text.') from exc
        conversion='exact-utf8-source'
    elif ext.endswith('.docx'):
        content=docx_to_markdown(raw);conversion='docx-text-extraction-not-fidelity-preserving'
    else:raise HTTPException(415,'Choose an existing Markdown, text or DOCX manuscript.')
    return JSONResponse({'source':meta,'markdown':content,'conversion':conversion,
                         'sourcePreserved':True},headers=HEADERS)


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


@router.post('/projects/{project_id}/preview')
def preview_document(project_id:str,body:Draft,request:Request):
    owner=_subject(request)
    with session_scope() as db:
        _project(db,owner,project_id)
        if body.sourceArtifactId:_source_meta(db,owner,project_id,body.sourceArtifactId)
        path='/v1/private-research/reporting-studio/publication/projects/'+quote(project_id,safe='')
        html,ids=render_html(body.markdown,lambda aid:path+'/assets/'+quote(aid,safe='')+'/svg')
        sources=_verify_figures(db,owner,project_id,ids)
    return JSONResponse({'html':html,'figures':sources,'sourceVerified':bool(body.sourceArtifactId),
                         'equations':'LaTeX source displayed, not mathematically executed',
                         'scientificValidationPerformed':False},headers=HEADERS)


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
        former=snapshots(row.package,body.documentId) if body.documentId else []
        last=former[-1] if former else None
        if (last['revision'] if last else 0)!=body.expectedDocumentRevision:
            raise HTTPException(409,'Publication revision changed. Reload before saving.')
        if body.documentId and last is None:
            raise HTTPException(404,'Publication not found in this project.')
        if last and body.sourceArtifactId!=(last.get('source') or {}).get('artifactId'):
            raise HTTPException(409,'Source cannot be changed within a publication lineage.')
        source=_source_meta(db,owner,project_id,body.sourceArtifactId)
        _,figures=render_html(body.markdown)
        figure_sources=_verify_figures(db,owner,project_id,figures)
        document_id=body.documentId or 'publication-'+uuid4().hex
        version=(last['revision']+1) if last else 1
        from datetime import datetime,timezone
        publication={'schema':SCHEMA,'documentId':document_id,'revision':version,
              'title':body.title.strip(),'markdown':body.markdown,'source':source,
              'figureSources':figure_sources,'createdAt':datetime.now(timezone.utc).isoformat(),
              'projectRevision':row.revision+1,'markdownSHA256':hashlib.sha256(body.markdown.encode()).hexdigest(),
              'scientificStatus':'unreviewed','rightsStatus':'not-redistribution-approved',
              'computationsExecuted':False,'sourceBytesModified':False}
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


@router.get('/projects/{project_id}/documents/{document_id}/history')
def document_history(project_id:str,document_id:str,request:Request):
    owner=_subject(request)
    with session_scope() as db:
        row=_project(db,owner,project_id)
        versions=_historical_versions(db,owner,project_id,document_id)
        if not versions:raise HTTPException(404,'Publication not found.')
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
    body,_=render_html(pub['markdown'],lambda aid:figures.get(aid,''))
    title=escape(pub['title'])
    css='''body{font:11pt/1.65 Georgia,serif;max-width:760px;margin:45px auto;color:#202b29;padding:0 18px}h1,h2,h3{font-family:Arial,sans-serif;color:#143b32}h1{font-size:26pt}h2{font-size:17pt;margin-top:28px}table{border-collapse:collapse;width:100%;font:9pt Arial}td,th{border:1px solid #b9c6c0;padding:7px;text-align:left}figure{text-align:center;margin:24px 0}figure img{max-width:100%}figcaption{font:9pt Arial;color:#526b63}pre{white-space:pre-wrap;background:#f3f6f4;padding:12px}.meta{font:9pt Arial;color:#526b63;border-bottom:1px solid #cedbd4;padding-bottom:16px}blockquote{border-left:3px solid #82a89c;padding-left:16px}'''
    meta=f'Saved version {pub["revision"]} · SHA-256 {pub["markdownSHA256"]} · Scientific content not independently verified'
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>'+title+'</title><style>'+css+'</style></head><body><p class="meta">'+escape(meta)+'</p><h1>'+title+'</h1>'+body+'</body></html>').encode()


def _pdf_inline(value: str) -> str:
    """Only ReportLab-supported inline tags, never raw user HTML."""
    return (_esc_line(value)
            .replace('<span class="citation">','<font color="#126b55">')
            .replace('</span>','</font>')
            .replace('<strong>','<b>').replace('</strong>','</b>')
            .replace('<em>','<i>').replace('</em>','</i>')
            .replace('<code>','<font name="Courier">').replace('</code>','</font>'))


def _pdf(pub:dict,figure_bytes:dict[str,bytes]):
    from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Preformatted,Table,TableStyle,Image,KeepTogether
    from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import A4
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='SCBody',parent=styles['BodyText'],fontSize=10.5,leading=16,spaceAfter=9))
    styles.add(ParagraphStyle(name='SCCaption',parent=styles['Normal'],fontSize=9,alignment=TA_CENTER,spaceAfter=12,textColor=colors.HexColor('#526b63')))
    out=BytesIO(); doc=SimpleDocTemplate(out,pagesize=A4,rightMargin=48,leftMargin=48,topMargin=50,bottomMargin=48,title=pub['title'])
    story=[Paragraph(escape(pub['title']),styles['Title']),Spacer(1,10),
           Paragraph('Saved revision '+str(pub['revision'])+' · Scientific verification not performed',styles['SCCaption'])]
    for block in parse_blocks(pub['markdown']):
        k=block['kind']
        if k=='heading':story.append(Paragraph(_pdf_inline(block['text']),styles['Heading1' if block['level']<=2 else 'Heading2']))
        elif k=='paragraph':story.append(Paragraph(_pdf_inline(block['text']),styles['SCBody']))
        elif k=='quote':story.append(Paragraph(escape(block['text']),styles['SCBody']))
        elif k in ('code','math'):story.append(Preformatted(block['text'][:4000],styles['Code']))
        elif k=='list':
            story.append(KeepTogether([Paragraph('&#8226; '+_pdf_inline(item),styles['SCBody']) for item in block['items']]))
        elif k=='table':
            rows=[block['headers']]+block['rows']
            data=[[Paragraph(escape(v[:300]),styles['Normal']) for v in row] for row in rows[:31]]
            ncols=len(block['headers']);data=[(r+['']*ncols)[:ncols] for r in data]
            t=Table(data,repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('GRID',(0,0),(-1,-1),.3,colors.grey),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e6eee9')),('VALIGN',(0,0),(-1,-1),'TOP')]))
            story.append(t);story.append(Spacer(1,12))
        elif k=='figure':
            raw=figure_bytes.get(block['assetId'])
            if raw:
                try:
                    from svglib.svglib import svg2rlg
                    from reportlab.graphics import renderPDF
                    drawing=svg2rlg(BytesIO(raw));
                    if drawing:
                        ratio=min(1,492/(drawing.width or 1),450/(drawing.height or 1));drawing.scale(ratio,ratio)
                        drawing.width*=ratio;drawing.height*=ratio
                        story.append(drawing)
                except Exception:
                    story.append(Paragraph('[Figure available as preserved SVG attachment]',styles['SCCaption']))
            else:story.append(Paragraph('[Figure source unavailable]',styles['SCCaption']))
            story.append(Paragraph(escape(block['caption']),styles['SCCaption']))
    doc.build(story)
    return out.getvalue()


def _docx_rich(doc, content: str, style: str | None = None):
    para=doc.add_paragraph(style=style)
    parts=re.split(r'(\*\*[^*]+\*\*|(?<!\*)\*[^*]+\*(?!\*)|`[^`]+`)',content)
    for part in parts:
        if not part:continue
        if part.startswith('**') and part.endswith('**'):
            para.add_run(part[2:-2]).bold=True
        elif part.startswith('*') and part.endswith('*'):
            para.add_run(part[1:-1]).italic=True
        elif part.startswith('`') and part.endswith('`'):
            run=para.add_run(part[1:-1]);run.font.name='Consolas'
        else:para.add_run(part)
    return para


def _docx(pub:dict,figure_bytes:dict[str,bytes]):
    from docx import Document
    from docx.shared import Inches,Pt
    doc=Document(); doc.add_heading(pub['title'],0)
    doc.add_paragraph('Saved revision '+str(pub['revision'])+' · Scientific verification not performed')
    for block in parse_blocks(pub['markdown']):
        k=block['kind']
        if k=='heading':doc.add_heading(block['text'],level=min(block['level'],4))
        elif k=='paragraph':_docx_rich(doc,block['text'])
        elif k=='quote':doc.add_paragraph(block['text'],style='Quote')
        elif k in ('code','math'):doc.add_paragraph(block['text'],style='Normal')
        elif k=='list':
            for item in block['items']:_docx_rich(doc,item,'List Bullet')
        elif k=='table':
            cols=len(block['headers']);t=doc.add_table(rows=1,cols=cols);t.style='Table Grid'
            for i,v in enumerate(block['headers']):t.rows[0].cells[i].text=v
            for row in block['rows']:
                cells=t.add_row().cells
                for i,v in enumerate(row[:cols]):cells[i].text=v
        elif k=='figure':
            raw=figure_bytes.get(block['assetId'])
            if raw:
                try:
                    import cairosvg
                    png=cairosvg.svg2png(bytestring=raw,output_width=1100)
                    doc.add_picture(BytesIO(png),width=Inches(6.0))
                except Exception:
                    doc.add_paragraph('[Preserved SVG figure; embedding unavailable]')
            else:doc.add_paragraph('[Figure source unavailable]')
            doc.add_paragraph(block['caption'],style='Caption')
    buf=BytesIO();doc.save(buf);return buf.getvalue()


@router.get('/projects/{project_id}/documents/{document_id}/export.{format}')
def export_publication(project_id:str,document_id:str,format:str,request:Request,revision:int|None=None):
    if format not in ('html','pdf','docx'):raise HTTPException(404,'Format unsupported.')
    owner=_subject(request)
    with session_scope() as db:
        _,pub=_saved(db,owner,project_id,document_id,revision)
        expected={x['artifactId']:x['sha256'] for x in pub.get('figureSources',[])}
        figures={}
        for aid,digest in expected.items():
            meta,raw=_original_asset(db,owner,project_id,aid)
            if meta['sha256']!=digest:raise HTTPException(409,'Saved figure source hash changed.')
            figures[aid]=sanitize_svg(raw)
        if pub.get('source'):
            source_id=pub['source']['artifactId'];meta,_=_original_asset(db,owner,project_id,source_id)
            if meta['sha256']!=pub['source']['sha256']:
                raise HTTPException(409,'Original manuscript hash changed.')
    if format=='html':
        uri={k:'data:image/svg+xml;base64,'+base64.b64encode(v).decode('ascii') for k,v in figures.items()}
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
                'Content-Security-Policy':"sandbox" if format=='html' else "default-src 'none'"})
