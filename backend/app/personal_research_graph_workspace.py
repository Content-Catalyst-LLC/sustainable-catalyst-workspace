from __future__ import annotations

from collections import Counter
from typing import Any
from sqlalchemy.orm import Session

from .repository import get_project, project_metadata
from .scientific_objects import list_objects, relations as scientific_object_relations
from .source_evidence_citation_workspace import project_workspace as source_evidence_workspace
from .integrated_project_workspace import project_workspace as integrated_project_workspace
from .utils import sha256_hex

SCHEMA = "sc-workspace-personal-research-graph/1.0"
GRAPH_SCHEMA = "sc-workspace-personal-research-graph-model/1.0"

LENSES = (
    "knowledge",
    "evidence",
    "sources",
    "data",
    "analysis",
    "timeline",
    "geography",
    "decision",
    "provenance",
)

def profile() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "version": "3.81.0",
        "release": "Personal Research Graph & Workspace Visual Map",
        "backendAuthoritative": True,
        "projectOwned": True,
        "privateByDefault": True,
        "canonicalGraphSource": "persistent-workspace-project-and-research-objects",
        "separateGraphDatabaseRequired": False,
        "deterministicGraphProjection": True,
        "oneGraphMultipleLenses": True,
        "lenses": list(LENSES),
        "libraryKnowledgeAutomaticallyInserted": False,
        "externalKnowledgeRequiresExplicitImport": True,
        "sourceAuthoritiesPreserved": True,
        "provenancePreserved": True,
        "automaticEntityMerge": False,
        "automaticTruthDetermination": False,
        "automaticEvidenceRanking": False,
        "automaticCredibilityScoring": False,
        "automaticCausalityInference": False,
        "automaticNarrativeSelection": False,
        "genericMutation": False,
        "databaseMigrationRequired": False,
        "wordpressRequired": False,
    }

def _node(node_id: str, kind: str, label: str, **props: Any) -> dict[str, Any]:
    return {"id": node_id, "kind": kind, "label": label or node_id, **props}

def _edge(source: str, target: str, relation: str, **props: Any) -> dict[str, Any]:
    return {"source": source, "target": target, "relation": relation, **props}

def _source_node_id(source_id: str) -> str:
    return f"workspace:source:{source_id}"

def _statement_node_id(statement_id: str) -> str:
    return f"workspace:statement:{statement_id}"

def _scientific_node_id(kind: str, object_id: str) -> str:
    return f"workspace:{kind}:{object_id}"

def _lens_for_kind(kind: str) -> list[str]:
    mapping = {
        "project": ["knowledge", "provenance"],
        "source": ["knowledge", "sources", "evidence", "provenance"],
        "statement": ["knowledge", "evidence", "provenance"],
        "citation": ["sources", "evidence", "provenance"],
        "artifact": ["sources", "data", "provenance"],
        "dataset": ["data", "analysis", "provenance"],
        "model": ["analysis", "provenance"],
        "parameter-set": ["analysis", "provenance"],
        "execution-run": ["analysis", "timeline", "provenance"],
        "execution-environment": ["analysis", "provenance"],
        "runtime-adapter": ["analysis", "provenance"],
        "study-package": ["analysis", "decision", "provenance"],
        "visualization-spec": ["analysis", "knowledge", "provenance"],
        "scientific-receipt": ["analysis", "timeline", "provenance"],
    }
    return mapping.get(kind, ["knowledge", "provenance"])

def build_graph(db: Session, user_key: str, project_id: str, lens: str | None = None) -> dict[str, Any]:
    project_row = get_project(db, user_key, project_id)
    if project_row is None:
        raise KeyError(project_id)

    if lens and lens not in LENSES:
        raise ValueError(f"Unsupported research graph lens: {lens}")

    project = project_metadata(project_row)
    evidence = source_evidence_workspace(db, user_key, project_id)
    integrated = integrated_project_workspace(db, user_key, project_id)
    scientific = list_objects(db, user_key, None, project_id, None, 1000)

    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, Any]] = []

    project_node = f"workspace:project:{project_id}"
    nodes[project_node] = _node(
        project_node,
        "project",
        str(project.get("title") or project_id),
        projectId=project_id,
        revision=project.get("revision"),
        fingerprint=project.get("projectFingerprint") or project.get("fingerprint"),
        lenses=_lens_for_kind("project"),
        ownership="workspace-user-project",
        visibility="private-default",
    )

    for source in evidence.get("sources") or []:
        source_id = str(source.get("sourceId") or "")
        if not source_id:
            continue
        nid = _source_node_id(source_id)
        nodes[nid] = _node(
            nid,
            "source",
            str(source.get("title") or source_id),
            sourceId=source_id,
            publisher=source.get("publisher"),
            publishedAt=source.get("publishedAt"),
            retrievedAt=source.get("retrievedAt"),
            fingerprint=source.get("contentFingerprint"),
            sourceType=source.get("sourceType") or source.get("kind"),
            lenses=_lens_for_kind("source"),
        )
        edges.append(_edge(project_node, nid, "contains-source", humanAsserted=True))

    for statement in evidence.get("statements") or []:
        statement_id = str(statement.get("statementId") or "")
        if not statement_id:
            continue
        nid = _statement_node_id(statement_id)
        text = str(statement.get("text") or statement.get("statement") or statement.get("title") or statement_id)
        nodes[nid] = _node(
            nid,
            "statement",
            text[:240],
            statementId=statement_id,
            statementType=statement.get("statementType") or statement.get("kind"),
            status=statement.get("status"),
            revision=statement.get("revision"),
            fingerprint=statement.get("fingerprint"),
            lenses=_lens_for_kind("statement"),
        )
        edges.append(_edge(project_node, nid, "contains-statement", humanAsserted=True))

    for link in evidence.get("evidenceLinks") or []:
        sid = str(link.get("statementId") or "")
        source_id = str(link.get("sourceId") or "")
        target_ref = str(link.get("evidenceRef") or link.get("targetRef") or "")
        relation = str(link.get("relation") or "evidence-for")
        if sid:
            source_node = _statement_node_id(sid)
            if source_node in nodes:
                if source_id and _source_node_id(source_id) in nodes:
                    edges.append(_edge(_source_node_id(source_id), source_node, relation, humanAsserted=bool(link.get("humanAsserted", True)), locator=link.get("locator") or link.get("locatorRef")))
                elif target_ref:
                    target_node = f"workspace:reference:{target_ref}"
                    nodes.setdefault(target_node, _node(target_node, "reference", target_ref, reference=target_ref, lenses=["evidence", "provenance"]))
                    edges.append(_edge(target_node, source_node, relation, humanAsserted=bool(link.get("humanAsserted", True))))

    for binding in evidence.get("sourceEvidenceBindings") or []:
        source_id = str(binding.get("sourceId") or "")
        target_ref = str(binding.get("evidenceRef") or binding.get("targetRef") or "")
        if source_id and target_ref and _source_node_id(source_id) in nodes:
            target_node = f"workspace:reference:{target_ref}"
            nodes.setdefault(target_node, _node(target_node, "reference", target_ref, reference=target_ref, lenses=["evidence", "provenance"]))
            edges.append(_edge(_source_node_id(source_id), target_node, str(binding.get("relation") or "supports-reference"), humanAsserted=bool(binding.get("humanAsserted", True))))

    for item in scientific:
        kind = str(item.get("kind") or "")
        object_id = str(item.get("objectId") or "")
        if not kind or not object_id:
            continue
        nid = _scientific_node_id(kind, object_id)
        nodes[nid] = _node(
            nid,
            kind,
            str(item.get("name") or object_id),
            objectId=object_id,
            projectId=item.get("projectId"),
            revision=item.get("revision"),
            fingerprint=item.get("fingerprint"),
            createdAt=item.get("createdAt"),
            updatedAt=item.get("updatedAt"),
            summary=item.get("summary"),
            lenses=_lens_for_kind(kind),
        )
        edges.append(_edge(project_node, nid, f"contains-{kind}"))
        try:
            relation_payload = scientific_object_relations(db, user_key, kind, object_id)
        except Exception:
            relation_payload = {"items": []}
        for rel in relation_payload.get("items") or []:
            target_kind = str(rel.get("targetKind") or "")
            target_id = str(rel.get("targetId") or "")
            if target_kind == "project" and target_id == project_id:
                continue
            if not target_kind or not target_id:
                continue
            target_node = _scientific_node_id(target_kind, target_id)
            nodes.setdefault(
                target_node,
                _node(target_node, target_kind, target_id, objectId=target_id, lenses=_lens_for_kind(target_kind)),
            )
            edges.append(_edge(
                nid,
                target_node,
                str(rel.get("relation") or "related-to"),
                details=rel.get("details") or {},
            ))

    for citation in evidence.get("citations") or []:
        citation_id = str(citation.get("citationId") or "")
        if not citation_id:
            continue
        nid = f"workspace:citation:{citation_id}"
        nodes[nid] = _node(
            nid,
            "citation",
            str(citation.get("title") or citation_id),
            citationId=citation_id,
            locator=citation.get("locator"),
            fingerprint=citation.get("sourceFingerprint"),
            lenses=_lens_for_kind("citation"),
        )
        edges.append(_edge(project_node, nid, "contains-citation"))
        source_id = str(citation.get("sourceId") or "")
        statement_id = str(citation.get("statementId") or "")
        if source_id and _source_node_id(source_id) in nodes:
            edges.append(_edge(_source_node_id(source_id), nid, "cited-by"))
        if statement_id and _statement_node_id(statement_id) in nodes:
            edges.append(_edge(nid, _statement_node_id(statement_id), "cites-for-statement"))

    # De-duplicate edges deterministically.
    dedup: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for edge in edges:
        key = (
            str(edge.get("source") or ""),
            str(edge.get("target") or ""),
            str(edge.get("relation") or ""),
            str(edge.get("details") or edge.get("locator") or ""),
        )
        dedup[key] = edge
    edges = list(dedup.values())

    all_nodes = list(nodes.values())
    if lens:
        keep = {n["id"] for n in all_nodes if lens in (n.get("lenses") or []) or n["id"] == project_node}
        filtered_edges = [e for e in edges if e["source"] in keep and e["target"] in keep]
        connected = {project_node}
        for edge in filtered_edges:
            connected.add(edge["source"])
            connected.add(edge["target"])
        all_nodes = [n for n in all_nodes if n["id"] in connected]
        edges = filtered_edges

    all_nodes.sort(key=lambda x: (str(x.get("kind") or ""), str(x.get("label") or ""), str(x.get("id") or "")))
    edges.sort(key=lambda x: (str(x.get("source") or ""), str(x.get("relation") or ""), str(x.get("target") or "")))

    kind_counts = Counter(str(node.get("kind") or "unknown") for node in all_nodes)
    relation_counts = Counter(str(edge.get("relation") or "related-to") for edge in edges)

    fingerprint_payload = {
        "projectId": project_id,
        "projectFingerprint": project.get("projectFingerprint") or project.get("fingerprint"),
        "nodes": [{"id": n["id"], "kind": n["kind"], "fingerprint": n.get("fingerprint")} for n in all_nodes],
        "edges": [{"source": e["source"], "target": e["target"], "relation": e["relation"]} for e in edges],
    }
    graph_fingerprint = sha256_hex(fingerprint_payload)

    return {
        "schema": GRAPH_SCHEMA,
        "version": "3.81.0",
        "projectId": project_id,
        "project": project,
        "lens": lens or "all",
        "ownership": "workspace-user-project",
        "visibility": "private-default",
        "graphFingerprint": graph_fingerprint,
        "nodeCount": len(all_nodes),
        "edgeCount": len(edges),
        "kindCounts": dict(sorted(kind_counts.items())),
        "relationCounts": dict(sorted(relation_counts.items())),
        "nodes": all_nodes,
        "edges": edges,
        "availableLenses": list(LENSES),
        "integratedSummary": integrated.get("summary") or {},
        "sourceAuthoritiesPreserved": True,
        "libraryKnowledgeAutomaticallyInserted": False,
        "automaticTruthDetermination": False,
        "automaticEvidenceRanking": False,
        "automaticCausalityInference": False,
    }
