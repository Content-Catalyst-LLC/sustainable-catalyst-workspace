from __future__ import annotations

from collections import Counter
from typing import Any
from sqlalchemy.orm import Session

from .personal_research_graph_workspace import build_graph as build_personal_graph

PROFILE_SCHEMA = "sc-shared-research-graph-runtime-profile/1.0"
GRAPH_SCHEMA = "sc-shared-research-graph/1.0"
VERSION = "3.82.0"

LENSES = (
    "all", "knowledge", "evidence", "sources", "data", "analysis",
    "timeline", "geography", "decision", "provenance",
)

NODE_KIND_GROUPS = {
    "project":"project","source":"source","citation":"source","statement":"evidence",
    "reference":"evidence","artifact":"artifact","dataset":"data","model":"model",
    "parameter-set":"analysis","execution-run":"analysis","execution-environment":"analysis",
    "runtime-adapter":"analysis","study-package":"finding","visualization-spec":"analysis",
    "scientific-receipt":"analysis","finding":"finding","decision":"decision",
}

def profile() -> dict[str, Any]:
    return {
        "schema": PROFILE_SCHEMA,
        "version": VERSION,
        "release": "Shared Research Graph Runtime & Interactive Project Knowledge Surface",
        "sharedAcrossProducts": True,
        "compatibleProductRoles": ["library","workspace","lab","workbench","decision-studio","site-intelligence"],
        "dataAuthoritySeparatedFromRenderer": True,
        "workspaceProjectAuthorityPreserved": True,
        "libraryKnowledgeAuthorityPreserved": True,
        "labExperimentAuthorityPreserved": True,
        "oneGraphContractMultipleProductLenses": True,
        "search": True,
        "nodeLayerFiltering": True,
        "relationshipFiltering": True,
        "selectionInspector": True,
        "directRelationshipTrace": True,
        "evidenceTrace": True,
        "provenanceTrace": True,
        "zoomPan": True,
        "publicDemoProject": True,
        "publicDemoContainsPrivateData": False,
        "automaticTruthDetermination": False,
        "automaticEvidenceRanking": False,
        "automaticCredibilityScoring": False,
        "automaticCausalityInference": False,
        "databaseMigrationRequired": False,
        "wordpressRequired": False,
        "lenses": list(LENSES),
    }

def _normalize_node(node: dict[str, Any], product: str = "workspace") -> dict[str, Any]:
    kind = str(node.get("kind") or "reference")
    node_id = str(node.get("id") or node.get("objectId") or "")
    return {
        **node,
        "id": node_id,
        "kind": kind,
        "group": NODE_KIND_GROUPS.get(kind, kind),
        "label": str(node.get("label") or node.get("title") or node_id),
        "sourceProduct": str(node.get("sourceProduct") or product),
        "authority": str(node.get("authority") or "workspace-project"),
        "provenanceInspectable": True,
    }

def _normalize_edge(edge: dict[str, Any]) -> dict[str, Any]:
    return {
        **edge,
        "source": str(edge.get("source") or ""),
        "target": str(edge.get("target") or ""),
        "relation": str(edge.get("relation") or "related-to"),
        "explicit": bool(edge.get("explicit", True)),
        "traceable": True,
    }

def normalize_graph(graph: dict[str, Any], *, product: str = "workspace", public_demo: bool = False) -> dict[str, Any]:
    nodes = [_normalize_node(x, product) for x in graph.get("nodes") or [] if x.get("id")]
    edges = [_normalize_edge(x) for x in graph.get("edges") or [] if x.get("source") and x.get("target")]
    kinds = Counter(x["group"] for x in nodes)
    relations = Counter(x["relation"] for x in edges)
    return {
        "schema": GRAPH_SCHEMA,
        "version": VERSION,
        "graphId": str(graph.get("graphId") or f"{product}:{graph.get('projectId') or 'graph'}"),
        "sourceProduct": product,
        "projectId": graph.get("projectId"),
        "project": graph.get("project") or {},
        "lens": graph.get("lens") or "all",
        "availableLenses": list(graph.get("availableLenses") or LENSES[1:]),
        "publicDemo": public_demo,
        "ownership": "public-demo" if public_demo else graph.get("ownership", "workspace-user-project"),
        "visibility": "public-demonstration" if public_demo else graph.get("visibility", "private-default"),
        "graphFingerprint": graph.get("graphFingerprint"),
        "nodeCount": len(nodes),
        "edgeCount": len(edges),
        "kindCounts": dict(sorted(kinds.items())),
        "relationCounts": dict(sorted(relations.items())),
        "nodes": nodes,
        "edges": edges,
        "interaction": {
            "search": True,
            "nodeLayerFiltering": True,
            "relationshipFiltering": True,
            "selectionInspector": True,
            "directRelationshipTrace": True,
            "evidenceTrace": True,
            "provenanceTrace": True,
            "zoomPan": True,
        },
        "boundaries": {
            "sourceAuthoritiesPreserved": True,
            "automaticTruthDetermination": False,
            "automaticEvidenceRanking": False,
            "automaticCausalityInference": False,
            "silentExternalKnowledgeInsertion": False,
        },
    }

def project_graph(db: Session, user_key: str, project_id: str, lens: str | None = None) -> dict[str, Any]:
    return normalize_graph(build_personal_graph(db, user_key, project_id, lens), product="workspace")

def demo_graph(lens: str | None = None) -> dict[str, Any]:
    nodes = [
        {"id":"demo:project","kind":"project","label":"Accelerated Weathering Research","lenses":list(LENSES[1:]),"summary":"A demonstration project connecting sources, evidence, data, analysis, models, findings and a decision record."},
        {"id":"demo:source:literature","kind":"source","label":"Enhanced weathering research literature","lenses":["knowledge","sources","evidence","provenance"],"summary":"Demonstration source family representing peer-reviewed enhanced-weathering research.","authority":"public-demo-source"},
        {"id":"demo:source:guidance","kind":"source","label":"Carbon accounting & inventory guidance","lenses":["knowledge","sources","evidence","provenance"],"summary":"Demonstration methodological source used to frame accounting and MRV questions.","authority":"public-demo-source"},
        {"id":"demo:evidence:dissolution","kind":"statement","label":"Field dissolution rates vary by site conditions","lenses":["knowledge","evidence","provenance"],"summary":"Demonstration evidence statement about dependence on mineral, soil, climate and field conditions."},
        {"id":"demo:evidence:mrv","kind":"statement","label":"MRV design constrains attributable claims","lenses":["knowledge","evidence","decision","provenance"],"summary":"Demonstration evidence statement highlighting monitoring and attribution constraints."},
        {"id":"demo:data:soil","kind":"dataset","label":"Soil chemistry observations","lenses":["data","analysis","provenance"],"summary":"Demonstration structured observations for pH, mineral application and soil response."},
        {"id":"demo:analysis:sensitivity","kind":"scientific-receipt","label":"Sensitivity analysis","lenses":["analysis","timeline","provenance"],"summary":"Demonstration analysis identifying assumptions with the strongest influence on outcomes."},
        {"id":"demo:model:carbon","kind":"model","label":"Carbon removal scenario model","lenses":["analysis","provenance"],"summary":"Demonstration model linking weathering assumptions, observations and uncertainty."},
        {"id":"demo:finding:site","kind":"finding","label":"Finding: outcome is strongly site-sensitive","lenses":["knowledge","evidence","analysis","decision","provenance"],"summary":"Demonstration finding derived from evidence and sensitivity analysis."},
        {"id":"demo:decision:research","kind":"decision","label":"Decision: prioritize field validation and MRV design","lenses":["decision","timeline","provenance"],"summary":"Demonstration research decision based on visible evidence gaps and uncertainty."},
    ]
    edges = [
        {"source":"demo:project","target":"demo:source:literature","relation":"contains-source"},
        {"source":"demo:project","target":"demo:source:guidance","relation":"contains-source"},
        {"source":"demo:source:literature","target":"demo:evidence:dissolution","relation":"supports"},
        {"source":"demo:source:guidance","target":"demo:evidence:mrv","relation":"supports"},
        {"source":"demo:project","target":"demo:data:soil","relation":"contains-dataset"},
        {"source":"demo:data:soil","target":"demo:analysis:sensitivity","relation":"used-by"},
        {"source":"demo:evidence:dissolution","target":"demo:analysis:sensitivity","relation":"informs"},
        {"source":"demo:evidence:mrv","target":"demo:analysis:sensitivity","relation":"constrains"},
        {"source":"demo:analysis:sensitivity","target":"demo:model:carbon","relation":"parameterizes"},
        {"source":"demo:model:carbon","target":"demo:finding:site","relation":"produces"},
        {"source":"demo:evidence:dissolution","target":"demo:finding:site","relation":"supports"},
        {"source":"demo:evidence:mrv","target":"demo:finding:site","relation":"qualifies"},
        {"source":"demo:finding:site","target":"demo:decision:research","relation":"informs"},
        {"source":"demo:evidence:mrv","target":"demo:decision:research","relation":"informs"},
    ]
    active = lens or "all"
    if active not in LENSES:
        raise ValueError(f"Unsupported shared research graph lens: {active}")
    if active != "all":
        keep = {"demo:project"}
        keep.update(n["id"] for n in nodes if active in (n.get("lenses") or []))
        nodes = [n for n in nodes if n["id"] in keep]
        edges = [e for e in edges if e["source"] in keep and e["target"] in keep]
    return normalize_graph({
        "graphId":"workspace-public-demo:accelerated-weathering",
        "projectId":"public-demo-accelerated-weathering",
        "project":{"id":"public-demo-accelerated-weathering","title":"Accelerated Weathering Research — Interactive Demo"},
        "lens":active,
        "availableLenses":list(LENSES[1:]),
        "graphFingerprint":"workspace-public-demo-accelerated-weathering-v3820",
        "nodes":nodes,
        "edges":edges,
    }, product="workspace", public_demo=True)
