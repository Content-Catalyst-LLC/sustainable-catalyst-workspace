import base64,hashlib,json
from types import SimpleNamespace
import httpx
from sqlalchemy.orm import Session
from test_research_reporting import setup,env,REPORTING
from test_wxr_private_projects import ROOT,ORIGIN
from app import reporting_scientific_handoff as handoff,session_auth

def test_verified_pull_ownership_destination_integrity(setup,monkeypatch):
    client,engine,settings,pid=setup
    monkeypatch.setattr(handoff,'session_scope',lambda:Session(engine,expire_on_commit=False))
    monkeypatch.setattr(handoff,'get_settings',lambda:SimpleNamespace(route_workbench_url='http://workbench.test'))
    sid='12345678-1234-1234-1234-123456789abc';fid='22345678-1234-1234-1234-123456789abc'
    raw=b'{"schema":"sc-lab-scientific-visualization/1.0","synthetic":true}'
    sha=hashlib.sha256(raw).hexdigest()
    receipt={'figure':{'id':fid,'sessionId':sid,'metadata':{'workspaceProjectId':pid,'sha256':sha,'libraryArtifactId':'artifact:sha256:'+sha,'contentBase64':base64.b64encode(raw).decode()}}}
    real=httpx.Client
    def upstream(req):
        assert req.headers['Authorization']=='Bearer '+'x'*32
        return httpx.Response(200,json=receipt)
    monkeypatch.setattr(handoff.httpx,'Client',lambda **kw:real(transport=httpx.MockTransport(upstream),**kw))
    target=f'{REPORTING}/projects/{pid}/workbench-figures'
    body={'sessionId':sid,'figureId':fid,'workbenchToken':'x'*32}
    assert client.post(target,json=body).status_code==403
    receipt['figure']['metadata']['workspaceProjectId']='wrong'
    assert client.post(target,json=body,headers=ORIGIN).status_code==409
    receipt['figure']['metadata']['workspaceProjectId']=pid
    receipt['figure']['metadata']['sha256']='0'*64
    assert client.post(target,json=body,headers=ORIGIN).status_code==409
    receipt['figure']['metadata']['sha256']=sha
    r=client.post(target,json=body,headers=ORIGIN)
    assert r.status_code==201,r.text
    artifact=r.json()
    assert client.get(f"{ROOT}/{pid}/files/{artifact['artifactId']}/download").content==raw
    client.cookies.set('sc_workspace_session',session_auth.issue_session_token('other'))
    assert client.post(target,json=body,headers=ORIGIN).status_code==404

def test_isolated_origin_configuration(monkeypatch):
    from app.wxr_private_projects import private_research_origin
    from fastapi import HTTPException
    import pytest
    monkeypatch.setenv('SC_WORKSPACE_PRIVATE_RESEARCH_ORIGIN','https://localhost:18765')
    monkeypatch.setenv('SC_WORKSPACE_ENVIRONMENT','development')
    assert private_research_origin()=='https://localhost:18765'
    monkeypatch.setenv('SC_WORKSPACE_ENVIRONMENT','production')
    with pytest.raises(HTTPException):private_research_origin()
