from __future__ import annotations
from typing import Any
from sqlalchemy.orm import Session

from .repository import get_project, project_metadata
from .source_evidence_citation_workspace import project_workspace as source_evidence_workspace
from .dataset_exploration_workspace import browse as dataset_workspace
from .model_runtime_workspace import browse as model_runtime_workspace
from .visual_analysis_workspace import browse as visual_analysis_workspace
from .session_timeline_workspace import timeline as session_timeline_workspace

SCHEMA="sc-workspace-integrated-research-project/1.0"

def profile()->dict[str,Any]:
    return {
      "schema":SCHEMA,
      "version":"3.80.0",
      "release":"Integrated Research Project Workspace",
      "backendAuthoritative":True,
      "projectAuthority":"workspace-project-registry",
      "sourceEvidenceIntegrated":True,
      "datasetsIntegrated":True,
      "modelsRuntimesIntegrated":True,
      "visualAnalysisIntegrated":True,
      "sessionTimelineIntegrated":True,
      "crossWorkspaceSummary":True,
      "sourceAuthoritiesPreserved":True,
      "standaloneFirst":True,
      "wordpressRequired":False,
      "genericMutation":False,
      "automaticScientificInterpretation":False,
      "automaticTruthDetermination":False,
      "automaticModelSelection":False,
      "automaticExecution":False,
      "databaseMigrationRequired":False,
    }

def project_workspace(db:Session,user_key:str,project_id:str)->dict[str,Any]:
    row=get_project(db,user_key,project_id)
    if row is None:
        raise KeyError(project_id)

    project=project_metadata(row)
    evidence=source_evidence_workspace(db,user_key,project_id)
    datasets=dataset_workspace(db,user_key,project_id,None,None,None,500)
    models=model_runtime_workspace(db,user_key,project_id,None,250)
    visuals=visual_analysis_workspace(db,user_key,project_id,None,250)
    timeline=session_timeline_workspace(db,user_key,project_id,500)

    ec=evidence.get("counts") or {}
    mc=models.get("counts") or {}
    vs=visuals.get("summary") or {}

    summary={
      "sources":int(ec.get("sources") or 0),
      "statements":int(ec.get("statements") or 0),
      "evidenceLinks":int(ec.get("evidenceLinks") or 0)+int(ec.get("sourceEvidenceBindings") or 0),
      "citations":int(ec.get("citations") or 0),
      "datasets":int(datasets.get("count") or 0),
      "models":int(mc.get("models") or 0),
      "executionEnvironments":int(mc.get("environments") or 0),
      "runtimeAdapters":int(mc.get("runtimeAdapters") or 0),
      "recentRuns":int(mc.get("recentRuns") or 0),
      "visualizations":int(vs.get("visualizations") or 0),
      "linkedViewEdges":int(vs.get("linkedViewEdges") or 0),
      "timelineEvents":int(timeline.get("count") or 0),
    }

    return {
      "schema":SCHEMA,
      "version":"3.80.0",
      "project":project,
      "summary":summary,
      "workspaces":{
        "sourceEvidenceCitation":evidence,
        "datasets":datasets,
        "modelsRuntimes":models,
        "visualAnalysis":visuals,
        "sessionTimeline":timeline,
      },
      "canonicalMutationEndpoints":{
        "project":"/v1/projects",
        "datasets":"/v1/datasets",
        "models":"/v1/models",
        "executionEnvironments":"/v1/execution-environments",
        "runtimeAdapters":"/v1/runtime-adapters",
        "visualizations":"/v1/visualization-specs",
      },
      "sourceAuthoritiesPreserved":True,
      "automaticScientificInterpretation":False,
      "automaticTruthDetermination":False,
      "automaticExecution":False,
    }
