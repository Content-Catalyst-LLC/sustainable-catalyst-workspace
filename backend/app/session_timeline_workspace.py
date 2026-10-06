from __future__ import annotations
from typing import Any
from sqlalchemy.orm import Session
from .registry import list_execution_runs, list_run_events
from .execution_provenance import list_snapshots as list_execution_snapshots
from .research_session_bindings import project_binding_state
from .platform_core_runtime import list_receipts as list_core_receipts
from .unified_research_context import list_snapshots as list_context_snapshots
from .visual_research_workspace import list_snapshots as list_visual_snapshots

SCHEMA="sc-workspace-session-timeline-provenance/1.0"

def profile()->dict[str,Any]:
    return {"schema":SCHEMA,"version":"3.79.0","release":"Session Timeline & Provenance",
    "backendAuthoritative":True,"chronologicalProjection":True,"projectScoped":True,
    "executionEvents":True,"executionSnapshots":True,"researchSessionBindings":True,
    "platformCoreReceipts":True,"unifiedContextSnapshots":True,"visualResearchSnapshots":True,
    "fingerprintVisibility":True,"sourceAuthorityPreserved":True,"genericMutation":False,
    "automaticCausalityInference":False,"automaticNarrativeSelection":False,"databaseMigrationRequired":False}

def _timestamp(item:dict[str,Any])->str:
    for key in ("createdAt","updatedAt","startedAt","finishedAt","acceptedAt"):
        value=item.get(key)
        if value:return str(value)
    return ""

def _event(kind:str,item:dict[str,Any],title:str="",object_id:str="",status:str="",fingerprint:str="")->dict[str,Any]:
    return {"kind":kind,"timestamp":_timestamp(item),"title":title or kind,"objectId":object_id,
    "status":status,"fingerprint":fingerprint,"sourceAuthority":kind,"payload":item}

def timeline(db:Session,user_key:str,project_id:str,limit:int=500)->dict[str,Any]:
    events=[]
    runs=list_execution_runs(db,user_key,None,project_id,250)
    for run in runs:
        rid=str(run.get("runId") or "")
        events.append(_event("execution-run",run,str(run.get("name") or rid),rid,str(run.get("status") or ""),
        str(run.get("reproducibilityFingerprint") or run.get("inputFingerprint") or "")))
        for evt in list_run_events(db,user_key,rid):
            x=dict(evt);x["runId"]=rid
            events.append(_event("execution-event",x,str(evt.get("eventType") or "execution event"),rid,str(evt.get("status") or ""),""))
    for snap in list_execution_snapshots(db,user_key,project_id,100):
        events.append(_event("execution-provenance-snapshot",snap,"Execution provenance snapshot",
        str(snap.get("snapshotId") or ""),"",str(snap.get("provenanceFingerprint") or "")))
    bindings=project_binding_state(db,user_key,project_id)
    for binding in bindings.get("bindings") or []:
        events.append(_event("research-session-binding",binding,str(binding.get("bindingType") or "Research session binding"),
        str(binding.get("bindingId") or binding.get("objectId") or binding.get("workspaceRef") or ""),
        str(binding.get("status") or ""),str(binding.get("objectFingerprint") or binding.get("workspaceFingerprint") or "")))
    for receipt in list_core_receipts(db,user_key,project_id,250):
        events.append(_event("platform-core-receipt",receipt,str(receipt.get("action") or "Platform Core receipt"),
        str(receipt.get("receiptId") or ""),str(receipt.get("status") or ""),str(receipt.get("fingerprint") or "")))
    for snap in list_context_snapshots(db,user_key,project_id,100):
        events.append(_event("unified-context-snapshot",snap,"Unified research context snapshot",
        str(snap.get("snapshotId") or ""),"",str(snap.get("contextFingerprint") or snap.get("fingerprint") or "")))
    for snap in list_visual_snapshots(db,user_key,project_id,100):
        events.append(_event("visual-research-snapshot",snap,"Visual research snapshot",
        str(snap.get("snapshotId") or ""),"",str(snap.get("workspaceFingerprint") or snap.get("fingerprint") or "")))
    events.sort(key=lambda x:(str(x.get("timestamp") or ""),str(x.get("kind") or ""),str(x.get("objectId") or "")),reverse=True)
    events=events[:max(1,min(limit,1000))]
    counts={}
    for event in events:
        k=str(event.get("kind") or "unknown");counts[k]=counts.get(k,0)+1
    return {"schema":SCHEMA,"version":"3.79.0","projectId":project_id,
    "sessionBound":bool(bindings.get("sessionBound")),"coreSessionId":str(bindings.get("coreSessionId") or ""),
    "events":events,"count":len(events),"counts":counts,"sourceAuthorityPreserved":True,
    "automaticCausalityInference":False,"automaticNarrativeSelection":False}
