from __future__ import annotations
import base64, json
from datetime import datetime, timezone
from typing import Any, Callable
from uuid import uuid4
import httpx
from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from .config import get_settings
from .models import InterchangeReceipt
from .object_store import get_artifact, read_artifact_content, store_artifact
from .registry import store_run_output
from .schemas import ArtifactStoreRequest, ExecutionRunOutputRequest

OPERATIONS=(
 "workspace.interchange.arrow-ipc.write","workspace.interchange.parquet.write",
 "workspace.interchange.arrow-ipc.read","workspace.interchange.parquet.read",
 "workspace.interchange.convert.arrow-to-parquet","workspace.interchange.convert.parquet-to-arrow",
 "workspace.interchange.verify","workspace.interchange.schema",
)
ProgressCallback=Callable[[int,dict[str,Any]],bool]

def operation_catalog(): return [{"operation":x,"runtime":"arrow-parquet-interchange","serverConfiguredOnly":True,"arbitraryCode":False} for x in OPERATIONS]
def runtime_health():
 s=get_settings(); url=s.runtime_interchange_url.strip()
 if not url: return {"configured":False,"available":False,"runtime":"arrow-parquet-interchange"}
 health=url[:-len('/v1/execute')]+'/health' if url.endswith('/v1/execute') else url.rstrip('/')+'/health'
 try: r=httpx.get(health,timeout=min(s.interchange_timeout_seconds,5.0))
 except httpx.HTTPError as exc: return {"configured":True,"available":False,"error":exc.__class__.__name__}
 try: body=r.json()
 except ValueError: body={}
 return {"configured":True,"available":200<=r.status_code<300 and body.get('ok') is True,"httpStatus":r.status_code,"service":body.get('service',''),"version":body.get('version',''),"runtime":body.get('runtime',''),"pyarrowVersion":body.get('pyarrowVersion',''),"operations":body.get('operations',[]),"boundedOperationsOnly":True,"arbitraryCodeExecution":False}

def _format_for_artifact(row)->str:
 if row.media_type in {'application/vnd.apache.arrow.stream','application/vnd.apache.arrow.file'}: return 'arrow-ipc-stream'
 if row.media_type=='application/vnd.apache.parquet': return 'parquet'
 return ''

def execute_interchange_operation(db:Session,row,progress_callback:ProgressCallback|None=None)->dict[str,Any]:
 if row.operation not in OPERATIONS: raise HTTPException(status_code=400,detail='Interchange operation is not registered')
 s=get_settings(); url=s.runtime_interchange_url.strip(); token=s.runtime_interchange_token.strip()
 if not url: raise HTTPException(status_code=409,detail='Arrow/Parquet interchange runtime is not configured')
 payload=dict(((row.payload or {}).get('payload') or {})); source_artifact_id=str(payload.get('artifactId') or '').strip(); source_sha=''
 if source_artifact_id:
  art=get_artifact(db,row.user_key,source_artifact_id)
  if art is None: raise HTTPException(status_code=404,detail='Interchange source artifact not found')
  raw=read_artifact_content(art); source_sha=art.sha256
  payload['contentBase64']=base64.b64encode(raw).decode('ascii'); payload.setdefault('format',_format_for_artifact(art))
  if not payload.get('format'): raise HTTPException(status_code=400,detail='Interchange source artifact media type is not Arrow or Parquet')
 if progress_callback: progress_callback(20,{"stage":"interchange-runtime-selected"})
 envelope={"schema":"sc-workspace-interchange-execution-envelope/1.0","workspaceVersion":s.service_version,"jobId":row.job_id,"operation":row.operation,"payload":payload,"serverConfiguredOnly":True,"arbitraryCodeExecution":False}
 headers={'Content-Type':'application/json','Accept':'application/json'}
 if token: headers['Authorization']=f'Bearer {token}'
 try: resp=httpx.post(url,json=envelope,headers=headers,timeout=s.interchange_timeout_seconds)
 except httpx.HTTPError as exc: raise HTTPException(status_code=502,detail=f'Interchange runtime transport failed: {exc.__class__.__name__}') from exc
 if not 200<=resp.status_code<300: raise HTTPException(status_code=502,detail=f'Interchange runtime returned HTTP {resp.status_code}')
 body=resp.json(); result=body.get('result') if isinstance(body,dict) else {}; result=result if isinstance(result,dict) else {}
 if progress_callback: progress_callback(70,{"stage":"interchange-runtime-complete"})
 binary_b64=result.pop('contentBase64',None); binary_artifact=None
 if binary_b64:
  fmt=str(result.get('format') or ''); ext='parquet' if fmt=='parquet' else 'arrow'; media='application/vnd.apache.parquet' if fmt=='parquet' else 'application/vnd.apache.arrow.stream'
  aid=f'interchange-{row.job_id}-{ext}'
  existing=get_artifact(db,row.user_key,aid)
  binary_artifact=store_artifact(db,row.user_key,ArtifactStoreRequest.model_validate({'schema':'sc-workspace-artifact-store/1.0','artifactId':aid,'projectId':row.project_id or None,'filename':f'{aid}.{ext}','mediaType':media,'contentBase64':binary_b64,'expectedRevision':existing.revision if existing else 0,'metadata':{'kind':'native-interchange','format':fmt,'operation':row.operation,'jobId':row.job_id,'schemaFingerprint':((result.get('descriptor') or {}).get('schemaFingerprint') or '')}}))
 result_doc={"schema":"sc-workspace-native-interchange-result/1.0","runtime":"arrow-parquet-interchange","operation":row.operation,"result":result,"binaryArtifactId":binary_artifact.artifact_id if binary_artifact else ''}
 raw_json=json.dumps(result_doc,sort_keys=True,separators=(',',':'),ensure_ascii=False,default=str).encode()
 if len(raw_json)>s.compute_max_result_bytes: raise HTTPException(status_code=413,detail='Interchange result metadata exceeds limit')
 result_id=f'interchange-result-{row.job_id}'; existing=get_artifact(db,row.user_key,result_id)
 result_art=store_artifact(db,row.user_key,ArtifactStoreRequest.model_validate({'schema':'sc-workspace-artifact-store/1.0','artifactId':result_id,'projectId':row.project_id or None,'filename':f'{result_id}.json','mediaType':'application/vnd.sc.workspace.interchange-result+json','contentBase64':base64.b64encode(raw_json).decode('ascii'),'expectedRevision':existing.revision if existing else 0,'metadata':{'kind':'interchange-result','operation':row.operation,'jobId':row.job_id}}))
 run_id=str(((row.payload or {}).get('executionRunId') or '')).strip()
 if run_id:
  store_run_output(db,row.user_key,run_id,ExecutionRunOutputRequest.model_validate({'schema':'sc-workspace-execution-run-output/1.0','outputId':'interchange-result','artifactId':result_art.artifact_id,'role':'result','label':'Native interchange result','mediaType':result_art.media_type,'sha256':result_art.sha256,'bytes':result_art.bytes,'metadata':{'operation':row.operation}}))
 count=int(db.scalar(select(func.count()).select_from(InterchangeReceipt).where(InterchangeReceipt.user_key==row.user_key)) or 0)
 if count>=s.max_interchange_receipts_per_account: raise HTTPException(status_code=409,detail='Interchange receipt limit reached')
 desc=result.get('descriptor') if isinstance(result.get('descriptor'),dict) else {}
 rec=InterchangeReceipt(receipt_id=f'ixr_{uuid4().hex}',user_key=row.user_key,job_id=row.job_id,execution_run_id=run_id,operation=row.operation,source_format=str(result.get('sourceFormat') or payload.get('format') or '')[:64],result_format=str(result.get('format') or payload.get('format') or '')[:64],source_artifact_id=source_artifact_id[:160],result_artifact_id=(binary_artifact.artifact_id if binary_artifact else result_art.artifact_id),source_sha256=str(result.get('sourceSha256') or source_sha)[:64],result_sha256=(binary_artifact.sha256 if binary_artifact else str(result.get('sha256') or result_art.sha256))[:64],schema_fingerprint=str(desc.get('schemaFingerprint') or '')[:64],row_count=int(desc.get('rowCount') or 0),column_count=int(desc.get('columnCount') or 0),verified=bool(result.get('verified',False)),details_json={'runtime':'arrow-parquet-interchange','resultMetadataArtifactId':result_art.artifact_id,'boundedOperationsOnly':True,'arbitraryCodeExecution':False})
 db.add(rec); db.commit(); db.refresh(rec)
 if progress_callback: progress_callback(95,{"stage":"interchange-persisted","receiptId":rec.receipt_id})
 return {"schema":"sc-workspace-job-result/1.0","interchange":result_doc,"resultArtifactId":result_art.artifact_id,"binaryArtifactId":binary_artifact.artifact_id if binary_artifact else '',"interchangeReceiptId":rec.receipt_id,"resultSha256":rec.result_sha256}

def receipt_metadata(r:InterchangeReceipt)->dict[str,Any]: return {"receiptId":r.receipt_id,"jobId":r.job_id,"executionRunId":r.execution_run_id,"operation":r.operation,"sourceFormat":r.source_format,"resultFormat":r.result_format,"sourceArtifactId":r.source_artifact_id,"resultArtifactId":r.result_artifact_id,"sourceSha256":r.source_sha256,"resultSha256":r.result_sha256,"schemaFingerprint":r.schema_fingerprint,"rowCount":r.row_count,"columnCount":r.column_count,"verified":r.verified,"details":r.details_json or {},"createdAt":r.created_at.isoformat()}
def list_receipts(db:Session,user_key:str,limit:int=100): return [receipt_metadata(x) for x in db.scalars(select(InterchangeReceipt).where(InterchangeReceipt.user_key==user_key).order_by(InterchangeReceipt.created_at.desc()).limit(limit)).all()]
def get_receipt(db:Session,user_key:str,receipt_id:str): return db.execute(select(InterchangeReceipt).where(InterchangeReceipt.user_key==user_key,InterchangeReceipt.receipt_id==receipt_id)).scalar_one_or_none()
