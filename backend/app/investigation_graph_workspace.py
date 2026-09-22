from __future__ import annotations

from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import (
    InvestigationGraphSnapshot,
    InvestigationHypothesisSet,
    InvestigationStatementHead,
    ProjectHead,
)
from .investigative_research_workspace import build_project_workspace as build_investigative_workspace
from .utils import iso, sha256_hex

INVESTIGATION_GRAPH_WORKSPACE_SCHEMA = "sc-workspace-investigation-graph-contradiction-hypothesis-workspace/1.0"
INVESTIGATION_GRAPH_SCHEMA = "sc-workspace-investigation-graph/2.0"
HYPOTHESIS_SET_REQUEST_SCHEMA = "sc-workspace-investigation-hypothesis-set-request/1.0"
HYPOTHESIS_SET_SCHEMA = "sc-workspace-investigation-hypothesis-set/1.0"
GRAPH_SNAPSHOT_REQUEST_SCHEMA = "sc-workspace-investigation-graph-snapshot-request/1.0"
GRAPH_SNAPSHOT_SCHEMA = "sc-workspace-investigation-graph-snapshot/1.0"
HYPOTHESIS_SET_STATUSES = ("open", "under-review", "documented", "unresolved", "closed")

class InvestigationHypothesisSetRequest(BaseModel):
    schema: Literal["sc-workspace-investigation-hypothesis-set-request/1.0"]
    projectId: str = Field(min_length=1, max_length=160)
    hypothesisSetId: str = Field(default="", max_length=160)
    title: str = Field(min_length=1, max_length=500)
    description: str = Field(default="", max_length=8000)
    questionStatementId: str = Field(default="", max_length=160)
    hypothesisStatementIds: list[str] = Field(min_length=2, max_length=50)
    status: Literal["open", "under-review", "documented", "unresolved", "closed"] = "open"
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def unique_hypotheses(self):
        ids=[x for x in self.hypothesisStatementIds if x]
        if len(set(ids)) != len(ids):
            raise ValueError("hypothesisStatementIds must be unique")
        return self

class InvestigationGraphSnapshotRequest(BaseModel):
    schema: Literal["sc-workspace-investigation-graph-snapshot-request/1.0"]
    includeVisualGraph: bool = True


def profile() -> dict[str, Any]:
    return {
        "schema": INVESTIGATION_GRAPH_WORKSPACE_SCHEMA,
        "workspaceVersion": "3.8.0",
        "release": "Investigation Graph, Contradiction & Competing Hypothesis Workspace",
        "backendAuthoritative": True,
        "referenceFirst": True,
        "specialistObjectAuthorityPreserved": True,
        "hypothesisSets": True,
        "contradictionClusters": True,
        "competingHypothesisMatrix": True,
        "descriptiveCoverage": True,
        "immutableGraphSnapshots": True,
        "visualResearchGraphOverlay": True,
        "humanAssertedRelationsPreserved": True,
        "automaticTruthDetermination": False,
        "automaticEvidenceRanking": False,
        "automaticHypothesisRanking": False,
        "preferredHypothesisSelection": False,
        "automaticDecisionAuthority": False,
    }


def _project(db: Session, user_key: str, project_id: str) -> ProjectHead:
    row=db.get(ProjectHead,{"user_key":user_key,"project_id":project_id})
    if row is None: raise KeyError(project_id)
    return row


def _statement(db: Session, user_key: str, statement_id: str) -> InvestigationStatementHead | None:
    return db.get(InvestigationStatementHead,{"user_key":user_key,"statement_id":statement_id})


def hypothesis_set_metadata(row: InvestigationHypothesisSet) -> dict[str, Any]:
    return {
        "schema": HYPOTHESIS_SET_SCHEMA,
        "hypothesisSetId": row.hypothesis_set_id,
        "projectId": row.project_id,
        "title": row.title,
        "description": row.description,
        "questionStatementId": row.question_statement_id,
        "hypothesisStatementIds": row.hypothesis_ids_json or [],
        "status": row.status,
        "setFingerprint": row.set_fingerprint,
        "metadata": row.metadata_json or {},
        "createdAt": iso(row.created_at),
        "updatedAt": iso(row.updated_at),
    }


def store_hypothesis_set(db: Session, user_key: str, payload: InvestigationHypothesisSetRequest) -> tuple[dict[str, Any], bool]:
    _project(db,user_key,payload.projectId)
    ids=list(dict.fromkeys(payload.hypothesisStatementIds))
    for sid in ids:
        row=_statement(db,user_key,sid)
        if row is None: raise LookupError(sid)
        if row.project_id != payload.projectId: raise ValueError("hypothesis statement belongs to a different project")
        if row.statement_type != "hypothesis": raise ValueError(f"statement {sid} is not a hypothesis")
    if payload.questionStatementId:
        q=_statement(db,user_key,payload.questionStatementId)
        if q is None: raise LookupError(payload.questionStatementId)
        if q.project_id != payload.projectId: raise ValueError("question statement belongs to a different project")
    set_id=payload.hypothesisSetId or ("hypothesis-set-"+uuid4().hex[:24])
    row=db.get(InvestigationHypothesisSet,{"user_key":user_key,"hypothesis_set_id":set_id})
    created=row is None
    if row is not None and row.project_id != payload.projectId: raise ValueError("hypothesis set belongs to a different project")
    fp=sha256_hex({"projectId":payload.projectId,"hypothesisSetId":set_id,"title":payload.title,"description":payload.description,"questionStatementId":payload.questionStatementId,"hypothesisStatementIds":sorted(ids),"status":payload.status,"metadata":payload.metadata})
    if row is None:
        row=InvestigationHypothesisSet(user_key=user_key,hypothesis_set_id=set_id,project_id=payload.projectId)
        db.add(row)
    row.title=payload.title; row.description=payload.description; row.question_statement_id=payload.questionStatementId
    row.hypothesis_ids_json=ids; row.status=payload.status; row.set_fingerprint=fp; row.metadata_json=payload.metadata
    db.commit(); db.refresh(row)
    return hypothesis_set_metadata(row), created


def list_hypothesis_sets(db: Session, user_key: str, project_id: str | None=None, limit: int=250) -> list[dict[str, Any]]:
    q=select(InvestigationHypothesisSet).where(InvestigationHypothesisSet.user_key==user_key)
    if project_id: q=q.where(InvestigationHypothesisSet.project_id==project_id)
    rows=db.scalars(q.order_by(InvestigationHypothesisSet.updated_at.desc()).limit(limit)).all()
    return [hypothesis_set_metadata(x) for x in rows]


def get_hypothesis_set(db: Session,user_key: str,set_id: str) -> dict[str,Any] | None:
    row=db.get(InvestigationHypothesisSet,{"user_key":user_key,"hypothesis_set_id":set_id})
    return hypothesis_set_metadata(row) if row else None


def build_graph(db: Session,user_key: str,project_id: str,include_visual_graph: bool=True) -> dict[str,Any]:
    base=build_investigative_workspace(db,user_key,project_id,include_visual_graph)
    graph=base.get("graph") or {"nodes":[],"edges":[]}
    sets=list_hypothesis_sets(db,user_key,project_id,500)
    nodes=list(graph.get("nodes") or [])
    edges=list(graph.get("edges") or [])
    for hs in sets:
        set_node=f"workspace:hypothesis-set:{hs['hypothesisSetId']}"
        nodes.append({"id":set_node,"kind":"hypothesis-set","hypothesisSetId":hs["hypothesisSetId"],"title":hs["title"],"status":hs["status"],"fingerprint":hs["setFingerprint"]})
        for sid in hs.get("hypothesisStatementIds") or []:
            edges.append({"source":set_node,"target":f"workspace:investigation-statement:{sid}","relation":"contains-competing-hypothesis","humanCurated":True})
        if hs.get("questionStatementId"):
            edges.append({"source":f"workspace:investigation-statement:{hs['questionStatementId']}","target":set_node,"relation":"frames-hypothesis-set","humanCurated":True})
    nodes=sorted(nodes,key=lambda x:str(x.get("id") or ""))
    edges=sorted(edges,key=lambda x:(str(x.get("source") or ""),str(x.get("target") or ""),str(x.get("relation") or "")))
    out={"schema":INVESTIGATION_GRAPH_SCHEMA,"projectId":project_id,"nodes":nodes,"edges":edges}
    out["graphFingerprint"]=sha256_hex(out)
    return out


def contradiction_clusters(db: Session,user_key: str,project_id: str) -> dict[str,Any]:
    base=build_investigative_workspace(db,user_key,project_id,False)
    statements={x["statementId"]:x for x in base.get("statements") or []}
    adjacency: dict[str,set[str]]={}
    links=[]
    for rel in base.get("statementRelations") or []:
        if rel.get("relation") != "contradicts": continue
        a=str(rel.get("fromStatementId") or ""); b=str(rel.get("toStatementId") or "")
        if not a or not b: continue
        adjacency.setdefault(a,set()).add(b); adjacency.setdefault(b,set()).add(a); links.append(rel)
    seen=set(); clusters=[]
    for start in sorted(adjacency):
        if start in seen: continue
        stack=[start]; comp=[]; seen.add(start)
        while stack:
            cur=stack.pop(); comp.append(cur)
            for nxt in sorted(adjacency.get(cur,set())):
                if nxt not in seen: seen.add(nxt); stack.append(nxt)
        clusters.append({"clusterId":"contradiction-cluster-"+sha256_hex(sorted(comp))[:20],"statementIds":sorted(comp),"statements":[statements[x] for x in sorted(comp) if x in statements],"relationCount":sum(1 for r in links if r.get("fromStatementId") in comp and r.get("toStatementId") in comp)})
    return {"schema":"sc-workspace-investigation-contradiction-clusters/1.0","projectId":project_id,"clusters":clusters,"count":len(clusters),"automaticResolution":False,"automaticTruthDetermination":False}


def hypothesis_matrix(db: Session,user_key: str,project_id: str) -> dict[str,Any]:
    base=build_investigative_workspace(db,user_key,project_id,False)
    evidence=base.get("evidenceLinks") or []
    sets=list_hypothesis_sets(db,user_key,project_id,500)
    rows=[]
    for hs in sets:
        cols=[]
        for sid in hs.get("hypothesisStatementIds") or []:
            rels={k:0 for k in ("supports","contradicts","contextualizes","challenges","derived-from","corroborates")}
            refs=[]
            for link in evidence:
                if link.get("statementId") != sid: continue
                r=str(link.get("relation") or "")
                if r in rels: rels[r]+=1
                refs.append({"evidenceLinkId":link.get("evidenceLinkId"),"evidenceRef":link.get("evidenceRef"),"relation":r,"sourceFingerprint":link.get("sourceFingerprint")})
            cols.append({"hypothesisStatementId":sid,"relationshipCounts":rels,"evidenceReferences":refs})
        rows.append({"hypothesisSet":hs,"hypotheses":cols})
    return {"schema":"sc-workspace-competing-hypothesis-matrix/1.0","projectId":project_id,"sets":rows,"count":len(rows),"descriptiveOnly":True,"automaticHypothesisRanking":False,"preferredHypothesisSelection":False}


def coverage(db: Session,user_key: str,project_id: str) -> dict[str,Any]:
    base=build_investigative_workspace(db,user_key,project_id,False)
    evidence=base.get("evidenceLinks") or []
    relations=base.get("statementRelations") or []
    statements=base.get("statements") or []
    by_statement={x["statementId"]:{"evidenceLinks":0,"statementRelations":0} for x in statements}
    for x in evidence:
        sid=x.get("statementId")
        if sid in by_statement: by_statement[sid]["evidenceLinks"]+=1
    for x in relations:
        for sid in (x.get("fromStatementId"),x.get("toStatementId")):
            if sid in by_statement: by_statement[sid]["statementRelations"]+=1
    uncovered=[sid for sid,c in by_statement.items() if c["evidenceLinks"]==0]
    return {"schema":"sc-workspace-investigation-descriptive-coverage/1.0","projectId":project_id,"statementCoverage":by_statement,"statementsWithoutEvidenceLinks":sorted(uncovered),"counts":{"statements":len(statements),"withEvidence":len(statements)-len(uncovered),"withoutEvidence":len(uncovered)},"qualityScore":None,"automaticEvidenceRanking":False}


def graph_snapshot_metadata(row: InvestigationGraphSnapshot) -> dict[str,Any]:
    return {"schema":GRAPH_SNAPSHOT_SCHEMA,"snapshotId":row.snapshot_id,"projectId":row.project_id,"graphFingerprint":row.graph_fingerprint,"contradictionClusterCount":row.contradiction_cluster_count,"hypothesisSetCount":row.hypothesis_set_count,"nodeCount":row.node_count,"edgeCount":row.edge_count,"createdAt":iso(row.created_at)}


def create_graph_snapshot(db: Session,user_key: str,project_id: str,payload: InvestigationGraphSnapshotRequest) -> dict[str,Any]:
    graph=build_graph(db,user_key,project_id,payload.includeVisualGraph)
    clusters=contradiction_clusters(db,user_key,project_id)
    sets=list_hypothesis_sets(db,user_key,project_id,500)
    row=InvestigationGraphSnapshot(user_key=user_key,snapshot_id="investigation-graph-snapshot-"+uuid4().hex[:24],project_id=project_id,graph_fingerprint=graph["graphFingerprint"],contradiction_cluster_count=int(clusters["count"]),hypothesis_set_count=len(sets),node_count=len(graph["nodes"]),edge_count=len(graph["edges"]),graph_json={"graph":graph,"contradictions":clusters,"hypothesisSets":sets})
    db.add(row); db.commit(); db.refresh(row)
    return graph_snapshot_metadata(row)


def list_graph_snapshots(db: Session,user_key: str,project_id: str,limit: int=100) -> list[dict[str,Any]]:
    rows=db.scalars(select(InvestigationGraphSnapshot).where(InvestigationGraphSnapshot.user_key==user_key,InvestigationGraphSnapshot.project_id==project_id).order_by(InvestigationGraphSnapshot.created_at.desc()).limit(limit)).all()
    return [graph_snapshot_metadata(x) for x in rows]
