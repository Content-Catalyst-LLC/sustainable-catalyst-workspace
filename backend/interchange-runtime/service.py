from __future__ import annotations
import base64, hashlib, io, json, os
from typing import Any
from fastapi import FastAPI, Header, HTTPException

SERVICE="Sustainable Catalyst Workspace Arrow/Parquet Interchange Runtime"
SERVICE_VERSION="2.16.0"
RUNTIME="arrow-parquet-interchange"
OPERATIONS=(
 "workspace.interchange.arrow-ipc.write","workspace.interchange.parquet.write",
 "workspace.interchange.arrow-ipc.read","workspace.interchange.parquet.read",
 "workspace.interchange.convert.arrow-to-parquet","workspace.interchange.convert.parquet-to-arrow",
 "workspace.interchange.verify","workspace.interchange.schema",
)
TOKEN=os.getenv("SC_WORKSPACE_INTERCHANGE_RUNTIME_TOKEN","").strip()
MAX_PAYLOAD=int(os.getenv("SC_WORKSPACE_INTERCHANGE_MAX_PAYLOAD_BYTES","26214400"))
MAX_ROWS=int(os.getenv("SC_WORKSPACE_INTERCHANGE_MAX_ROWS","50000"))
MAX_COLS=int(os.getenv("SC_WORKSPACE_INTERCHANGE_MAX_COLUMNS","256"))
app=FastAPI(title=SERVICE,version=SERVICE_VERSION,docs_url=None,redoc_url=None)

def _pa():
 import pyarrow as pa
 import pyarrow.parquet as pq
 return pa,pq

def _auth(value:str|None):
 if TOKEN and value != f"Bearer {TOKEN}": raise HTTPException(status_code=401,detail="Invalid interchange runtime credential")

def _sha(raw:bytes)->str: return hashlib.sha256(raw).hexdigest()
def _b64(raw:bytes)->str: return base64.b64encode(raw).decode("ascii")
def _unb64(value:Any)->bytes:
 if not isinstance(value,str): raise HTTPException(status_code=400,detail="contentBase64 is required")
 try: raw=base64.b64decode(value.encode("ascii"),validate=True)
 except Exception as exc: raise HTTPException(status_code=400,detail="contentBase64 is invalid") from exc
 if len(raw)>MAX_PAYLOAD: raise HTTPException(status_code=413,detail="Interchange binary exceeds limit")
 return raw

def _rows(payload:dict[str,Any])->list[dict[str,Any]]:
 rows=payload.get("rows")
 if not isinstance(rows,list): raise HTTPException(status_code=400,detail="rows must be an array")
 if len(rows)>MAX_ROWS: raise HTTPException(status_code=413,detail="Interchange row limit exceeded")
 out=[]; cols=set()
 for row in rows:
  if not isinstance(row,dict): raise HTTPException(status_code=400,detail="Each row must be an object")
  clean={str(k)[:160]:v for k,v in row.items()}; cols.update(clean); out.append(clean)
 if len(cols)>MAX_COLS: raise HTTPException(status_code=413,detail="Interchange column limit exceeded")
 if len(json.dumps(out,separators=(",",":"),default=str).encode())>MAX_PAYLOAD: raise HTTPException(status_code=413,detail="Interchange payload limit exceeded")
 return out

def _desc(table)->dict[str,Any]:
 fields=[{"name":f.name,"arrowType":str(f.type),"nullable":bool(f.nullable)} for f in table.schema]
 canonical=json.dumps(fields,sort_keys=True,separators=(",",":"))
 return {"schema":"sc-workspace-native-arrow-table/1.0","rowCount":table.num_rows,"columnCount":table.num_columns,"columns":fields,"schemaFingerprint":_sha(canonical.encode())}

def _read(raw:bytes,fmt:str):
 pa,pq=_pa(); bio=io.BytesIO(raw)
 if fmt=="parquet": return pq.read_table(bio)
 if fmt=="arrow-ipc-stream": return pa.ipc.open_stream(bio).read_all()
 raise HTTPException(status_code=400,detail="Unsupported interchange format")

def _write(table,fmt:str)->bytes:
 pa,pq=_pa(); bio=io.BytesIO()
 if fmt=="parquet": pq.write_table(table,bio,compression="zstd",version="2.6",write_statistics=True)
 elif fmt=="arrow-ipc-stream":
  with pa.ipc.new_stream(bio,table.schema) as writer: writer.write_table(table)
 else: raise HTTPException(status_code=400,detail="Unsupported interchange format")
 raw=bio.getvalue()
 if len(raw)>MAX_PAYLOAD: raise HTTPException(status_code=413,detail="Interchange result exceeds limit")
 return raw

def _table_records(table,limit=25): return table.slice(0,min(limit,table.num_rows)).to_pylist()

@app.get("/health")
def health():
 try:
  pa,_=_pa(); pv=pa.__version__; available=True
 except Exception: pv=""; available=False
 return {"ok":available,"service":SERVICE,"version":SERVICE_VERSION,"runtime":RUNTIME,"pyarrowVersion":pv,"operations":list(OPERATIONS),"boundedOperationsOnly":True,"arbitraryCodeExecution":False}

@app.post("/v1/execute")
def execute(envelope:dict[str,Any], authorization:str|None=Header(default=None)):
 _auth(authorization)
 op=str(envelope.get("operation") or "")
 if op not in OPERATIONS: raise HTTPException(status_code=400,detail="Operation is not registered")
 payload=envelope.get("payload") if isinstance(envelope.get("payload"),dict) else {}
 pa,_=_pa(); source_format=""; result_format=""; source_sha=""
 if op.endswith(".write") or op=="workspace.interchange.schema": table=pa.Table.from_pylist(_rows(payload))
 else:
  source_format=str(payload.get("format") or ("arrow-ipc-stream" if "arrow-ipc" in op else "parquet"))
  raw=_unb64(payload.get("contentBase64")); source_sha=_sha(raw); table=_read(raw,source_format)
 if table.num_rows>MAX_ROWS or table.num_columns>MAX_COLS: raise HTTPException(status_code=413,detail="Interchange table exceeds limits")
 desc=_desc(table)
 if op=="workspace.interchange.schema": return {"ok":True,"runtime":RUNTIME,"operation":op,"result":{"kind":"schema","descriptor":desc,"verified":True}}
 if op=="workspace.interchange.verify":
  expected=str(payload.get("expectedSha256") or ""); expected_schema=str(payload.get("expectedSchemaFingerprint") or "")
  verified=(not expected or expected==source_sha) and (not expected_schema or expected_schema==desc["schemaFingerprint"])
  return {"ok":True,"runtime":RUNTIME,"operation":op,"result":{"kind":"verification","format":source_format,"sha256":source_sha,"descriptor":desc,"verified":verified}}
 if op.endswith(".read"):
  return {"ok":True,"runtime":RUNTIME,"operation":op,"result":{"kind":"read","format":source_format,"sha256":source_sha,"descriptor":desc,"recordsPreview":_table_records(table),"verified":True}}
 if op=="workspace.interchange.convert.arrow-to-parquet": result_format="parquet"
 elif op=="workspace.interchange.convert.parquet-to-arrow": result_format="arrow-ipc-stream"
 elif op=="workspace.interchange.arrow-ipc.write": result_format="arrow-ipc-stream"
 elif op=="workspace.interchange.parquet.write": result_format="parquet"
 else: raise HTTPException(status_code=400,detail="Unsupported interchange operation")
 out=_write(table,result_format)
 return {"ok":True,"runtime":RUNTIME,"operation":op,"result":{"kind":"materialized","sourceFormat":source_format,"format":result_format,"sourceSha256":source_sha,"sha256":_sha(out),"bytes":len(out),"descriptor":desc,"contentBase64":_b64(out),"recordsPreview":_table_records(table),"verified":True}}
