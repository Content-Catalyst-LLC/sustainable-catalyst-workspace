"""Pull an owned immutable Workbench figure into native private artifact storage."""
import base64
import hashlib
import json
import httpx
from fastapi import HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field, SecretStr
from .config import get_settings
from .wxr_private_projects import _subject, _write, _project, ResearchUpload, store_private_file
from .db import session_scope

class ScientificHandoff(BaseModel):
    model_config=ConfigDict(extra='forbid')
    sessionId:str=Field(pattern=r'^[a-f0-9-]{36}$')
    figureId:str=Field(pattern=r'^[a-f0-9-]{36}$')
    workbenchToken:SecretStr=Field(min_length=20,max_length=20000)

class WorkbenchConnection(BaseModel):
    model_config=ConfigDict(extra='forbid')
    workbenchToken:SecretStr=Field(min_length=20,max_length=20000)

def workbench_catalog(project_id:str,body:WorkbenchConnection,request:Request):
    subject=_subject(request);_write(request)
    with session_scope() as db:_project(db,subject,project_id)
    url=get_settings().route_workbench_url.rstrip('/')
    if not url:raise HTTPException(503,'Workbench integration is not configured.')
    try:
        with httpx.Client(timeout=15,follow_redirects=False,trust_env=False) as client:
            def get(path):
                with client.stream('GET',url+path,headers={'Authorization':'Bearer '+body.workbenchToken.get_secret_value()}) as r:
                    if r.status_code in (401,403):raise HTTPException(401,'Workbench authorization is unavailable or expired.')
                    if r.status_code!=200:raise HTTPException(502,'Workbench catalog is unavailable.')
                    chunks=[];size=0
                    for chunk in r.iter_bytes():
                        size+=len(chunk)
                        if size>1_000_000:raise HTTPException(413,'Workbench catalog exceeds the limit.')
                        chunks.append(chunk)
                    return json.loads(b''.join(chunks))
            figures=[]
            for project in get('/standalone/v1/projects')['projects'][:20]:
                if project.get('metadata',{}).get('workspaceProjectId')!=project_id:continue
                for session in get('/standalone/v1/projects/'+project['id']+'/research-sessions')['researchSessions'][:20]:
                    if session.get('metadata',{}).get('workspaceProjectId')!=project_id:continue
                    for figure in get('/standalone/v1/research-sessions/'+session['id']+'/scientific-figures')['figures']:
                        figures.append({'sessionId':session['id'],'figureId':figure['id'],'label':figure['label'],'sha256':figure['sha256']})
                        if len(figures)>=100:return {'figures':figures,'truncated':True}
            return {'figures':figures,'truncated':False}
    except httpx.HTTPError as exc:raise HTTPException(502,'Workbench is unavailable.') from exc
    except (KeyError,ValueError,TypeError) as exc:raise HTTPException(502,'Invalid Workbench catalog.') from exc

def import_workbench_figure(project_id:str,body:ScientificHandoff,request:Request):
    subject=_subject(request);_write(request)
    with session_scope() as db:_project(db,subject,project_id)
    url=get_settings().route_workbench_url.rstrip('/')
    if not url:raise HTTPException(503,'Workbench integration is not configured.')
    try:
        with httpx.Client(timeout=20,follow_redirects=False,trust_env=False) as client:
            with client.stream('GET',url+'/standalone/v1/research-sessions/'+body.sessionId+'/scientific-figures/'+body.figureId,
                headers={'Authorization':'Bearer '+body.workbenchToken.get_secret_value()}) as response:
                if response.status_code in (401,403,404):raise HTTPException(404,'Owned Workbench figure was not found.')
                if response.status_code!=200:raise HTTPException(502,'Workbench retrieval failed.')
                chunks=[];size=0
                for chunk in response.iter_bytes():
                    size+=len(chunk)
                    if size>2_100_000:raise HTTPException(413,'Workbench handoff exceeds the limit.')
                    chunks.append(chunk)
                receipt=json.loads(b''.join(chunks))['figure']
        metadata=receipt['metadata']
        if receipt['id']!=body.figureId or receipt['sessionId']!=body.sessionId or metadata['workspaceProjectId']!=project_id:
            raise HTTPException(409,'Scientific figure destination binding mismatch.')
        raw=base64.b64decode(metadata['contentBase64'],validate=True)
        digest=hashlib.sha256(raw).hexdigest()
        if digest!=metadata['sha256'] or metadata['libraryArtifactId']!='artifact:sha256:'+digest:
            raise HTTPException(409,'Scientific source bytes failed SHA256 verification.')
        obj=json.loads(raw)
        if obj.get('schema') not in {'sc-lab-scientific-visualization/1.0','sc-lab-source-bound-scientific-figure/1.0'}:raise ValueError()
        if obj.get('schema')=='sc-lab-source-bound-scientific-figure/1.0' and obj['spec']['project_id']!=project_id:
            raise HTTPException(409,'Scientific source project binding mismatch.')
        # Preserve canonical Lab bytes. The native adapter validates on insertion.
        return store_private_file(project_id,ResearchUpload(filename='lab-figure-'+body.figureId+'.json',contentBase64=metadata['contentBase64']),request,
            handoff={'workbenchSessionId':body.sessionId,'workbenchFigureId':body.figureId,
                     'libraryArtifactId':metadata['libraryArtifactId'],'sha256':digest,
                     'workspaceProjectId':project_id,'ownershipChecked':True})
    except httpx.HTTPError as exc:raise HTTPException(502,'Workbench is unavailable.') from exc
    except (ValueError,KeyError,TypeError) as exc:raise HTTPException(422,'Invalid scientific handoff receipt.') from exc
