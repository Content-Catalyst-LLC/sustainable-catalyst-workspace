from __future__ import annotations
from collections import Counter
from typing import Any
from sqlalchemy.orm import Session
from .registry import list_models, get_model, list_model_revisions, model_metadata, list_execution_runs
from .environments import list_environments, get_environment, list_environment_revisions, environment_metadata
from .runtime_adapters import list_adapters, get_adapter, list_adapter_revisions, adapter_metadata

SCHEMA="sc-workspace-model-runtime/1.0"
DETAIL_SCHEMA="sc-workspace-model-runtime-detail/1.0"

def profile()->dict[str,Any]:
    return {
      "schema":SCHEMA,"version":"3.77.0","release":"Model & Runtime Workspace",
      "backendAuthoritative":True,
      "modelAuthority":"workspace-model-registry",
      "environmentAuthority":"workspace-execution-environment-registry",
      "runtimeAdapterAuthority":"workspace-runtime-adapter-registry",
      "executionRunAuthority":"workspace-execution-run-registry",
      "projectScopedFiltering":True,"textSearch":True,
      "modelRevisionHistory":True,"environmentRevisionHistory":True,
      "runtimeAdapterRevisionHistory":True,"fingerprintInspection":True,
      "runtimeCompatibilityChecksAvailable":True,
      "compatibilityEndpointPattern":"/v1/runtime-adapters/{adapter_id}/compatibility",
      "executionProvenanceVisible":True,"genericMutation":False,
      "automaticModelSelection":False,"automaticRuntimeSelection":False,
      "automaticExecution":False,"databaseMigrationRequired":False
    }

def _searchable(item:dict[str,Any])->str:
    keys=("modelId","environmentId","adapterId","runId","projectId","name","description",
          "modelKind","framework","algorithm","versionLabel","executionTarget","executionOperation",
          "runtimeFamily","runtimeVersion","adapterType","trustLevel","status","operation",
          "targetProduct","metadata","tags")
    return " ".join(str(item.get(k) or "") for k in keys).casefold()

def browse(db:Session,user_key:str,project_id:str|None=None,q:str|None=None,limit:int=250)->dict[str,Any]:
    models=list_models(db,user_key,project_id)
    environments=list_environments(db,user_key,project_id)
    adapters=list_adapters(db,user_key,project_id)
    runs=list_execution_runs(db,user_key,None,project_id,min(max(1,limit),250))
    needle=(q or "").strip().casefold()
    if needle:
        models=[x for x in models if needle in _searchable(x)]
        environments=[x for x in environments if needle in _searchable(x)]
        adapters=[x for x in adapters if needle in _searchable(x)]
        runs=[x for x in runs if needle in _searchable(x)]
    return {
      "schema":SCHEMA,"version":"3.77.0","projectId":project_id or "","query":q or "",
      "models":models[:limit],"environments":environments[:limit],
      "runtimeAdapters":adapters[:limit],"recentRuns":runs[:limit],
      "counts":{"models":len(models),"environments":len(environments),"runtimeAdapters":len(adapters),"recentRuns":len(runs)},
      "facets":{
        "framework":dict(sorted(Counter(str(x.get("framework") or "unspecified") for x in models).items())),
        "runtimeFamily":dict(sorted(Counter(str(x.get("runtimeFamily") or "unspecified") for x in adapters).items())),
        "runStatus":dict(sorted(Counter(str(x.get("status") or "unspecified") for x in runs).items()))
      },
      "canonicalMutationEndpoints":{"models":"/v1/models","executionEnvironments":"/v1/execution-environments","runtimeAdapters":"/v1/runtime-adapters"},
      "automaticExecution":False
    }

def detail(db:Session,user_key:str,kind:str,object_id:str)->dict[str,Any]|None:
    kind=(kind or "").strip().lower()
    if kind=="model":
        row=get_model(db,user_key,object_id)
        if row is None:return None
        item=model_metadata(row); revs=list_model_revisions(db,user_key,object_id)
        return {"schema":DETAIL_SCHEMA,"version":"3.77.0","kind":"model","item":item,"revisions":revs,
                "revisionCount":len(revs),"fingerprint":item.get("fingerprint"),
                "executionBinding":{"target":item.get("executionTarget"),"operation":item.get("executionOperation")},
                "inputSchema":item.get("inputSchema") or {},"outputSchema":item.get("outputSchema") or {},
                "lineage":item.get("lineage") or {}}
    if kind=="environment":
        row=get_environment(db,user_key,object_id)
        if row is None:return None
        item=environment_metadata(row); revs=list_environment_revisions(db,user_key,object_id)
        return {"schema":DETAIL_SCHEMA,"version":"3.77.0","kind":"environment","item":item,"revisions":revs,
                "revisionCount":len(revs),"fingerprint":item.get("fingerprint"),
                "runtime":item.get("runtime") or {},"dependencies":item.get("dependencies") or {},
                "container":item.get("container") or {},"hardware":item.get("hardware") or {},
                "randomSeeds":item.get("randomSeeds") or {},"secretsCaptured":False}
    if kind=="adapter":
        row=get_adapter(db,user_key,object_id)
        if row is None:return None
        item=adapter_metadata(row); revs=list_adapter_revisions(db,user_key,object_id)
        return {"schema":DETAIL_SCHEMA,"version":"3.77.0","kind":"runtime-adapter","item":item,"revisions":revs,
                "revisionCount":len(revs),"fingerprint":item.get("fingerprint"),
                "capabilities":item.get("capabilities") or [],"platformConstraints":item.get("platformConstraints") or {},
                "dependencyManagers":item.get("dependencyManagers") or [],
                "compatibilityCheck":{"available":True,"method":"POST","endpoint":f"/v1/runtime-adapters/{object_id}/compatibility","executionPerformed":False},
                "arbitraryCommandExecution":False}
    return None
