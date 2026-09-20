from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import CrossProductResearchHandoff, CrossProductResearchHandoffReceipt
from .scientific_objects import OBJECT_KINDS, get_object
from .utils import iso, sha256_hex

HANDOFF_SCHEMA="sc-workspace-research-handoff/1.0"
PRODUCTS=("workspace","knowledge-library","research-librarian","workbench","research-lab","decision-studio","site-intelligence","catalyst-data","platform-core")
INTENTS=("analyze","simulate","visualize","validate","compare","decide","publish","investigate","cite","continue-research")

class HandoffObjectRef(BaseModel):
    kind: str
    objectId: str = Field(min_length=1,max_length=160)
    revision: int|None=None
    fingerprint: str|None=None

class ResearchHandoffRequest(BaseModel):
    schema: Literal["sc-workspace-research-handoff-request/1.0"]
    handoffId: str|None=None
    projectId: str=""
    sourceProduct: str
    destinationProduct: str
    intent: str
    objects: list[HandoffObjectRef]=Field(min_length=1,max_length=100)
    context: dict[str,Any]=Field(default_factory=dict)
    @model_validator(mode="after")
    def valid(self):
        if self.sourceProduct not in PRODUCTS or self.destinationProduct not in PRODUCTS: raise ValueError("unsupported Sustainable Catalyst product")
        if self.sourceProduct==self.destinationProduct: raise ValueError("source and destination products must differ")
        if self.intent not in INTENTS: raise ValueError("unsupported handoff intent")
        for ref in self.objects:
            if ref.kind not in OBJECT_KINDS: raise ValueError(f"unsupported scientific object kind: {ref.kind}")
        return self

class ResearchHandoffAcceptRequest(BaseModel):
    schema: Literal["sc-workspace-research-handoff-accept-request/1.0"]
    destinationProduct: str
    destinationObjectId: str|None=None
    destinationReceiptId: str|None=None
    notes: dict[str,Any]=Field(default_factory=dict)

def profile():
    return {"schema":"sc-workspace-cross-product-research-handoff-fabric/1.0","backendAuthoritative":True,"browserAuthoritativeState":False,"supportedProducts":list(PRODUCTS),"supportedIntents":list(INTENTS),"scientificObjectKinds":list(OBJECT_KINDS),"revisionPinning":True,"fingerprintPinning":True,"provenancePreserved":True,"durableReceipts":True,"destinationAcceptanceReceipt":True,"genericDestinationMutation":False,"arbitraryCodeExecution":False}

def _meta(row):
    return {"schema":HANDOFF_SCHEMA,"handoffId":row.handoff_id,"projectId":row.project_id,"sourceProduct":row.source_product,"destinationProduct":row.destination_product,"intent":row.intent,"status":row.status,"packageFingerprint":row.package_fingerprint,"objects":row.object_refs_json,"context":row.context_json,"destinationResult":row.destination_result_json,"createdAt":iso(row.created_at),"acceptedAt":iso(row.accepted_at) if row.accepted_at else None}

def _receipt(row):
    return {"receiptId":row.receipt_id,"handoffId":row.handoff_id,"action":row.action,"sourceProduct":row.source_product,"destinationProduct":row.destination_product,"status":row.status,"packageFingerprint":row.package_fingerprint,"details":row.details_json,"createdAt":iso(row.created_at)}

def create_handoff(db:Session,user_key:str,payload:ResearchHandoffRequest):
    pinned=[]
    for ref in payload.objects:
        item=get_object(db,user_key,ref.kind,ref.objectId)
        if item is None: raise ValueError(f"scientific object not found: {ref.kind}:{ref.objectId}")
        if ref.revision is not None and item.get("revision") != ref.revision: raise ValueError(f"revision mismatch for {ref.kind}:{ref.objectId}")
        if ref.fingerprint and item.get("fingerprint") != ref.fingerprint: raise ValueError(f"fingerprint mismatch for {ref.kind}:{ref.objectId}")
        pinned.append({"kind":ref.kind,"objectId":ref.objectId,"revision":item.get("revision"),"fingerprint":item.get("fingerprint"),"objectFingerprint":item.get("objectFingerprint")})
    req=payload.model_dump(mode="json"); request_fp=sha256_hex(req); handoff_id=(payload.handoffId or ("handoff_"+uuid4().hex))[:96]
    existing=db.get(CrossProductResearchHandoff,{"user_key":user_key,"handoff_id":handoff_id})
    if existing:
        if existing.request_fingerprint!=request_fp: raise ValueError("handoff id already exists with a different request")
        return {"ok":True,"replayed":True,"item":_meta(existing)}
    package={"schema":HANDOFF_SCHEMA,"handoffId":handoff_id,"projectId":payload.projectId,"sourceProduct":payload.sourceProduct,"destinationProduct":payload.destinationProduct,"intent":payload.intent,"objects":pinned,"context":payload.context}
    package_fp=sha256_hex(package)
    row=CrossProductResearchHandoff(user_key=user_key,handoff_id=handoff_id,project_id=payload.projectId,source_product=payload.sourceProduct,destination_product=payload.destinationProduct,intent=payload.intent,status="prepared",request_fingerprint=request_fp,package_fingerprint=package_fp,object_refs_json=pinned,context_json=payload.context,destination_result_json={})
    db.add(row); rec=CrossProductResearchHandoffReceipt(user_key=user_key,receipt_id="handoff-create-"+uuid4().hex[:24],handoff_id=handoff_id,action="create",source_product=payload.sourceProduct,destination_product=payload.destinationProduct,status="prepared",package_fingerprint=package_fp,details_json={"objectCount":len(pinned),"intent":payload.intent}); db.add(rec); db.commit()
    return {"ok":True,"replayed":False,"item":_meta(row),"receipt":_receipt(rec)}

def get_handoff(db,user_key,handoff_id):
    row=db.get(CrossProductResearchHandoff,{"user_key":user_key,"handoff_id":handoff_id}); return _meta(row) if row else None

def accept_handoff(db,user_key,handoff_id,payload:ResearchHandoffAcceptRequest):
    row=db.get(CrossProductResearchHandoff,{"user_key":user_key,"handoff_id":handoff_id})
    if not row: return None
    if payload.destinationProduct!=row.destination_product: raise ValueError("destination product does not match prepared handoff")
    if row.status=="accepted": return {"ok":True,"replayed":True,"item":_meta(row)}
    row.status="accepted"; row.accepted_at=datetime.now(timezone.utc); row.destination_result_json={"destinationObjectId":payload.destinationObjectId,"destinationReceiptId":payload.destinationReceiptId,"notes":payload.notes}
    rec=CrossProductResearchHandoffReceipt(user_key=user_key,receipt_id="handoff-accept-"+uuid4().hex[:24],handoff_id=handoff_id,action="accept",source_product=row.source_product,destination_product=row.destination_product,status="accepted",package_fingerprint=row.package_fingerprint,details_json=row.destination_result_json); db.add(rec); db.commit()
    return {"ok":True,"replayed":False,"item":_meta(row),"receipt":_receipt(rec)}

def list_receipts(db,user_key,limit=100):
    rows=db.scalars(select(CrossProductResearchHandoffReceipt).where(CrossProductResearchHandoffReceipt.user_key==user_key).order_by(CrossProductResearchHandoffReceipt.created_at.desc()).limit(limit)).all(); return [_receipt(x) for x in rows]
