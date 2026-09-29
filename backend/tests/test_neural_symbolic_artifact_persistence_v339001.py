from __future__ import annotations
import base64, json, pathlib, sys
from types import SimpleNamespace
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from app.schemas import ArtifactStoreRequest

POLYGLOT=ROOT/'app'/'polyglot.py'


def _payload(blob: dict, row, existing=None):
    raw=json.dumps(blob,sort_keys=True,separators=(",",":"),ensure_ascii=False,default=str).encode()
    prefix='neural-symbolic-inference'
    return ArtifactStoreRequest.model_validate({
        'schema':'sc-workspace-artifact-store/1.0',
        'artifactId':f'{prefix}-{row.job_id}',
        'projectId':row.project_id or None,
        'filename':f'{prefix}-{row.job_id}.json',
        'mediaType':'application/vnd.sc.workspace.neural-symbolic-inference+json',
        'contentBase64':base64.b64encode(raw).decode('ascii'),
        'expectedRevision':existing.revision if existing is not None else 0,
        'metadata':{
            'kind':blob.get('kind'),'language':'neural','operation':row.operation,'jobId':row.job_id,
            'runtime':'python-pytorch-neural','artifactFingerprint':blob.get('artifactFingerprint'),
            'role':'analysis','truthValueAssigned':False,'isObservedEvidence':False,
        },
    })


def test_current_artifact_store_contract_round_trip():
    row=SimpleNamespace(job_id='job-repair',project_id='project-1',operation='workspace.neural.neural-symbolic-infer')
    blob={'schema':'sc-workspace-neural-symbolic-inference-artifact/1.0','kind':'neural-symbolic-inference','artifactFingerprint':'fp-1','truthValueAssigned':False,'isObservedEvidence':False}
    req=_payload(blob,row)
    data=req.model_dump(by_alias=True)
    assert data['schema']=='sc-workspace-artifact-store/1.0'
    assert data['artifactId']=='neural-symbolic-inference-job-repair'
    assert data['expectedRevision']==0
    assert json.loads(base64.b64decode(data['contentBase64']))==blob
    assert data['metadata']['truthValueAssigned'] is False
    assert data['metadata']['isObservedEvidence'] is False


def test_existing_artifact_revision_is_reused():
    row=SimpleNamespace(job_id='job-repair',project_id='',operation='workspace.neural.neural-symbolic-infer')
    blob={'schema':'sc-workspace-neural-symbolic-inference-artifact/1.0','kind':'neural-symbolic-inference'}
    req=_payload(blob,row,SimpleNamespace(revision=7))
    assert req.expectedRevision==7
    assert req.projectId is None


def test_polyglot_no_longer_uses_obsolete_symbolic_store_request():
    source=POLYGLOT.read_text()
    assert 'sc-workspace-artifact-store-request/1.0' not in source
    assert 'existing_symbolic=get_artifact' in source
    assert 'workspaceNeuralSymbolicArtifact' in source
