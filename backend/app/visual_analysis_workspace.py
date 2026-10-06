from __future__ import annotations
from typing import Any
from sqlalchemy.orm import Session

from .visualization_specs import (
    profile as visualization_profile,
    list_specs as list_visualization_specs,
    get_spec as get_visualization_spec,
    list_revisions as list_visualization_revisions,
    metadata as visualization_metadata,
)
from .visual_research_workspace import (
    profile as visual_research_profile,
    build_project_workspace as build_visual_research_workspace,
    list_snapshots as list_visual_research_snapshots,
)

SCHEMA="sc-workspace-visual-analysis-linked-views/1.0"
DETAIL_SCHEMA="sc-workspace-visual-analysis-detail/1.0"

def profile()->dict[str,Any]:
    vp=visualization_profile()
    vr=visual_research_profile()
    return {
      "schema":SCHEMA,
      "version":"3.78.0",
      "release":"Visual Analysis & Linked Views",
      "backendAuthoritative":True,
      "visualizationAuthority":"workspace-visualization-spec-registry",
      "visualResearchAuthority":"workspace-visual-research-workspace",
      "rendererNeutral":bool(vp.get("rendererNeutral")),
      "linkedViews":bool(vp.get("linkedViews")),
      "sourceProvenancePinning":bool(vp.get("sourceProvenancePinning")),
      "revisionHistory":bool(vp.get("revisionHistory")),
      "sceneGraphProjection":bool(vr.get("sceneGraphProjection")),
      "researchObjectBindingProjection":bool(vr.get("researchObjectBindingProjection")),
      "linkedViewGraph":bool(vr.get("linkedViewGraph")),
      "durableSnapshots":bool(vr.get("durableVisualWorkspaceSnapshots")),
      "browserDefinesAnalyticalMeaning":False,
      "automaticScientificInterpretation":False,
      "automaticEvidenceRanking":False,
      "genericMutation":False,
      "databaseMigrationRequired":False,
    }

def browse(db:Session,user_key:str,project_id:str|None=None,q:str|None=None,limit:int=250)->dict[str,Any]:
    items=list_visualization_specs(db,user_key,project_id,min(max(1,limit),500))
    needle=(q or "").strip().casefold()
    if needle:
        items=[x for x in items if needle in " ".join(str(x.get(k) or "") for k in ("visualizationId","projectId","title","sceneKind","specFingerprint")).casefold()]
    project_workspace=None
    snapshots=[]
    if project_id:
        try:
            project_workspace=build_visual_research_workspace(db,user_key,project_id)
            snapshots=list_visual_research_snapshots(db,user_key,project_id,100)
        except KeyError:
            project_workspace=None
    linked_edges=0
    source_refs=0
    node_count=0
    if isinstance(project_workspace,dict):
        linked_edges=int(project_workspace.get("linkedViewEdgeCount") or 0)
        source_refs=len(project_workspace.get("sourceRefs") or [])
        graph=project_workspace.get("sceneGraph") or {}
        node_count=len(graph.get("nodes") or [])
    return {
      "schema":SCHEMA,"version":"3.78.0","projectId":project_id or "","query":q or "",
      "visualizations":items,"count":len(items),
      "projectVisualResearch":project_workspace,
      "snapshots":snapshots,
      "summary":{"visualizations":len(items),"linkedViewEdges":linked_edges,"sourceReferences":source_refs,"sceneGraphNodes":node_count,"snapshots":len(snapshots)},
      "canonicalMutationEndpoint":"/v1/visualization-specs",
      "automaticScientificInterpretation":False,
    }

def detail(db:Session,user_key:str,visualization_id:str)->dict[str,Any]|None:
    row=get_visualization_spec(db,user_key,visualization_id)
    if row is None:return None
    item=visualization_metadata(row)
    revisions=list_visualization_revisions(db,user_key,visualization_id,100)
    spec=row.spec_json or {}
    return {
      "schema":DETAIL_SCHEMA,"version":"3.78.0","item":item,"spec":spec,
      "revisions":revisions,"revisionCount":len(revisions),
      "sceneKind":item.get("sceneKind"),"specFingerprint":item.get("specFingerprint"),
      "views":list(spec.get("views") or []),"sources":list(spec.get("sources") or []),
      "links":list(spec.get("links") or []),"interactions":list(spec.get("interactions") or []),
      "sourceProvenancePinned":True,"rendererNeutral":True,
      "browserDefinesAnalyticalMeaning":False,
    }
